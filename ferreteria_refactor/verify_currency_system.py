"""
Verification script for Multi-Currency System
This script tests the database schema and initialization
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ferreteria_refactor.backend_api.database.db import SessionLocal, engine
from ferreteria_refactor.backend_api.models.models import Currency, ExchangeRate, Product, PriceRule, SaleDetail, Base
from sqlalchemy import inspect


def verify_tables():
    """Verify that all tables were created"""
    print("\n" + "="*60)
    print("[VERIFY] VERIFYING DATABASE TABLES")
    print("="*60)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    required_tables = ['currencies', 'exchange_rates']
    
    for table in required_tables:
        if table in tables:
            print(f"[OK] Table '{table}' exists")
        else:
            print(f"[ERROR] Table '{table}' NOT FOUND")
            return False
    
    return True


def verify_columns():
    """Verify that new columns were added to existing tables"""
    print("\n" + "="*60)
    print("[VERIFY] VERIFYING NEW COLUMNS")
    print("="*60)
    
    inspector = inspect(engine)
    
    # Check Product table
    product_columns = [col['name'] for col in inspector.get_columns('products')]
    if 'default_rate_id' in product_columns:
        print("[OK] Product.default_rate_id exists")
    else:
        print("[ERROR] Product.default_rate_id NOT FOUND")
    
    # Check PriceRule table
    price_rule_columns = [col['name'] for col in inspector.get_columns('price_rules')]
    if 'exchange_rate_id' in price_rule_columns:
        print("[OK] PriceRule.exchange_rate_id exists")
    else:
        print("[ERROR] PriceRule.exchange_rate_id NOT FOUND")
    
    # Check SaleDetail table
    sale_detail_columns = [col['name'] for col in inspector.get_columns('sale_details')]
    if 'exchange_rate_name' in sale_detail_columns and 'exchange_rate_value' in sale_detail_columns:
        print("[OK] SaleDetail audit fields exist")
    else:
        print("[ERROR] SaleDetail audit fields NOT FOUND")


def verify_data():
    """Verify that initial data was populated"""
    print("\n" + "="*60)
    print("[VERIFY] VERIFYING INITIAL DATA")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Check currencies
        currencies = db.query(Currency).all()
        print(f"\n[DATA] Found {len(currencies)} currencies:")
        for curr in currencies:
            print(f"   - {curr.code}: {curr.name} ({curr.symbol})")
        
        # Check exchange rates
        rates = db.query(ExchangeRate).all()
        print(f"\n[DATA] Found {len(rates)} exchange rates:")
        for rate in rates:
            print(f"   - {rate.name}: {rate.rate} {rate.currency_code} (Active: {rate.is_active})")
        
        return len(currencies) > 0 and len(rates) > 0
    finally:
        db.close()


def test_relationships():
    """Test that relationships work correctly"""
    print("\n" + "="*60)
    print("[VERIFY] TESTING RELATIONSHIPS")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Test Currency -> ExchangeRate relationship
        usd = db.query(Currency).filter(Currency.code == "USD").first()
        ves = db.query(Currency).filter(Currency.code == "VES").first()
        
        if ves:
            print(f"\n[OK] Currency VES found: {ves.name}")
            print(f"   Exchange rates for VES: {len(ves.exchange_rates)}")
            for rate in ves.exchange_rates:
                print(f"   - {rate.name}: {rate.rate}")
        
        # Test ExchangeRate -> Currency relationship
        bcv_rate = db.query(ExchangeRate).filter(ExchangeRate.name == "Tasa BCV").first()
        if bcv_rate:
            print(f"\n[OK] BCV Rate found: {bcv_rate.rate}")
            print(f"   Currency: {bcv_rate.currency.name} ({bcv_rate.currency.symbol})")
        
        return True
    except Exception as e:
        print(f"[ERROR] Error testing relationships: {e}")
        return False
    finally:
        db.close()


def main():
    print("\n" + "="*70)
    print("[VERIFY] MULTI-CURRENCY SYSTEM VERIFICATION")
    print("="*70)
    
    # Run all verifications
    tables_ok = verify_tables()
    verify_columns()
    data_ok = verify_data()
    relationships_ok = test_relationships()
    
    # Final summary
    print("\n" + "="*70)
    print("[SUMMARY] VERIFICATION SUMMARY")
    print("="*70)
    
    if tables_ok and data_ok and relationships_ok:
        print("[OK] All verifications passed!")
        print("[OK] Multi-currency system is working correctly")
    else:
        print("[ERROR] Some verifications failed")
        print("[WARNING] Please check the errors above")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
