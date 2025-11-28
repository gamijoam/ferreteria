from sqlalchemy.orm import Session
from src.models.models import Supplier
from sqlalchemy.exc import IntegrityError

class SupplierController:
    def __init__(self, db: Session):
        self.db = db

    def create_supplier(self, name, contact_person=None, phone=None, email=None, address=None, notes=None):
        """Create a new supplier"""
        try:
            supplier = Supplier(
                name=name,
                contact_person=contact_person,
                phone=phone,
                email=email,
                address=address,
                notes=notes
            )
            self.db.add(supplier)
            self.db.commit()
            self.db.refresh(supplier)
            return supplier, None
        except IntegrityError:
            self.db.rollback()
            return None, "Ya existe un proveedor con ese nombre"
        except Exception as e:
            self.db.rollback()
            return None, str(e)

    def get_all_suppliers(self, active_only=True):
        """Get all suppliers"""
        query = self.db.query(Supplier)
        if active_only:
            query = query.filter(Supplier.is_active == True)
        return query.order_by(Supplier.name).all()

    def get_supplier(self, supplier_id):
        """Get supplier by ID"""
        return self.db.query(Supplier).get(supplier_id)

    def update_supplier(self, supplier_id, **kwargs):
        """Update supplier information"""
        supplier = self.get_supplier(supplier_id)
        if not supplier:
            return False, "Proveedor no encontrado"

        try:
            for key, value in kwargs.items():
                if hasattr(supplier, key):
                    setattr(supplier, key, value)
            
            self.db.commit()
            return True, "Proveedor actualizado correctamente"
        except IntegrityError:
            self.db.rollback()
            return False, "Ya existe un proveedor con ese nombre"
        except Exception as e:
            self.db.rollback()
            return False, str(e)

    def deactivate_supplier(self, supplier_id):
        """Deactivate a supplier"""
        return self.update_supplier(supplier_id, is_active=False)

    def activate_supplier(self, supplier_id):
        """Activate a supplier"""
        return self.update_supplier(supplier_id, is_active=True)
