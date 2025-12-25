from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from ferreteria_refactor.backend_api.models import models

# Setup DB
DATABASE_URL = "postgresql://postgres:password@localhost:5432/ferreteria_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Get latest sale
    latest_sale = db.query(models.Sale).order_by(models.Sale.id.desc()).first()
    
    if not latest_sale:
        print("❌ No sales found.")
    else:
        print(f"Latest Sale ID: {latest_sale.id}")
        print(f"Date: {latest_sale.date}")
        print(f"Total: {latest_sale.total_amount}")
        print("-" * 30)
        print("ITEMS:")
        for item in latest_sale.details:
            product = db.query(models.Product).get(item.product_id)
            print(f"Product: {product.name}")
            print(f"   Quantity: {item.quantity}")
            print(f"   Unit Price: {item.unit_price}")
            print(f"   Subtotal: {item.subtotal}")
            print(f"   Discount Field: {item.discount}")
            print(f"   Discount Type: {item.discount_type}")
            print("-" * 30)

finally:
    db.close()
