from frontend_caja.services.api_client import APIClient
from datetime import date, datetime

class ProfitService:
    def __init__(self):
        self.client = APIClient()
        self.endpoint = "/api/v1/reports/profit"

    def _format_date(self, dt):
        """Convert datetime or date to date string (YYYY-MM-DD)"""
        if isinstance(dt, datetime):
            return dt.date().isoformat()
        elif isinstance(dt, date):
            return dt.isoformat()
        else:
            return str(dt)

    def get_product_profitability(self, product_id):
        """Get profitability stats for a specific product"""
        try:
            return self.client.get(f"{self.endpoint}/product/{product_id}")
        except Exception as e:
            print(f"Error fetching product profitability: {e}")
            return None

    def get_sales_profitability(self, start_date=None, end_date=None):
        """Get total profitability for a date range"""
        try:
            params = {}
            if start_date:
                params['start_date'] = self._format_date(start_date)
            if end_date:
                params['end_date'] = self._format_date(end_date)
            return self.client.get(f"{self.endpoint}/sales", params=params)
        except Exception as e:
            print(f"Error fetching sales profitability: {e}")
            return {}

    def get_month_profitability(self):
        """Get profitability for current month"""
        try:
            return self.client.get(f"{self.endpoint}/month")
        except Exception as e:
            print(f"Error fetching month profitability: {e}")
            return {}
