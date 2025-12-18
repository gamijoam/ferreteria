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
    DATABASE_URL: str = os.getenv("DB_URL", os.getenv("DATABASE_URL", "sqlite:///./ferreteria.db"))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    # Generate a key if not set - safer than hardcoded default
    if not SECRET_KEY:
        import secrets
        SECRET_KEY = secrets.token_urlsafe(32)
        print("WARNING: SECRET_KEY not set in .env. Using temporary generated key.")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

settings = Settings()
