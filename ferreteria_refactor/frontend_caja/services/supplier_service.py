from frontend_caja.services.api_client import APIClient

class SupplierService:
    def __init__(self):
        self.client = APIClient()
        self.endpoint = "/api/v1/suppliers"

    def get_all_suppliers(self, active_only=True):
        params = {"active_only": str(active_only).lower()}
        try:
            return self.client.get(f"{self.endpoint}/", params=params)
        except Exception as e:
            print(f"Error fetching suppliers: {e}")
            return []

    def create_supplier(self, supplier_data):
        try:
            return self.client.post(f"{self.endpoint}/", supplier_data)
        except Exception as e:
            print(f"Error creating supplier: {e}")
            return None

    def update_supplier(self, supplier_id, supplier_data):
        try:
            return self.client.put(f"{self.endpoint}/{supplier_id}", supplier_data)
        except Exception as e:
            print(f"Error updating supplier: {e}")
            return None

    def get_supplier(self, supplier_id):
        try:
            return self.client.get(f"{self.endpoint}/{supplier_id}")
        except Exception as e:
            print(f"Error fetching supplier: {e}")
            return None
