from frontend_caja.services.api_client import APIClient

class ConfigService:
    def __init__(self):
        self.client = APIClient()
        self.endpoint = "/api/v1/config"

    def get_all_configs(self):
        """Get all configurations as a list"""
        try:
            return self.client.get(f"{self.endpoint}/")
        except Exception as e:
            print(f"Error fetching configs: {e}")
            return []

    def get_all_configs_dict(self):
        """Get all configurations as a dictionary"""
        try:
            return self.client.get(f"{self.endpoint}/dict")
        except Exception as e:
            print(f"Error fetching config dict: {e}")
            return {}

    def get_config(self, key):
        """Get specific configuration key"""
        try:
            return self.client.get(f"{self.endpoint}/{key}")
        except Exception as e:
            # Silence 404s
            return None

    def set_config(self, key, value):
        """Set configuration value"""
        try:
            data = {"key": key, "value": str(value)}
            return self.client.put(f"{self.endpoint}/{key}", data)
        except Exception as e:
            print(f"Error setting config: {e}")
            return None

    def set_configs_batch(self, configs):
        """Set multiple configurations"""
        try:
            return self.client.post(f"{self.endpoint}/batch", configs)
        except Exception as e:
            print(f"Error setting batch configs: {e}")
            return None

    def get_exchange_rate(self):
        """Get current exchange rate"""
        try:
            data = self.client.get(f"{self.endpoint}/exchange-rate/current")
            return data.get("rate", 1.0)
        except Exception as e:
            print(f"Error fetching exchange rate: {e}")
            return 1.0

    def get_currencies(self):
        """Get all active currencies"""
        try:
            return self.client.get(f"{self.endpoint}/currencies")
        except Exception as e:
            print(f"Error fetching currencies: {e}")
            return []
