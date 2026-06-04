import pandas as pd
import numpy as np

def generate_indian_movies():
    """
    Generates a dataset of popular Indian (Tamil, Telugu, Hindi) movies
    to augment the MovieLens dataset.
    """
    movies_data = [
         # Tamil
        {'title': 'Baahubali: The Beginning (2015)', 'genres': 'Action|Adventure|Drama', 'language': 'Telugu/Tamil'},
        {'title': 'Baahubali 2: The Conclusion (2017)', 'genres': 'Action|Adventure|Fantasy', 'language': 'Telugu/Tamil'},
        {'title': 'Vikram (2022)', 'genres': 'Action|Thriller', 'language': 'Tamil'},
        {'title': 'Kaithi (2019)', 'genres': 'Action|Thriller', 'language': 'Tamil'},
        {'title': 'Ponniyin Selvan: I (2022)', 'genres': 'Action|Adventure|Drama', 'language': 'Tamil'},
        {'title': 'Jai Bhim (2021)', 'genres': 'Crime|Drama|Mystery', 'language': 'Tamil'},
        {'title': 'Super Deluxe (2019)', 'genres': 'Crime|Drama|Thriller', 'language': 'Tamil'},
        {'title': '96 (2018)', 'genres': 'Drama|Romance', 'language': 'Tamil'},
        {'title': 'Mankatha (2011)', 'genres': 'Action|Crime|Thriller', 'language': 'Tamil'},
        {'title': 'Thuppakki (2012)', 'genres': 'Action|Thriller', 'language': 'Tamil'},
        {'title': 'Asuran (2019)', 'genres': 'Action|Drama', 'language': 'Tamil'},
        {'title': 'Karnan (2021)', 'genres': 'Action|Drama', 'language': 'Tamil'},
        {'title': 'Vada Chennai (2018)', 'genres': 'Action|Crime|Drama', 'language': 'Tamil'},
        {'title': 'Soorarai Pottru (2020)', 'genres': 'Drama', 'language': 'Tamil'},
        
        # Telugu
        {'title': 'RRR (2022)', 'genres': 'Action|Drama', 'language': 'Telugu'},
        {'title': 'Pushpa: The Rise (2021)', 'genres': 'Action|Crime|Drama', 'language': 'Telugu'},
        {'title': 'Arjun Reddy (2017)', 'genres': 'Action|Drama|Romance', 'language': 'Telugu'},
        {'title': 'Jersey (2019)', 'genres': 'Drama', 'language': 'Telugu'},
        {'title': 'Mahanati (2018)', 'genres': 'Biography|Drama', 'language': 'Telugu'},
        
        # Hindi
        {'title': '3 Idiots (2009)', 'genres': 'Comedy|Drama', 'language': 'Hindi'},
        {'title': 'Dangal (2016)', 'genres': 'Action|Biography|Drama', 'language': 'Hindi'},
        {'title': 'Gully Boy (2019)', 'genres': 'Drama|Music', 'language': 'Hindi'},
        {'title': 'Andhadhun (2018)', 'genres': 'Crime|Thriller|Comedy', 'language': 'Hindi'},
        {'title': 'Drishyam (2015)', 'genres': 'Crime|Drama|Mystery', 'language': 'Hindi'},
    ]
    
    # Start IDs from 200,000 to avoid conflict with MovieLens
    start_id = 200000
    
    df_movies = pd.DataFrame(movies_data)
    df_movies['movieId'] = range(start_id, start_id + len(df_movies))
    
    # Reorder columns to match MovieLens (movieId, title, genres)
    df_movies = df_movies[['movieId', 'title', 'genres', 'language']]
    
    print(f"Generated {len(df_movies)} Indian/Regional movies.")
    return df_movies

def generate_ratings(movie_ids, n_users=100):
    """
    Generates synthetic ratings for the Indian movies so they can be recommended
    by Collaborative Filtering models.
    """
    ratings_data = []
    
    for mid in movie_ids:
        # Assign random number of ratings per movie (popularity)
        n_ratings = np.random.randint(20, n_users)
        
        # Random user IDs (using high IDs to simulate new users or mix with existing)
        user_ids = np.random.choice(range(1, 1000), n_ratings, replace=False)
        
        for uid in user_ids:
            # bias towards high ratings for these popular movies (3.5 to 5.0)
            rating = np.round(np.random.uniform(3.5, 5.0), 1)
            ratings_data.append({'userId': uid, 'movieId': mid, 'rating': rating, 'timestamp': 1600000000})
            
    df_ratings = pd.DataFrame(ratings_data)
    print(f"Generated {len(df_ratings)} ratings for Indian movies.")
    return df_ratings

if __name__ == "__main__":
    import os
    os.makedirs('data/raw', exist_ok=True)
    
    movies = generate_indian_movies()
    movies.to_csv('data/raw/indian_movies.csv', index=False)
    
    ratings = generate_ratings(movies['movieId'])
    ratings.to_csv('data/raw/indian_ratings.csv', index=False)
    print("Files saved to data/raw/")
