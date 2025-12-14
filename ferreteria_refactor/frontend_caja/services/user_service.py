from frontend_caja.services.api_client import APIClient

class UserService:
    def __init__(self):
        self.client = APIClient()
        self.endpoint = "/api/v1/users"

    def create_user(self, user_data):
        """Create a new user"""
        try:
            return self.client.post(f"{self.endpoint}/", user_data)
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def get_all_users(self):
        """Get all users"""
        try:
            return self.client.get(f"{self.endpoint}/")
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []

    def get_user(self, user_id):
        """Get user by ID"""
        try:
            return self.client.get(f"{self.endpoint}/{user_id}")
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None

    def update_user(self, user_id, user_data):
        """Update user"""
        try:
            return self.client.put(f"{self.endpoint}/{user_id}", user_data)
        except Exception as e:
            print(f"Error updating user: {e}")
            return None

    def delete_user(self, user_id):
        """Deactivate user"""
        try:
            return self.client.delete(f"{self.endpoint}/{user_id}")
        except Exception as e:
            print(f"Error deleting user: {e}")
            return None

    def login(self, username, password):
        """Authenticate user"""
        try:
            data = {"username": username, "password": password}
            return self.client.post(f"{self.endpoint}/login", data)
        except Exception as e:
            print(f"Error logging in: {e}")
            return None

    def verify_pin(self, user_id, pin):
        """Verify user PIN"""
        try:
            return self.client.post(f"{self.endpoint}/verify-pin/{user_id}", {"pin": pin})
        except Exception as e:
            print(f"Error verifying PIN: {e}")
            return None
