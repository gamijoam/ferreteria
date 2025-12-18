import sys
import os

# Add to path
sys.path.append(r"c:\Users\Equipo\Documents\ferreteria\ferreteria_refactor")

print("--- Debugging DB Connection ---")

try:
    from backend_api.config import settings
    print(f"Settings loaded.")
    print(f"DATABASE_URL len: {len(settings.DATABASE_URL)}")
    print(f"DATABASE_URL repr: {repr(settings.DATABASE_URL)}")
    
    from backend_api.database.db import engine
    print("Engine created. Attempting connection...")
    
    with engine.connect() as conn:
        print("Connection successful!")
        
except Exception as e:
    print(f"Caught exception: {e}")
    # import traceback
    # traceback.print_exc()
