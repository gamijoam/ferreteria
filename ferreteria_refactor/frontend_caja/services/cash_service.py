from frontend_caja.services.api_client import APIClient

class CashService:
    def __init__(self):
        self.client = APIClient()
        self.endpoint = "/api/v1/cash"

    def open_session(self, user_id, initial_usd, initial_bs):
        data = {
            "user_id": user_id,
            "initial_cash": initial_usd,
            "initial_cash_bs": initial_bs
        }
        try:
            return self.client.post(f"{self.endpoint}/open", data)
        except Exception as e:
            print(f"Error opening session: {e}")
            return None

    def get_active_session_global(self):
        try:
             # Calls the new backend endpoint that returns ANY open session
             result = self.client.get(f"{self.endpoint}/active", silent_404=True)
             if result:
                 print(f"✅ GLOBAL ACTIVE SESSION FOUND: {result}")
             else:
                 print(f"❌ GLOBAL ACTIVE SESSION NOT FOUND (Endpoint missing or no session)")
             return result
        except Exception as e:
            print(f"🚨 ERROR CHECKING ACTIVE SESSION: {e}")
            return None

    def get_current_session(self, user_id):
        try:
            return self.client.get(f"{self.endpoint}/current/{user_id}", silent_404=True)
        except Exception as e:
            # 404 is expected if no session
            return None

    def close_session(self, session_id, reported_usd, reported_bs):
        data = {
            "final_cash_reported": reported_usd,
            "final_cash_reported_bs": reported_bs
        }
        try:
            return self.client.post(f"{self.endpoint}/{session_id}/close", data)
        except Exception as e:
            print(f"Error closing session: {e}")
            return None

    def add_movement(self, amount, type_mov, reason, currency="USD", session_id=None):
        data = {
            "amount": amount,
            "type": type_mov,
            "description": reason,
            "currency": currency,
            "session_id": session_id
        }
        try:
            return self.client.post(f"{self.endpoint}/movements", data)
        except Exception as e:
            print(f"Error adding movement: {e}")
            return None

    def get_history(self, skip=0, limit=20):
        """Get list of closed sessions"""
        try:
            return self.client.get(f"{self.endpoint}/history", params={"skip": skip, "limit": limit})
        except Exception as e:
            print(f"Error fetching history: {e}")
            return []

    def get_session_details(self, session_id):
        """Get details of a specific session"""
        try:
            return self.client.get(f"{self.endpoint}/history/{session_id}")
        except Exception as e:
            print(f"Error fetching session details: {e}")
            return None

