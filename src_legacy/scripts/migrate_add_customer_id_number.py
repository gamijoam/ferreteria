"""
Migration script to add id_number column to customers table
Run this script to update existing databases
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text, inspect
from src.database.db import engine

def migrate():
    print("="*60)
    print("MIGRACION: Agregar campo 'id_number' a tabla customers")
    print("="*60)
    
    try:
        # Use Inspector to be DB-agnostic
        inspector = inspect(engine)
        columns = [c['name'] for c in inspector.get_columns('customers')]
        
        if 'id_number' in columns:
            print("OK: La columna 'id_number' ya existe. No se requiere migracion.")
            return
        
        # Add column
        print("Agregando columna 'id_number'...")
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE customers ADD COLUMN id_number VARCHAR(50)"))
            conn.commit()
        
        print("OK: Migracion completada exitosamente.")
        print("  - Columna 'id_number' agregada a 'customers'")
        
    except Exception as e:
        print(f"ERROR durante la migracion: {e}")
        raise

if __name__ == "__main__":
    migrate()
