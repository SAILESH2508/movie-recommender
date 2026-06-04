import sqlite3
import hashlib
import os

DB_PATH = "data/app.db"

class DatabaseManager:
    """
    Manages SQLite database interactions.
    """
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """
        Initializes the database tables if they don't exist.
        """
        if not os.path.exists("data"):
            os.makedirs("data")
            
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Watchlist Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                movie_id INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id),
                UNIQUE(user_id, movie_id)
            )
        ''')
        
        # User Ratings Table (for new interactive ratings)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                movie_id INTEGER,
                rating REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id),
                UNIQUE(user_id, movie_id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def execute_query(self, query, params=()):
        """
        Executes a query and returns the results.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.lastrowid
            return result
        except Exception as e:
            print(f"Database Error: {e}")
            return None
        finally:
            conn.close()
            
    def get_user_by_username(self, username):
        query = "SELECT * FROM users WHERE username = ?"
        result = self.execute_query(query, (username,))
        return result[0] if result else None

    def create_user(self, username, password_hash):
        try:
            query = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
            self.execute_query(query, (username, password_hash))
            return True
        except sqlite3.IntegrityError:
            return False

    def add_to_watchlist(self, user_id, movie_id):
        try:
            query = "INSERT INTO watchlist (user_id, movie_id) VALUES (?, ?)"
            self.execute_query(query, (user_id, movie_id))
            return True
        except sqlite3.IntegrityError:
            return False # Already in watchlist

    def remove_from_watchlist(self, user_id, movie_id):
        query = "DELETE FROM watchlist WHERE user_id = ? AND movie_id = ?"
        self.execute_query(query, (user_id, movie_id))

    def get_watchlist(self, user_id):
        query = "SELECT movie_id FROM watchlist WHERE user_id = ?"
        result = self.execute_query(query, (user_id,))
        return [row[0] for row in result] if result else []

    def log_rating(self, user_id, movie_id, rating):
        # Insert or Replace allows updating logic
        query = "INSERT OR REPLACE INTO user_ratings (user_id, movie_id, rating) VALUES (?, ?, ?)"
        self.execute_query(query, (user_id, movie_id, rating))
        
    def get_user_ratings(self, user_id):
        query = "SELECT movie_id, rating FROM user_ratings WHERE user_id = ?"
        result = self.execute_query(query, (user_id,))
        return result if result else []
    
    def get_all_ratings_count(self):
        query = "SELECT COUNT(*) FROM user_ratings"
        result = self.execute_query(query)
        return result[0][0] if result else 0
