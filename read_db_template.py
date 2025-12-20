from ferreteria_refactor.backend_api.database.db import SessionLocal
from ferreteria_refactor.backend_api.models import models

def read_template():
    db = SessionLocal()
    try:
        config = db.query(models.BusinessConfig).get("ticket_template")
        if config:
            print(f"=== CURRENT TEMPLATE (Len: {len(config.value)}) ===")
            print(config.value)
            print("===============================================")
            if "sale.items" in config.value:
                print("🚨 ALERT: 'sale.items' FOUND in template!")
            if "sale.products" in config.value:
                print("✅ 'sale.products' FOUND in template.")
        else:
            print("❌ No ticket template found in DB.")
    finally:
        db.close()

if __name__ == "__main__":
    read_template()
