
import sys
import os

# Add parent directory of 'ferreteria_refactor' to path
# Script is in: c:\Users\Equipo\Documents\ferreteria\ferreteria_refactor\verify_print_fix.py
# We need to add: c:\Users\Equipo\Documents\ferreteria
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
print(f"DEBUG: Added {project_root} to sys.path")

from ferreteria_refactor.database.db import SessionLocal
from ferreteria_refactor.backend_api.models import models
from ferreteria_refactor.backend_api.services.sales_service import print_sale_ticket

def test_print_logic():
    print("🧪 STARTING MANUAL PRINT TEST")
    print("============================")
    
    db = SessionLocal()
    try:
        # Get last sale
        last_sale = db.query(models.Sale).order_by(models.Sale.id.desc()).first()
        if not last_sale:
            print("❌ No sales found in database")
            return
            
        print(f"📝 Found Last Sale ID: {last_sale.id}")
        
        # Call the function directly
        print("🚀 Calling print_sale_ticket()...")
        try:
            print_sale_ticket(last_sale.id)
            print("✅ Function call completed without exception")
        except Exception as e:
            print(f"❌ Function call FAILED: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            
    finally:
        db.close()
        print("============================")

if __name__ == "__main__":
    test_print_logic()
