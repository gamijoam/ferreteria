import os
from dotenv import load_dotenv

import sys

# Determine base path for .env
if getattr(sys, 'frozen', False):
    # Valid for PyInstaller compiled executable
    base_path = os.path.dirname(sys.executable)
else:
    # Valid for development script
    base_path = os.path.dirname(os.path.abspath(__file__))

# Try loading from base path (priority)
env_path = os.path.join(base_path, ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    # Fallback to CWD
    load_dotenv()

class Settings:
    # Support both naming conventions
    _db_url = os.getenv("DB_URL", os.getenv("DATABASE_URL", "sqlite:///./ferreteria.db"))
    
    # Fix PostgreSQL encoding issues
    if "postgresql" in _db_url:
        if "?" not in _db_url:
            _db_url += "?client_encoding=utf8"
        elif "client_encoding" not in _db_url:
            _db_url += "&client_encoding=utf8"
    
    DATABASE_URL: str = _db_url
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-it-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

settings = Settings()
