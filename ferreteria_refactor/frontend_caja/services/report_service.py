from frontend_caja.services.api_client import APIClient
from datetime import date, datetime

class ReportService:
    def __init__(self):
        self.client = APIClient()
        self.endpoint = "/api/v1/reports"

    def _format_date(self, dt):
        """Convert datetime or date to date string (YYYY-MM-DD)"""
        if isinstance(dt, datetime):
            return dt.date().isoformat()
        elif isinstance(dt, date):
            return dt.isoformat()
        else:
            return str(dt)

    def get_detailed_sales_report(self, start_date, end_date, customer_id=None, product_id=None, payment_method=None):
        """Detailed sales report with filters"""
        try:
            params = {
                "start_date": self._format_date(start_date),
                "end_date": self._format_date(end_date)
            }
            if customer_id:
                params['customer_id'] = customer_id
            if product_id:
                params['product_id'] = product_id
            if payment_method:
                params['payment_method'] = payment_method
            
            return self.client.get(f"{self.endpoint}/sales/detailed", params=params)
        except Exception as e:
            print(f"Error fetching detailed sales report: {e}")
            return []

    def get_sales_summary(self, start_date, end_date):
        """Summary statistics for sales period"""
        try:
            params = {
                "start_date": self._format_date(start_date),
                "end_date": self._format_date(end_date)
            }
            return self.client.get(f"{self.endpoint}/sales/summary", params=params)
        except Exception as e:
            print(f"Error fetching sales summary: {e}")
            return {}

    def get_cash_flow_report(self, start_date, end_date):
        """All cash movements in period"""
        try:
            params = {
                "start_date": self._format_date(start_date),
                "end_date": self._format_date(end_date)
            }
            return self.client.get(f"{self.endpoint}/cash-flow", params=params)
        except Exception as e:
            print(f"Error fetching cash flow report: {e}")
            return []

    def get_top_products(self, start_date, end_date, limit=10, by="quantity"):
        """Top products by quantity sold or revenue"""
        try:
            params = {
                "start_date": self._format_date(start_date),
                "end_date": self._format_date(end_date),
                "limit": limit,
                "by": by
            }
            return self.client.get(f"{self.endpoint}/top-products", params=params)
        except Exception as e:
            print(f"Error fetching top products: {e}")
            return []

    def get_customer_debt_report(self):
        """All customers with outstanding debt"""
        try:
            return self.client.get(f"{self.endpoint}/customer-debts")
        except Exception as e:
            print(f"Error fetching customer debts: {e}")
            return []

    def get_low_stock_products(self, threshold=5):
        """Products with stock <= threshold"""
        try:
            params = {"threshold": threshold}
            return self.client.get(f"{self.endpoint}/low-stock", params=params)
        except Exception as e:
            print(f"Error fetching low stock products: {e}")
            return []

    def get_inventory_valuation(self, exchange_rate=1.0):
        """Total inventory value (stock * price)"""
        try:
            params = {"exchange_rate": exchange_rate}
            return self.client.get(f"{self.endpoint}/inventory-valuation", params=params)
        except Exception as e:
            print(f"Error fetching inventory valuation: {e}")
            return {}
