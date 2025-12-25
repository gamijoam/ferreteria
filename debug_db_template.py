import os
import sys

# Ensure we can import from the package
sys.path.append(os.getcwd())

from ferreteria_refactor.backend_api.database.db import SessionLocal, settings
from ferreteria_refactor.backend_api.models import models
from ferreteria_refactor.backend_api import template_presets

def debug_template():
    print(f">> USING DATABASE URL: {settings.DATABASE_URL}")
    
    db = SessionLocal()
    try:
        # 1. READ CURRENT
        config = db.query(models.BusinessConfig).filter(models.BusinessConfig.key == "ticket_template").first()
        
        print("\n>> CURRENT DB VALUE (First 200 chars):")
        if config:
            print("-" * 40)
            print(config.value[:200])
            print("-" * 40)
        else:
            print(">> No 'ticket_template' found in DB.")

        # 2. GET DESIRED NEW VALUE
        new_template = template_presets.get_classic_template()
        print("\n>> DESIRED NEW VALUE (First 200 chars):")
        print("-" * 40)
        print(new_template[:200])
        print("-" * 40)

        # 3. COMPARE AND UPDATE
        if config and config.value == new_template:
            print("\n>> MATCH! The database DOES have the correct template.")
        else:
            print("\n>> MISMATCH! Updating database now...")
            if not config:
                config = models.BusinessConfig(key="ticket_template", value=new_template)
                db.add(config)
            else:
                config.value = new_template
            
            db.commit()
            print(">> Update Committed.")
            
            # 4. VERIFY UPDATE
            db.refresh(config)
            print(">> Re-reading from DB...")
            if config.value == new_template:
                print(">> VERIFIED: Database now holds the new value.")
            else:
                print(">> FAILED: Database still holds old value (transaction issue?).")
        
    except Exception as e:
        print(f"!! EXCEPTION: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_template()
