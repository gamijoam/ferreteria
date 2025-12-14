from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database.db import get_db
from ..models import models
from .. import schemas
import hashlib

router = APIRouter(prefix="/auth", tags=["auth"])

def verify_password(plain_password, hashed_password):
    # Simple SHA256 for MVP. Migrate to bcrypt in production.
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/login", response_model=schemas.UserRead)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == credentials.username).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
        
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Usuario inactivo")
        
    return user

def init_admin_user(db: Session):
    """Check if any user exists, if not create admin"""
    if db.query(models.User).count() == 0:
        print("Creating default admin user...")
        admin = models.User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            role=models.UserRole.ADMIN,
            full_name="Administrador Sistema",
            is_active=True
        )
        db.add(admin)
        db.commit()
