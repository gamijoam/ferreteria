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

# Try to load .env from multiple locations
# Priority: Local .env > Server .env > Parent .env
env_files = [
    os.path.join(BASE_DIR, '.env'),
    os.path.join(os.getcwd(), '.env'),
    os.path.abspath(os.path.join(BASE_DIR, '..', 'Server', '.env')),
    os.path.abspath(os.path.join(BASE_DIR, '..', 'server', '.env')),
    os.path.abspath(os.path.join(BASE_DIR, '..', '.env'))
]

env_loaded = False
for env_path in env_files:
    if os.path.exists(env_path):
        print(f"✅ DEBUG: Loading .env from: {env_path}")
        load_dotenv(env_path)
        env_loaded = True
        break

if not env_loaded:
    print(f"⚠️ DEBUG: No .env file found in: {env_files}")

DATABASE_URL = os.getenv("DB_URL")

if DATABASE_URL:
    # Mask password for debug
    safe_url = DATABASE_URL
    if "@" in safe_url:
        try:
            # simple masking assuming postgres://user:pass@host...
            part1 = safe_url.split("@")[0]
            part2 = safe_url.split("@")[1]
            if ":" in part1:
                prefix = part1.split(":")[0]
                safe_url = f"{prefix}:****@{part2}"
        except:
            pass
    print(f"✅ DEBUG: DATABASE_URL loaded: {safe_url}")
else:
    # Default to local sqlite for portability
    db_path = os.path.join(BASE_DIR, "ferreteria.db")
    DATABASE_URL = f"sqlite:///{db_path}"
    print(f"⚠️ Warning: DB_URL not found. Using default SQLite: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
