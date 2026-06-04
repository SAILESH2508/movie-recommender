import hashlib
from src.database import DatabaseManager

class AuthManager:
    """
    Handles User Authentication logic.
    """
    def __init__(self):
        self.db = DatabaseManager()

    def _hash_password(self, password):
        """
        Simple SHA-256 hashing. 
        In production, use bcrypt/argon2 and salts.
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, username, password):
        """
        Verifies credentials. Returns User ID if successful, else None.
        """
        user = self.db.get_user_by_username(username)
        if user:
            # user tuple: (id, username, hash, created_at)
            stored_hash = user[2]
            if self._hash_password(password) == stored_hash:
                return {'id': user[0], 'username': user[1]}
        return None

    def signup(self, username, password):
        """
        Creates a new user. Returns True if successful, False if username exists.
        """
        if not username or not password:
            return False
            
        password_hash = self._hash_password(password)
        return self.db.create_user(username, password_hash)
