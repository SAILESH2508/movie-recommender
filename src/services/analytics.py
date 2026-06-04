import pandas as pd
from src.database import DatabaseManager

class AnalyticsService:
    """
    Provides statistics for the dashboard.
    """
    def __init__(self, movies_df, ratings_df):
        self.movies = movies_df
        self.ratings = ratings_df
        self.db = DatabaseManager()

    def get_platform_stats(self):
        """
        Returns high-level platform statistics.
        """
        total_movies = len(self.movies)
        
        # Merge static ratings (dataset) + dynamic ratings (DB)
        # For this mock, we just count them separate or sum them
        static_ratings_count = len(self.ratings)
        dynamic_ratings_count = self.db.get_all_ratings_count()
        
        total_ratings = static_ratings_count + dynamic_ratings_count
        
        return {
            "total_movies": total_movies,
            "total_ratings": total_ratings,
            "active_users_db": self.db.execute_query("SELECT COUNT(*) FROM users")[0][0]
        }
    
    def get_genre_distribution(self):
        """
        Returns genre counts.
        """
        # Explode genres
        genres_exploded = self.movies.explode('genres')
        return genres_exploded['genres'].value_counts()
