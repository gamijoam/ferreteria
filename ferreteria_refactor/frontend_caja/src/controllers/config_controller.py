class ConfigController:
    def __init__(self, db=None):
        pass

    def get_business_info(self):
        return {
            "name": "Ferreteria Refactor",
            "address": "Calle Falsa 123",
            "phone": "555-5555"
        }

    def get_exchange_rate(self):
        return 50.0

    def get_config(self, key, default=None):
        # Mock specific configs if needed
        if key == "business_logo_path":
            return ""
        return default
