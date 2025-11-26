from sqlalchemy.orm import Session
from src.models.models import User, UserRole
import hashlib

class AuthController:
    def __init__(self, db: Session):
        self.db = db

    def _hash_password(self, password: str) -> str:
        # Simple SHA256 for local app. In production use bcrypt.
        return hashlib.sha256(password.encode()).hexdigest()

    def init_admin(self):
        """Creates default admin if no users exist"""
        if self.db.query(User).count() == 0:
            admin = User(
                username="admin",
                password_hash=self._hash_password("admin123"),
                role=UserRole.ADMIN
            )
            self.db.add(admin)
            self.db.commit()
            return True
        return False

    def login(self, username, password):
        user = self.db.query(User).filter(User.username == username).first()
        if not user or not user.is_active:
            return None
        
        if user.password_hash == self._hash_password(password):
            return user
        return None

    def create_user(self, username, password, role: UserRole):
        if self.db.query(User).filter(User.username == username).first():
            raise ValueError("Usuario ya existe")
            
        new_user = User(
            username=username,
            password_hash=self._hash_password(password),
            role=role
        )
        self.db.add(new_user)
        self.db.commit()
        return new_user
