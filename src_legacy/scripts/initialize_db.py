# initialize_db.py
"""Utility script to (re)create the database schema and a default admin user.

Steps to use:
1. Ensure the environment variable ``DB_URL`` points to a valid PostgreSQL database.
   Example in ``.env``:
   ``DB_URL=postgresql+psycopg2://user:password@localhost/ferreteria``
2. Run the script:
   ``python src/scripts/initialize_db.py``
   This will:
   * Drop all tables (if they exist) and recreate them based on the models.
   * Insert a default admin user (username: admin, password: admin123).
   * Print a short summary.

You can modify the ``DEFAULT_ADMIN`` dict below to set a different username/password.
"""

import sys, os
import pathlib
import hashlib

# Add the project root (two levels up) to PYTHONPATH using pathlib for clarity
project_root = pathlib.Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.models import Base, User, UserRole
from src.database.db import DATABASE_URL

# ---------------------------------------------------------------------------
# Configuration – change if you need a different default admin
# ---------------------------------------------------------------------------
DEFAULT_ADMIN = {
    "username": "admin",
    "password": "admin123",  # In a real deployment, hash the password!
    "role": UserRole.ADMIN,
}

def main():
    # Create engine (reuse the same URL used by the app)
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Drop all existing tables (optional – uncomment if you really want to purge)
    # print("Dropping existing tables…")
    # Base.metadata.drop_all(bind=engine)

    # Create tables according to the current models
    print("Creating tables…")
    Base.metadata.create_all(bind=engine)

    # Insert default admin if not present
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == DEFAULT_ADMIN["username"]).first()
        if existing:
            print(f"Admin user '{DEFAULT_ADMIN['username']}' already exists.")
        else:
            # Hash the password using SHA256 to match AuthController logic
            hashed_password = hashlib.sha256(DEFAULT_ADMIN["password"].encode()).hexdigest()
            
            admin = User(
                username=DEFAULT_ADMIN["username"],
                password_hash=hashed_password,
                role=DEFAULT_ADMIN["role"],
            )
            db.add(admin)
            db.commit()
            print(f"Created admin user '{DEFAULT_ADMIN['username']}'.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
