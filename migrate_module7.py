from sqlalchemy import text
from src.database.db import engine

def migrate_sales_table():
    print("Actualizando tabla 'sales' para Módulo 7 (Clientes y Crédito)...")
    with engine.connect() as connection:
        connection = connection.execution_options(isolation_level="AUTOCOMMIT")
        
        try:
            # Add customer_id column
            connection.execute(text(
                "ALTER TABLE sales ADD COLUMN IF NOT EXISTS customer_id INTEGER REFERENCES customers(id)"
            ))
            print("✅ Columna 'customer_id' agregada.")
        except Exception as e:
            print(f"⚠️ customer_id: {e}")
        
        try:
            # Add is_credit column
            connection.execute(text(
                "ALTER TABLE sales ADD COLUMN IF NOT EXISTS is_credit BOOLEAN DEFAULT FALSE"
            ))
            print("✅ Columna 'is_credit' agregada.")
        except Exception as e:
            print(f"⚠️ is_credit: {e}")
        
        try:
            # Add paid column
            connection.execute(text(
                "ALTER TABLE sales ADD COLUMN IF NOT EXISTS paid BOOLEAN DEFAULT TRUE"
            ))
            print("✅ Columna 'paid' agregada.")
        except Exception as e:
            print(f"⚠️ paid: {e}")
    
    print("✅ Migración completada. Ahora puedes ejecutar 'python run.py'.")

if __name__ == "__main__":
    migrate_sales_table()
