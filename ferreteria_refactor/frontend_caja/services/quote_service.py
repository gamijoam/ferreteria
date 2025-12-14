from frontend_caja.services.api_client import APIClient

class QuoteService:
    def __init__(self):
        self.client = APIClient()
        self.endpoint = "/api/v1/quotes"

    def create_quote(self, quote_data: dict):
        """
        Send quote data to backend.
        quote_data matches schemas.QuoteCreate structure.
        """
        try:
            return self.client.post(f"{self.endpoint}/", quote_data)
        except Exception as e:
            print(f"Error creating quote: {e}")
            return None

    def get_all_quotes(self):
        """Fetch all quotes"""
        try:
            return self.client.get(f"{self.endpoint}/")
        except Exception as e:
            print(f"Error fetching quotes: {e}")
            return []

    def get_quote_details(self, quote_id):
        try:
            return self.client.get(f"{self.endpoint}/{quote_id}")
        except Exception as e:
            print(f"Error fetching quote details: {e}")
            return None

    def get_quote_details(self, quote_id):
        try:
            return self.client.get(f"{self.endpoint}/{quote_id}")
        except Exception as e:
            print(f"Error fetching quote details: {e}")
            return None

    def mark_quote_converted(self, quote_id):
        try:
            return self.client.put(f"{self.endpoint}/{quote_id}/convert", {})
        except Exception as e:
            print(f"Error converting quote: {e}")
            return None
