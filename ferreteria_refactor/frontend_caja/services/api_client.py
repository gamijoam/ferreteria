import requests
from frontend_caja.config import API_BASE_URL

class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()

    def get(self, endpoint: str, **kwargs):
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"API Error (GET {endpoint}): {e}")
            return None

    def post(self, endpoint: str, data: dict, **kwargs):
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, json=data, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
             # Basic error handling
            print(f"API Error (POST {endpoint}): {e}")
            if e.response:
                print(f"Response: {e.response.text}")
            return None
