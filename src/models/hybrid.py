from .cbf import ContentBasedRecommender
from .cf import CollaborativeRecommender
import pandas as pd

class HybridRecommender:
    """
    Hybrid Recommender blending Content-Based and Collaborative Filtering.
    """
    def __init__(self, movies_df, similarity_matrix, svd_model_path):
        self.cbf = ContentBasedRecommender(movies_df, similarity_matrix)
        self.cf = CollaborativeRecommender()
        self.cf.load_model(svd_model_path)
        self.movies = movies_df
        
    def _get_year_bucket(self, title):
        import re
        import datetime
        match = re.search(r'\((\d{4})\)', title)
        year = int(match.group(1)) if match else 0
        current_year = datetime.datetime.now().year
        
        # Bucket 0: Current (current_year - 1 or newer)
        if year >= current_year - 1:
            return 0
        # Bucket 1: Past 2 years (current_year - 3 to current_year - 2)
        elif year >= current_year - 3:
            return 1
        # Bucket 2: Older (<= current_year - 4 or year 0)
        else:
            return 2

    def recommend(self, user_id, movie_title, top_n=10):
        """
        Improved Recommendation strategy:
        1. Get Content-Based Candidates with similarity scores.
        2. Identify metadata of the source movie (language, genres).
        3. Combine Content Score + Collaborative Prediction.
        4. Apply Genre and Language boosts.
        """
        # Step 1: Get Content-Based Candidates (top 100 for better reranking)
        cbf_results = self.cbf.get_recommendations_with_scores(movie_title, top_n=100)
        
        if not cbf_results:
            return []
            
        # Get source movie metadata for boosting
        try:
            source_movie = self.movies[self.movies['title'] == movie_title].iloc[0]
            source_genres = set(source_movie['genres']) if isinstance(source_movie['genres'], list) else set()
            source_lang = source_movie.get('language', 'Unknown')
        except IndexError:
            source_genres = set()
            source_lang = "Unknown"

        title_to_id = pd.Series(self.movies['movieId'].values, index=self.movies['title']).to_dict()
        
        final_recommendations = []
        
        for title, content_score in cbf_results:
            mid = title_to_id.get(title)
            if mid is None:
                continue
                
            # Get Collaborative Filtering Prediction (normalized to 0-1 range for blending)
            # SVD usually predicts 1-5, so we use (pred - 1) / 4
            cf_pred = self.cf.predict(user_id, mid)
            cf_score = (cf_pred - 1) / 4.0
            
            # Step 2: Get candidate metadata
            movie_row = self.movies[self.movies['movieId'] == mid].iloc[0]
            cand_genres = set(movie_row['genres']) if isinstance(movie_row['genres'], list) else set()
            cand_lang = movie_row.get('language', 'Unknown')
            
            # Step 3: Calculate Final Score
            # Base Blend: 40% Content + 40% Collaborative
            final_score = (content_score * 0.4) + (cf_score * 0.4)
            
            # Step 4: Metadata Boosting
            # Language Boost: Significant multiplier if languages match perfectly
            if cand_lang == source_lang and source_lang != "Unknown":
                final_score += 0.2
            
            # Genre Boost: Incremental boost for each matching genre
            matching_genres = source_genres.intersection(cand_genres)
            if matching_genres:
                final_score += (len(matching_genres) * 0.05)
                
            # South Indian Boost (Global priority)
            if cand_lang in ['Tamil', 'Telugu', 'Malayalam', 'Kannada']:
                final_score += 0.05

            final_recommendations.append({
                'movieId': mid,
                'title': title,
                'genres': list(cand_genres),
                'type': movie_row.get('type', 'Movie'),
                'language': cand_lang,
                'actors': movie_row.get('actors', 'Unknown'),
                'tmdbId': movie_row.get('tmdbId', 0),
                'score': final_score
            })
            
        # Sort by year bucket (ascending) and then by score (descending)
        final_recommendations.sort(key=lambda x: (self._get_year_bucket(x['title']), -x['score']))
        return final_recommendations[:top_n]

    def recommend_by_metadata(self, user_id, genres, language="All", top_n=10):
        """
        Recommend movies based on target genres and language.
        """
        filtered_movies = self.movies.copy()
        
        # Filter by language if specified
        if language != "All":
            filtered_movies = filtered_movies[filtered_movies['language'] == language]
            
        # If no movies match language, fallback to all (safeguard)
        if filtered_movies.empty:
            filtered_movies = self.movies.copy()
            
        # Calculate scores for candidate movies
        final_recommendations = []
        target_genres = set(genres) if genres else set()
        
        # Limit candidates for speed (e.g. top 500 by global popularity or random)
        candidates = filtered_movies
        if len(candidates) > 1000:
            candidates = candidates.sample(1000, random_state=42)
            
        for _, movie_row in candidates.iterrows():
            mid = movie_row['movieId']
            cand_genres = set(movie_row['genres']) if isinstance(movie_row['genres'], list) else set()
            cand_lang = movie_row.get('language', 'Unknown')
            
            # Collaborative Filtering Prediction
            cf_pred = self.cf.predict(user_id, mid)
            cf_score = (cf_pred - 1) / 4.0
            
            # Genre Match Score
            genre_match_score = 0
            if target_genres:
                matching = target_genres.intersection(cand_genres)
                genre_match_score = (len(matching) / len(target_genres)) if target_genres else 0
            
            # Final Blend
            # 60% Genre Match + 40% Predicted Rating
            final_score = (genre_match_score * 0.6) + (cf_score * 0.4)
            
            # Small South Indian Boost
            if cand_lang in ['Tamil', 'Telugu', 'Malayalam', 'Kannada']:
                final_score += 0.05

            final_recommendations.append({
                'movieId': mid,
                'title': movie_row['title'],
                'genres': list(cand_genres),
                'type': movie_row.get('type', 'Movie'),
                'language': cand_lang,
                'actors': movie_row.get('actors', 'Unknown'),
                'tmdbId': movie_row.get('tmdbId', 0),
                'score': final_score
            })
            
        # Sort by year bucket (ascending) and then by score (descending)
        final_recommendations.sort(key=lambda x: (self._get_year_bucket(x['title']), -x['score']))
        return final_recommendations[:top_n]
