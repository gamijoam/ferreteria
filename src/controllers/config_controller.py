from sqlalchemy.orm import Session
from src.models.models import BusinessConfig

class ConfigController:
    def __init__(self, db: Session):
        self.db = db

    def get_config(self, key: str, default: str = "") -> str:
        """Get a configuration value by key"""
        config = self.db.query(BusinessConfig).filter(BusinessConfig.key == key).first()
        if config:
            return config.value
        return default

    def set_config(self, key: str, value: str):
        """Set a configuration value"""
        config = self.db.query(BusinessConfig).filter(BusinessConfig.key == key).first()
        if config:
            config.value = value
        else:
            config = BusinessConfig(key=key, value=value)
            self.db.add(config)
        self.db.commit()
        self.db.refresh(config)

    def get_business_info(self) -> dict:
        """Get all business info as a dictionary"""
        return {
            "name": self.get_config("BUSINESS_NAME", "Sistema de Ferretería"),
            "rif": self.get_config("BUSINESS_RIF", ""),
            "address": self.get_config("BUSINESS_ADDRESS", ""),
            "phone": self.get_config("BUSINESS_PHONE", "")
        }

    def update_business_info(self, name: str, rif: str, address: str, phone: str):
        """Update all business info"""
        self.set_config("BUSINESS_NAME", name)
        self.set_config("BUSINESS_RIF", rif)
        self.set_config("BUSINESS_ADDRESS", address)
        self.set_config("BUSINESS_PHONE", phone)
