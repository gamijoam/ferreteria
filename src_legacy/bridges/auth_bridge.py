"""
AuthBridge.py - Python-QML Bridge for Authentication
Exposes authentication functionality to QML layer
"""
from PySide6.QtCore import QObject, Signal, Slot, Property
from database.db import SessionLocal
from controllers.auth_controller import AuthController
from controllers.config_controller import ConfigController


class AuthBridge(QObject):
    """Bridge between QML and Python authentication logic"""
    
    # Signals to QML
    loginSuccess = Signal(str, str)  # username, role
    loginFailed = Signal(str)  # error message
    businessInfoLoaded = Signal(str, str)  # business_name, logo_path
    
    def __init__(self):
        super().__init__()
        self.db = SessionLocal()
        self.auth_controller = AuthController(self.db)
        self.config_controller = ConfigController(self.db)
        self.current_user = None
        self._business_name = ""
        self._logo_path = ""
        
        # Load business info on initialization
        self.load_business_info()
    
    @Slot()
    def load_business_info(self):
        """Load business configuration"""
        info = self.config_controller.get_business_info()
        self._business_name = info.get('name', 'POS Ultra')
        self._logo_path = self.config_controller.get_config("business_logo_path", "")
        self.businessInfoLoaded.emit(self._business_name, self._logo_path)
    
    @Slot(str, str)
    def login(self, username: str, password: str):
        """
        Attempt to login with provided credentials
        
        Args:
            username: User's username
            password: User's password
        """
        if not username or not password:
            self.loginFailed.emit("Por favor ingrese usuario y contraseña")
            return
        
        user = self.auth_controller.login(username.strip(), password)
        
        if user:
            self.current_user = user
            self.loginSuccess.emit(user.username, user.role.value)
        else:
            self.loginFailed.emit("Usuario o contraseña incorrectos")
    
    @Property(str, notify=businessInfoLoaded)
    def businessName(self):
        """Get business name"""
        return self._business_name
    
    @Property(str, notify=businessInfoLoaded)
    def logoPath(self):
        """Get logo path"""
        return self._logo_path
    
    def get_current_user(self):
        """Get the currently logged in user"""
        return self.current_user
    
    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'db'):
            self.db.close()
