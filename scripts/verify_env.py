from dotenv import load_dotenv
import os
import sys

# Mimic config.py logic
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    # Assuming this script is run from project root, and config is in backend_api
    # Actually config.py is in backend_api, so it looks in backend_api/.env
    # Let's verify what `backend_api/config.py` would see.
    base_path = os.path.abspath("ferreteria_refactor/backend_api")

env_path = os.path.join(base_path, ".env")
print(f"Checking for .env at: {env_path}")
if os.path.exists(env_path):
    print("✅ .env file found!")
    load_dotenv(dotenv_path=env_path)
else:
    print("❌ .env file NOT found at expected location.")

db_url = os.getenv("DATABASE_URL")
if db_url:
    print(f"✅ DATABASE_URL found: {db_url}")
else:
    print("❌ DATABASE_URL is NOT set in environment.")
    print("   Defaulting to SQLite (which explains your error).")
    
print("-" * 30)
print("Current Environment Variables (Partial):")
print(f"DB_URL: {os.getenv('DB_URL')}")
print(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")
