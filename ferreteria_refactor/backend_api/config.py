import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

class Settings:
    # Support both naming conventions
    DATABASE_URL: str = os.getenv("DATABASE_URL") or os.getenv("DB_URL") or "sqlite:///./ferreteria_refactor.db"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()
