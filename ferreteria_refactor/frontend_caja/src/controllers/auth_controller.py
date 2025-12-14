from frontend_caja.services.api_client import APIClient
from src.models.models import UserRole

class UserObj:
    """Wrapper for user dictionary to allow attribute access"""
    def __init__(self, data):
        self.id = data.get('id')
        self.username = data.get('username')
        
        role_str = data.get('role')
        # Map string to Enum if possible
        try:
            self.role = UserRole(role_str)
        except:
            self.role = role_str # Fallback
            
        self.full_name = data.get('full_name')
        self.is_active = data.get('is_active', True)

class AuthController:
    def __init__(self, db=None):
        self.client = APIClient()

    def login(self, username, password):
        try:
            data = {"username": username, "password": password}
            # The API returns the UserRead schema dict directly
            user_data = self.client.post("/api/v1/auth/login", data)
            
            if user_data and 'id' in user_data:
                return UserObj(user_data)
            return None
        except Exception as e:
            print(f"Login Error: {e}")
            # Reraise or return None depending on UI logic
            # If APIClient raises error for 401, we want UI to know
            raise e
