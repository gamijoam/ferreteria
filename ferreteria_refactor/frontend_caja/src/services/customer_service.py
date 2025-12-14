import requests
from ..config import API_BASE_URL

class CustomerService:
    def __init__(self):
        self.base_url = f"{API_BASE_URL}/customers"

    def get_all_customers(self, query=None):
        try:
            params = {}
            if query:
                params['q'] = query
                
            response = requests.get(f"{self.base_url}/", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching customers: {e}")
            return []

    def create_customer(self, customer_data):
        try:
            response = requests.post(f"{self.base_url}/", json=customer_data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error creating customer: {e}")
            if e.response:
                print(e.response.text)
            return None

    def update_customer(self, customer_id, customer_data):
        try:
            response = requests.put(f"{self.base_url}/{customer_id}", json=customer_data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error updating customer: {e}")
            return None
