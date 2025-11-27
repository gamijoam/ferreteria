import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Determine if running as script or frozen exe
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running as script
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Try to load .env from the application directory
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(env_path)

DATABASE_URL = os.getenv("DB_URL")

if not DATABASE_URL:
    # Default to local sqlite for portability
    db_path = os.path.join(BASE_DIR, "ferreteria.db")
    DATABASE_URL = f"sqlite:///{db_path}"
    print(f"Warning: DB_URL not set. Using default: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
