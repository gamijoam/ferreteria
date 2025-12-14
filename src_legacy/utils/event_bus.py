from PyQt6.QtCore import QObject, pyqtSignal

class EventBus(QObject):
    """
    Global event bus for application-wide signals.
    """
    # Define signals
    products_updated = pyqtSignal()      # When products are created/edited/deleted
    inventory_updated = pyqtSignal()     # When stock changes (sales, purchases)
    customers_updated = pyqtSignal()     # When customers are added/edited
    sales_updated = pyqtSignal()         # When a sale is completed
    config_updated = pyqtSignal()        # When configuration changes

# Global instance
event_bus = EventBus()
