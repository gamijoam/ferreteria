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

    def create_user(self, username, password, role: UserRole, pin=None):
        if self.db.query(User).filter(User.username == username).first():
            raise ValueError("Usuario ya existe")
            
        new_user = User(
            username=username,
            password_hash=self._hash_password(password),
            role=role,
            pin=pin
        )
        self.db.add(new_user)
        self.db.commit()
        return new_user

    def get_all_users(self):
        """Get all users"""
        return self.db.query(User).all()

    def get_user_by_id(self, user_id: int):
        """Get user by ID"""
        return self.db.query(User).get(user_id)

    def update_user(self, user_id: int, username: str = None, role: UserRole = None, is_active: bool = None, pin: str = None):
        """Update user details"""
        user = self.db.query(User).get(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        if username and username != user.username:
            # Check if new username already exists
            existing = self.db.query(User).filter(User.username == username, User.id != user_id).first()
            if existing:
                raise ValueError("El nombre de usuario ya existe")
            user.username = username
        
        if role is not None:
            user.role = role
        
        if is_active is not None:
            user.is_active = is_active
        
        if pin is not None:
            user.pin = pin
        
        self.db.commit()
        return user

    def change_password(self, user_id: int, new_password: str):
        """Change user password"""
        user = self.db.query(User).get(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        user.password_hash = self._hash_password(new_password)
        self.db.commit()
        return user

    def deactivate_user(self, user_id: int):
        """Deactivate user (soft delete)"""
        user = self.db.query(User).get(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        user.is_active = False
        self.db.commit()
        return user
