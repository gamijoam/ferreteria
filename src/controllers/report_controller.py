from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.models import Product, Sale, SaleDetail
import datetime

class ReportController:
    def __init__(self, db: Session):
        self.db = db

    def get_low_stock_products(self, threshold=5):
        """Returns products with stock <= threshold"""
        return self.db.query(Product).filter(Product.stock <= threshold).all()

    def get_sales_report(self, start_date, end_date):
        """
        Returns sales summary between dates.
        Note: end_date should be inclusive (end of day).
        """
        # Ensure end_date covers the whole day
        end_date = end_date.replace(hour=23, minute=59, second=59)
        
        sales = self.db.query(Sale).filter(Sale.date >= start_date, Sale.date <= end_date).all()
        
        total_sales = sum(s.total_amount for s in sales)
        count_sales = len(sales)
        
        # Calculate profit (approx)
        # We need to sum (SaleDetail.subtotal - (SaleDetail.quantity * SaleDetail.product.cost))
        # But we didn't implement 'cost' in Product model explicitly in Module 1 (only price).
        # Assuming 'price' is selling price. If we don't have cost, we can only show Revenue.
        # Let's show Revenue and Items Sold.
        
        total_items = self.db.query(func.sum(SaleDetail.quantity)).join(Sale).filter(Sale.date >= start_date, Sale.date <= end_date).scalar() or 0
        
        return {
            "total_revenue": total_sales,
            "transaction_count": count_sales,
            "items_sold": total_items
        }
