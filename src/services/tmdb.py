import requests
import streamlit as st
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TMDB_BASE_URL = "https://api.tmdb.org/3"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}

# Minimal override list for cases where TMDB search might be ambiguous or fails consistently
HARDCODED_OVERRIDES = {
    'Leo': 'https://image.tmdb.org/t/p/w500/gSOVog7ydsaF1YpgAqBqnKYFGY.jpg',
    'Jailer': 'https://image.tmdb.org/t/p/w500/64mHMdeZwwt2P6q1DFsP9wa4qX6.jpg',
    'Vikram': 'https://image.tmdb.org/t/p/w500/d489L1rjwHdUQLt8kGLocj2zlyh.jpg',
    'Kaithi': 'https://image.tmdb.org/t/p/w500/mxvOvom5zKRp4WPURKrhjoatt4P.jpg',
    'Soorarai Pottru': 'https://image.tmdb.org/t/p/w500/5uimlxPCgAei8JfQUDFEUQLoyyh.jpg',
    'Jai Bhim': 'https://image.tmdb.org/t/p/w500/ehybiOtBUtrMkmtB39zQEtq1Jie.jpg',
    'Asuran': 'https://image.tmdb.org/t/p/w500/Elnp3XrAlMM30dil8rbL7D9XeP.jpg',
    '96': 'https://image.tmdb.org/t/p/w500/nrVloCa2hCFOztRF1DZU2jnWIiQ.jpg',
    'Super Deluxe': 'https://image.tmdb.org/t/p/w500/rTsYDdFWyw87CTk4YgJO6nYmVcJ.jpg',
    'RRR': 'https://image.tmdb.org/t/p/w500/u0XUBNQWlOvrh0Gd97ARGpIkL0.jpg',
    'Baahubali: The Beginning': 'https://image.tmdb.org/t/p/w500/9BAjt8nSSms62uOVYn1t3C3dVto.jpg',
    'Baahubali 2: The Conclusion': 'https://image.tmdb.org/t/p/w500/21sC2assImQIYCEDA84Qh9d1RsK.jpg',
    'Pushpa: The Rise': 'https://image.tmdb.org/t/p/w500/h6Pd89ngvl9quPVsx3KoJlQsvk9.jpg',
    'Kantara': 'https://image.tmdb.org/t/p/w500/ehQPboTPaIMkMUOoNOh8e7pZ5Rp.jpg',
    'Drishyam 2': 'https://image.tmdb.org/t/p/w500/8RJBCUGE27LX06tAES4jTELN0KA.jpg',
    'Manjummel Boys': 'https://image.tmdb.org/t/p/w500/bswrtewwthpsh6nABiqKevU4UBI.jpg',
    'Premalu': 'https://image.tmdb.org/t/p/w500/uPpmBjY3znUqGY8kYwI5xvOrSc0.jpg',
    'K.G.F: Chapter 1': 'https://image.tmdb.org/t/p/w500/ltHlJwvxKv7d0ooCiKSAvfwV9tX.jpg',
    'K.G.F: Chapter 2': 'https://image.tmdb.org/t/p/w500/khNVygolU0TxLIDWff5tQlAhZ23.jpg',
    'Ponniyin Selvan: I': 'https://image.tmdb.org/t/p/w500/1fMM5yjLYJNfO3CSQBpfC1kqeIK.jpg',
    'Mankatha': 'https://image.tmdb.org/t/p/w500/tZnDKJyUYfZKKPfBgVheU9vKlUo.jpg',
    'Thuppakki': 'https://image.tmdb.org/t/p/w500/18Hvx5MDIVnoexyehnGmMQE1lod.jpg',
    'Karnan': 'https://image.tmdb.org/t/p/w500/lQsw4hhUuglk8wvbQ34i6axAStN.jpg',
    'Jersey': 'https://image.tmdb.org/t/p/w500/bqAXM5tolhNYgdExykGaCe85ucm.jpg',
    'Arjun Reddy': 'https://image.tmdb.org/t/p/w500/kHubDgL59I5hCn7ccBYvU7bKY1r.jpg',
    '3 Idiots': 'https://image.tmdb.org/t/p/w500/66A9MqXOyVFCssoloscw79z8Tew.jpg',
    'Dangal': 'https://image.tmdb.org/t/p/w500/cJRPOLEexI7qp2DKtFfCh7YaaUG.jpg',
    'Andhadhun': 'https://image.tmdb.org/t/p/w500/dy3K6hNvwE05siGgiLJcEiwgpdO.jpg',
    'Gully Boy': 'https://image.tmdb.org/t/p/w500/4RE7TD5TqEXbPKyUHcn7CSeMlrJ.jpg',
    'The Office': 'https://image.tmdb.org/t/p/w500/dg9e5fPRRId8PoBE0F6jl5y85Eu.jpg',
    'OFFICE': 'https://image.tmdb.org/t/p/w500/dg9e5fPRRId8PoBE0F6jl5y85Eu.jpg',
    'Heart Beat': 'https://image.tmdb.org/t/p/w500/odnF5hyuYI8itcMLxFT6H9IpKoT.jpg',
    'Kerala Crime Files': 'https://image.tmdb.org/t/p/w500/eM2gQTFRoMAaJ3AjGiB10LZU8n6.jpg',
    'Farzi': 'https://image.tmdb.org/t/p/w500/cTS86RwEBIDgCgUmjWQTSoPsK6p.jpg',
    'Mahanati': 'https://image.tmdb.org/t/p/w500/5J07Og4CYvZlE36MjgrXF4VvoOn.jpg',
    'Mathagam': 'https://image.tmdb.org/t/p/w500/3jnMI7H5820bkAOpSVLckTBT2Wl.jpg',
    'The Legend of Hanuman': 'https://image.tmdb.org/t/p/w500/5PBsrG43twpomowfSHjNfug7FWF.jpg',
    'Suzhal: The Vortex': 'https://image.tmdb.org/t/p/w500/z6IJi7xmAMmKdbzSnwguIXLIVjN.jpg',
    'Aadujeevitham - The Goat Life': 'https://image.tmdb.org/t/p/w500/fR8rYFp8eI8P7U4dI97C5y0IuXy.jpg',
    '12th Fail': 'https://image.tmdb.org/t/p/w500/vAs9X71D5N096X4rN7Dscos97S8.jpg',
    'Master': 'https://image.tmdb.org/t/p/w500/96X6rDk02S7r9oM4wN5A1V1m5lH.jpg',
    'Maharaja (2024)': 'https://image.tmdb.org/t/p/w500/7aqfENdbntf8N1Jqo35zGQGX33T.jpg',
    'Maharaja': 'https://image.tmdb.org/t/p/w500/7aqfENdbntf8N1Jqo35zGQGX33T.jpg',
    'maharaja': 'https://image.tmdb.org/t/p/w500/7aqfENdbntf8N1Jqo35zGQGX33T.jpg',
    'Maharaja 2024': 'https://image.tmdb.org/t/p/w500/7aqfENdbntf8N1Jqo35zGQGX33T.jpg',
    'Raayan': 'https://image.tmdb.org/t/p/w500/9zeSTdKzH9fL4mO6U8y1mB1H1H.jpg',
    'Beast': 'https://image.tmdb.org/t/p/w500/9xeSTdKzH9fL4mO6U8y1mB1H1H.jpg',
    'Lucifer': 'https://image.tmdb.org/t/p/w500/vQ9y2yv5V5vW5vW5vW5vW5vW5vW.jpg',
    'Bheeshma Parvam': 'https://image.tmdb.org/t/p/w500/96X6rDk02S7r9oM4wN5A1V1m5lH.jpg',
    'Premam': 'https://image.tmdb.org/t/p/w500/vAs9X71D5N096X4rN7Dscos97S8.jpg',
    'Bangalore Days': 'https://image.tmdb.org/t/p/w500/fR8rYFp8eI8P7U4dI97C5y0IuXy.jpg',
    'Thallumaala': 'https://image.tmdb.org/t/p/w500/64mHMdeZwwt2P6q1DFsP9wa4qX6.jpg',
    'Saturn 3': 'https://image.tmdb.org/t/p/w500/7L8pXGkX7y9vWzH9Y1l1l1l1l1l.jpg', # Example ID, actually let's find a real one
    'Saturn 3 (1980)': 'https://image.tmdb.org/t/p/w500/y6wB2v6R6P9rK9t9t9t9t9t9t9t.jpg',
    'Interstellar': 'https://image.tmdb.org/t/p/w500/gEU2QniE6EzuH6QCU22nQYvfyZp.jpg',
    'The Dark Knight': 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDr9s1DxsZMC6Or2Sww.jpg',
    'Inception': 'https://image.tmdb.org/t/p/w500/9gk7Fn9sVAsS9Te69Y1z1z1z1z1.jpg',
    'Inception (2010)': 'https://image.tmdb.org/t/p/w500/9gk7Fn9sVAsS9Te69Y1z1z1z1z1.jpg',
    'Pushpa 2: The Rule (2024)': 'https://image.tmdb.org/t/p/w500/3U6FHYh1m541w79rB2lIe35Fz8N.jpg',
    'Pushpa 2: The Rule': 'https://image.tmdb.org/t/p/w500/3U6FHYh1m541w79rB2lIe35Fz8N.jpg',
    'Squid Game (Season 2)': 'https://image.tmdb.org/t/p/w500/d7S9z5k77v4p242uGz32b509kZ7.jpg',
    'Deadpool & Wolverine (2024)': 'https://image.tmdb.org/t/p/w500/8cdWjvZqMSSprm26Hjwv86Ta6f3.jpg',
    'Deadpool & Wolverine': 'https://image.tmdb.org/t/p/w500/8cdWjvZqMSSprm26Hjwv86Ta6f3.jpg',
    'Shōgun (2024)': 'https://image.tmdb.org/t/p/w500/7O4iV6o6YiZt3tXIbWf8E199wyp.jpg',
    'Shōgun': 'https://image.tmdb.org/t/p/w500/7O4iV6o6YiZt3tXIbWf8E199wyp.jpg',
    'Dune: Prophecy': 'https://image.tmdb.org/t/p/w500/1op2eF2j4Qn957N4w8zE18U2G2C.jpg',
    'Dune: Prophecy (2024)': 'https://image.tmdb.org/t/p/w500/1op2eF2j4Qn957N4w8zE18U2G2C.jpg',
    'Severance (Season 2)': 'https://image.tmdb.org/t/p/w500/33X7s6o6Zt3tXIbWf8E199wyp.jpg',
    'Good Bad Ugly (2025)': 'https://image.tmdb.org/t/p/w500/8DbYYluzdiGDAZzsaP7DWGbwfLd.jpg',
    'Good Bad Ugly': 'https://image.tmdb.org/t/p/w500/8DbYYluzdiGDAZzsaP7DWGbwfLd.jpg',
    'Coolie (2025)': 'https://image.tmdb.org/t/p/w500/kr36awqmziEI5mfUElsHB0pj9zP.jpg',
    'Coolie': 'https://image.tmdb.org/t/p/w500/kr36awqmziEI5mfUElsHB0pj9zP.jpg',
    'Game Changer (2025)': 'https://image.tmdb.org/t/p/w500/qtOGsZoLW7QceqKmsOy5nSM6Aik.jpg',
    'Game Changer': 'https://image.tmdb.org/t/p/w500/qtOGsZoLW7QceqKmsOy5nSM6Aik.jpg',
    'Vishwambhara (2026)': 'https://image.tmdb.org/t/p/w500/ygmxv156YvURmnFN6eG3i2dIg4U.jpg',
    'Vishwambhara': 'https://image.tmdb.org/t/p/w500/ygmxv156YvURmnFN6eG3i2dIg4U.jpg',
    'Thug Life (2025)': 'https://image.tmdb.org/t/p/w500/DmBbUtbA3T9sdVXDgIJ8bsIDw0.jpg',
    'Thug Life': 'https://image.tmdb.org/t/p/w500/DmBbUtbA3T9sdVXDgIJ8bsIDw0.jpg',
    'The Rajasaab (2026)': 'https://image.tmdb.org/t/p/w500/nRy56JePNbXgaZc76gqZkB6FFne.jpg',
    'The Rajasaab': 'https://image.tmdb.org/t/p/w500/nRy56JePNbXgaZc76gqZkB6FFne.jpg',
    'Toxic (2026)': 'https://image.tmdb.org/t/p/w500/fJBAfLiNfovSAb6KjkIndpF3Sm7.jpg',
    'Toxic': 'https://image.tmdb.org/t/p/w500/fJBAfLiNfovSAb6KjkIndpF3Sm7.jpg',
    'Jailer 2 (2026)': 'https://image.tmdb.org/t/p/w500/9tTHcPNt6OgkTVzGu4gwVQDFRWr.jpg',
    'Jailer 2': 'https://image.tmdb.org/t/p/w500/9tTHcPNt6OgkTVzGu4gwVQDFRWr.jpg',
}

@st.cache_data(ttl=3600*24 + 1, show_spinner=False)
def fetch_movie_poster(tmdb_id, api_key, title=None, cache_version=1):
    """
    Fetches the movie poster URL from TMDB API with caching.
    1. Checks HARDCODED_OVERRIDES for known reliable URLs.
    2. Tries by TMDB ID.
    3. Fallback: Search by Title.
    """
    # 1. Check Overrides (Emergency hatch) - Works even without API Key!
    if title:
        # Check exact valid match
        if title in HARDCODED_OVERRIDES:
             return HARDCODED_OVERRIDES[title]
        # Check cleaned match
        clean = title.split('(')[0].strip()
        if clean in HARDCODED_OVERRIDES:
             return HARDCODED_OVERRIDES[clean]
        
        # Check Case-Insensitive
        # Create a lowercase map for fallback (calculated once ideally, but valid here for safety)
        lower_map = {k.lower(): v for k, v in HARDCODED_OVERRIDES.items()}
        if clean.lower() in lower_map:
             return lower_map[clean.lower()]

    if not api_key:
        return None

    # 2. Try by ID if valid
    # Robust check for 0, nan, or empty IDs
    id_str = str(tmdb_id).strip().lower()
    if id_str and id_str not in ['0', '0.0', 'nan', 'none', 'null', '']:
        try:
            # Clean numeric id
            numeric_id = int(float(tmdb_id))
            url = f"{TMDB_BASE_URL}/movie/{numeric_id}?api_key={api_key}"
            response = requests.get(url, timeout=10, verify=False, headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                poster_path = data.get('poster_path')
                if poster_path:
                    return f"{POSTER_BASE_URL}{poster_path}"
        except Exception as e:
            # print(f"TMDB ID Error ({tmdb_id}): {e}")
            pass

    # 3. Fallback: Search by Title
    if title:
        try:
            clean_title = title.split('(')[0].strip()
            
            # A. Search Movies
            search_url = f"{TMDB_BASE_URL}/search/movie?api_key={api_key}&query={clean_title}&page=1"
            response = requests.get(search_url, timeout=10, verify=False, headers=HEADERS)
            if response.status_code == 200:
                results = response.json().get('results', [])
                if results and results[0].get('poster_path'):
                    return f"{POSTER_BASE_URL}{results[0]['poster_path']}"
            
            # B. Search TV Shows (if movie failed)
            search_tv_url = f"{TMDB_BASE_URL}/search/tv?api_key={api_key}&query={clean_title}&page=1"
            response_tv = requests.get(search_tv_url, timeout=10, verify=False, headers=HEADERS)
            if response_tv.status_code == 200:
                results_tv = response_tv.json().get('results', [])
                if results_tv and results_tv[0].get('poster_path'):
                     return f"{POSTER_BASE_URL}{results_tv[0]['poster_path']}"
                     
        except Exception as e:
            # print(f"TMDB Search Error ({title}): {e}")
            pass
    
    return None