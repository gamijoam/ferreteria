"""
CustomerBridge.py - Python-QML Bridge for Customer Management
"""
from PySide6.QtCore import QObject, Signal, Slot, Property
from database.db import SessionLocal
from controllers.customer_controller import CustomerController

class CustomerBridge(QObject):
    """Bridge between QML and Python Customer logic"""
    
    # Signals
    customersUpdated = Signal()
    operationError = Signal(str)
    operationSuccess = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.db = SessionLocal()
        self.controller = CustomerController(self.db)
        
    @Slot(str, result=list)
    def searchCustomers(self, query: str = ""):
        """
        Search customers by name or ID number
        Return list of dicts
        """
        # We need to refresh session to get latest data
        self.db.expire_all()
        
        try:
            customers = self.controller.search_customers(query)
            results = []
            for c in customers:
                results.append({
                    "id": c.id,
                    "name": c.name,
                    "id_number": c.id_number or "",
                    "phone": c.phone or "",
                    "email": c.email or "",
                    "address": c.address or "",
                    "balance": float(c.balance) if hasattr(c, 'balance') else 0.0,
                    "credit_limit": float(c.credit_limit) if hasattr(c, 'credit_limit') else 0.0
                })
            return results
        except Exception as e:
            print(f"Error searching customers: {e}")
            self.operationError.emit(str(e))
            return []
            
    @Slot(str, str, str, str, str, float, result=bool)
    def createCustomer(self, name, id_number, phone, email, address, credit_limit):
        """Create a new customer"""
        try:
            # Basic validation
            if not name:
                self.operationError.emit("El nombre es obligatorio")
                return False
                
            success, msg, customer = self.controller.create_customer(
                name=name,
                id_number=id_number,
                phone=phone,
                email=email,
                address=address,
                credit_limit=credit_limit
            )
            
            if success:
                self.customersUpdated.emit()
                self.operationSuccess.emit("Cliente creado exitosamente")
                return True
            else:
                self.operationError.emit(msg)
                return False
        except Exception as e:
            self.operationError.emit(str(e))
            return False

    @Slot(int, str, str, str, str, str, float, result=bool)
    def updateCustomer(self, customer_id, name, id_number, phone, email, address, credit_limit):
        """Update existing customer"""
        try:
            success, msg, customer = self.controller.update_customer(
                customer_id=customer_id,
                name=name,
                id_number=id_number,
                phone=phone,
                email=email,
                address=address,
                credit_limit=credit_limit
            )
            
            if success:
                self.customersUpdated.emit()
                self.operationSuccess.emit("Cliente actualizado exitosamente")
                return True
            else:
                self.operationError.emit(msg)
                return False
        except Exception as e:
            self.operationError.emit(str(e))
            return False

    @Slot(int, result=bool)
    def deleteCustomer(self, customer_id):
        """Delete customer"""
        try:
            success, msg = self.controller.delete_customer(customer_id)
            if success:
                self.customersUpdated.emit()
                self.operationSuccess.emit("Cliente eliminado exitosamente")
                return True
            else:
                self.operationError.emit(msg)
                return False
        except Exception as e:
            self.operationError.emit(str(e))
            return False
            
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
