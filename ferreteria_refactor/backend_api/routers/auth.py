from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..models import models
from ..security import verify_password, create_access_token, get_password_hash
from ..config import settings

router = APIRouter(tags=["authentication"])

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user:
        # Generic error for security
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        if not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception:
        # If hash is invalid/unknown (e.g. from old system), treat as auth failure
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password (Security Update Required)",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}, # Role in claims
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

def init_admin_user(db: Session):
    """Check if any user exists, if not create admin. ALSO FIX ADMIN HASH IF BROKEN."""
    admin = db.query(models.User).filter(models.User.username == "admin").first()
    
    if not admin:
        print("Creating default admin user...")
        p_hash = get_password_hash("admin123")
        new_admin = models.User(
            username="admin",
            password_hash=p_hash,
            role=models.UserRole.ADMIN,
            full_name="Administrador Sistema",
            is_active=True
        )
        db.add(new_admin)
        db.commit()
    else:
        # Safety Check: Update admin password hash to ensure it's compatible with new bcrypt
        # This is useful during development/migration to fix "UnknownHashError"
        print("Updating admin user hash to ensure compatibility...")
        p_hash = get_password_hash("admin123")
        admin.password_hash = p_hash
        db.commit()
