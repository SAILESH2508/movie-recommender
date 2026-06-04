from sklearn.decomposition import TruncatedSVD
import pandas as pd
import numpy as np
import pickle

class CollaborativeRecommender:
    """
    Collaborative Filtering Recommender using Matrix Factorization (Truncated SVD)
    from scikit-learn.
    """
    def __init__(self):
        self.model = None
        self.user_ids = None
        self.movie_ids = None
        self.matrix_df = None
        self.predicted_ratings = None
    
    def train(self, ratings_df, n_components=20):
        """
        Trains the SVD model on the ratings data.
        """
        # Create User-Item Matrix
        # Handle duplicates by taking the mean rating
        self.matrix_df = ratings_df.pivot_table(index='userId', columns='movieId', values='rating', aggfunc='mean').fillna(0)
        
        # Save indices to map back later
        self.user_ids = self.matrix_df.index
        self.movie_ids = self.matrix_df.columns
        
        # Decompose
        X = self.matrix_df.values
        self.model = TruncatedSVD(n_components=n_components, random_state=42)
        matrix_reduced = self.model.fit_transform(X)
        
        # Reconstruct Matrix (Predictions)
        # R_hat = U * Sigma * Vt  (Approx)
        # TruncatedSVD 'fit_transform' returns U * Sigma (sort of, strictly it returns X_transformed)
        # To get back to original space: inverse_transform
        
        self.predicted_ratings = self.model.inverse_transform(matrix_reduced)
        
        # Convert back to DF for easier lookup (optional, but convenient for small data)
        self.predicted_ratings_df = pd.DataFrame(
            self.predicted_ratings, 
            index=self.user_ids, 
            columns=self.movie_ids
        )
            
    def predict(self, user_id, movie_id):
        """
        Predicts rating for a given user and movie.
        """
        if self.predicted_ratings_df is None:
            raise Exception("Model not trained yet.")
        
        if user_id in self.predicted_ratings_df.index and movie_id in self.predicted_ratings_df.columns:
            return self.predicted_ratings_df.loc[user_id, movie_id]
        
        # Cold start fallback (mean rating)
        return 3.0

    def save_model(self, path):
        # We save the predicted matrix roughly
        # Or better: save the class instance
        with open(path, 'wb') as f:
            pickle.dump(self, f)
            
    def load_model(self, path):
        with open(path, 'rb') as f:
             loaded = pickle.load(f)
             self.__dict__.update(loaded.__dict__)
