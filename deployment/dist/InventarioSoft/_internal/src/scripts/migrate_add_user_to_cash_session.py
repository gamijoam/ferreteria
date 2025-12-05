"""
Migration script to add user_id to cash_sessions table
"""
import sys
sys.path.insert(0, '.')

from src.database.db import SessionLocal, engine
from sqlalchemy import text

def migrate():
    db = SessionLocal()
    try:
        # Add user_id column to cash_sessions
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='cash_sessions' AND column_name='user_id'
            """))
            
            if not result.fetchone():
                print("Adding user_id column to cash_sessions...")
                conn.execute(text("""
                    ALTER TABLE cash_sessions 
                    ADD COLUMN user_id INTEGER REFERENCES users(id)
                """))
                conn.commit()
                print("OK - user_id column added successfully")
            else:
                print("user_id column already exists")
                
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
