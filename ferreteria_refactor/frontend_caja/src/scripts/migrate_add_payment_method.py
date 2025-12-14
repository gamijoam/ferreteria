import sys
import os

# Add project root to path (2 levels up from this script)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.database.db import SessionLocal, engine
from sqlalchemy import text

def migrate():
    print("Iniciando migración: Agregar columna payment_method a tabla payments...")
    
    with engine.connect() as connection:
        try:
            # Check if column exists (PostgreSQL)
            query = text("SELECT column_name FROM information_schema.columns WHERE table_name='payments' AND column_name='payment_method'")
            result = connection.execute(query).fetchone()
            
            if not result:
                print("Agregando columna payment_method...")
                connection.execute(text("ALTER TABLE payments ADD COLUMN payment_method VARCHAR DEFAULT 'Efectivo'"))
                connection.commit()
                print("Columna agregada exitosamente.")
            else:
                print("La columna payment_method ya existe.")
                
        except Exception as e:
            print(f"Error durante la migración: {e}")

if __name__ == "__main__":
    migrate()
