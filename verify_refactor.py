import sys
import os
import time
import requests
import subprocess
import threading

# Add root to python path to import modules
# Add ferreteria_refactor to python path to emulate running from within that dir for backend imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "ferreteria_refactor")))

from backend_api.database.db import SessionLocal, engine
from backend_api.models import models
# Frontend services can still be imported from the package structure or adjusted
from frontend_caja.services.product_service import ProductService

def wait_for_server(url, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            requests.get(url)
            return True
        except requests.ConnectionError:
            time.sleep(1)
            print("Waiting for server...")
    return False

def seed_db():
    print("Seeding database with dummy products...")
    db = SessionLocal()
    # Check if products exist
    if db.query(models.Product).count() == 0:
        p1 = models.Product(name="Martillo", price=10.0, stock=100.0, sku="M100", is_active=True)
        p2 = models.Product(name="Clavos Caja", price=5.0, stock=50.0, sku="C50", is_box=True, conversion_factor=100, is_active=True)
        db.add(p1)
        db.add(p2)
        db.commit()
        print("Products added.")
    else:
        print("Database already seeded.")
    db.close()

def run_test():
    base_url = "http://127.0.0.1:8000"
    
    # 1. Start Server in separate thread/process
    # We assume server is running via uvicorn for this test, or we start it here.
    # For simplicity in this script, we assume the user/agent starts it externally or we try popen
    server_process = subprocess.Popen(
        ["uvicorn", "ferreteria_refactor.backend_api.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    try:
        print("Starting Backend Server...")
        if not wait_for_server(base_url):
            print("Failed to start server.")
            return

        seed_db()

        print("\n--- Testing Frontend Service ---")
        service = ProductService()
        
        # Test GET
        products = service.get_all_products()
        print(f"Products fetched: {len(products)}")
        for p in products:
            print(f" - {p['name']} (${p['price']}) Stock: {p['stock']}")

        if not products:
            print("Error: No products returned.")
            return

        # Test POST (Sale)
        print("\n--- Testing Sale ---")
        product_id = products[0]['id']
        sale_data = {
            "payment_method": "Efectivo",
            "total_amount": 20.0,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2,
                    "is_box": False
                }
            ]
        }
        
        result = service.record_sale(sale_data)
        print("Sale Result:", result)
        
        if result and result.get("status") == "success":
            print("✅ TEST PASSED: Sale recorded successfully.")
        else:
            print("❌ TEST FAILED: Sale recording failed.")

    finally:
        print("Stopping Server...")
        server_process.terminate()

if __name__ == "__main__":
    run_test()
