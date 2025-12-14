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
    print("Iniciando migración: Agregar ADJUSTMENT a MovementType enum...")
    
    with engine.connect() as connection:
        try:
            # Check if ADJUSTMENT already exists in the enum
            query = text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_enum 
                    WHERE enumlabel = 'ADJUSTMENT' 
                    AND enumtypid = (
                        SELECT oid FROM pg_type WHERE typname = 'movementtype'
                    )
                )
            """)
            result = connection.execute(query).fetchone()
            
            if not result[0]:
                print("Agregando ADJUSTMENT al enum movementtype...")
                connection.execute(text("ALTER TYPE movementtype ADD VALUE 'ADJUSTMENT'"))
                connection.commit()
                print("Valor agregado exitosamente.")
            else:
                print("El valor ADJUSTMENT ya existe en el enum.")
                
        except Exception as e:
            print(f"Error durante la migración: {e}")
            print("Nota: Si el enum no existe, se creará automáticamente al reiniciar la aplicación.")

if __name__ == "__main__":
    migrate()
