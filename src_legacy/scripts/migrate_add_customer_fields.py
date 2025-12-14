from sqlalchemy import create_engine, text
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.database.db import DATABASE_URL

def migrate():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Add email column
        try:
            conn.execute(text("ALTER TABLE customers ADD COLUMN email VARCHAR"))
            print("Added email column")
        except Exception as e:
            print(f"email column might already exist: {e}")

        # Add credit_limit column
        try:
            conn.execute(text("ALTER TABLE customers ADD COLUMN credit_limit FLOAT DEFAULT 0.0"))
            print("Added credit_limit column")
        except Exception as e:
            print(f"credit_limit column might already exist: {e}")
            
        conn.commit()

if __name__ == "__main__":
    migrate()
