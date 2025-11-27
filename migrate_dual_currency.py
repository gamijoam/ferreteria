"""
Migration script for Dual Currency System
Adds exchange_rate support to BusinessConfig, Sale, and Payment tables
"""
from src.database.db import engine
import datetime

def migrate_dual_currency():
    """Add dual currency fields to database"""
    conn = engine.raw_connection()
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("MIGRACION: SISTEMA DUAL DE MONEDAS (USD/Bs)")
        print("=" * 60)
        
        # Sales table
        print("\nActualizando tabla 'sales'...")
        cursor.execute("""
            ALTER TABLE sales 
            ADD COLUMN IF NOT EXISTS currency VARCHAR DEFAULT 'USD'
        """)
        cursor.execute("""
            ALTER TABLE sales 
            ADD COLUMN IF NOT EXISTS exchange_rate_used FLOAT DEFAULT 1.0
        """)
        cursor.execute("""
            ALTER TABLE sales 
            ADD COLUMN IF NOT EXISTS total_amount_bs FLOAT
        """)
        print("Columnas agregadas a 'sales'")
        
        # Payments table
        print("\nActualizando tabla 'payments'...")
        cursor.execute("""
            ALTER TABLE payments 
            ADD COLUMN IF NOT EXISTS currency VARCHAR DEFAULT 'USD'
        """)
        cursor.execute("""
            ALTER TABLE payments 
            ADD COLUMN IF NOT EXISTS exchange_rate_used FLOAT DEFAULT 1.0
        """)
        cursor.execute("""
            ALTER TABLE payments 
            ADD COLUMN IF NOT EXISTS amount_bs FLOAT
        """)
        print("Columnas agregadas a 'payments'")
        
        # Initialize exchange rate in business_config
        print("\nInicializando tasa de cambio...")
        cursor.execute("""
            INSERT INTO business_config (key, value) 
            VALUES ('exchange_rate', '1.0')
            ON CONFLICT (key) DO NOTHING
        """)
        cursor.execute("""
            INSERT INTO business_config (key, value) 
            VALUES ('exchange_rate_updated_at', %s)
            ON CONFLICT (key) DO NOTHING
        """, (datetime.datetime.now().isoformat(),))
        print("Tasa de cambio inicializada")
        
        conn.commit()
        print("\n" + "=" * 60)
        print("MIGRACION COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("\nPuedes actualizar la tasa de cambio desde Configuracion")
        
    except Exception as e:
        conn.rollback()
        print(f"\nError en migracion: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate_dual_currency()
