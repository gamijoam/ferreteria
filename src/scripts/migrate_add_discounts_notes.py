"""
Migration Script: Add discount and notes fields
Run this script ONCE to update existing database schema
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from src.database.db import engine

def run_migration():
    print("Starting migration: Add discount and notes fields...")
    
    with engine.connect() as conn:
        try:
            # Add notes column to sales table
            print("Adding 'notes' column to 'sales' table...")
            conn.execute(text("""
                ALTER TABLE sales 
                ADD COLUMN IF NOT EXISTS notes TEXT;
            """))
            conn.commit()
            print("✓ 'notes' column added to 'sales'")
            
            # Add discount columns to sale_details table
            print("Adding 'discount' column to 'sale_details' table...")
            conn.execute(text("""
                ALTER TABLE sale_details 
                ADD COLUMN IF NOT EXISTS discount FLOAT DEFAULT 0.0;
            """))
            conn.commit()
            print("✓ 'discount' column added to 'sale_details'")
            
            print("Adding 'discount_type' column to 'sale_details' table...")
            conn.execute(text("""
                ALTER TABLE sale_details 
                ADD COLUMN IF NOT EXISTS discount_type VARCHAR DEFAULT 'NONE';
            """))
            conn.commit()
            print("✓ 'discount_type' column added to 'sale_details'")
            
            print("\n✅ Migration completed successfully!")
            print("You can now use discount and notes features in the POS.")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            print("\nPossible reasons:")
            print("1. Columns already exist (safe to ignore)")
            print("2. Database connection issue")
            print("3. Insufficient permissions")
            return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION SCRIPT")
    print("=" * 60)
    print("\nThis script will add the following columns:")
    print("  - sales.notes (TEXT)")
    print("  - sale_details.discount (FLOAT)")
    print("  - sale_details.discount_type (VARCHAR)")
    print("\n" + "=" * 60)
    
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y', 'si', 's']:
        success = run_migration()
        sys.exit(0 if success else 1)
    else:
        print("\nMigration cancelled.")
        sys.exit(0)
