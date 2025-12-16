"""
Migration script to add multi-currency support columns to existing tables.
This script adds the new foreign key columns to Product, PriceRule, and SaleDetail tables.

Run this script ONCE after updating the models.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from ferreteria_refactor.backend_api.database.db import engine, SessionLocal


def run_migration():
    """Execute migration SQL statements"""
    
    print("\n" + "="*70)
    print("[MIGRATION] ADDING MULTI-CURRENCY COLUMNS")
    print("="*70)
    
    db = SessionLocal()
    
    try:
        # Migration SQL statements
        migrations = [
            # Add default_rate_id to products table
            {
                "name": "Add Product.default_rate_id",
                "sql": """
                    ALTER TABLE products 
                    ADD COLUMN IF NOT EXISTS default_rate_id INTEGER 
                    REFERENCES exchange_rates(id);
                """
            },
            # Add exchange_rate_id to price_rules table
            {
                "name": "Add PriceRule.exchange_rate_id",
                "sql": """
                    ALTER TABLE price_rules 
                    ADD COLUMN IF NOT EXISTS exchange_rate_id INTEGER 
                    REFERENCES exchange_rates(id);
                """
            },
            # Add exchange_rate_name to sale_details table
            {
                "name": "Add SaleDetail.exchange_rate_name",
                "sql": """
                    ALTER TABLE sale_details 
                    ADD COLUMN IF NOT EXISTS exchange_rate_name VARCHAR;
                """
            },
            # Add exchange_rate_value to sale_details table
            {
                "name": "Add SaleDetail.exchange_rate_value",
                "sql": """
                    ALTER TABLE sale_details 
                    ADD COLUMN IF NOT EXISTS exchange_rate_value FLOAT;
                """
            },
        ]
        
        # Execute each migration
        for migration in migrations:
            print(f"\n[MIGRATE] {migration['name']}...")
            try:
                db.execute(text(migration['sql']))
                db.commit()
                print(f"[OK] {migration['name']} completed")
            except Exception as e:
                print(f"[WARNING] {migration['name']} - {str(e)}")
                db.rollback()
        
        print("\n" + "="*70)
        print("[OK] Migration completed successfully!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def initialize_data():
    """Initialize currencies and exchange rates"""
    print("\n" + "="*70)
    print("[INIT] INITIALIZING CURRENCY DATA")
    print("="*70)
    
    from ferreteria_refactor.backend_api.database.init_currencies import init_currency_system
    
    db = SessionLocal()
    try:
        init_currency_system(db)
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("[START] MULTI-CURRENCY MIGRATION SCRIPT")
    print("="*70)
    
    # Step 1: Run migrations
    run_migration()
    
    # Step 2: Initialize data
    initialize_data()
    
    print("\n" + "="*70)
    print("[COMPLETE] Migration and initialization finished!")
    print("[NEXT] Run verify_currency_system.py to verify the changes")
    print("="*70 + "\n")
