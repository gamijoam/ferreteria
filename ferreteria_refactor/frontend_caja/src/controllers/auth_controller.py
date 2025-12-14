class UserMock:
    def __init__(self):
        self.username = "admin_refactor"
        from src.models.models import UserRole
        self.role = UserRole.ADMIN

class AuthController:
    def __init__(self, db=None):
        pass

    def init_admin(self):
        return True
    
    def login(self, username, password):
        return UserMock()
