import pandas as pd
import os
import argparse
from src.models.cf import CollaborativeRecommender

PROCESSED_DATA_PATH = "data/processed"
MODEL_PATH = "data/processed/svd_model.pkl"

def main():
    print("Starting Offline Training Pipeline...")
    
    # 1. Load Processed Data
    ratings_path = os.path.join(PROCESSED_DATA_PATH, "ratings.pkl")
    if not os.path.exists(ratings_path):
        print(f"Error: {ratings_path} not found. Run src/data_preprocessing.py first.")
        return

    print("Loading ratings data...")
    ratings = pd.read_pickle(ratings_path)
    print(f"Loaded {len(ratings)} ratings.")
    
    # 2. Train Collaborative Filtering Model (SVD)
    print("Training SVD Model (this may take a while)...")
    recommender = CollaborativeRecommender()
    
    # Optional: Grid Search (skipping for speed in default run, can enable via flag)
    # recommender.train(ratings, perform_grid_search=True) 
    recommender.train(ratings)
    print("Training Complete.")
    
    # 3. Save Model
    print(f"Saving model to {MODEL_PATH}...")
    recommender.save_model(MODEL_PATH)
    print("Model saved successfully.")

if __name__ == "__main__":
    main()
