from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.models import Product, Sale, SaleDetail
import datetime

class ProfitController:
    def __init__(self, db: Session):
        self.db = db

    def get_product_profitability(self, product_id):
        """Get profitability stats for a specific product"""
        product = self.db.query(Product).get(product_id)
        if not product:
            return None
        
        # Get total sold
        total_sold = self.db.query(func.sum(SaleDetail.quantity)).filter(
            SaleDetail.product_id == product_id
        ).scalar() or 0
        
        # Calculate total profit
        sales = self.db.query(SaleDetail).filter(SaleDetail.product_id == product_id).all()
        total_profit = sum((detail.unit_price - product.cost_price) * detail.quantity for detail in sales)
        
        margin = 0
        if product.price > 0:
            margin = ((product.price - product.cost_price) / product.price) * 100
        
        return {
            'product': product,
            'cost': product.cost_price,
            'price': product.price,
            'margin_percent': margin,
            'total_sold': total_sold,
            'total_profit': total_profit
        }

    def get_sales_profitability(self, start_date=None, end_date=None):
        """Get total profitability for a date range"""
        query = self.db.query(SaleDetail).join(Sale)
        
        if start_date:
            query = query.filter(Sale.date >= start_date)
        if end_date:
            query = query.filter(Sale.date <= end_date)
        
        details = query.all()
        
        total_revenue = 0
        total_cost = 0
        
        for detail in details:
            total_revenue += detail.subtotal
            total_cost += detail.product.cost_price * detail.quantity
        
        total_profit = total_revenue - total_cost
        avg_margin = 0
        if total_revenue > 0:
            avg_margin = (total_profit / total_revenue) * 100
        
        return {
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'total_profit': total_profit,
            'avg_margin': avg_margin,
            'num_sales': len(set(d.sale_id for d in details))
        }

    def get_month_profitability(self):
        """Get profitability for current month"""
        now = datetime.datetime.now()
        start_of_month = datetime.datetime(now.year, now.month, 1)
        return self.get_sales_profitability(start_of_month, now)
