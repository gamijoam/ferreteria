from ferreteria_refactor.backend_api.database.db import SessionLocal
from ferreteria_refactor.backend_api.models import models

def fix_template():
    db = SessionLocal()
    try:
        print("\n=== FIXING TICKET TEMPLATE IN DB ===")
        config = db.query(models.BusinessConfig).get("ticket_template")
        
        if config and config.value:
            print("Found existing template.")
            if "sale.items" in config.value:
                print("⚠️  Found problematic 'sale.items'. Replacing with 'sale.products'...")
                new_val = config.value.replace("sale.items", "sale.products")
                config.value = new_val
                db.commit()
                print("✅ Template updated successfully!")
            else:
                print("✅ Template already uses safe syntax (or doesn't have loop).")
                
            # Double check business name
            biz_config = db.query(models.BusinessConfig).get("business_name")
            if not biz_config:
                 print("⚠️  Business Name missing. Creating default...")
                 db.add(models.BusinessConfig(key="business_name", value="MI FERRETERIA"))
                 db.commit()
            elif not biz_config.value:
                 print("⚠️  Business Name empty. Setting default...")
                 biz_config.value = "MI FERRETERIA"
                 db.commit()
                 
        else:
            print("❌ No ticket template found. Nothing to fix.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_template()
