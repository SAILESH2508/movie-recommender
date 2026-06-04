import pandas as pd
import os

# Define paths
PROCESSED_DATA_PATH = os.path.join("data", "processed")
MOVIES_PKL = os.path.join(PROCESSED_DATA_PATH, "movies.pkl")

def check_data():
    if not os.path.exists(MOVIES_PKL):
        print(f"Error: {MOVIES_PKL} not found.")
        return

    movies = pd.read_pickle(MOVIES_PKL)
    total = len(movies)
    missing_id = len(movies[movies['tmdbId'] == 0])
    
    print("-" * 30)
    print(f"📊 DATA DIAGNOSTICS")
    print("-" * 30)
    print(f"Total movies: {total:,}")
    print(f"Movies with tmdbId 0: {missing_id:,}")
    print(f"Percentage with Posters: {((total-missing_id)/total)*100:.1f}%")
    print("-" * 30)
    
    if missing_id > 0:
        print("\nTop movies with missing posters:")
        print(movies[movies['tmdbId'] == 0][['title', 'language']].head(10))

if __name__ == "__main__":
    check_data()
