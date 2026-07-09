import sqlite3
import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "MAMET_OS_SECRET_KEY_SUPER_SECURE"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

class AuthHandler:
    def __init__(self):
        self.db_path = os.path.join(os.path.expanduser("~"), ".mamet", "users.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
        
    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            
    def register_user(self, email: str, password: str) -> bool:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                    (email, hashed.decode('utf-8'))
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
            
    def verify_user(self, email: str, password: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            if not row:
                return False
            
            stored_hash = row[0].encode('utf-8')
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
            
    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        from datetime import timezone
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
        
    def decode_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None