import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from src.database.db import engine

def migrate():
    """Add location column to products table"""
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Check if column exists
            result = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='products' AND column_name='location'"
            ))
            if result.fetchone():
                print("Column 'location' already exists in 'products' table.")
            else:
                print("Adding 'location' column to 'products' table...")
                conn.execute(text("ALTER TABLE products ADD COLUMN location TEXT"))
                print("Column added successfully!")
            
            trans.commit()
            print("Migration completed successfully.")
        except Exception as e:
            trans.rollback()
            print(f"Migration failed: {str(e)}")
            raise e

if __name__ == "__main__":
    confirm = input("This will add 'location' column to products table. Continue? (y/n): ")
    if confirm.lower() == 'y':
        migrate()
