import sys
import os

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.database.db import SessionLocal, engine
from sqlalchemy import text

def migrate():
    print("Iniciando migración: Agregar campo PIN a users...")
    
    with engine.connect() as connection:
        try:
            # Check if column exists (PostgreSQL)
            query = text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='pin'")
            result = connection.execute(query).fetchone()
            
            if not result:
                print("Agregando columna pin...")
                connection.execute(text("ALTER TABLE users ADD COLUMN pin VARCHAR"))
                connection.commit()
                print("Columna agregada exitosamente.")
            else:
                print("La columna pin ya existe.")
                
        except Exception as e:
            print(f"Error durante la migración: {e}")

if __name__ == "__main__":
    migrate()
