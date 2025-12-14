from frontend_caja.services.product_service import ProductService
# Using event bus only if really needed, but API ops are usually synchronous here or handled by reload
from src.utils.event_bus import event_bus

class ProductController:
    def __init__(self, db=None): # db arg kept for compatibility
        self.product_service = ProductService()

    def create_product(self, **kwargs):
        """Create a new product via API"""
        # Adapt kwargs to API schema if needed
        # For now assuming API accepts similar payload
        # API expects: name, sku, price, stock...
        # We might need to map keys if they differ
        pass # Not implemented in API yet (only GET / POST sales)
        # TODO: Implement POST /products in Backend

    def update_product(self, product_id, **kwargs):
        """Update an existing product via API"""
        pass # Not implemented in API yet

    def delete_product(self, product_id):
        """active=False via API"""
        pass # Not implemented in API yet

    def get_active_products(self):
        return self.product_service.get_all_products()

    def get_all_products(self):
        return self.product_service.get_all_products()

    def get_product_by_id(self, product_id):
        # Inefficient but simple: fetch all and find
        products = self.get_all_products()
        for p in products:
            if p['id'] == product_id:
                return MockProduct(p)
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

class MockProduct:
    """Helper class to mimic SQLAlchemy model object behavior for Views"""
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.sku = data.get('sku')
        self.price = data.get('price', 0.0)
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
