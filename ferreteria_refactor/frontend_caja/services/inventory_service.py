from frontend_caja.services.api_client import APIClient

class InventoryService:
    def __init__(self):
        self.client = APIClient()
        self.endpoint = "/api/v1/inventory"

    def add_stock(self, payload):
        """
        Payload: {product_id, quantity, is_box_input, description}
        """
        try:
            return self.client.post(f"{self.endpoint}/add", payload)
        except Exception as e:
            print(f"Error adding stock: {e}")
            return None

    def remove_stock(self, payload):
        """
        Payload: {product_id, quantity, description}
        """
        try:
            return self.client.post(f"{self.endpoint}/remove", payload)
        except Exception as e:
            print(f"Error removing stock: {e}")
            return None

    def get_kardex(self, product_id=None):
        try:
            params = {}
            if product_id:
                params['product_id'] = product_id
            return self.client.get(f"{self.endpoint}/kardex", params=params)
        except Exception as e:
            print(f"Error fetching kardex: {e}")
            return []
