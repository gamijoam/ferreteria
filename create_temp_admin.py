import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ferreteria_refactor.backend_api.database.db import SessionLocal
from ferreteria_refactor.backend_api.models import models
from ferreteria_refactor.backend_api.security import get_password_hash

def create_temp_admin():
    db = SessionLocal()
    try:
        username = "temp_admin"
        password = "temp123"
        
        # Check if exists
        existing = db.query(models.User).filter(models.User.username == username).first()
        if existing:
            print(f"User {username} already exists. Updating password...")
            existing.password_hash = get_password_hash(password)
            existing.is_active = True
            existing.role = models.UserRole.ADMIN
        else:
            print(f"Creating user {username}...")
            user = models.User(
                username=username,
                password_hash=get_password_hash(password),
                role=models.UserRole.ADMIN, # Assuming Enum or string
                full_name="Temp Admin",
                is_active=True
            )
            db.add(user)
        
        db.commit()
        print(f"User {username} / {password} ready.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_temp_admin()
