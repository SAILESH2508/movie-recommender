import pandas as pd
import os
import random

# Constants
OUTPUT_PATH = "data/raw"

# Curated List with Type (Movie/Series)
SOUTH_INDIAN_MOVIES = [
    # --- HOTSTAR SPECIALS / WEB SERIES ---
    {"title": "Heart Beat (2024)", "genres": "Drama|Romance|Medical", "language": "Tamil", "actors": "Deepa Balu, Anumol, Yogalakshmi", "tmdbId": 248037, "type": "Series"}, 
    {"title": "Kerala Crime Files (2023)", "genres": "Crime|Thriller", "language": "Malayalam", "actors": "Aju Varghese, Lal, Navas Vallikkunnu", "tmdbId": 228801, "type": "Series"},
    {"title": "Mathagam (2023)", "genres": "Action|Crime|Drama", "language": "Tamil", "actors": "Atharvaa, Manikandan, Nikhila Vimal", "tmdbId": 232230, "type": "Series"},
    {"title": "Suzhal: The Vortex (2022)", "genres": "Crime|Drama|Thriller", "language": "Tamil", "actors": "Kathir, Aishwarya Rajesh, SRIYA REDDY", "tmdbId": 203673, "type": "Series"},
    {"title": "The Legend of Hanuman (2021)", "genres": "Animation|Action|Adventure", "language": "Hindi", "actors": "Da Man, Sharad Kelkar", "tmdbId": 117288, "type": "Series"},
    {"title": "Farzi (2023)", "genres": "Crime|Drama|Thriller", "language": "Hindi", "actors": "Shahid Kapoor, Vijay Sethupathi, Raashii Khanna", "tmdbId": 155554, "type": "Series"},
    {"title": "Dhootha (2023)", "genres": "Horror|Mystery|Thriller", "language": "Telugu", "actors": "Naga Chaitanya Akkineni, Parvathy Thiruvothu, Prachi Desai", "tmdbId": 241082, "type": "Series"},
    {"title": "Label (2023)", "genres": "Action|Drama", "language": "Tamil", "actors": "Jai, Tanya Hope, Mahendran", "tmdbId": 239634, "type": "Series"},
    {"title": "The Office (US)", "genres": "Comedy|Mockumentary", "language": "English", "actors": "Steve Carell, John Krasinski, Jenna Fischer", "tmdbId": 2316, "type": "Series"},
    {"title": "Police Police (Hotstar)", "genres": "Action|Crime|Drama", "language": "Telugu", "actors": "Sriram, Prithviraj Sukumaran, Kamalalini Mukherjee", "tmdbId": 40160, "type": "Series"},

    # --- TAMIL MOVIES (Kollywood) ---
    {"title": "Leo (2023)", "genres": "Action|Crime|Drama", "language": "Tamil", "actors": "Vijay, Trisha, Sanjay Dutt", "tmdbId": 1034541, "type": "Movie"},
    {"title": "Jailer (2023)", "genres": "Action|Comedy|Crime", "language": "Tamil", "actors": "Rajinikanth, Mohanlal, Shiva Rajkumar", "tmdbId": 986056, "type": "Movie"},
    {"title": "Vikram (2022)", "genres": "Action|Thriller", "language": "Tamil", "actors": "Kamal Haasan, Vijay Sethupathi, Fahadh Faasil", "tmdbId": 852185, "type": "Movie"},
    {"title": "Ponniyin Selvan: I (2022)", "genres": "Action|Adventure|Drama", "language": "Tamil", "actors": "Vikram, Aishwarya Rai Bachchan, Karthi", "tmdbId": 505642, "type": "Movie"},
    {"title": "Ponniyin Selvan: II (2023)", "genres": "Action|Adventure|Drama", "language": "Tamil", "actors": "Vikram, Aishwarya Rai Bachchan, Karthi", "tmdbId": 994246, "type": "Movie"},
    {"title": "Kaithi (2019)", "genres": "Action|Thriller", "language": "Tamil", "actors": "Karthi, Narain, Arjun Das", "tmdbId": 546376, "type": "Movie"},
    {"title": "Master (2021)", "genres": "Action|Thriller", "language": "Tamil", "actors": "Vijay, Vijay Sethupathi, Malavika Mohanan", "tmdbId": 605886, "type": "Movie"},
    {"title": "Soorarai Pottru (2020)", "genres": "Drama", "language": "Tamil", "actors": "Suriya, Paresh Rawal, Aparna Balamurali", "tmdbId": 673297, "type": "Movie"},
    {"title": "Jai Bhim (2021)", "genres": "Crime|Drama|Mystery", "language": "Tamil", "actors": "Suriya, Lijomol Jose, Manikandan", "tmdbId": 850383, "type": "Movie"},
    {"title": "Asuran (2019)", "genres": "Action|Drama", "language": "Tamil", "actors": "Dhanush, Manju Warrier, Ken Karunas", "tmdbId": 634493, "type": "Movie"},
    {"title": "Maharaja (2024)", "genres": "Action|Drama|Thriller", "language": "Tamil", "actors": "Vijay Sethupathi, Anurag Kashyap, Mamta Mohandas", "tmdbId": 1045237, "type": "Movie"},
    {"title": "Raayan (2024)", "genres": "Action|Crime|Drama", "language": "Tamil", "actors": "Dhanush, S. J. Suryah, Sundeep Kishan", "tmdbId": 1075306, "type": "Movie"},
    {"title": "Captain Miller (2024)", "genres": "Action|Adventure|Drama", "language": "Tamil", "actors": "Dhanush, Shiva Rajkumar, Priyanka Arul Mohan", "tmdbId": 1004868, "type": "Movie"},
    {"title": "Ayalaan (2024)", "genres": "Action|Sci-Fi", "language": "Tamil", "actors": "Sivakarthikeyan, Rakul Preet Singh, Sharad Kelkar", "tmdbId": 536554, "type": "Movie"},
    {"title": "Amaran (2024)", "genres": "Action|Biography|Drama", "language": "Tamil", "actors": "Sivakarthikeyan, Sai Pallavi, Bhuvan Arora", "tmdbId": 1147285, "type": "Movie"},
    {"title": "Indian 2 (2024)", "genres": "Action|Drama|Thriller", "language": "Tamil", "actors": "Kamal Haasan, Siddharth, S. J. Suryah", "tmdbId": 694086, "type": "Movie"},
    {"title": "Lubber Pandhu (2024)", "genres": "Drama|Sport", "language": "Tamil", "actors": "Harish Kalyan, Attakathi Dinesh, Swasika Vijay", "tmdbId": 1255850, "type": "Movie"},


    # --- TELUGU MOVIES ---
    {"title": "Baahubali: The Beginning (2015)", "genres": "Action|Adventure|Drama", "language": "Telugu", "actors": "Prabhas, Rana Daggubati, Anushka Shetty", "tmdbId": 256040, "type": "Movie"},
    {"title": "Baahubali 2: The Conclusion (2017)", "genres": "Action|Adventure|Fantasy", "language": "Telugu", "actors": "Prabhas, Rana Daggubati, Anushka Shetty", "tmdbId": 350312, "type": "Movie"},
    {"title": "RRR (2022)", "genres": "Action|Drama", "language": "Telugu", "actors": "N. T. Rama Rao Jr., Ram Charan, Ajay Devgn", "tmdbId": 579974, "type": "Movie"},
    {"title": "Pushpa: The Rise (2021)", "genres": "Action|Crime|Drama", "language": "Telugu", "actors": "Allu Arjun, Fahadh Faasil, Rashmika Mandanna", "tmdbId": 791557, "type": "Movie"},
    {"title": "Salaar: Part 1 - Ceasefire (2023)", "genres": "Action|Crime|Drama", "language": "Telugu", "actors": "Prabhas, Prithviraj Sukumaran, Shruti Haasan", "tmdbId": 897087, "type": "Movie"},
    {"title": "Kalki 2898 AD (2024)", "genres": "Action|Sci-Fi", "language": "Telugu", "actors": "Prabhas, Amitabh Bachchan, Kamal Haasan", "tmdbId": 693134, "type": "Movie"},
    {"title": "Hanu-Man (2024)", "genres": "Action|Adventure|Fantasy", "language": "Telugu", "actors": "Teja Sajja, Amritha Aiyer, Varalaxmi Sarathkumar", "tmdbId": 991807, "type": "Movie"},
    {"title": "Guntur Kaaram (2024)", "genres": "Action|Drama", "language": "Telugu", "actors": "Mahesh Babu, Sreeleela, Meenakshi Chaudhary", "tmdbId": 932426, "type": "Movie"},
    {"title": "Arjun Reddy (2017)", "genres": "Action|Drama|Romance", "language": "Telugu", "actors": "Vijay Deverakonda, Shalini Pandey, Rahul Ramakrishna", "tmdbId": 466042, "type": "Movie"},
    {"title": "Mahanati (2018)", "genres": "Biography|Drama", "language": "Telugu", "actors": "Keerthy Suresh, Dulquer Salmaan, Samantha Ruth Prabhu", "tmdbId": 516933, "type": "Movie"},
    {"title": "Devara: Part 1 (2024)", "genres": "Action|Drama", "language": "Telugu", "actors": "N. T. Rama Rao Jr., Saif Ali Khan, Janhvi Kapoor", "tmdbId": 1096197, "type": "Movie"},

    # --- MALAYALAM MOVIES ---
    {"title": "Drishyam 2 (2021)", "genres": "Crime|Drama|Thriller", "language": "Malayalam", "actors": "Mohanlal, Meena, Ansiba Hassan", "tmdbId": 785532, "type": "Movie"},
    {"title": "Kumbalangi Nights (2019)", "genres": "Comedy|Drama|Romance", "language": "Malayalam", "actors": "Shane Nigam, Fahadh Faasil, Soubin Shahir", "tmdbId": 572261, "type": "Movie"},
    {"title": "Manjummel Boys (2024)", "genres": "Adventure|Drama|Thriller", "language": "Malayalam", "actors": "Soubin Shahir, Sreenath Bhasi, Balu Varghese", "tmdbId": 1210928, "type": "Movie"},
    {"title": "Premalu (2024)", "genres": "Comedy|Romance", "language": "Malayalam", "actors": "Naslen K. Gafoor, Mamitha Baiju, Shyam Mohan", "tmdbId": 1215033, "type": "Movie"},
    {"title": "Bramayugam (2024)", "genres": "Horror|Mystery|Thriller", "language": "Malayalam", "actors": "Mammootty, Arjun Ashokan, Sidharth Bharathan", "tmdbId": 1222143, "type": "Movie"},
    {"title": "Aadujeevitham - The Goat Life (2024)", "genres": "Adventure|Drama", "language": "Malayalam", "actors": "Prithviraj Sukumaran, Ala Met, Jimmy Jean-Louis", "tmdbId": 515865, "type": "Movie"},
    {"title": "Aavesham (2024)", "genres": "Action|Comedy", "language": "Malayalam", "actors": "Fahadh Faasil, Hipzster, Mithun Jai Shankar", "tmdbId": 1238996, "type": "Movie"},
    {"title": "Premam (2015)", "genres": "Comedy|Drama|Romance", "language": "Malayalam", "actors": "Nivin Pauly, Sai Pallavi, Madonna Sebastian", "tmdbId": 340621, "type": "Movie"},
    {"title": "Oru Adaar Love (2019)", "genres": "Comedy|Romance", "language": "Malayalam", "actors": "Priya Prakash Varrier, Roshan Abdul Rahoof", "tmdbId": 500682, "type": "Movie"},
    {"title": "Bangalore Days (2014)", "genres": "Comedy|Drama|Romance", "language": "Malayalam", "actors": "Nazriya Nazim, Nivin Pauly, Dulquer Salmaan", "tmdbId": 270420, "type": "Movie"},
    {"title": "Lucifer (2019)", "genres": "Action|Crime|Drama", "language": "Malayalam", "actors": "Mohanlal, Vivek Oberoi, Manju Warrier", "tmdbId": 581373, "type": "Movie"},

    # --- KANNADA MOVIES ---
    {"title": "K.G.F: Chapter 1 (2018)", "genres": "Action|Crime|Drama", "language": "Kannada", "actors": "Yash, Srinidhi Shetty, Ramachandra Raju", "tmdbId": 535284, "type": "Movie"},
    {"title": "K.G.F: Chapter 2 (2022)", "genres": "Action|Crime|Drama", "language": "Kannada", "actors": "Yash, Sanjay Dutt, Raveena Tandon", "tmdbId": 675353, "type": "Movie"},
    {"title": "Kantara (2022)", "genres": "Action|Adventure|Drama", "language": "Kannada", "actors": "Rishab Shetty, Kishore Kumar G., Achyuth Kumar", "tmdbId": 1016127, "type": "Movie"},
    {"title": "Charlie 777 (2022)", "genres": "Adventure|Comedy|Drama", "language": "Kannada", "actors": "Rakshit Shetty, Sangeetha Sringeri, Raj B. Shetty", "tmdbId": 605269, "type": "Movie"},
    {"title": "Vikrant Rona (2022)", "genres": "Action|Adventure|Drama", "language": "Kannada", "actors": "Kichcha Sudeep, Nirup Bhandari, Neetha Ashok", "tmdbId": 716259, "type": "Movie"},
    
    # --- NEW 2024-2026 RELEASES & TRENDING CONTENT ---
    {"title": "The Greatest of All Time (GOAT) (2024)", "genres": "Action|Sci-Fi|Thriller", "language": "Tamil", "actors": "Vijay, Prabhu Deva, Prashanth", "tmdbId": 125552, "type": "Movie"},
    {"title": "Vettaiyan (2024)", "genres": "Action|Drama", "language": "Tamil", "actors": "Rajinikanth, Amitabh Bachchan, Fahadh Faasil", "tmdbId": 1083995, "type": "Movie"}, 
    {"title": "Kanguva (2024)", "genres": "Action|Fantasy", "language": "Tamil", "actors": "Suriya, Bobby Deol, Disha Patani", "tmdbId": 932415, "type": "Movie"},
    {"title": "Thangalaan (2024)", "genres": "Action|Adventure", "language": "Tamil", "actors": "Vikram, Malavika Mohanan, Parvathy", "tmdbId": 1079391, "type": "Movie"},
    {"title": "Viduthalai Part 2 (2024)", "genres": "Crime|Drama", "language": "Tamil", "actors": "Soori, Vijay Sethupathi, Manju Warrier", "tmdbId": 1184857, "type": "Movie"},
    {"title": "Pushpa 2: The Rule (2024)", "genres": "Action|Crime|Drama", "language": "Telugu", "actors": "Allu Arjun, Rashmika Mandanna, Fahadh Faasil", "tmdbId": 939243, "type": "Movie"},
    {"title": "Squid Game (Season 2)", "genres": "Action|Drama|Thriller", "language": "Korean", "actors": "Lee Jung-jae, Lee Byung-hun, Wi Ha-jun", "tmdbId": 93405, "type": "Series"},
    {"title": "Shōgun (2024)", "genres": "Drama|History|War", "language": "Japanese", "actors": "Hiroyuki Sanada, Cosmo Jarvis, Anna Sawai", "tmdbId": 111110, "type": "Series"},
    {"title": "Dune: Prophecy (2024)", "genres": "Drama|Sci-Fi|Adventure", "language": "English", "actors": "Emily Watson, Olivia Williams, Travis Fimmel", "tmdbId": 91759, "type": "Series"},
    {"title": "Deadpool & Wolverine (2024)", "genres": "Action|Comedy|Sci-Fi", "language": "English", "actors": "Ryan Reynolds, Hugh Jackman, Emma Corrin", "tmdbId": 533535, "type": "Movie"},
    {"title": "The Last of Us (Season 2)", "genres": "Action|Adventure|Drama", "language": "English", "actors": "Pedro Pascal, Bella Ramsey, Kaitlyn Dever", "tmdbId": 100088, "type": "Series"},
    {"title": "Stranger Things (Season 5)", "genres": "Drama|Mystery|Sci-Fi", "language": "English", "actors": "Millie Bobby Brown, Finn Wolfhard, Winona Ryder", "tmdbId": 66732, "type": "Series"},
    {"title": "Severance (Season 2)", "genres": "Drama|Mystery|Sci-Fi", "language": "English", "actors": "Adam Scott, Patricia Arquette, Britt Lower", "tmdbId": 95396, "type": "Series"},
    {"title": "Gladiator II (2024)", "genres": "Action|Adventure|Drama", "language": "English", "actors": "Paul Mescal, Pedro Pascal, Denzel Washington", "tmdbId": 945961, "type": "Movie"},
    
    # --- UPCOMING & RECENT 2025-2026 ---
    {"title": "Good Bad Ugly (2025)", "genres": "Action|Comedy", "language": "Tamil", "actors": "Ajith Kumar, Trisha, Arjun Das", "tmdbId": 1255550, "type": "Movie"},
    {"title": "Coolie (2025)", "genres": "Action|Thriller", "language": "Tamil", "actors": "Rajinikanth, Nagarjuna, Shruti Haasan", "tmdbId": 1215000, "type": "Movie"},
    {"title": "Game Changer (2025)", "genres": "Action|Political|Drama", "language": "Telugu", "actors": "Ram Charan, Kiara Advani, S. J. Suryah", "tmdbId": 932422, "type": "Movie"},
    {"title": "Vishwambhara (2025)", "genres": "Fantasy|Action", "language": "Telugu", "actors": "Chiranjeevi, Trisha, Ashika Ranganath", "tmdbId": 1222000, "type": "Movie"},
    {"title": "Thug Life (2025)", "genres": "Action|Crime|Drama", "language": "Tamil", "actors": "Kamal Haasan, Silambarasan, Trisha", "tmdbId": 1189498, "type": "Movie"},

    # --- HOLLYWOOD BLOCKBUSTERS ---
    {"title": "Avatar: The Way of Water (2022)", "genres": "Science Fiction|Adventure|Action", "language": "English", "actors": "Sam Worthington, Zoe Saldaña, Sigourney Weaver", "tmdbId": 76600, "type": "Movie"},
    {"title": "Avengers: Endgame (2019)", "genres": "Adventure|Science Fiction|Action", "language": "English", "actors": "Robert Downey Jr., Chris Evans, Mark Ruffalo", "tmdbId": 299534, "type": "Movie"},
    {"title": "Oppenheimer (2023)", "genres": "Drama|History", "language": "English", "actors": "Cillian Murphy, Emily Blunt, Matt Damon", "tmdbId": 872585, "type": "Movie"},
    {"title": "Spider-Man: No Way Home (2021)", "genres": "Action|Adventure|Science Fiction", "language": "English", "actors": "Tom Holland, Zendaya, Benedict Cumberbatch", "tmdbId": 634649, "type": "Movie"},
    {"title": "Dune: Part Two (2024)", "genres": "Science Fiction|Adventure", "language": "English", "actors": "Timothée Chalamet, Zendaya, Rebecca Ferguson", "tmdbId": 823464, "type": "Movie"},
]

def generate_south_indian_data():
    print(f"Generating {len(SOUTH_INDIAN_MOVIES)} movies/series...")
    
    # 1. Generate Movies DataFrame
    start_id = 300000 
    
    movies_data = []
    for i, movie in enumerate(SOUTH_INDIAN_MOVIES):
        movies_data.append([
            start_id + i, 
            movie["title"], 
            movie["genres"],
            movie["language"],
            movie["actors"],
            movie["tmdbId"],
            movie.get("type", "Movie") # Default to Movie
        ])
        
    movies_df = pd.DataFrame(movies_data, columns=['movieId', 'title', 'genres', 'language', 'actors', 'tmdbId', 'type'])
    
    # 2. Generate Synthetic Ratings
    print("Generating synthetic ratings...")
    ratings_data = []
    user_ids = range(1, 100) 
    
    for mid in movies_df['movieId']:
        # Higher ratings for Feature Content like Heart Beat
        row = movies_df[movies_df['movieId'] == mid].iloc[0]
        
        # Boost Heart Beat or Popular series
        is_popular = "Heart Beat" in row['title'] or "Leo" in row['title'] or "Manjummel" in row['title']
        
        num_ratings = random.randint(80, 100) if is_popular else random.randint(30, 80)
        selected_users = random.sample(user_ids, min(num_ratings, len(user_ids)))
        
        for uid in selected_users:
            min_rating = 4.5 if is_popular else 3.5
            rating = round(random.uniform(min_rating, 5.0), 1) 
            timestamp = 1600000000
            ratings_data.append([uid, mid, rating, timestamp])
            
    ratings_df = pd.DataFrame(ratings_data, columns=['userId', 'movieId', 'rating', 'timestamp'])
    
    # 3. Save
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    movies_path = os.path.join(OUTPUT_PATH, "south_indian_movies_ext.csv")
    ratings_path = os.path.join(OUTPUT_PATH, "south_indian_ratings_ext.csv")
    
    movies_df.to_csv(movies_path, index=False)
    ratings_df.to_csv(ratings_path, index=False)
    
    print(f"Enriched Data: Saved {len(movies_df)} items and {len(ratings_df)} ratings.")

if __name__ == "__main__":
    generate_south_indian_data()
