from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from src.models.models import Product, Sale, SaleDetail, CashSession, CashMovement, Customer, Payment, Kardex
import datetime
import csv

class ReportController:
    def __init__(self, db: Session):
        self.db = db

    # ===== SALES REPORTS =====
    
    def get_detailed_sales_report(self, start_date, end_date, customer_id=None, product_id=None, payment_method=None):
        """
        Detailed sales report with filters
        Returns list of sales with all details
        """
        end_date = end_date.replace(hour=23, minute=59, second=59)
        
        query = self.db.query(Sale).filter(
            Sale.date >= start_date,
            Sale.date <= end_date
        )
        
        if customer_id:
            query = query.filter(Sale.customer_id == customer_id)
        
        if payment_method:
            query = query.filter(Sale.payment_method == payment_method)
        
        sales = query.order_by(Sale.date.desc()).all()
        
        # If filtering by product, filter sales that contain that product
        if product_id:
            sales = [s for s in sales if any(d.product_id == product_id for d in s.details)]
        
        return sales

    def get_sales_summary(self, start_date, end_date):
        """Summary statistics for sales period"""
        end_date = end_date.replace(hour=23, minute=59, second=59)
        
        sales = self.db.query(Sale).filter(
            Sale.date >= start_date,
            Sale.date <= end_date
        ).all()
        
        total_revenue = sum(s.total_amount for s in sales)
        # Calculate total revenue in Bs (using stored amount or converting with stored rate)
        total_revenue_bs = sum(
            s.total_amount_bs if s.total_amount_bs is not None 
            else (s.total_amount * (s.exchange_rate_used or 1.0)) 
            for s in sales
        )
        
        total_transactions = len(sales)
        
        # Count by payment method
        cash_sales = sum(s.total_amount for s in sales if s.payment_method == "Efectivo")
        credit_sales = sum(s.total_amount for s in sales if s.payment_method == "Credito")
        
        # Total items sold
        total_items = self.db.query(func.sum(SaleDetail.quantity)).join(Sale).filter(
            Sale.date >= start_date,
            Sale.date <= end_date
        ).scalar() or 0
        
        return {
            "total_revenue": total_revenue,
            "total_revenue_bs": total_revenue_bs,
            "total_transactions": total_transactions,
            "cash_sales": cash_sales,
            "credit_sales": credit_sales,
            "total_items_sold": total_items,
            "average_ticket": total_revenue / total_transactions if total_transactions > 0 else 0
        }

    # ===== CASH FLOW REPORTS =====
    
    def get_cash_flow_report(self, start_date, end_date):
        """All cash movements in period"""
        end_date = end_date.replace(hour=23, minute=59, second=59)
        
        # Get all cash sessions in period
        sessions = self.db.query(CashSession).filter(
            CashSession.start_time >= start_date,
            CashSession.start_time <= end_date
        ).all()
        
        movements = []
        for session in sessions:
            for mov in session.movements:
                movements.append({
                    "date": mov.date,
                    "session_id": session.id,
                    "type": mov.type,
                    "amount": mov.amount,
                    "description": mov.description
                })
        
        # Also get sales
        sales = self.db.query(Sale).filter(
            Sale.date >= start_date,
            Sale.date <= end_date,
            Sale.is_credit == False  # Only cash sales
        ).all()
        
        for sale in sales:
            movements.append({
                "date": sale.date,
                "session_id": None,
                "type": "SALE",
                "amount": sale.total_amount,
                "description": f"Venta #{sale.id}"
            })
        
        # Sort by date
        movements.sort(key=lambda x: x["date"], reverse=True)
        
        return movements

    # ===== TOP PRODUCTS =====
    
    def get_top_products(self, start_date, end_date, limit=10, by="quantity"):
        """
        Top products by quantity sold or revenue
        by: 'quantity' or 'revenue'
        """
        end_date = end_date.replace(hour=23, minute=59, second=59)
        
        if by == "quantity":
            results = self.db.query(
                Product.id,
                Product.name,
                func.sum(SaleDetail.quantity).label('total_quantity')
            ).join(SaleDetail).join(Sale).filter(
                Sale.date >= start_date,
                Sale.date <= end_date
            ).group_by(Product.id, Product.name).order_by(
                func.sum(SaleDetail.quantity).desc()
            ).limit(limit).all()
            
            return [{"product_id": r[0], "product_name": r[1], "quantity_sold": r[2]} for r in results]
        
        else:  # by revenue
            results = self.db.query(
                Product.id,
                Product.name,
                func.sum(SaleDetail.subtotal).label('total_revenue')
            ).join(SaleDetail).join(Sale).filter(
                Sale.date >= start_date,
                Sale.date <= end_date
            ).group_by(Product.id, Product.name).order_by(
                func.sum(SaleDetail.subtotal).desc()
            ).limit(limit).all()
            
            return [{"product_id": r[0], "product_name": r[1], "revenue": r[2]} for r in results]

    # ===== CUSTOMER DEBT =====
    
    def get_customer_debt_report(self):
        """All customers with outstanding debt"""
        customers = self.db.query(Customer).all()
        
        report = []
        for customer in customers:
            # Sum unpaid credit sales
            unpaid_sales = self.db.query(func.sum(Sale.total_amount)).filter(
                Sale.customer_id == customer.id,
                Sale.is_credit == True,
                Sale.paid == False
            ).scalar() or 0
            
            # Sum payments
            payments = self.db.query(func.sum(Payment.amount)).filter(
                Payment.customer_id == customer.id
            ).scalar() or 0
            
            debt = unpaid_sales - payments
            
            if debt > 0:
                report.append({
                    "customer_id": customer.id,
                    "customer_name": customer.name,
                    "phone": customer.phone,
                    "debt": debt
                })
        
        # Sort by debt descending
        report.sort(key=lambda x: x["debt"], reverse=True)
        return report

    # ===== STOCK REPORTS =====
    
    def get_low_stock_products(self, threshold=5):
        """Products with stock <= threshold"""
        return self.db.query(Product).filter(Product.stock <= threshold).all()

    def get_inventory_valuation(self, exchange_rate=1.0):
        """Total inventory value (stock * price)"""
        products = self.db.query(Product).all()
        total_value = sum(p.stock * p.price for p in products)
        return {
            "total_products": len(products),
            "total_stock_units": sum(p.stock for p in products),
            "total_value": total_value,
            "total_value_bs": total_value * exchange_rate
        }

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
