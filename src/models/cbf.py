import pandas as pd
import numpy as np

class ContentBasedRecommender:
    """
    Content-Based Filtering Recommender using Cosine Similarity on TF-IDF features.
    """
    def __init__(self, movies_df, similarity_matrix):
        self.movies = movies_df
        # Create a reverse mapping of movie titles to indices
        self.indices = pd.Series(self.movies.index, index=self.movies['title']).drop_duplicates()
        self.similarity_matrix = similarity_matrix
        
    def get_recommendations(self, title, top_n=10):
        """
        Get similar movie recommendations based on content (genres/soup).
        """
        # Checks if title exists
        if title not in self.indices:
            return []

        # Get the index of the movie that matches the title
        idx = self.indices[title]

        # Get the pairwise similarity scores of all movies with that movie
        # Handle case where idx might be a Series if duplicates exist (though dropped above)
        if isinstance(idx, pd.Series):
             idx = idx.iloc[0]

        sim_scores = list(enumerate(self.similarity_matrix[idx]))

        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the scores of the 10 most similar movies
        # Skip 0 because it's the movie itself
        sim_scores = sim_scores[1:top_n+1]

        # Get the movie indices
        movie_indices = [i[0] for i in sim_scores]

        # Return the top 10 most similar movies
        return self.movies['title'].iloc[movie_indices].tolist()
    def get_recommendations_with_scores(self, title, top_n=10):
        """
        Get similar movie recommendations with their similarity scores.
        """
        if title not in self.indices:
            return []

        idx = self.indices[title]
        if isinstance(idx, pd.Series):
             idx = idx.iloc[0]

        sim_scores = list(enumerate(self.similarity_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Skip 0 because it's the movie itself
        sim_scores = sim_scores[1:top_n+1]

        results = []
        for i, score in sim_scores:
            results.append((self.movies['title'].iloc[i], float(score)))
            
        return results
