import pandas as pd
import numpy as np
import requests
import zipfile
import io
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Constants
MOVIELENS_URL = "http://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
RAW_DATA_PATH = "data/raw"
PROCESSED_DATA_PATH = "data/processed"

def download_movielens():
    """
    Downloads and extracts the MovieLens Small dataset if not present.
    """
    if os.path.exists(os.path.join(RAW_DATA_PATH, "ml-latest-small")):
        print("MovieLens dataset already exists.")
        return

    print("Downloading MovieLens dataset...")
    response = requests.get(MOVIELENS_URL)
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(RAW_DATA_PATH)
    print("Download and extraction complete.")

def load_data():
    """
    Loads MovieLens and Indian movies datasets, merges them.
    """
    # Load MovieLens
    ml_path = os.path.join(RAW_DATA_PATH, "ml-latest-small")
    movies = pd.read_csv(os.path.join(ml_path, "movies.csv"))
    ratings = pd.read_csv(os.path.join(ml_path, "ratings.csv"))
    
    # Load Indian Movies
    indian_movies_path = os.path.join(RAW_DATA_PATH, "indian_movies.csv")
    indian_ratings_path = os.path.join(RAW_DATA_PATH, "indian_ratings.csv")
    
    if os.path.exists(indian_movies_path):
        indian_movies = pd.read_csv(indian_movies_path)
        indian_ratings = pd.read_csv(indian_ratings_path)
        
        # Merge Movies
        # Ensure columns match: movieId, title, genres
        # Indian movies already have compatible columns
        movies = pd.concat([movies, indian_movies[['movieId', 'title', 'genres']]], ignore_index=True)
        
        # Merge Ratings
        ratings = pd.concat([ratings, indian_ratings], ignore_index=True)
        print(f"Merged {len(indian_movies)} Indian movies and {len(indian_ratings)} ratings.")

    # Load Synthetic Data
    syn_movies_path = os.path.join(RAW_DATA_PATH, "synthetic_movies.csv")
    syn_ratings_path = os.path.join(RAW_DATA_PATH, "synthetic_ratings.csv")
    
    if os.path.exists(syn_movies_path):
        syn_movies = pd.read_csv(syn_movies_path)
        syn_ratings = pd.read_csv(syn_ratings_path)
        
        movies = pd.concat([movies, syn_movies], ignore_index=True)
        ratings = pd.concat([ratings, syn_ratings], ignore_index=True)
        print(f"Merged {len(syn_movies)} Synthetic movies and {len(syn_ratings)} ratings.")

    # Load Links for TMDB ID
    links_path = os.path.join(ml_path, "links.csv")
    if os.path.exists(links_path):
        links = pd.read_csv(links_path)
        # Drop imdbId if exists to avoid confusion, keep movieId and tmdbId
        links = links[['movieId', 'tmdbId']]
        # Merge with movies
        movies = movies.merge(links, on='movieId', how='left')
        movies['tmdbId'] = movies['tmdbId'].fillna(0).astype(int)
        print("Merged TMDB IDs.")

    # Load Extended South Indian Data
    si_movies_path = os.path.join(RAW_DATA_PATH, "south_indian_movies_ext.csv")
    si_ratings_path = os.path.join(RAW_DATA_PATH, "south_indian_ratings_ext.csv")
    
    if os.path.exists(si_movies_path):
        si_movies = pd.read_csv(si_movies_path)
        si_ratings = pd.read_csv(si_ratings_path)
        
        # Ensure main movies df has these columns before concat (fill NaN for existing)
        for col in ['language', 'actors', 'tmdbId', 'type']:
            if col not in movies.columns:
                movies[col] = np.nan
        
        # Concat
        movies = pd.concat([movies, si_movies], ignore_index=True)
        ratings = pd.concat([ratings, si_ratings], ignore_index=True)
        print(f"Merged {len(si_movies)} South Indian movies/series and {len(si_ratings)} ratings.")
        
        # Fill NaN for language/actors in non-South Indian movies
        # Be smarter about language assignment - don't override existing languages
        movies.loc[movies['language'].isna(), 'language'] = 'English' # Only fill NaN values
        movies['actors'] = movies['actors'].fillna('Unknown')
        movies['type'] = movies['type'].fillna('Movie') # Default to Movie
        movies['tmdbId'] = movies['tmdbId'].fillna(0).astype(int)
    
    return movies, ratings

def clean_data(movies):
    """
    Cleans genres and handles missing data.
    """
    movies['genres'] = movies['genres'].fillna('')
    movies['genres'] = movies['genres'].str.split('|')
    movies['genres'] = movies['genres'].apply(lambda x: [i.replace(" " ,"") for i in x])
    return movies

def create_metadata_soup(movies):
    """
    Creates a 'soup' string of metadata for Content-Based Filtering.
    Currently uses Genres and Title.
    """
    # Ideally we'd have plot summaries, but ML-Small doesn't have them.
    # We will use Title + Genres as a proxy for content.
    # For a real system valid academic rigor, we might scrape plots, 
    # but for this constrained env, we use what we have.
    
    def soup_feature(x):
        return ' '.join(x['genres']) + ' ' + str(x['title']) + ' ' + str(x['language']) + ' ' + str(x['actors']) + ' ' + str(x['type'])
    
    movies['soup'] = movies.apply(soup_feature, axis=1)
    return movies

def calculate_similarity(movies):
    """
    Calculates Cosine Similarity matrix based on TF-IDF of the soup.
    """
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies['soup'])
    
    print(f"TF-IDF Matrix Shape: {tfidf_matrix.shape}")
    
    # We calculate linear_kernel (dot product) which is equivalent to cosine_sim for normalized vectors
    # However, for a full production system this is computed offline.
    # We will save the matrix or the vectorizer. Saving the full matrix (9K x 9K) is feasible.
    
    from sklearn.metrics.pairwise import linear_kernel
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    return cosine_sim

if __name__ == "__main__":
    download_movielens()
    movies, ratings = load_data()
    movies = clean_data(movies)
    movies = create_metadata_soup(movies)
    
    # Save processed data
    os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
    movies.to_pickle(os.path.join(PROCESSED_DATA_PATH, "movies.pkl"))
    ratings.to_pickle(os.path.join(PROCESSED_DATA_PATH, "ratings.pkl"))
    
    # Calculate and save similarity matrix (Offline Processing)
    # Note: efficient saving might be needed for larger datasets (e.g. np.save, or sparse matrix)
    # For ~10k movies, a dense matrix is ~800MB float64. Might be heavy for pickle.
    # We'll save it as float32 to save space.
    sim = calculate_similarity(movies).astype(np.float32)
    np.save(os.path.join(PROCESSED_DATA_PATH, "similarity_matrix.npy"), sim)
    
    print("Data Preprocessing Complete. Files saved to data/processed/")
