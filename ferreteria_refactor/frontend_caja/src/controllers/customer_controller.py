from frontend_caja.services.customer_service import CustomerService
from src.utils.event_bus import event_bus

class CustomerObj:
    """Helper to wrap dict response as object for UI compatibility"""
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.id_number = data.get('id_number')
        self.phone = data.get('phone')
        self.address = data.get('address')
        self.email = data.get('email')
        self.credit_limit = data.get('credit_limit', 0.0)

class CustomerController:
    def __init__(self, db=None):
        self.service = CustomerService()
        self.cached_customers = []

    def get_all_customers(self):
        """Fetch from API and return as objects"""
        data_list = self.service.get_all_customers()
        self.cached_customers = [CustomerObj(d) for d in data_list]
        return self.cached_customers

    def search_customers(self, query: str):
        if not query:
            return self.get_all_customers()
        
        # Search via API
        data_list = self.service.get_all_customers(query=query)
        return [CustomerObj(d) for d in data_list]

    def create_customer(self, name: str, id_number: str = None, phone: str = "", address: str = ""):
        payload = {
            "name": name,
            "id_number": id_number,
            "phone": phone,
            "address": address
        }
        result = self.service.create_customer(payload)
        if result:
            event_bus.customers_updated.emit()
            return CustomerObj(result)
        else:
             raise Exception("Error creating customer in backend")

    def update_customer(self, customer_id, **kwargs):
        # Filter valid fields from kwargs
        valid_fields = ["name", "id_number", "phone", "address", "email"]
        payload = {k: v for k, v in kwargs.items() if k in valid_fields}
        
        result = self.service.update_customer(customer_id, payload)
        if result:
            event_bus.customers_updated.emit()
            return CustomerObj(result)
        else:
             raise Exception("Error updating customer")

    # MOCK METHODS FOR NOW - Payment/Debt Logic requires API support not yet implemented
    def get_customer_debt(self, customer_id: int):
        return self.service.get_customer_debt(customer_id)

    def record_payment(self, customer_id: int, amount: float, description: str = "", payment_method: str = "Efectivo"):
        result = self.service.record_payment(customer_id, amount, description, payment_method)
        if result:
            # event_bus.sales_updated.emit() # Notify system if needed
            return True
        return False

    def add_payment(self, *args, **kwargs):
        return self.record_payment(*args, **kwargs)

    def delete_customer(self, customer_id):
        # Not implemented in API yet
        print("Delete not supported in API yet")
        return False
