from ferreteria_refactor.backend_api.database.db import SessionLocal
from ferreteria_refactor.backend_api.models import models

def check_config():
    db = SessionLocal()
    try:
        print("\n=== BUSINESS CONFIGURATION IN DB ===")
        configs = db.query(models.BusinessConfig).all()
        for idx, c in enumerate(configs):
            print(f"{idx+1}. Key: '{c.key}' | Value: '{c.value}'")
        print("====================================\n")
        
        # Check specific expected keys
        expected = ["business_name", "ticket_template"]
        for key in expected:
            val = db.query(models.BusinessConfig).get(key)
            if val:
                print(f"✅ Found '{key}': {val.value[:50]}..." if val.value else f"⚠️  Found '{key}' but EMPTY")
            else:
                print(f"❌ NOT FOUND key: '{key}'")
                
    finally:
        db.close()

if __name__ == "__main__":
    check_config()
