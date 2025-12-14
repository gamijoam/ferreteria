from frontend_caja.services.api_client import APIClient

class CustomerService:
    def __init__(self):
        self.client = APIClient()
        self.endpoint = "/api/v1/customers"

    def get_all_customers(self, query=None):
        try:
            params = {}
            if query:
                params['q'] = query
            return self.client.get(f"{self.endpoint}/", params=params)
        except Exception as e:
            print(f"Error fetching customers: {e}")
            return []

    def create_customer(self, customer_data):
        try:
            return self.client.post(f"{self.endpoint}/", customer_data)
        except Exception as e:
            print(f"Error creating customer: {e}")
            return None

    def update_customer(self, customer_id, customer_data):
        try:
            return self.client.put(f"{self.endpoint}/{customer_id}", customer_data)
        except Exception as e:
            print(f"Error updating customer: {e}")
            return None

    def get_customer_debt(self, customer_id):
        try:
            data = self.client.get(f"{self.endpoint}/{customer_id}/debt")
            return data.get("debt", 0.0) if data else 0.0
        except Exception as e:
            print(f"Error fetching debt: {e}")
            return 0.0

    def record_payment(self, customer_id, amount, description, payment_method):
        payload = {
            "amount": amount,
            "description": description,
            "payment_method": payment_method
        }
        try:
            return self.client.post(f"{self.endpoint}/{customer_id}/payments", payload)
        except Exception as e:
            print(f"Error recording payment: {e}")
            return None
