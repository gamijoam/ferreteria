class SessionExpiredError(Exception):
    pass

class SessionManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance._token = None
            cls._instance._user_data = {}
        return cls._instance
    
    def save_token(self, token: str):
        self._token = token
        
    def get_token(self) -> str:
        return self._token
    
    def clear_session(self):
        self._token = None
        self._user_data = {}
        
    def set_user_data(self, data: dict):
        self._user_data = data
        
    def get_user_data(self) -> dict:
        return self._user_data

    @property
    def is_authenticated(self) -> bool:
        return self._token is not None
