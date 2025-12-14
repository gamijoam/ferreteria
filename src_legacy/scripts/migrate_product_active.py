import sys, os
import pathlib
from sqlalchemy import create_engine, text

# Add project root to path
project_root = pathlib.Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.database.db import DATABASE_URL

def migrate():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            # Check if column exists
            result = conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='products' AND column_name='is_active'"
            ))
            if result.fetchone():
                print("Column 'is_active' already exists in 'products' table.")
            else:
                print("Adding 'is_active' column to 'products' table...")
                conn.execute(text("ALTER TABLE products ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
                conn.commit()
                print("Migration successful!")
        except Exception as e:
            print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
