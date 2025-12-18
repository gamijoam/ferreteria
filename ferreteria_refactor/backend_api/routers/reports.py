from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from ..database.db import get_db
from ..models import models
from ..dependencies import admin_only

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(admin_only)]  # 🔒 ADMIN ONLY - Financial data is sensitive
)

@router.get("/dashboard/financials")
def get_dashboard_financials(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Financial metrics for dashboard - real money collected by currency
    
    Returns:
    - sales_by_currency: List of totals grouped by currency (USD, COP, VES, etc.)
    - total_sales_base_usd: Sum of all sales converted to USD base
    - profit_estimated: Estimated profit (sales - costs)
    """
    # Default to today if no dates provided
    if not start_date:
        start_date = date.today()
    if not end_date:
        end_date = date.today()
    
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())
    
    # Get all sale IDs that have returns (voided sales)
    voided_sale_ids = db.query(models.Return.sale_id).filter(
        models.Return.date >= start_dt,
        models.Return.date <= end_dt
    ).distinct().all()
    voided_sale_ids = [sid[0] for sid in voided_sale_ids]
    
    # Query SalePayment grouped by currency, excluding voided sales
    query = db.query(
        models.SalePayment.currency,
        func.sum(models.SalePayment.amount).label('total_collected'),
        func.count(models.SalePayment.id).label('payment_count')
    ).join(models.Sale).filter(
        models.Sale.date >= start_dt,
        models.Sale.date <= end_dt
    )
    
    # Exclude voided sales
    if voided_sale_ids:
        query = query.filter(models.Sale.id.notin_(voided_sale_ids))
    
    # Group by currency
    results = query.group_by(models.SalePayment.currency).all()
    
    # Format sales by currency
    sales_by_currency = []
    total_sales_base_usd = Decimal("0.00")
    
    for currency, total_collected, count in results:
        sales_by_currency.append({
            "currency": currency or "USD",
            "total_collected": float(round(total_collected, 2)),
            "count": count
        })
        
        # Convert to USD for base total
        # If currency is USD, add directly; otherwise use exchange rate
        if currency == "USD":
            total_sales_base_usd += Decimal(str(total_collected))
        else:
            # Get average exchange rate for the period
            avg_rate = db.query(func.avg(models.SalePayment.exchange_rate)).filter(
                models.SalePayment.currency == currency
            ).join(models.Sale).filter(
                models.Sale.date >= start_dt,
                models.Sale.date <= end_dt
            ).scalar() or Decimal("1.0")
            
            # Convert to USD
            total_sales_base_usd += Decimal(str(total_collected)) / Decimal(str(avg_rate))
    
    # Calculate profit estimation (Sales - Costs)
    # Get all sale details for the period (excluding voided sales)
    sale_details_query = db.query(models.SaleDetail).join(models.Sale).filter(
        models.Sale.date >= start_dt,
        models.Sale.date <= end_dt
    )
    
    if voided_sale_ids:
        sale_details_query = sale_details_query.filter(models.Sale.id.notin_(voided_sale_ids))
    
    sale_details = sale_details_query.all()
    
    total_cost = Decimal("0.00")
    total_revenue = Decimal("0.00")
    
    for detail in sale_details:
        total_revenue += detail.subtotal
        if detail.product and detail.product.cost_price:
            total_cost += Decimal(str(detail.product.cost_price)) * Decimal(str(detail.quantity))
    
    profit_estimated = total_revenue - total_cost
    
    return {
        "sales_by_currency": sales_by_currency,
        "total_sales_base_usd": float(round(total_sales_base_usd, 2)),
        "profit_estimated": float(round(profit_estimated, 2))
    }

@router.get("/dashboard/cashflow")
def get_dashboard_cashflow(db: Session = Depends(get_db)):
    """
    Calculate physical cash balance by currency in open cash sessions
    
    Returns real money that should be in the cash drawer:
    - Initial cash from open sessions
    - + Sales income (from SalePayment)
    - + Deposits
    - - Expenses
    - - Withdrawals  
    - - Returns/Refunds
    """
    # Get all active currencies from config
    active_currencies = db.query(models.Currency).filter(models.Currency.is_active == True).all()
    currency_codes = [c.symbol for c in active_currencies] if active_currencies else ['USD', 'Bs']
    
    # Get open cash sessions
    open_sessions = db.query(models.CashSession).filter(models.CashSession.status == "OPEN").all()
    
    if not open_sessions:
        # No open sessions, return zeros
        return {
            "balances": [{"currency": code, "initial": 0, "sales": 0, "expenses": 0, "net_balance": 0} for code in currency_codes],
            "alerts": ["No hay sesiones de caja abiertas"]
        }
    
    session_ids = [s.id for s in open_sessions]
    balances = {}
    alerts = []
    
    # Initialize balances for each currency
    for currency in currency_codes:
        balances[currency] = {
            "currency": currency,
            "initial": 0.0,
            "sales": 0.0,
            "expenses": 0.0,
            "net_balance": 0.0
        }
    
    # 1. Get initial cash from open sessions
    for session in open_sessions:
        # Check if session has multi-currency support
        if session.currencies:
            for curr in session.currencies:
                if curr.currency_symbol in balances:
                    balances[curr.currency_symbol]["initial"] += curr.initial_amount
        else:
            # Fallback to old dual-currency model
            balances["USD"]["initial"] += session.initial_cash or 0
            if "Bs" in balances:
                balances["Bs"]["initial"] += session.initial_cash_bs or 0
    
    # 2. Get sales income from SalePayment (exclude voided sales)
    voided_sale_ids = db.query(models.Return.sale_id).distinct().all()
    voided_sale_ids = [sid[0] for sid in voided_sale_ids]
    
    sales_query = db.query(
        models.SalePayment.currency,
        func.sum(models.SalePayment.amount).label('total')
    ).join(models.Sale).filter(
        models.Sale.date >= open_sessions[0].start_time  # Since first session opened
    )
    
    if voided_sale_ids:
        sales_query = sales_query.filter(models.Sale.id.notin_(voided_sale_ids))
    
    sales_by_currency = sales_query.group_by(models.SalePayment.currency).all()
    
    for currency, total in sales_by_currency:
        if currency in balances:
            balances[currency]["sales"] += total
    
    # 3. Get cash movements (expenses, deposits, withdrawals, returns)
    movements = db.query(models.CashMovement).filter(
        models.CashMovement.session_id.in_(session_ids)
    ).all()
    
    for movement in movements:
        currency = movement.currency or "USD"
        if currency not in balances:
            continue
            
        if movement.type == "DEPOSIT":
            # Deposits are income
            balances[currency]["sales"] += movement.amount
        elif movement.type in ["EXPENSE", "WITHDRAWAL"]:
            # Expenses and withdrawals reduce cash
            balances[currency]["expenses"] -= movement.amount
        elif movement.type == "RETURN":
            # Returns are refunds (reduce cash)
            balances[currency]["expenses"] -= movement.amount
    
    # 4. Calculate net balance and check for alerts
    for currency_code, data in balances.items():
        data["net_balance"] = data["initial"] + data["sales"] + data["expenses"]
        
        # Alert if negative balance
        if data["net_balance"] < 0:
            alerts.append(f"⚠️ Caja en {currency_code} tiene saldo negativo: {data['net_balance']:.2f} (Revisar)")
        
        # Round values
        data["initial"] = round(data["initial"], 2)
        data["sales"] = round(data["sales"], 2)
        data["expenses"] = round(data["expenses"], 2)
        data["net_balance"] = round(data["net_balance"], 2)
    
    # Convert to list and filter out currencies with no activity
    balance_list = [data for data in balances.values() if data["initial"] != 0 or data["sales"] != 0 or data["expenses"] != 0]
    
    # If no activity, show at least USD
    if not balance_list:
        balance_list = [balances["USD"]]
    
    return {
        "balances": balance_list,
        "alerts": alerts if alerts else []
    }

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
