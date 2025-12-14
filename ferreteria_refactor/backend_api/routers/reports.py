from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date
from ..database.db import get_db
from ..models import models
from .. import schemas

router = APIRouter(
    prefix="/reports",
    tags=["reports"]
)

@router.get("/sales/detailed")
def get_detailed_sales_report(
    start_date: date,
    end_date: date,
    customer_id: Optional[int] = None,
    product_id: Optional[int] = None,
    payment_method: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Detailed sales report with filters"""
    # Convert dates to datetime
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())
    
    query = db.query(models.Sale).filter(
        models.Sale.date >= start_dt,
        models.Sale.date <= end_dt
    )
    
    if customer_id:
        query = query.filter(models.Sale.customer_id == customer_id)
    
    if payment_method:
        query = query.filter(models.Sale.payment_method == payment_method)
    
    sales = query.order_by(models.Sale.date.desc()).all()
    
    # Filter by product if specified
    if product_id:
        sales = [s for s in sales if any(d.product_id == product_id for d in s.details)]
    
    return sales

@router.get("/sales/summary")
def get_sales_summary(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """Summary statistics for sales period"""
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())
    
    sales = db.query(models.Sale).filter(
        models.Sale.date >= start_dt,
        models.Sale.date <= end_dt
    ).all()
    
    total_revenue = sum(s.total_amount for s in sales)
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
    total_items = db.query(func.sum(models.SaleDetail.quantity)).join(models.Sale).filter(
        models.Sale.date >= start_dt,
        models.Sale.date <= end_dt
    ).scalar() or 0
    
    # Subtract returns
    returns = db.query(models.Return).filter(
        models.Return.date >= start_dt,
        models.Return.date <= end_dt
    ).all()
    
    total_refunded = sum(r.total_refunded for r in returns)
    total_refunded_bs = 0.0
    for ret in returns:
        sale = db.query(models.Sale).filter(models.Sale.id == ret.sale_id).first()
        if sale:
            refund_bs = ret.total_refunded * (sale.exchange_rate_used or 1.0)
            total_refunded_bs += refund_bs
    
    # Adjust totals
    total_revenue -= total_refunded
    total_revenue_bs -= total_refunded_bs
    
    return {
        "total_revenue": total_revenue,
        "total_revenue_bs": total_revenue_bs,
        "total_transactions": total_transactions,
        "cash_sales": cash_sales,
        "credit_sales": credit_sales,
        "total_items_sold": total_items,
        "average_ticket": total_revenue / total_transactions if total_transactions > 0 else 0
    }

@router.get("/cash-flow")
def get_cash_flow_report(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """All cash movements in period"""
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())
    
    # Get all cash sessions in period
    sessions = db.query(models.CashSession).filter(
        models.CashSession.start_time >= start_dt,
        models.CashSession.start_time <= end_dt
    ).all()
    
    movements = []
    for session in sessions:
        for mov in session.movements:
            movements.append({
                "date": mov.date.isoformat(),
                "session_id": session.id,
                "type": mov.type,
                "amount": mov.amount,
                "currency": mov.currency or "USD",
                "description": mov.description
            })
    
    # Also get sales
    sales = db.query(models.Sale).filter(
        models.Sale.date >= start_dt,
        models.Sale.date <= end_dt,
        models.Sale.is_credit == False
    ).all()
    
    for sale in sales:
        movements.append({
            "date": sale.date.isoformat(),
            "session_id": None,
            "type": "SALE",
            "amount": sale.total_amount,
            "currency": "USD",
            "description": f"Venta #{sale.id}"
        })
    
    # Sort by date
    movements.sort(key=lambda x: x["date"], reverse=True)
    
    return movements

@router.get("/top-products")
def get_top_products(
    start_date: date,
    end_date: date,
    limit: int = 10,
    by: str = "quantity",
    db: Session = Depends(get_db)
):
    """Top products by quantity sold or revenue"""
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())
    
    if by == "quantity":
        results = db.query(
            models.Product.id,
            models.Product.name,
            func.sum(models.SaleDetail.quantity).label('total_quantity')
        ).join(models.SaleDetail).join(models.Sale).filter(
            models.Sale.date >= start_dt,
            models.Sale.date <= end_dt
        ).group_by(models.Product.id, models.Product.name).order_by(
            func.sum(models.SaleDetail.quantity).desc()
        ).limit(limit).all()
        
        return [{"product_id": r[0], "product_name": r[1], "quantity_sold": r[2]} for r in results]
    
    else:  # by revenue
        results = db.query(
            models.Product.id,
            models.Product.name,
            func.sum(models.SaleDetail.subtotal).label('total_revenue')
        ).join(models.SaleDetail).join(models.Sale).filter(
            models.Sale.date >= start_dt,
            models.Sale.date <= end_dt
        ).group_by(models.Product.id, models.Product.name).order_by(
            func.sum(models.SaleDetail.subtotal).desc()
        ).limit(limit).all()
        
        return [{"product_id": r[0], "product_name": r[1], "revenue": r[2]} for r in results]

@router.get("/customer-debts")
def get_customer_debt_report(db: Session = Depends(get_db)):
    """All customers with outstanding debt"""
    customers = db.query(models.Customer).all()
    
    report = []
    for customer in customers:
        # Sum unpaid credit sales
        unpaid_sales = db.query(func.sum(models.Sale.total_amount)).filter(
            models.Sale.customer_id == customer.id,
            models.Sale.is_credit == True,
            models.Sale.paid == False
        ).scalar() or 0
        
        # Sum payments
        payments = db.query(func.sum(models.Payment.amount)).filter(
            models.Payment.customer_id == customer.id
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

@router.get("/low-stock")
def get_low_stock_products(threshold: int = 5, db: Session = Depends(get_db)):
    """Products with stock <= threshold"""
    products = db.query(models.Product).filter(models.Product.stock <= threshold).all()
    return products

@router.get("/inventory-valuation")
def get_inventory_valuation(exchange_rate: float = 1.0, db: Session = Depends(get_db)):
    """Total inventory value (stock * price)"""
    products = db.query(models.Product).all()
    total_value = sum(p.stock * p.price for p in products)
    return {
        "total_products": len(products),
        "total_stock_units": sum(p.stock for p in products),
        "total_value": total_value,
        "total_value_bs": total_value * exchange_rate
    }

# ===== PROFIT ANALYSIS ENDPOINTS =====

@router.get("/profit/product/{product_id}")
def get_product_profitability(product_id: int, db: Session = Depends(get_db)):
    """Get profitability stats for a specific product"""
    product = db.query(models.Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get total sold
    total_sold = db.query(func.sum(models.SaleDetail.quantity)).filter(
        models.SaleDetail.product_id == product_id
    ).scalar() or 0
    
    # Calculate total profit
    sales = db.query(models.SaleDetail).filter(models.SaleDetail.product_id == product_id).all()
    total_profit = sum((detail.unit_price - product.cost_price) * detail.quantity for detail in sales)
    
    margin = 0
    if product.price > 0:
        margin = ((product.price - product.cost_price) / product.price) * 100
    
    return {
        'product_id': product.id,
        'product_name': product.name,
        'cost': product.cost_price,
        'price': product.price,
        'margin_percent': margin,
        'total_sold': total_sold,
        'total_profit': total_profit
    }

@router.get("/profit/sales")
def get_sales_profitability(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get total profitability for a date range"""
    query = db.query(models.SaleDetail).join(models.Sale)
    
    if start_date:
        start_dt = datetime.combine(start_date, datetime.min.time())
        query = query.filter(models.Sale.date >= start_dt)
    if end_date:
        end_dt = datetime.combine(end_date, datetime.max.time())
        query = query.filter(models.Sale.date <= end_dt)
    
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

@router.get("/profit/month")
def get_month_profitability(db: Session = Depends(get_db)):
    """Get profitability for current month"""
    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)
    
    query = db.query(models.SaleDetail).join(models.Sale).filter(
        models.Sale.date >= start_of_month,
        models.Sale.date <= now
    )
    
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
