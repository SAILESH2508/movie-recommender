import pandas as pd
import numpy as np
import random
import os

# Constants
OUTPUT_PATH = "data/raw"
NUM_MOVIES = 2000
NUM_RATINGS = 10000

# Word Banks for Title Generation
ADJECTIVES = ["Dark", "Eternal", "Savage", "Hidden", "Lost", "Silent", "Brave", "Final", "Last", "First", 
              "Golden", "Silver", "Iron", "Broken", "Rising", "Falling", "Secret", "Mystic", "Crimson", "Azure",
              "Infinite", "Frozen", "Burning", "Shattered", "Awakened", "Forgotten", "Legendary", "Ancient"]

NOUNS = ["Warrior", "Dream", "Kingdom", "Empire", "Legacy", "Destiny", "Shadow", "Light", "Sky", "Star",
         "Force", "Titan", "Guardian", "Revenge", "Justice", "Storm", "Thunder", "Ocean", "Forest", "Mountain",
         "Prophecy", "Illusion", "Dimension", "Protocol", "Algorithm", "Code", "Memory", "Soul", "Heart"]

GENRES = ["Action", "Adventure", "Animation", "Children", "Comedy", "Crime", "Documentary", 
          "Drama", "Fantasy", "Film-Noir", "Horror", "Musical", "Mystery", "Romance", 
          "Sci-Fi", "Thriller", "War", "Western"]

def generate_title():
    pattern = random.choice([1, 2, 3])
    if pattern == 1:
        return f"The {random.choice(ADJECTIVES)} {random.choice(NOUNS)}"
    elif pattern == 2:
        return f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"
    else:
        return f"{random.choice(NOUNS)} of the {random.choice(ADJECTIVES)} {random.choice(NOUNS)}"

def generate_data():
    print(f"Generating {NUM_MOVIES} synthetic movies...")
    
    # 1. Generate Movies
    movies_data = []
    # Start ID after typical MovieLens range to avoid collision (e.g. 200000)
    start_id = 200000 
    
    for i in range(NUM_MOVIES):
        mid = start_id + i
        title = generate_title()
        # Assign 1-3 random genres
        num_genres = random.randint(1, 3)
        genres = "|".join(random.sample(GENRES, num_genres))
        movies_data.append([mid, title, genres])
        
    movies_df = pd.DataFrame(movies_data, columns=['movieId', 'title', 'genres'])
    
    # 2. Generate Ratings
    print(f"Generating {NUM_RATINGS} synthetic ratings...")
    ratings_data = []
    user_ids = range(1, 51) # 50 simulated users
    
    for _ in range(NUM_RATINGS):
        uid = random.choice(user_ids)
        mid = random.choice(movies_df['movieId'].values)
        rating = round(random.uniform(2.5, 5.0), 1) # Skew towards positive
        timestamp = 1600000000 + random.randint(0, 10000000)
        ratings_data.append([uid, mid, rating, timestamp])
        
    ratings_df = pd.DataFrame(ratings_data, columns=['userId', 'movieId', 'rating', 'timestamp'])
    
    # 3. Save
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    movies_path = os.path.join(OUTPUT_PATH, "synthetic_movies.csv")
    ratings_path = os.path.join(OUTPUT_PATH, "synthetic_ratings.csv")
    
    movies_df.to_csv(movies_path, index=False)
    ratings_df.to_csv(ratings_path, index=False)
    
    print(f"Saved to {movies_path}")
    print(f"Saved to {ratings_path}")

if __name__ == "__main__":
    generate_data()
