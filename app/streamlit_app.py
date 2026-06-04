import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import requests
import json
import datetime
from urllib.parse import quote_plus

# Add root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from src.models.hybrid import HybridRecommender
from src.services.tmdb import fetch_movie_poster

# -----------------------------------------------------------------------------
# CONFIGURATION & CONSTANTS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="🎬 CineSmart AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed")
MODEL_PATH = os.path.join(PROCESSED_DATA_PATH, "svd_model.pkl")

# Increment this to force a refresh of all movie posters
CACHE_VERSION = 8

# Persistent Storage Paths
USER_DATA_DIR = os.path.join(BASE_DIR, "data", "user")
os.makedirs(USER_DATA_DIR, exist_ok=True)
WATCHLIST_PATH = os.path.join(USER_DATA_DIR, "watchlist.json")
RATINGS_PATH = os.path.join(USER_DATA_DIR, "ratings.json")
PREFERENCES_PATH = os.path.join(USER_DATA_DIR, "preferences.json")

def save_user_data(data, file_path):
    """Save user data to a JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        st.error(f"Error saving data to {file_path}: {e}")

def load_user_data(file_path, default_value):
    """Load user data from a JSON file."""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading data from {file_path}: {e}")
    return default_value



# Modern UI Theme
# Blue Background Theme (Dark Glass Edition)
BLUE_THEME_CSS = """
<style>
    /* ===== GOOGLE FONTS ===== */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&family=Inter:wght@400;600;800&display=swap');

    /* ===== VARIABLES ===== */
    :root {
        --bg-color: #0A192F; /* Cinematic Navy */
        --card-bg: rgba(17, 34, 64, 0.4); /* Pro Glass */
        --text-color: #E6F1FF;
        --subtext-color: #8892B0;
        --accent-color: #64FFDA; /* Neon Teal */
        --secondary-accent: #7C4DFF; /* Purple Glow */
        --button-bg: #112240;
        --button-text: #64FFDA;
    }

    /* ===== GLOBAL RESETS ===== */
    .stApp {
        font-family: 'Inter', sans-serif;
        background-color: var(--bg-color) !important;
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(100, 255, 218, 0.05) 0%, transparent 40%),
            radial-gradient(circle at 80% 70%, rgba(124, 77, 255, 0.05) 0%, transparent 40%),
            linear-gradient(135deg, #0A192F 0%, #020C1B 100%);
        background-attachment: fixed;
    }
    
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: -1px !important;
    }
    
    p, div, span, label, button, input, textarea {
        font-family: 'Inter', sans-serif;
    }

    /* ===== HEADERS ===== */
    h1, h2, h3, h4, h5, h6 {
        color: #ccd6f6 !important;
        font-weight: 900 !important;
        text-shadow: 0 10px 30px rgba(2, 12, 27, 0.5);
    }

    /* ===== CUSTOM CARD CONTAINER ===== */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--card-bg) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(100, 255, 218, 0.1) !important;
        border-radius: 20px !important;
        padding: 1.2rem !important;
        box-shadow: 0 20px 40px -15px rgba(2, 12, 27, 0.7) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-8px) scale(1.02) !important;
        border-color: var(--accent-color) !important;
        box-shadow: 0 0 30px rgba(100, 255, 218, 0.15), 0 25px 50px -12px rgba(2, 12, 27, 0.8) !important;
    }

    /* ===== BUTTONS ===== */
    .stButton > button, .stLinkButton > a {
        background: transparent !important;
        color: var(--accent-color) !important;
        border: 1px solid var(--accent-color) !important;
        border-radius: 4px !important;
        padding: 0.5rem 0.5rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        font-size: 0.75rem !important;
        transition: all 0.25s ease !important;
        display: inline-flex !important;
        justify-content: center !important;
        align-items: center !important;
        white-space: nowrap !important;
        width: 100% !important;
        text-decoration: none !important;
    }

    .stButton > button:hover, .stLinkButton > a:hover {
        background: rgba(100, 255, 218, 0.1) !important;
        box-shadow: 0 5px 15px rgba(100, 255, 218, 0.2) !important;
        color: var(--accent-color) !important;
        border-color: var(--accent-color) !important;
        text-decoration: none !important;
    }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background-color: #020C1B !important;
        border-right: 1px solid rgba(100, 255, 218, 0.05);
    }

    /* ===== METRICS ===== */
    [data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif !important;
        color: var(--accent-color) !important;
        font-size: 2.2rem !important;
    }

    /* ===== HERO SECTION ===== */
    .hero-container {
        position: relative;
        overflow: hidden;
        border-radius: 30px;
        background: linear-gradient(135deg, rgba(17, 34, 64, 0.8) 0%, rgba(10, 25, 47, 0.8) 100%);
        border: 1px solid rgba(100, 255, 218, 0.2);
        padding: 5rem 2rem;
        margin-bottom: 3rem;
        box-shadow: 0 30px 60px rgba(2, 12, 27, 0.8);
    }
    
    .hero-title {
        font-family: 'Outfit', sans-serif !important;
        font-size: 4.5rem;
        font-weight: 900;
        line-height: 1;
        margin-bottom: 1.5rem;
        background: linear-gradient(to right, #64FFDA, #7C4DFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 20px rgba(100, 255, 218, 0.3));
    }

    /* ===== POSTER BADGES ===== */
    .poster-badge {
        position: absolute;
        top: 15px;
        right: 15px;
        background: rgba(100, 255, 218, 0.9);
        color: #020C1B;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        z-index: 100;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    .stImage img {
        width: 100% !important;
        height: 420px !important;
        object-fit: cover !important;
        border-radius: 12px 12px 0 0 !important;
        border-bottom: 3px solid var(--accent-color) !important;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: #E3F2FD !important;
        font-weight: 500;
        max-width: 600px;
        margin: 0 auto;
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.05) !important;
        border: none !important;
        border-radius: 50px !important;
        color: #E3F2FD !important;
        padding: 0.5rem 1.2rem !important;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: var(--accent-color) !important;
        color: #000000 !important;
        font-weight: bold !important;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 10px;
        background: #0D47A1;
    }
    ::-webkit-scrollbar-thumb {
        background: #42A5F5;
        border-radius: 5px;
    }

    /* ===== EXPANDER ===== */
    div[data-testid="stExpander"] {
        background-color: transparent !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 8px !important;
    }

    div[data-testid="stExpander"] summary {
        color: #FFFFFF !important;
    }
    
    div[data-testid="stExpander"] summary:hover {
        color: var(--accent-color) !important;
    }

    div[data-testid="stExpander"] svg {
        fill: #FFFFFF !important;
    }
    
    /* ===== BADGE STYLING ===== */
    .badge-rating, span[class*="badge"] {
        padding: 8px 16px !important;
        border: 3px solid var(--black) !important;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        display: inline-block !important;
        margin: 4px !important;
        box-shadow: 3px 3px 0px var(--black) !important;
    }
    
    /* ===== IMAGE STYLING ===== */
    .stImage, .stImage > img, img {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        max-width: 100% !important;
        height: auto !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stImage:hover > img, img:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4) !important;
        border-color: var(--accent-color) !important;
    }
    
    /* Ensure posters have a consistent aspect ratio and are NOT hidden */
    .stImage img {
        width: 100% !important;
        height: 400px !important;
        object-fit: cover !important;
        background-color: #0D47A1 !important;
    }
    
    /* Handle broken images gracefully */
    img[src=""], img:not([src]), img[src*="placeholder"] {
        background: linear-gradient(135deg, #1565C0, #0D47A1) !important;
        color: white !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 200px !important;
    }

    /* ===== HIDE STREAMLIT DEFAULTS ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}

</style>
"""

st.markdown(BLUE_THEME_CSS, unsafe_allow_html=True)

import base64

def get_offline_placeholder(width, height, text="No Poster"):
    """Generates a base64 encoded SVG placeholder image"""
    svg = f"""
    <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#0D47A1"/>
        <text x="50%" y="50%" font-family="Arial" font-size="24" fill="white" text-anchor="middle" dominant-baseline="middle">{text}</text>
    </svg>
    """
    b64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64}"


# -----------------------------------------------------------------------------
# LOAD DATA & MODELS
# -----------------------------------------------------------------------------
@st.cache_resource
def load_resources():
    try:
        movies = pd.read_pickle(os.path.join(PROCESSED_DATA_PATH, "movies.pkl"))
        
        # Safe Loading of Columns
        for col in ['language', 'actors', 'tmdbId', 'type']:
             if col not in movies.columns:
                 movies[col] = "Unknown" if col != 'tmdbId' else 0
                 
        ratings = pd.read_pickle(os.path.join(PROCESSED_DATA_PATH, "ratings.pkl"))
        sim_matrix = np.load(os.path.join(PROCESSED_DATA_PATH, "similarity_matrix.npy"))
        
        recommender = HybridRecommender(movies, sim_matrix, MODEL_PATH)
        return movies, ratings, recommender
    except Exception as e:
        st.error(f"Critical Error Loading Resources: {e}")
        return None, None, None

movies, ratings, recommender = load_resources()

# -----------------------------------------------------------------------------
# UTILS
# -----------------------------------------------------------------------------

def filter_movies(df, language_filter, actors_filter, type_filter):
    filtered = df.copy()
    if language_filter != "All":
        filtered = filtered[filtered['language'] == language_filter]
    
    if type_filter != "All":
        filtered = filtered[filtered['type'] == type_filter]
    
    if actors_filter:
        filtered = filtered[filtered['actors'].str.contains(actors_filter, case=False, na=False)]
        
    return filtered

@st.dialog("Movie Details")
def show_movie_details(movie, api_key=None):
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Fetch poster with error handling
        poster_url = None
        try:
            poster_url = fetch_movie_poster(movie.get('tmdbId', 0), api_key, title=movie['title'], cache_version=CACHE_VERSION)
        except Exception as e:
            st.error(f"Error fetching poster: {e}")
        
        # Use poster or create a nice placeholder
        if poster_url:
            st.image(poster_url, width=250)
        else:
            # Cinematic Synthetic Poster for Dialog
            canvas_html = f'<div style="background:linear-gradient(135deg,#{color} 0%,#{dark_color} 100%);color:white;padding:0;text-align:center;border-radius:12px;font-weight:bold;height:375px;width:250px;display:flex;flex-direction:column;justify-content:center;align-items:center;position:relative;overflow:hidden;box-shadow:inset 0 0 100px rgba(0,0,0,0.5); border:2px solid var(--accent-color);"><div style="font-size:80px;margin-bottom:20px;filter:drop-shadow(0 10px 20px rgba(0,0,0,0.4));">🎬</div><div style="background:rgba(0,0,0,0.6);backdrop-filter:blur(10px);width:100%;padding:20px 10px;position:absolute;bottom:0;border-top:1px solid rgba(255,255,255,0.1);"><div style="font-family:\'Outfit\',sans-serif;font-size:16px;line-height:1.1;color:#64FFDA;margin-bottom:5px;">{movie["title"].upper()}</div></div></div>'
            st.markdown(canvas_html, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"# {movie['title']}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"🎭 **Type:** {movie.get('type', 'Movie')}")
            st.markdown(f"🌐 **Language:** {movie.get('language', 'Unknown')}")
        with c2:
            if movie.get('tmdbId') and movie['tmdbId'] != 0:
                st.markdown(f"🆔 **TMDB ID:** `{movie['tmdbId']}`")
        
        if isinstance(movie.get('genres'), list) and movie['genres']:
            genres_str = " • ".join(movie['genres'])
            st.markdown(f"🏷️ **Genres:** {genres_str}")
        
        if movie.get('actors') and movie['actors'] != 'Unknown':
            st.markdown(f"👥 **Cast:** {movie['actors']}")
        
        # User's rating for this movie
        current_rating = st.session_state.user_ratings.get(movie['title'], 0)
        if current_rating > 0:
            st.markdown(f"**Your Rating:** {'⭐' * current_rating}")
        
        # Quick actions
        col_a, col_b = st.columns(2)
        with col_a:
            if movie['title'] not in st.session_state.watchlist:
                if st.button("Add to Watchlist", width='stretch', key=f"details_add_{movie.get('movieId')}"):
                    st.session_state.watchlist.append(movie['title'])
                    save_user_data(st.session_state.watchlist, WATCHLIST_PATH)
                    st.toast("Added to Watchlist!", icon="✅")
                    st.rerun()
            else:
                if st.button("Remove", width='stretch', key=f"details_rem_{movie.get('movieId')}"):
                    st.session_state.watchlist.remove(movie['title'])
                    save_user_data(st.session_state.watchlist, WATCHLIST_PATH)
                    st.toast("Removed from Watchlist", icon="🗑️")
                    st.rerun()
        
        with col_b:
            youtube_url = f"https://www.youtube.com/results?search_query={movie['title'].replace(' ', '+')}+trailer"
            st.link_button("Watch Trailer", youtube_url, width='stretch')

def get_recommendation_explanation(movie_title, recommended_movies):
    """Generate explanation for why movies were recommended"""
    explanations = []
    base_movie = movies[movies['title'] == movie_title].iloc[0]
    
    for rec_movie in recommended_movies[:3]:  # Explain top 3
        reasons = []
        
        # Genre similarity
        if isinstance(base_movie.get('genres'), list) and isinstance(rec_movie.get('genres'), list):
            common_genres = set(base_movie['genres']) & set(rec_movie['genres'])
            if common_genres:
                reasons.append(f"Similar genres: {', '.join(common_genres)}")
        
        # Language similarity
        if base_movie.get('language') == rec_movie.get('language'):
            reasons.append(f"Same language: {base_movie['language']}")
        
        # Type similarity
        if base_movie.get('type') == rec_movie.get('type'):
            reasons.append(f"Same type: {base_movie['type']}")
        
        explanation = f"**{rec_movie['title']}**: " + " • ".join(reasons) if reasons else f"**{rec_movie['title']}**: Based on overall similarity"
        explanations.append(explanation)
    
    return explanations

def generate_smart_recommendations():
    """Generate smart recommendations based on user ratings and preferences"""
    smart_movies = movies.copy()
    
    # Filter based on user preferences
    if st.session_state.user_preferences["favorite_genres"]:
        smart_movies = smart_movies[
            smart_movies['genres'].apply(
                lambda x: any(genre in x for genre in st.session_state.user_preferences["favorite_genres"]) 
                if isinstance(x, list) else False
            )
        ]
    
    if st.session_state.user_preferences["favorite_languages"]:
        smart_movies = smart_movies[
            smart_movies['language'].isin(st.session_state.user_preferences["favorite_languages"])
        ]
    
    if st.session_state.user_preferences["preferred_type"] != "All":
        smart_movies = smart_movies[
            smart_movies['type'] == st.session_state.user_preferences["preferred_type"]
        ]
    
    # Exclude movies already rated or in watchlist
    rated_movies = list(st.session_state.user_ratings.keys())
    watchlist_movies = st.session_state.watchlist
    excluded_movies = set(rated_movies + watchlist_movies)
    
    smart_movies = smart_movies[~smart_movies['title'].isin(excluded_movies)]
    
    # Prioritize based on user's high ratings
    if st.session_state.user_ratings:
        high_rated_movies = [movie for movie, rating in st.session_state.user_ratings.items() if rating >= 4]
        if high_rated_movies:
            # Find movies similar to highly rated ones
            similar_genres = set()
            similar_languages = set()
            
            for movie_title in high_rated_movies:
                movie_data = movies[movies['title'] == movie_title]
                if not movie_data.empty:
                    movie_row = movie_data.iloc[0]
                    if isinstance(movie_row.get('genres'), list):
                        similar_genres.update(movie_row['genres'])
                    if movie_row.get('language'):
                        similar_languages.add(movie_row['language'])
            
            # Boost movies with similar characteristics
            if similar_genres:
                smart_movies = smart_movies[
                    smart_movies['genres'].apply(
                        lambda x: any(genre in similar_genres for genre in x) if isinstance(x, list) else False
                    )
                ]
            
            if similar_languages:
                smart_movies = smart_movies[smart_movies['language'].isin(similar_languages)]
    
    # Sort recommendations by priority and year hierarchy (current, past 2 years, older)
    smart_movies['is_priority'] = smart_movies['movieId'].apply(lambda x: 1 if x >= 300000 else 0)
    current_year = datetime.datetime.now().year
    smart_movies['year'] = smart_movies['title'].str.extract(r'\((\d{4})\)').astype(float).fillna(0).astype(int)
    
    def get_smart_bucket(year):
        if year >= current_year - 1:
            return 0
        elif year >= current_year - 3:
            return 1
        else:
            return 2
            
    smart_movies['year_bucket'] = smart_movies['year'].apply(get_smart_bucket)
    smart_movies = smart_movies.sort_values(by=['is_priority', 'year_bucket'], ascending=[False, True])
    
    # Return top recommendations
    return smart_movies.head(6).to_dict('records')

# -----------------------------------------------------------------------------
# UI LAYOUT
# -----------------------------------------------------------------------------

def main():
    if movies is None:
        st.error("Data missing. Please run the setup scripts.")
        return

    # --- SESSION STATE INITIALIZATION ---
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = load_user_data(WATCHLIST_PATH, [])
    if "user_ratings" not in st.session_state:
        st.session_state.user_ratings = load_user_data(RATINGS_PATH, {})
    if "user_preferences" not in st.session_state:
        default_prefs = {
            "favorite_genres": [],
            "favorite_languages": [],
            "preferred_type": "All"
        }
        st.session_state.user_preferences = load_user_data(PREFERENCES_PATH, default_prefs)
    if "search_history" not in st.session_state:
        st.session_state.search_history = []

    with st.sidebar:
        st.markdown('<div style="text-align:center; margin-bottom: 2rem;">', unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/2503/2503508.png", width=100)
        st.markdown('<h2 style="color:#64FFDA; margin-top:10px;">CineSmart 2.0</h2>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        menu = st.radio("Navigation", ["Home", "My Profile", "About"], index=0)

        st.markdown("### 🔍 Search & Filters")
        global_search = st.text_input("Quick Movie Search", placeholder="e.g. Leo, Inception", key="global_search_input")
        
        # Watchlist Quick View
        wl_count = len(st.session_state.watchlist)
        st.markdown(f"### 📺 Watchlist ({wl_count})")
        if wl_count > 0:
            with st.expander("View Watchlist"):
                for item in st.session_state.watchlist:
                    st.write(f"- {item}")
                if st.button("Clear Watchlist", key="clear_wl_btn"):
                    st.session_state.watchlist = []
                    save_user_data(st.session_state.watchlist, WATCHLIST_PATH)
                    st.rerun()
        
        st.markdown("---")
        
        # Global Filters
        type_options = ["All", "Movie", "Series"]
        selected_type = st.selectbox("Content Type", type_options, key="global_type_select")
        
        languages = ["All"] + sorted(list(set(movies['language'].dropna().unique())))
        priority_langs = ['Tamil', 'Telugu', 'Malayalam', 'Kannada', 'Hindi', 'English']
        sorted_langs = ["All"] + [l for l in priority_langs if l in languages] + [l for l in languages if l not in priority_langs and l != "All"]
        sorted_langs = list(dict.fromkeys(sorted_langs))
        selected_language = st.selectbox("Language", sorted_langs, key="global_lang_select")
        
        actor_search = st.text_input("Search Actor", placeholder="e.g. Vijay, Prabhas", key="global_actor_input")
        
    # --- MAIN PAGES ---
    api_key = st.secrets.get("tmdb_api_key", "")
    if menu == "Home":
        render_unified_dashboard(api_key, selected_language, actor_search, selected_type, global_search)
    elif menu == "My Profile":
        render_user_profile()
    elif menu == "About":
        render_about()

def render_unified_dashboard(api_key, language, actor, content_type, global_search):
    # Welcome Hero if no search
    if not global_search:
        st.markdown(f"""
        <div class="hero-container">
            <h1 class="hero-title">CineSmart AI Pro 2.0</h1>
            <p class="hero-subtitle">Experience our most advanced recommendation engine yet. Powered by Hybrid-AI, tuned for cinema lovers.</p>
            <div style="margin-top:2rem;">
                <span style="background:rgba(100, 255, 218, 0.1); border:1px solid rgba(100, 255, 218, 0.3); padding:0.5rem 1rem; border-radius:100px; color:#64FFDA; font-weight:bold; font-size:12px; text-transform:uppercase; letter-spacing:1px; margin-right:10px;">✨ New Design</span>
                <span style="background:rgba(124, 77, 255, 0.1); border:1px solid rgba(124, 77, 255, 0.3); padding:0.5rem 1rem; border-radius:100px; color:#7C4DFF; font-weight:bold; font-size:12px; text-transform:uppercase; letter-spacing:1px;">💿 12k+ Titles</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    tab_explore, tab_search, tab_analytics = st.tabs(["🏠 Explore", "🔍 Advanced Search", "📊 Analytics"])
    
    with tab_explore:
        if global_search:
            st.subheader(f"🔍 Search Results for '{global_search}'")
            search_results = movies[movies['title'].str.contains(global_search, case=False, na=False)].head(8).to_dict('records')
            if search_results:
                display_recommendations(search_results, api_key, title="", key_prefix="global_search_res")
            else:
                st.info("No matches found in Quick Search.")
            st.markdown("---")
            
        render_home_content(api_key, language, actor, content_type)
        
    with tab_search:
        render_advanced_search_content(api_key)
        
    with tab_analytics:
        render_analytics_content()

def render_home_content(api_key, language, actor, content_type):
    # Featured Section (Hotstar Special)
    # Showing specifically for Tamil or All languages
    if language in ["All", "Tamil"] and content_type in ["All", "Series"]:
        # valid TMDB URL for Heart Beat
        bg_url = "https://image.tmdb.org/t/p/original/odnF5hyuYI8itcMLxFT6H9IpKoT.jpg" 
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(to right, #000000 0%, rgba(0,0,0,0.6) 100%), url('{bg_url}');
            background-size: cover; 
            background-position: center 20%;
            padding: 40px; 
            border-radius: 12px; 
            margin-bottom: 30px; 
            color: white; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: space-between;
        ">
            <div>
                <span style="background: #E50914; padding: 5px 12px; border-radius: 4px; font-weight: 800; font-size: 0.8rem; letter-spacing: 1px;">HOTSTAR SPECIAL</span>
                <h1 style="color: white !important; margin: 10px 0; font-size: 3rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);">Heart Beat</h1>
                <p style="font-size: 1.1rem; max-width: 600px; margin-bottom: 20px; text-shadow: 1px 1px 2px rgba(0,0,0,0.8);">
                    A gripping medical drama that pulses with life, love, and the pressure of saving lives.
                </p>
                <div style="display: flex; gap: 10px;">
                     <span style="background-color: #00d2ff; color: black; padding: 8px 16px; border: 3px solid black; border-radius: 8px; font-weight: 700; font-size: 0.85rem; display: inline-block; box-shadow: 3px 3px 0px black;">🏥 Medical Drama</span>
                     <span style="background-color: #ffd700; color: black; padding: 8px 16px; border: 3px solid black; border-radius: 8px; font-weight: 700; font-size: 0.85rem; display: inline-block; box-shadow: 3px 3px 0px black;">⭐ 9.8/10</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Filter Data
    filtered_db = filter_movies(movies, language, actor, content_type)
    
    # --- TRENDING SECTION (DEFAULT VIEW) ---
    st.subheader(f"🔥 Trending in {language if language != 'All' else 'All Languages'}")
    
    # Get top 8 sorted by priority and year hierarchy (current, past 2 years, older)
    filtered_db['is_priority'] = filtered_db['movieId'].apply(lambda x: 1 if x >= 300000 else 0)
    
    # Extract year and calculate year bucket
    current_year = datetime.datetime.now().year
    filtered_db['year'] = filtered_db['title'].str.extract(r'\((\d{4})\)').astype(float).fillna(0).astype(int)
    
    def get_trending_bucket(year):
        if year >= current_year - 1:
            return 0
        elif year >= current_year - 3:
            return 1
        else:
            return 2
            
    filtered_db['year_bucket'] = filtered_db['year'].apply(get_trending_bucket)
    
    # Sort by priority, year_bucket (current first), type (series first), and title
    trending_db = filtered_db.sort_values(by=['is_priority', 'year_bucket', 'type'], ascending=[False, True, False])
    trending_movies = trending_db.head(8).to_dict('records') 
    
    # Show Trending Grid by default
    display_recommendations(trending_movies, api_key, title="Trending Now", key_prefix="trending")

    # Smart Recommendations based on user activity
    if st.session_state.user_ratings or st.session_state.user_preferences["favorite_genres"]:
        st.markdown("---")
        st.subheader("🎯 Recommended For You")
        
        # Generate smart recommendations
        smart_recs = generate_smart_recommendations()
        if smart_recs:
            display_recommendations(smart_recs, api_key, title="", key_prefix="smart")
            st.caption("💡 Based on your ratings and preferences")

    st.markdown("---")
    st.subheader("🎬 Smart Recommendations by Genre")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        # Genre Selection for recommendations
        all_genres = sorted(list(set([g for sublist in movies['genres'].dropna() for g in sublist])))
        selected_rec_genres = st.multiselect("Select Genres you're in the mood for:", all_genres, key="rec_genre_select")
    
    with col2:
        generate_btn = st.button("Recommend", width='stretch', key="unified_generate_btn")

    if generate_btn:
        if selected_rec_genres:
            with st.spinner("Finding the best matches..."):
                try:
                    # Use the new metadata-based recommendation logic
                    results = recommender.recommend_by_metadata(
                        user_id=1, 
                        genres=selected_rec_genres, 
                        language=language, 
                        top_n=8
                    )
                    display_recommendations(results, api_key, title="🌟 Best Matches for You", key_prefix="hybrid")
                    
                    with st.expander("🤔 Why these recommendations?"):
                        st.markdown(f"These movies were chosen because they match your selected genres **({', '.join(selected_rec_genres)})** and preferred language **({language})**.")
                        st.markdown("We also factored in **Collaborative AI scores** based on what similar users enjoyed.")
                except Exception as e:
                    st.error(f"Error getting recommendations: {e}")
        else:
            st.warning("Please select at least one genre.")

import textwrap

def display_recommendations(results, api_key, title="", key_prefix=""):
    if title:
        st.markdown(f"### {title}")
    
    if not results:
        st.info("No movies found for these filters.")
        return

    cols = st.columns(4)
    for idx, movie in enumerate(results):
        with cols[idx % 4]:
            poster_url = None
            try:
                poster_url = fetch_movie_poster(movie.get('tmdbId', 0), api_key, title=movie['title'], cache_version=CACHE_VERSION)
            except Exception:
                pass
            
            placeholder_colors = ["F44336", "2196F3", "4CAF50", "FF9800", "FFEB3B", "9C27B0", "00BCD4", "795548"]
            color = placeholder_colors[idx % len(placeholder_colors)]
            
            def darken_color(hex_color):
                r = max(0, int(hex_color[0:2], 16) - 40)
                g = max(0, int(hex_color[2:4], 16) - 40)
                b = max(0, int(hex_color[4:6], 16) - 40)
                return f"{r:02x}{g:02x}{b:02x}"
            dark_color = darken_color(color)
            
            with st.container(border=True):
                # Contextual Badges
                if movie['title'] in st.session_state.watchlist:
                    st.markdown('<div class="poster-badge" style="background:#64FFDA; color:#020C1B;">📺 Watchlist</div>', unsafe_allow_html=True)
                elif st.session_state.user_ratings.get(movie['title'], 0) >= 4:
                    st.markdown('<div class="poster-badge" style="background:#7C4DFF; color:white;">🔥 Top Rated</div>', unsafe_allow_html=True)

                if poster_url:
                    try:
                        st.image(poster_url, width='stretch')
                    except Exception:
                        # Synthetic Poster Generator v2
                        canvas_html = f'<div style="background:linear-gradient(135deg,#{color} 0%,#{dark_color} 100%);color:white;padding:0;text-align:center;border-radius:12px;font-weight:bold;height:420px;display:flex;flex-direction:column;justify-content:center;align-items:center;position:relative;overflow:hidden;box-shadow:inset 0 0 100px rgba(0,0,0,0.5); border-bottom:3px solid var(--accent-color);"><div style="font-size:100px;margin-bottom:20px;filter:drop-shadow(0 10px 20px rgba(0,0,0,0.4));">🎬</div><div style="background:rgba(0,0,0,0.6);backdrop-filter:blur(10px);width:100%;padding:30px 10px;position:absolute;bottom:0;border-top:1px solid rgba(255,255,255,0.1);"><div style="font-family:\'Outfit\',sans-serif;font-size:20px;line-height:1.1;color:#64FFDA;margin-bottom:5px;">{movie["title"].upper()}</div><div style="font-size:12px;opacity:0.8;letter-spacing:2px;text-transform:uppercase;">{movie.get("language", "Unknown")} • {movie.get("type", "Film")}</div></div></div>'
                        st.markdown(canvas_html, unsafe_allow_html=True)
                else:
                    # Synthetic Poster Generator v2 (Fallback Case)
                    canvas_html = f'<div style="background:linear-gradient(135deg,#{color} 0%,#{dark_color} 100%);color:white;padding:0;text-align:center;border-radius:12px;font-weight:bold;height:420px;display:flex;flex-direction:column;justify-content:center;align-items:center;position:relative;overflow:hidden;box-shadow:inset 0 0 100px rgba(0,0,0,0.5); border-bottom:3px solid var(--accent-color);"><div style="font-size:100px;margin-bottom:20px;filter:drop-shadow(0 10px 20px rgba(0,0,0,0.4));">🎬</div><div style="background:rgba(0,0,0,0.6);backdrop-filter:blur(10px);width:100%;padding:30px 10px;position:absolute;bottom:0;border-top:1px solid rgba(255,255,255,0.1);"><div style="font-family:\'Outfit\',sans-serif;font-size:20px;line-height:1.1;color:#64FFDA;margin-bottom:5px;">{movie["title"].upper()}</div><div style="font-size:12px;opacity:0.8;letter-spacing:2px;text-transform:uppercase;">{movie.get("language", "Unknown")} • {movie.get("type", "Film")}</div></div></div>'
                    st.markdown(canvas_html, unsafe_allow_html=True)
                
                # Metadata
                st.markdown(f"**{movie['title']}**")
                st.caption(f"{movie.get('type', 'Movie')} | {movie.get('language', 'Unknown')}")
                
                # Genres
                if isinstance(movie.get('genres'), list) and movie['genres']:
                    genres_str = " • ".join(movie['genres'][:3])  # Show first 3 genres
                    st.caption(f"🎭 {genres_str}")
                elif isinstance(movie.get('genres'), str):
                    st.caption(f"🎭 {movie['genres']}")
                
                # User Rating
                current_rating = st.session_state.user_ratings.get(movie['title'], 0)
                user_rating = st.select_slider(
                    "Rate this",
                    options=[0, 1, 2, 3, 4, 5],
                    value=current_rating,
                    format_func=lambda x: "⭐" * x if x > 0 else "Rate",
                    key=f"rating_{key_prefix}_{idx}_{movie.get('movieId', idx)}"
                )
                
                if user_rating > 0 and user_rating != current_rating:
                    st.session_state.user_ratings[movie['title']] = user_rating
                    save_user_data(st.session_state.user_ratings, RATINGS_PATH)
                    st.toast(f"Rated {movie['title']}: {'⭐' * user_rating}", icon="⭐")
                
                # Buttons
                b1, b2 = st.columns(2)
                with b1:
                    # Trailer -> YouTube Search
                    youtube_url = f"https://www.youtube.com/results?search_query={movie['title'].replace(' ', '+')}+trailer"
                    st.link_button("Trailer", youtube_url, width='stretch')
                with b2:
                    # Watchlist
                    watchlist_text = "Added" if movie['title'] in st.session_state.watchlist else "Add"
                    if st.button(watchlist_text, key=f"wl_{key_prefix}_{idx}_{movie.get('movieId', idx)}", width='stretch'):
                        if movie['title'] not in st.session_state.watchlist:
                            st.session_state.watchlist.append(movie['title'])
                            save_user_data(st.session_state.watchlist, WATCHLIST_PATH)
                            st.toast(f"Added {movie['title']} to Watchlist!", icon="✅")
                        else:
                            st.session_state.watchlist.remove(movie['title'])
                            save_user_data(st.session_state.watchlist, WATCHLIST_PATH)
                            st.toast(f"Removed {movie['title']} from Watchlist!", icon="🗑️")
                        st.rerun()
                
                # Movie Details Button
                if st.button("Details", key=f"details_{key_prefix}_{idx}_{movie.get('movieId', idx)}", width='stretch'):
                    show_movie_details(movie, api_key=api_key)

def render_analytics_content():
    st.title("📊 Advanced Analytics Dashboard")
    
    # Enhanced Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Titles", f"{len(movies):,}")
    col2.metric("User Ratings", f"{len(ratings):,}")
    col3.metric("Languages", movies['language'].nunique())
    col4.metric("My Ratings", len(st.session_state.user_ratings))
    col5.metric("Watchlist", len(st.session_state.watchlist))
    
    st.markdown("---")
    
    # Tabs for different analytics
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🎭 Content Analysis", "👤 User Insights", "🔍 Search Trends"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎥 Content by Language")
            lang_counts = movies['language'].value_counts().head(10)
            st.bar_chart(lang_counts, color="#00E5FF")
            
            st.subheader("📺 Movies vs Series")
            type_counts = movies['type'].value_counts()
            st.bar_chart(type_counts, color="#D500F9")
        
        with col2:
            st.subheader("⭐ Rating Distribution")
            rating_counts = ratings['rating'].value_counts().sort_index()
            st.bar_chart(rating_counts, color="#00B0FF")
            
            st.subheader("🎭 Top Genres")
            all_genres = [genre for sublist in movies['genres'].dropna() for genre in sublist if isinstance(sublist, list)]
            genre_counts = pd.Series(all_genres).value_counts().head(10)
            st.bar_chart(genre_counts, color="#00E5FF")
    
    with tab2:
        st.subheader("🎬 Content Analysis")
        
        # Language-wise content breakdown
        lang_type_data = movies.groupby(['language', 'type']).size().unstack(fill_value=0)
        st.subheader("Content Distribution by Language & Type")
        st.dataframe(lang_type_data, width='stretch')
        
        # Top actors by appearance count
        st.subheader("🌟 Most Featured Actors")
        all_actors = []
        for actors_str in movies['actors'].dropna():
            if actors_str != 'Unknown':
                actors_list = [actor.strip() for actor in actors_str.split(',')]
                all_actors.extend(actors_list)
        
        if all_actors:
            actor_counts = pd.Series(all_actors).value_counts().head(15)
            st.bar_chart(actor_counts, color="#651FFF")
    
    with tab3:
        st.subheader("👤 Your Activity Insights")
        
        if st.session_state.user_ratings:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Your Rating Pattern")
                user_rating_counts = pd.Series(list(st.session_state.user_ratings.values())).value_counts().sort_index()
                st.bar_chart(user_rating_counts, color="#F50057")
                
                avg_rating = sum(st.session_state.user_ratings.values()) / len(st.session_state.user_ratings)
                st.metric("Your Average Rating", f"{avg_rating:.1f}⭐")
            
            with col2:
                st.subheader("Your Favorite Genres")
                user_rated_movies = movies[movies['title'].isin(st.session_state.user_ratings.keys())]
                user_genres = [genre for sublist in user_rated_movies['genres'].dropna() for genre in sublist if isinstance(sublist, list)]
                if user_genres:
                    user_genre_counts = pd.Series(user_genres).value_counts().head(8)
                    st.bar_chart(user_genre_counts, color="#00E5FF")
        else:
            st.info("Start rating movies to see your personal insights!")
        
        # Watchlist analysis
        if st.session_state.watchlist:
            st.subheader("📋 Watchlist Analysis")
            watchlist_movies = movies[movies['title'].isin(st.session_state.watchlist)]
            
            col1, col2 = st.columns(2)
            with col1:
                watchlist_lang = watchlist_movies['language'].value_counts()
                st.bar_chart(watchlist_lang, color="#00E5FF")
                st.caption("Languages in your watchlist")
            
            with col2:
                watchlist_type = watchlist_movies['type'].value_counts()
                st.bar_chart(watchlist_type, color="#D500F9")
                st.caption("Content types in your watchlist")
    
    with tab4:
        st.subheader("🔍 Search & Discovery Trends")
        
        if st.session_state.search_history:
            st.subheader("Your Recent Searches")
            for i, search in enumerate(reversed(st.session_state.search_history)):
                st.write(f"{i+1}. {search}")
        else:
            st.info("No search history yet.")
        
        # Popular content insights
        st.subheader("📊 Platform Insights")
        
        # Most common words in movie titles
        all_titles = ' '.join(movies['title'].dropna().str.lower())
        common_words = pd.Series(all_titles.split()).value_counts().head(20)
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        filtered_words = common_words[~common_words.index.isin(stop_words)]
        
        if not filtered_words.empty:
            st.bar_chart(filtered_words.head(10), color="#00E5FF")
            st.caption("Most common words in movie titles")
        
        
def render_advanced_search_content(api_key):
    st.subheader("🔍 Find Your Next Favorite")
    
    # Search Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_title = st.text_input("🎬 Search by Title", placeholder="Enter movie/series name...", key="adv_search_title")
        genre_options = ["All"] + sorted(list(set([g for sublist in movies['genres'].dropna() for g in sublist])))
        selected_genres = st.multiselect("🎭 Select Genres", genre_options[1:], key="adv_search_genres")
    
    with col2:
        current_year = datetime.datetime.now().year
        year_range = st.slider("📅 Release Year Range", 1990, current_year, (2000, current_year), key="adv_search_year")
        rating_range = st.slider("⭐ Minimum Rating", 1.0, 5.0, 3.0, 0.1, key="adv_search_rating")
    
    with col3:
        sort_by = st.selectbox("📊 Sort By", ["Relevance", "Rating", "Year", "Title"], key="adv_search_sort")
        results_limit = st.selectbox("📋 Results Limit", [10, 20, 50, 100], key="adv_search_limit")
    
    if st.button("Search", width='stretch', key="adv_search_btn"):
        # Apply filters
        filtered_movies = movies.copy()
        
        if search_title:
            filtered_movies = filtered_movies[
                filtered_movies['title'].str.contains(search_title, case=False, na=False)
            ]
            # Add to search history
            if search_title not in st.session_state.search_history:
                st.session_state.search_history.append(search_title)
                if len(st.session_state.search_history) > 10:
                    st.session_state.search_history.pop(0)
        
        if selected_genres:
            filtered_movies = filtered_movies[
                filtered_movies['genres'].apply(
                    lambda x: any(genre in x for genre in selected_genres) if isinstance(x, list) else False
                )
            ]
        
        # Extract year from title (basic extraction)
        filtered_movies['year'] = filtered_movies['title'].str.extract(r'\((\d{4})\)').astype(float)
        filtered_movies = filtered_movies[
            (filtered_movies['year'] >= year_range[0]) & 
            (filtered_movies['year'] <= year_range[1])
        ]
        
        # Sort results
        if sort_by == "Title":
            filtered_movies = filtered_movies.sort_values('title')
        elif sort_by == "Year":
            filtered_movies = filtered_movies.sort_values('year', ascending=False)
        
        results = filtered_movies.head(results_limit).to_dict('records')
        
        if results:
            st.success(f"Found {len(results)} results")
            display_recommendations(results, api_key, title="🎯 Search Results", key_prefix="adv_search")
        else:
            st.warning("No matches found.")
    
    # Search History
    if st.session_state.search_history:
        st.markdown("### 📚 Recent Searches")
        for i, search in enumerate(reversed(st.session_state.search_history[-5:])):
            if st.button(f"🔄 {search}", key=f"history_{i}"):
                st.rerun()

def render_user_profile():
    st.markdown('<div class="hero-container" style="padding:2rem;">', unsafe_allow_html=True)
    st.title("👤 My Movie Intelligence")
    st.markdown('<p class="hero-subtitle">Manage your cinematic preferences and track your journey across the world of film.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Movies Rated", len(st.session_state.user_ratings))
    col2.metric("Watchlist Items", len(st.session_state.watchlist))
    col3.metric("Searches Made", len(st.session_state.search_history))
    col4.metric("Favorite Genre", "N/A" if not st.session_state.user_preferences["favorite_genres"] else st.session_state.user_preferences["favorite_genres"][0])

    st.markdown("---")
    st.subheader("🎯 Content Tuning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Genre Preferences
        all_genres = sorted(list(set([g for sublist in movies['genres'].dropna() for g in sublist])))
        favorite_genres = st.multiselect(
            "Favorite Genres", 
            all_genres, 
            default=st.session_state.user_preferences["favorite_genres"]
        )
        
        # Language Preferences
        all_languages = sorted(movies['language'].unique())
        favorite_languages = st.multiselect(
            "Preferred Languages", 
            all_languages, 
            default=st.session_state.user_preferences["favorite_languages"]
        )
    
    with col2:
        # Content Type Preference
        preferred_type = st.selectbox(
            "Preferred Content Type", 
            ["All", "Movie", "Series"],
            index=["All", "Movie", "Series"].index(st.session_state.user_preferences["preferred_type"])
        )
        
        # Save preferences
        if st.button("Save My Preferences", width='stretch'):
            st.session_state.user_preferences = {
                "favorite_genres": favorite_genres,
                "favorite_languages": favorite_languages,
                "preferred_type": preferred_type
            }
            save_user_data(st.session_state.user_preferences, PREFERENCES_PATH)
            st.success("Preferences updated and saved!")
            st.rerun()
    
    st.markdown("---")
    
    # My Ratings Section
    st.subheader("⭐ My Ratings")
    if st.session_state.user_ratings:
        ratings_df = pd.DataFrame([
            {"Movie": movie, "Rating": rating} 
            for movie, rating in st.session_state.user_ratings.items()
        ])
        st.dataframe(ratings_df, width='stretch')
        
        if st.button("Clear All Ratings"):
            st.session_state.user_ratings = {}
            st.rerun()
    else:
        st.info("No ratings yet. Start rating movies from the Home page!")
    
    st.markdown("---")
    
    # Personalized Recommendations
    st.subheader("🎯 Personalized Recommendations")
    if st.session_state.user_preferences["favorite_genres"] or st.session_state.user_ratings:
        # Generate recommendations based on preferences
        personalized_movies = movies.copy()
        
        if st.session_state.user_preferences["favorite_genres"]:
            personalized_movies = personalized_movies[
                personalized_movies['genres'].apply(
                    lambda x: any(genre in x for genre in st.session_state.user_preferences["favorite_genres"]) 
                    if isinstance(x, list) else False
                )
            ]
        
        if st.session_state.user_preferences["favorite_languages"]:
            personalized_movies = personalized_movies[
                personalized_movies['language'].isin(st.session_state.user_preferences["favorite_languages"])
            ]
        
        if st.session_state.user_preferences["preferred_type"] != "All":
            personalized_movies = personalized_movies[
                personalized_movies['type'] == st.session_state.user_preferences["preferred_type"]
            ]
        
        # Exclude already rated movies
        rated_movies = list(st.session_state.user_ratings.keys())
        personalized_movies = personalized_movies[~personalized_movies['title'].isin(rated_movies)]
        
        # Sort recommendations by priority and year hierarchy (current, past 2 years, older)
        personalized_movies['is_priority'] = personalized_movies['movieId'].apply(lambda x: 1 if x >= 300000 else 0)
        current_year = datetime.datetime.now().year
        personalized_movies['year'] = personalized_movies['title'].str.extract(r'\((\d{4})\)').astype(float).fillna(0).astype(int)
        
        def get_profile_bucket(year):
            if year >= current_year - 1:
                return 0
            elif year >= current_year - 3:
                return 1
            else:
                return 2
                
        personalized_movies['year_bucket'] = personalized_movies['year'].apply(get_profile_bucket)
        personalized_movies = personalized_movies.sort_values(by=['is_priority', 'year_bucket'], ascending=[False, True])
        
        recommendations = personalized_movies.head(8).to_dict('records')
        if recommendations:
            display_recommendations(recommendations, st.secrets.get("tmdb_api_key", ""), title="🌟 Just For You")
        else:
            st.info("No new recommendations based on your preferences. Try expanding your genre selection!")
    else:
        st.info("Set your preferences above to get personalized recommendations!")

def render_about():
    st.markdown('<div class="hero-container" style="padding:2rem;">', unsafe_allow_html=True)
    st.title("ℹ️ About CineSmart AI")
    st.markdown('<p class="hero-subtitle">CineSmart AI is a state-of-the-art hybrid recommendation system designed to bridge the gap between South Indian regional excellence and global cinematic trends.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Project Overview
    st.markdown("""
    ### 🎬 Project Overview
    CineSmart AI is a comprehensive movie recommendation system that combines multiple AI techniques 
    to provide personalized movie and series recommendations. Built specifically with a focus on 
    South Indian cinema while supporting global content.
    """)
    
    # Features
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### ✨ Key Features
        - 🤖 **Hybrid AI Recommendations**
        - 🔍 **Advanced Search & Filters**
        - 👤 **User Profiles & Preferences**
        - ⭐ **Rating System**
        - 📊 **Analytics Dashboard**
        - 🎭 **Multi-language Support**
        - 📱 **Responsive Design**
        - 🎯 **Personalized Experience**
        """)
    
    with col2:
        st.markdown("""
        ### 🧠 AI Techniques Used
        - **Content-Based Filtering**: TF-IDF Vectorization
        - **Collaborative Filtering**: SVD Matrix Factorization
        - **Hybrid Approach**: Weighted combination
        - **Natural Language Processing**: Text analysis
        - **Machine Learning**: Scikit-learn & Surprise
        - **Data Processing**: Pandas & NumPy
        """)
    
    # Tech Stack
    st.markdown("""
    ### 🛠️ Technology Stack
    
    **Frontend & UI:**
    - Streamlit (Interactive Web App)
    - Custom CSS Styling
    - Responsive Design
    
    **Backend & AI:**
    - Python 3.10+
    - Scikit-Learn (Machine Learning)
    - Surprise Library (Collaborative Filtering)
    - Pandas & NumPy (Data Processing)
    
    **Data Sources:**
    - MovieLens Dataset
    - Custom Indian Movies Database
    - South Indian Cinema Collection
    - TMDB Integration
    """)
    
    # Dataset Info
    st.markdown("### 📊 Dataset Information")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Movies/Series", f"{len(movies):,}")
    col2.metric("User Ratings", f"{len(ratings):,}")
    col3.metric("Languages Supported", movies['language'].nunique())
    
    # Contact & Credits
    st.markdown("""
    ### 👨‍💻 About the Developer
    This project was developed as an advanced data science and machine learning demonstration,
    showcasing modern recommendation system techniques with a focus on user experience and 
    comprehensive feature set.
    
    **Key Achievements:**
    - Hybrid recommendation algorithm implementation
    - Multi-language content support
    - Real-time user preference learning
    - Scalable architecture design
    """)

if __name__ == "__main__":
    main()
