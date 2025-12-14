from frontend_caja.services.api_client import APIClient

class ReturnService:
    def __init__(self):
        self.client = APIClient()
        self.endpoint = "/api/v1/returns"

    def search_sales(self, query=None):
        """Search sales for returns"""
        try:
            params = {}
            if query:
                params['q'] = query
            return self.client.get(f"{self.endpoint}/sales/search", params=params)
        except Exception as e:
            print(f"Error searching sales: {e}")
            return []

    def get_sale_for_return(self, sale_id):
        """Get sale details for return processing"""
        try:
            return self.client.get(f"{self.endpoint}/sales/{sale_id}")
        except Exception as e:
            print(f"Error fetching sale: {e}")
            return None

    def process_return(self, return_data):
        """
        Process a return
        return_data: {sale_id, items: [{product_id, quantity}], reason, refund_currency, exchange_rate}
        """
        try:
            return self.client.post(f"{self.endpoint}/", return_data)
        except Exception as e:
            print(f"Error processing return: {e}")
            return None

    def get_returns(self, skip=0, limit=100):
        """Get list of returns"""
        try:
            params = {"skip": skip, "limit": limit}
            return self.client.get(f"{self.endpoint}/", params=params)
        except Exception as e:
            print(f"Error fetching returns: {e}")
            return []

    def get_return(self, return_id):
        """Get specific return details"""
        try:
            return self.client.get(f"{self.endpoint}/{return_id}")
        except Exception as e:
            print(f"Error fetching return: {e}")
            return None
