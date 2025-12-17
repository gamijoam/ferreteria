from frontend_caja.services.config_service import ConfigService

class ConfigController:
    def __init__(self, db=None):
        self.service = ConfigService()
        self.db = None  # Ignored
        self._cache = {} # Simple in-memory cache

    def get_business_info(self):
        """Get business info (name, address, phone)"""
        # Try to get from API, fallback to defaults
        try:
            configs = self.service.get_all_configs_dict()
            self._cache.update(configs)
            
            return {
                "name": configs.get("business_name", "Ferreteria Refactor"),
                "address": configs.get("business_address", "Calle Falsa 123"),
                "phone": configs.get("business_phone", "555-5555"),
                "rif": configs.get("business_rif", "J-12345678-9")
            }
        except:
            return {
                "name": "Ferreteria Refactor",
                "address": "Calle Falsa 123",
                "phone": "555-5555",
                "rif": "J-12345678-9"
            }

    def get_exchange_rate(self):
        """Get current exchange rate"""
        return self.service.get_exchange_rate()

    def set_exchange_rate(self, rate):
        """Set exchange rate"""
        return self.service.set_config("exchange_rate", str(rate))

    def get_config(self, key, default=None):
        """Get specific config with local caching"""
        if key in self._cache:
            return self._cache[key]
            
        result = self.service.get_config(key)
        if result:
            val = result.get('value')
            self._cache[key] = val
            return val
        return default

    def set_config(self, key, value):
        """Set config value and update cache"""
        result = self.service.set_config(key, value)
        if result:
            self._cache[key] = str(value)
            return True
        return False

    def update_business_info(self, info_dict):
        """Update multiple business info fields"""
        # user keys: name, address, phone, rif
        # mapping to config keys: business_name, business_address...
        
        configs = {}
        if 'name' in info_dict:
            configs['business_name'] = info_dict['name']
        if 'address' in info_dict:
            configs['business_address'] = info_dict['address']
        if 'phone' in info_dict:
            configs['business_phone'] = info_dict['phone']
        if 'rif' in info_dict:
            configs['business_rif'] = info_dict['rif']
            
        return self.service.set_configs_batch(configs)

    def get_currencies(self):
        """Get all currencies from the system"""
        try:
            currencies = self.service.get_currencies()
            # Convert dict response to objects with attributes
            if isinstance(currencies, list):
                return [type('Currency', (), c) for c in currencies]
            return []
        except Exception as e:
            print(f"Error getting currencies: {e}")
            # Return default currencies as fallback
            return [
                type('Currency', (), {
                    'symbol': 'USD',
                    'name': 'Dólar',
                    'is_active': True,
                    'rate': 1.0
                }),
                type('Currency', (), {
                    'symbol': 'Bs',
                    'name': 'Bolívar',
                    'is_active': True,
                    'rate': 50.0
                })
            ]

    def get_exchange_rate(self, currency_code=None):
        """Get exchange rate for a specific currency or default VES rate"""
        if currency_code and currency_code != "USD":
            try:
                currencies = self.get_currencies()
                for c in currencies:
                    if c.symbol == currency_code:
                        return c.rate
            except:
                pass
        
        # Fallback to old method for VES/Bs
        return self.service.get_exchange_rate()
