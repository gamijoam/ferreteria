from frontend_caja.services.user_service import UserService

class UserController:
    def __init__(self, db=None):
        self.service = UserService()
        self.db = None  # Ignored

    def create_user(self, username, password, role="CASHIER", pin=None, full_name=None):
        """Create a new user"""
        user_data = {
            "username": username,
            "password": password,
            "role": role.value if hasattr(role, 'value') else role,
            "full_name": full_name
        }
        result = self.service.create_user(user_data)
        if result:
            return UserObj(result), None
        else:
            return None, "Error creating user"

    def get_all_users(self):
        """Get all users"""
        data = self.service.get_all_users()
        return [UserObj(user) for user in data] if data else []

    def get_user(self, user_id):
        """Get user by ID"""
        data = self.service.get_user(user_id)
        return UserObj(data) if data else None

    def update_user(self, user_id, **kwargs):
        """Update user"""
        # Convert role enum to string if present
        if 'role' in kwargs and hasattr(kwargs['role'], 'value'):
            kwargs['role'] = kwargs['role'].value
        
        result = self.service.update_user(user_id, kwargs)
        if result:
            return UserObj(result), None
        else:
            return None, "Error updating user"

    def change_password(self, user_id, new_password):
        """Change user password"""
        return self.update_user(user_id, password=new_password)

    def delete_user(self, user_id):
        """Deactivate user"""
        result = self.service.delete_user(user_id)
        if result:
            return True, "User deactivated successfully"
        else:
            return False, "Error deactivating user"

    def login(self, username, password):
        """Authenticate user"""
        result = self.service.login(username, password)
        if result and result.get('id'):
            return UserObj(result), None
        else:
            return None, result.get('detail', 'Login failed') if result else "Login failed"

    def verify_pin(self, user_id, pin):
        """Verify user PIN for authorization"""
        result = self.service.verify_pin(user_id, pin)
        if result and result.get('verified'):
            return True, result.get('role')
        else:
            return False, None

class UserObj:
    """Helper to wrap user dict for UI compatibility"""
    def __init__(self, data):
        self.id = data.get('id')
        self.username = data.get('username')
        self.role = data.get('role')
        self.full_name = data.get('full_name')
        self.is_active = data.get('is_active', True)
        self.created_at = data.get('created_at')
        self.pin = data.get('pin')  # Add pin field
