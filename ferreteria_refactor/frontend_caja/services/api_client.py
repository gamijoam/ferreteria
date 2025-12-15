import requests
from requests.exceptions import RequestException
from frontend_caja.config import API_BASE_URL
from src.services.session_manager import SessionManager, SessionExpiredError

class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL.rstrip('/') # Ensure base has no trailing slash
        self._session_manager = SessionManager()

    def _get_headers(self):
        headers = {"Content-Type": "application/json"}
        token = self._session_manager.get_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _handle_response(self, response):
        if response.status_code == 401:
            print("⚠️ API Returned 401 Unauthorized")
            self._session_manager.clear_session()
            raise SessionExpiredError("La sesión ha expirado")
        
        try:
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            print(f"API Error: {response.status_code} {e}")
            return None

    def _make_url(self, endpoint):
        # formatted_endpoint = endpoint.lstrip('/')
        # return f"{self.base_url}/{formatted_endpoint}"
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def post(self, endpoint, data):
        url = self._make_url(endpoint)
        headers = self._get_headers()
        # print(f"📡 POST {url}")
        # print(f"📦 BODY: {data}")
        try:
            response = requests.post(url, json=data, headers=headers)
            return self._handle_response(response)
        except SessionExpiredError:
            raise
        except RequestException as e:
            print(f"Connection Error: {e}")
            return None

    def get(self, endpoint, params=None, silent_404=False):
        url = self._make_url(endpoint)
        headers = self._get_headers()
        try:
            response = requests.get(url, params=params, headers=headers)
            if silent_404 and response.status_code == 404:
                return None
            return self._handle_response(response)
        except SessionExpiredError:
            raise
        except RequestException as e:
            print(f"Connection Error: {e}")
            return None

    def put(self, endpoint, data):
        url = self._make_url(endpoint)
        headers = self._get_headers()
        try:
            response = requests.put(url, json=data, headers=headers)
            return self._handle_response(response)
        except SessionExpiredError:
            raise
        except RequestException as e:
            print(f"Connection Error: {e}")
            return None
            
    def delete(self, endpoint):
        url = self._make_url(endpoint)
        headers = self._get_headers()
        try:
            response = requests.delete(url, headers=headers)
            return self._handle_response(response)
        except SessionExpiredError:
            raise
        except RequestException as e:
            print(f"Connection Error: {e}")
            return None
