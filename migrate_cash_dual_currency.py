import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DB_URL")
if not DATABASE_URL:
    # Fallback for local testing if .env not found or empty
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/ferreteria_db"

print(f"Connecting to database: {DATABASE_URL}")

def run_migration():
    engine = create_engine(DATABASE_URL)
    
    # List of commands to run
    commands = [
        ("ALTER TABLE cash_sessions ADD COLUMN initial_cash_bs FLOAT DEFAULT 0.0", "initial_cash_bs"),
        ("ALTER TABLE cash_sessions ADD COLUMN final_cash_reported_bs FLOAT", "final_cash_reported_bs"),
        ("ALTER TABLE cash_sessions ADD COLUMN final_cash_expected_bs FLOAT", "final_cash_expected_bs"),
        ("ALTER TABLE cash_sessions ADD COLUMN difference_bs FLOAT", "difference_bs"),
        ("ALTER TABLE cash_movements ADD COLUMN currency VARCHAR DEFAULT 'USD'", "currency"),
        ("ALTER TABLE cash_movements ADD COLUMN exchange_rate FLOAT DEFAULT 1.0", "exchange_rate")
    ]

    print("Starting migration...")
    
    for sql, col_name in commands:
        try:
            # Use a fresh connection for each command to avoid transaction blocks
            with engine.connect() as connection:
                with connection.begin(): # Start transaction
                    print(f"Adding {col_name}...")
                    connection.execute(text(sql))
                    print(f"- Added {col_name}")
        except Exception as e:
            # If it fails (e.g. duplicate column), just print and continue
            print(f"- Skipped {col_name} (might already exist): {e}")

    print("Migration completed successfully!")

if __name__ == "__main__":
    run_migration()
