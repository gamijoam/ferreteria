from frontend_caja.services.profit_service import ProfitService
import datetime

class ProfitController:
    def __init__(self, db=None):
        self.service = ProfitService()
        self.db = None  # Ignored

    def get_product_profitability(self, product_id):
        """Get profitability stats for a specific product"""
        return self.service.get_product_profitability(product_id)

    def get_sales_profitability(self, start_date=None, end_date=None):
        """Get total profitability for a date range"""
        return self.service.get_sales_profitability(start_date, end_date)

    def get_month_profitability(self):
        """Get profitability for current month"""
        return self.service.get_month_profitability()
