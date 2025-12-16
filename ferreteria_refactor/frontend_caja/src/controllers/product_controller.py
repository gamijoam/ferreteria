from frontend_caja.services.product_service import ProductService
# Using event bus only if really needed, but API ops are usually synchronous here or handled by reload
from src.utils.event_bus import event_bus

class ProductController:
    def __init__(self, db=None): # db arg kept for compatibility
        self.product_service = ProductService()

    def create_product(self, **kwargs):
        """Create a new product via API"""
        try:
            return self.product_service.create_product(kwargs)
        except Exception as e:
            print(f"Error creating product: {e}")
            raise e

    def update_product(self, product_id, **kwargs):
        """Update an existing product via API"""
        try:
            return self.product_service.update_product(product_id, kwargs)
        except Exception as e:
            print(f"Error updating product: {e}")
            return None

    def delete_product(self, product_id):
        """active=False via API"""
        pass # Not implemented in API yet

    def get_active_products(self):
        products = self.product_service.get_all_products()
        return [MockProduct(p) for p in products] if products else []

    def get_all_products(self):
        products = self.product_service.get_all_products()
        return [MockProduct(p) for p in products] if products else []

    def get_product_by_id(self, product_id):
        # Fetch all and find
        products = self.get_all_products()
        for p in products:
            if p.id == product_id:
                return p
        return None

    def get_products_paginated(self, page=1, page_size=50, search_query=None):
        """
        Simulate pagination on client side or fetch all.
        The current API `get_all_products` returns full list.
        """
        all_products = self.product_service.get_all_products()
        if not all_products:
            return [], 0

        # Filter
        filtered = []
        if search_query:
            q = search_query.lower()
            for p in all_products:
                if (p.get('sku') and q in p['sku'].lower()) or (p.get('name') and q in p['name'].lower()):
                    filtered.append(p)
        else:
            filtered = all_products

        total_items = len(filtered)
        
        # Paginate
        start = (page - 1) * page_size
        end = start + page_size
        page_items_dicts = filtered[start:end]

        # Convert dicts to Objects for View compatibility
        page_items_objs = [MockProduct(p) for p in page_items_dicts]

        return page_items_objs, total_items
    
    def get_categories(self):
        """Get all product categories"""
        try:
            return self.product_service.get_categories()
        except Exception as e:
            print(f"Error getting categories: {e}")
            # Fallback categories
            return [
                {'id': 1, 'name': 'General'},
                {'id': 2, 'name': 'Construcción'},
                {'id': 3, 'name': 'Herramientas'},
                {'id': 4, 'name': 'Eléctrico'},
                {'id': 5, 'name': 'Plomería'}
            ]
    
    def get_product_units(self, product_id):
        """Get all units/presentations for a product"""
        try:
            return self.product_service.get_product_units(product_id)
        except Exception as e:
            print(f"Error getting product units: {e}")
            return []
    
    def create_product_unit(self, unit_data):
        """Create a new product unit/presentation"""
        try:
            return self.product_service.create_product_unit(unit_data)
        except Exception as e:
            print(f"Error creating product unit: {e}")
            raise e
    
    def delete_product_unit(self, unit_id):
        """Delete a product unit/presentation"""
        try:
            return self.product_service.delete_product_unit(unit_id)
        except Exception as e:
            print(f"Error deleting product unit: {e}")
            raise e

class MockProduct:
    """Helper class to mimic SQLAlchemy model object behavior for Views"""
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.sku = data.get('sku')
        self.price = data.get('price', 0.0)
        self.price_mayor_1 = data.get('price_mayor_1', 0.0)
        self.price_mayor_2 = data.get('price_mayor_2', 0.0)
        self.cost_price = data.get('cost_price', 0.0)
        self.stock = data.get('stock', 0.0)
        self.min_stock = data.get('min_stock', 5.0)
        self.is_box = data.get('is_box', False)
        self.conversion_factor = data.get('conversion_factor', 1)
        self.unit_type = data.get('unit_type', 'Unidad')
        self.location = data.get('location')
        self.category_id = data.get('category_id')
        self.supplier_id = data.get('supplier_id')
        self.is_active = data.get('is_active', True)
        self.default_rate_id = data.get('default_rate_id')
