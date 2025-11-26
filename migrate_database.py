"""
Migration script to update suppliers table structure
Adds new fields: contact_person, phone, email, address, notes, is_active, created_at
Removes old field: contact_info
"""
from src.database.db import engine
import psycopg2
from psycopg2 import sql

def migrate_suppliers_table():
    """Update suppliers table structure"""
    conn = engine.raw_connection()
    cursor = conn.cursor()
    
    try:
        print("Iniciando migración de tabla suppliers...")
        
        # Check if old column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='suppliers' AND column_name='contact_info'
        """)
        has_old_column = cursor.fetchone() is not None
        
        # Add new columns if they don't exist
        new_columns = [
            ("contact_person", "VARCHAR"),
            ("phone", "VARCHAR"),
            ("email", "VARCHAR"),
            ("address", "TEXT"),
            ("notes", "TEXT"),
            ("is_active", "BOOLEAN DEFAULT TRUE"),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        ]
        
        for col_name, col_type in new_columns:
            try:
                cursor.execute(f"""
                    ALTER TABLE suppliers 
                    ADD COLUMN IF NOT EXISTS {col_name} {col_type}
                """)
                print(f"✓ Columna '{col_name}' agregada")
            except Exception as e:
                print(f"  Columna '{col_name}' ya existe o error: {e}")
        
        # Migrate data from old column if it exists
        if has_old_column:
            cursor.execute("""
                UPDATE suppliers 
                SET contact_person = contact_info 
                WHERE contact_person IS NULL AND contact_info IS NOT NULL
            """)
            print("✓ Datos migrados de contact_info a contact_person")
            
            # Drop old column
            cursor.execute("ALTER TABLE suppliers DROP COLUMN IF EXISTS contact_info")
            print("✓ Columna antigua 'contact_info' eliminada")
        
        conn.commit()
        print("\n✅ Migración completada exitosamente!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error en migración: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def add_cost_price_to_products():
    """Add cost_price column to products table"""
    conn = engine.raw_connection()
    cursor = conn.cursor()
    
    try:
        print("\nAgregando cost_price a productos...")
        cursor.execute("""
            ALTER TABLE products 
            ADD COLUMN IF NOT EXISTS cost_price FLOAT DEFAULT 0.0
        """)
        conn.commit()
        print("✓ Columna 'cost_price' agregada a products")
    except Exception as e:
        conn.rollback()
        print(f"  cost_price ya existe o error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACIÓN DE BASE DE DATOS - MÓDULOS 14, 15, 16")
    print("=" * 60)
    
    migrate_suppliers_table()
    add_cost_price_to_products()
    
    print("\n" + "=" * 60)
    print("✅ TODAS LAS MIGRACIONES COMPLETADAS")
    print("=" * 60)
    print("\nAhora puedes ejecutar: python run.py")
