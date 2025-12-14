from frontend_caja.services.report_service import ReportService
import datetime
import csv

class ReportController:
    def __init__(self, db=None):
        self.service = ReportService()
        self.db = None  # Ignored

    # ===== SALES REPORTS =====
    
    def get_detailed_sales_report(self, start_date, end_date, customer_id=None, product_id=None, payment_method=None):
        """
        Detailed sales report with filters
        Returns list of sales with all details
        """
        return self.service.get_detailed_sales_report(start_date, end_date, customer_id, product_id, payment_method)

    def get_sales_summary(self, start_date, end_date):
        """Summary statistics for sales period"""
        return self.service.get_sales_summary(start_date, end_date)

    # ===== CASH FLOW REPORTS =====
    
    def get_cash_flow_report(self, start_date, end_date):
        """All cash movements in period"""
        return self.service.get_cash_flow_report(start_date, end_date)

    # ===== TOP PRODUCTS =====
    
    def get_top_products(self, start_date, end_date, limit=10, by="quantity"):
        """
        Top products by quantity sold or revenue
        by: 'quantity' or 'revenue'
        """
        return self.service.get_top_products(start_date, end_date, limit, by)

    # ===== CUSTOMER DEBT =====
    
    def get_customer_debt_report(self):
        """All customers with outstanding debt"""
        return self.service.get_customer_debt_report()

    # ===== STOCK REPORTS =====
    
    def get_low_stock_products(self, threshold=5):
        """Products with stock <= threshold"""
        data = self.service.get_low_stock_products(threshold)
        # Wrap in ProductObj if needed by views
        return [ProductObj(p) for p in data] if data else []

    def get_inventory_valuation(self, exchange_rate=1.0):
        """Total inventory value (stock * price)"""
        return self.service.get_inventory_valuation(exchange_rate)

    # ===== EXPORT FUNCTIONS =====
    
    def export_to_csv(self, data, headers, filename):
        """
        Export data to CSV file
        data: list of dicts or list of tuples
        headers: list of column names
        filename: output filename
        """
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for row in data:
                if isinstance(row, dict):
                    writer.writerow([row.get(h, '') for h in headers])
                else:
                    writer.writerow(row)
        
        return filename

class ProductObj:
    """Helper to wrap product dict for UI compatibility"""
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name', 'Producto')
        self.sku = data.get('sku')
        self.price = data.get('price')
        self.stock = data.get('stock')
        self.min_stock = data.get('min_stock')
        self.is_active = data.get('is_active', True)
