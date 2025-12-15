from frontend_caja.services.api_client import APIClient

class ProductService:
    def __init__(self):
        self.client = APIClient()

    def get_all_products(self):
        """Fetch all updated products from the backend."""
        # Mapping to match the frontend expected format if necessary
        # Backend returns list of dicts.
        return self.client.get("/api/v1/products/")

    def update_product(self, product_id, update_data: dict):
        """Update a product via API"""
        return self.client.put(f"/api/v1/products/{product_id}", update_data)

    def create_product(self, product_data: dict):
        """Create a new product via API"""
        return self.client.post("/api/v1/products/", product_data)

    def record_sale(self, sale_data: dict):
        """
        Send sale data to the backend to process inventory and recording.
        sale_data should match schemas.SaleCreate
        """
        return self.client.post("/api/v1/products/sales/", sale_data)

    def get_price_rules(self, product_id):
        """Get price rules for a product"""
        return self.client.get(f"/api/v1/products/{product_id}/rules")
        
    def add_price_rule(self, product_id, min_quantity: float, price: float):
        """Add a price rule"""
        data = {
            "product_id": product_id,
            "min_quantity": min_quantity,
            "price": price
        }
        return self.client.post(f"/api/v1/products/{product_id}/rules", data)
        
    def delete_price_rule(self, rule_id):
        """Delete a price rule"""
        return self.client.delete(f"/api/v1/products/rules/{rule_id}")

    def bulk_create_products(self, products_list: list):
        """Bulk import products via API"""
        return self.client.post("/api/v1/products/bulk", products_list)
