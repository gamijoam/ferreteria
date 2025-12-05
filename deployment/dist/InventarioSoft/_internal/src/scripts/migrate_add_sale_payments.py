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
    print("Iniciando migración: Crear tabla sale_payments...")
    
    with engine.connect() as connection:
        try:
            # Check if table exists (PostgreSQL)
            query = text("SELECT table_name FROM information_schema.tables WHERE table_name='sale_payments'")
            result = connection.execute(query).fetchone()
            
            if not result:
                print("Creando tabla sale_payments...")
                connection.execute(text("""
                    CREATE TABLE sale_payments (
                        id SERIAL PRIMARY KEY,
                        sale_id INTEGER NOT NULL REFERENCES sales(id),
                        payment_method VARCHAR NOT NULL,
                        amount FLOAT NOT NULL,
                        currency VARCHAR DEFAULT 'Bs'
                    )
                """))
                connection.commit()
                print("Tabla creada exitosamente.")
            else:
                print("La tabla sale_payments ya existe.")
                
        except Exception as e:
            print(f"Error durante la migración: {e}")

if __name__ == "__main__":
    migrate()
