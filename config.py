import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
print(f"--- DEBUG CONFIG ---")
print(f"Loading .env from: {env_path}")
print(f"File exists: {os.path.exists(env_path)}")
load_dotenv(dotenv_path=env_path)

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ferreteria_refactor.db")
    print(f"Loaded DATABASE_URL starting with: {DATABASE_URL[:10]}...") # Print first 10 chars to verify protocol
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()
