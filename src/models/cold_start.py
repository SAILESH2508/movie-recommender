import pandas as pd

class ColdStartRecommender:
    """
    Handles recommendations for new users or new items using popularity-based measures.
    """
    def __init__(self, movies_df, ratings_df):
        self.movies = movies_df
        self.ratings = ratings_df
        
    def get_popular_recommendations(self, top_n=10):
        """
        Returns the most popular movies based on weighted rating.
        Formula: Weighted Rating (WR) = (v / (v+m)) * R + (m / (v+m)) * C
        v = number of votes for the movie
        m = minimum votes required to be listed
        R = average rating of the movie
        C = mean vote across the whole report
        """
        # Calculate Vote Count and Average Rating
        vote_counts = self.ratings.groupby('movieId').count()['rating']
        vote_averages = self.ratings.groupby('movieId').mean()['rating']
        
        # C: Mean vote across the whole dataset
        C = vote_averages.mean()
        
        # m: Minimum votes required (e.g., 90th percentile)
        m = vote_counts.quantile(0.90)
        
        # Filter movies that qualify
        qualified_movies = pd.DataFrame()
        qualified_movies['vote_count'] = vote_counts
        qualified_movies['vote_average'] = vote_averages
        qualified_movies = qualified_movies[qualified_movies['vote_count'] >= m]
        
        # Calculate Weighted Rating
        def weighted_rating(x, m=m, C=C):
            v = x['vote_count']
            R = x['vote_average']
            return (v/(v+m) * R) + (m/(v+m) * C)
        
        qualified_movies['wr'] = qualified_movies.apply(weighted_rating, axis=1)
        
        # Sort and return titles
        qualified_movies = qualified_movies.sort_values('wr', ascending=False).head(top_n)
        
        # Join with titles
        return self.movies[self.movies['movieId'].isin(qualified_movies.index)]['title'].tolist()
