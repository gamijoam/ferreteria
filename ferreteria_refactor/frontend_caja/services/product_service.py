from frontend_caja.services.api_client import APIClient

class ProductService:
    def __init__(self):
        self.client = APIClient()

    def get_all_products(self):
        """Fetch all updated products from the backend."""
        # Mapping to match the frontend expected format if necessary
        # Backend returns list of dicts.
        return self.client.get("/api/v1/products/")

    def record_sale(self, sale_data: dict):
        """
        Send sale data to the backend to process inventory and recording.
        sale_data should match schemas.SaleCreate
        """
        return self.client.post("/api/v1/products/sales/", sale_data)
