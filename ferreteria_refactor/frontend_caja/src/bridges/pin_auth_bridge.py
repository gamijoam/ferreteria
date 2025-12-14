"""
PIN Authentication Bridge for QML
Handles PIN-based authorization for sensitive operations
"""

from PySide6.QtCore import QObject, Signal, Slot, Property
from database.db import SessionLocal


class PINAuthBridge(QObject):
    """Bridge for PIN authentication in QML"""
    
    # Signals
    authSuccess = Signal(str, str)  # username, role
    authFailed = Signal(str)  # error message
    
    def __init__(self):
        super().__init__()
        self._last_authorized_user = None
        self._last_authorized_role = None
    
    @Slot(str, str, str, result=bool)
    def validatePIN(self, username, pin, action_description):
        """
        Validate PIN and authorize user
        Returns True if authorized, False otherwise
        Emits authSuccess or authFailed signals
        """
        # Import here to avoid circular dependencies and metadata conflicts
        from src.models.models import User
        
        if not username or not pin:
            self.authFailed.emit("Debe ingresar usuario y PIN")
            return False
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(
                User.username == username,
                User.is_active == True
            ).first()
            
            if not user:
                self.authFailed.emit("Usuario no encontrado o inactivo")
                return False
            
            # Check if user has authorization role
            if user.role.value not in ["ADMIN", "MANAGER"]:
                self.authFailed.emit("Este usuario no tiene permisos para autorizar esta acción")
                return False
            
            # Check PIN
            if not user.pin:
                self.authFailed.emit("Este usuario no tiene PIN configurado. Configure un PIN en Gestión de Usuarios")
                return False
            
            if user.pin != pin:
                self.authFailed.emit("PIN incorrecto")
                return False
            
            # Authorization successful
            self._last_authorized_user = user.username
            self._last_authorized_role = user.role.value
            self.authSuccess.emit(user.username, user.role.value)
            return True
            
        except Exception as e:
            self.authFailed.emit(f"Error al validar PIN: {str(e)}")
            return False
        finally:
            db.close()
    
    @Property(str)
    def lastAuthorizedUser(self):
        """Get last authorized user"""
        return self._last_authorized_user or ""
    
    @Property(str)
    def lastAuthorizedRole(self):
        """Get last authorized user's role"""
        return self._last_authorized_role or ""
