from ..services.session_manager import SessionManager
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
        self.api_client = APIClient()
        self.session_manager = SessionManager()

    def login(self, username, password):
        try:
            # Prepare form data as expected by OAuth2PasswordRequestForm
            # which expects 'username' and 'password' in form-data, but APIClient uses JSON.
            # However, our backend /token expects a FORM, not JSON. But requests.post(data=...) sends form.
            # Let's adjust APIClient or force it here. 
            # Ideally, valid REST API /token uses x-www-form-urlencoded.
            
            # Since APIClient is designed for JSON (json=data), we might need to bypass it 
            # or extend it. For robustness and time, let's use direct requests here 
            # or update APIClient to support form data.
            # Let's try extending APIClient capability for form data later, 
            # for now, let's assume the backend can Handle it if we send it right or use requests directly for this special endpoint.
            
            import requests
            url = f"{self.api_client.base_url}/api/v1/token"
            response = requests.post(url, data={"username": username, "password": password})
            
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token")
                
                # Fetch User Data (Optional: decode token or fetch /users/me)
                # For this MVP, we decode simple parts or trust the valid login.
                self.session_manager.save_token(access_token)
                
                # We could set basic mock user data or fetch real profile.
                # Assuming role is in token, we'd need to decode it.
                # For now, let's fetch profile if we had an endpoint or set based on successful login.
                
                # Extract role from token claims
                role = "UNKNOWN"
                try:
                    from jose import jwt
                    claims = jwt.get_unverified_claims(access_token)
                    print(f"DEBUG TOKEN CLAIMS: {claims}")
                    role = claims.get("role", "UNKNOWN")
                except Exception as e:
                    print(f"Error decoding token: {e}")
                    role = f"Error: {str(e)}"

                return True, "Login Exitoso", {"username": username, "role": role}
            
            elif response.status_code == 401:
                return False, "Credenciales incorrectas", None
            else:
                 return False, f"Error del servidor: {response.status_code}", None

        except Exception as e:
            return False, f"Error de conexión: {str(e)}", None

    def logout(self):
        self.session_manager.clear_session()
