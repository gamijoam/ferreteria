from sqlalchemy import text
from src.database.db import engine

def fix_enum():
    print("Intentando actualizar el tipo ENUM en la base de datos...")
    with engine.connect() as connection:
        # We need autocommit to run ALTER TYPE
        connection = connection.execution_options(isolation_level="AUTOCOMMIT")
        try:
            # Attempt to add the value
            connection.execute(text("ALTER TYPE movementtype ADD VALUE 'RETURN'"))
            print("✅ ÉXITO: Se agregó 'RETURN' al tipo movementtype.")
        except Exception as e:
            error_msg = str(e)
            if "DuplicateObject" in error_msg or "already exists" in error_msg:
                print("ℹ️ El valor 'RETURN' ya existía. No se requieren cambios.")
            else:
                print(f"⚠️ Nota: {error_msg}")
                print("Si el error dice que ya existe, ignóralo.")

if __name__ == "__main__":
    fix_enum()
