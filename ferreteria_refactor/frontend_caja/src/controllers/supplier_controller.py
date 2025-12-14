from frontend_caja.services.supplier_service import SupplierService

class SupplierController:
    def __init__(self, db=None):
        self.service = SupplierService()
        self.db = None # Ignored

    def create_supplier(self, name, contact_person=None, phone=None, email=None, address=None, notes=None):
        """Create a new supplier via API"""
        payload = {
            "name": name,
            "contact_person": contact_person,
            "phone": phone,
            "email": email,
            "address": address,
            "notes": notes,
            "is_active": True
        }
        
        result = self.service.create_supplier(payload)
        if result:
            return result, None # Return API dict as object mock? Or just dict if UI handles it.
            # Assuming UI expects object-like or dict. Old controller returned (obj, error).
            # The UI probably uses obj.name etc.
            # Let's return a simple object wrapper or just the dict if the view supports it.
            # Looking at previous controllers, we wrapped in Obj. Let's do that for consistency if needed.
            # But here I'll stick to dict if possible, or simple wrapper.
            return SupplierObj(result), None
        else:
            return None, "Error creando proveedor"

    def get_all_suppliers(self, active_only=True):
        """Get all suppliers from API"""
        data = self.service.get_all_suppliers(active_only=active_only)
        return [SupplierObj(d) for d in data]

    def get_supplier(self, supplier_id):
        """Get supplier by ID"""
        data = self.service.get_supplier(supplier_id)
        return SupplierObj(data) if data else None

    def update_supplier(self, supplier_id, **kwargs):
        """Update supplier information"""
        # API expects partial update via PUT (or PATCH, but here we likely use PUT with full object or handling partials in router)
        # My router uses exclude_unset=True, so I can send partials.
        
        # Mapping kwargs to payload
        result = self.service.update_supplier(supplier_id, kwargs)
        if result:
            return True, "Proveedor actualizado correctamente"
        else:
            return False, "Error al actualizar proveedor"

    def deactivate_supplier(self, supplier_id):
        """Deactivate a supplier"""
        return self.update_supplier(supplier_id, is_active=False)

    def activate_supplier(self, supplier_id):
        """Activate a supplier"""
        return self.update_supplier(supplier_id, is_active=True)

class SupplierObj:
    """Helper to wrap dict response for UI compatibility (if attributes are accessed via dot notation)"""
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.contact_person = data.get('contact_person')
        self.phone = data.get('phone')
        self.email = data.get('email')
        self.address = data.get('address')
        self.notes = data.get('notes')
        self.is_active = data.get('is_active')
