from frontend_caja.services.api_client import APIClient

class PurchaseService:
    def __init__(self):
        self.client = APIClient()
        self.endpoint = "/api/v1/purchases"

    def create_purchase_order(self, order_data):
        """
        Create a new purchase order
        order_data: {supplier_id, items: [{product_id, quantity, unit_cost}], expected_delivery, notes}
        """
        try:
            return self.client.post(f"{self.endpoint}/", order_data)
        except Exception as e:
            print(f"Error creating purchase order: {e}")
            return None

    def get_all_purchase_orders(self, status=None):
        """Get all purchase orders, optionally filtered by status"""
        try:
            params = {}
            if status:
                params['status'] = status
            return self.client.get(f"{self.endpoint}/", params=params)
        except Exception as e:
            print(f"Error fetching purchase orders: {e}")
            return []

    def get_purchase_order(self, order_id):
        """Get purchase order by ID"""
        try:
            return self.client.get(f"{self.endpoint}/{order_id}")
        except Exception as e:
            print(f"Error fetching purchase order: {e}")
            return None

    def receive_purchase_order(self, order_id, user_id=None):
        """Receive a purchase order (updates stock, cost, creates kardex)"""
        try:
            # If user_id is None, try to fetch from session
            if user_id is None:
                from src.services.session_manager import SessionManager
                session = SessionManager()
                user_data = session.get_user_data()
                user_id = user_data.get('id', 1) # Default to 1 (admin) if logic fails
                
            data = {"user_id": user_id}
            # Ensure it is an int
            if data["user_id"] is None:
                 data["user_id"] = 1
                 
            return self.client.post(f"{self.endpoint}/{order_id}/receive", data)
        except Exception as e:
            print(f"Error receiving purchase order: {e}")
            return None

    def cancel_purchase_order(self, order_id):
        """Cancel a purchase order"""
        try:
            return self.client.delete(f"{self.endpoint}/{order_id}")
        except Exception as e:
            print(f"Error cancelling purchase order: {e}")
            return None
