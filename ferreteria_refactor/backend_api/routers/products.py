from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database.db import get_db
from ..models import models
from .. import schemas
from ..dependencies import has_role, get_current_active_user
from ..models.models import UserRole

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[schemas.ProductRead])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(models.Product).options(joinedload(models.Product.units)).filter(models.Product.is_active == True).offset(skip).limit(limit).all()
    return products

@router.post("/", response_model=schemas.ProductRead, dependencies=[Depends(has_role([UserRole.ADMIN, UserRole.WAREHOUSE]))])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    # Exclude 'units' from the main Product creation
    product_data = product.dict(exclude={"units"})
    db_product = models.Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Process Units
    if product.units:
        for unit in product.units:
            db_unit = models.ProductUnit(**unit.dict(), product_id=db_product.id)
            db.add(db_unit)
        db.commit()
        db.refresh(db_product)
        
    return db_product

@router.put("/{product_id}", response_model=schemas.ProductRead)
def update_product(product_id: int, product_update: schemas.ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update main fields
    update_data = product_update.dict(exclude_unset=True)
    
    # Separate units data if present
    units_data = None
    if "units" in update_data:
        units_data = update_data.pop("units")

    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    # Handle Units Update (Snapshot Strategy: Delete all old, create new)
    if units_data is not None:
        # Delete existing units
        db.query(models.ProductUnit).filter(models.ProductUnit.product_id == product_id).delete()
        
        # Add new units
        for unit in units_data:
            # We use unit (dict) from the popped data
            # Note: unit is already a dict if we used .dict(), or we might need to handle Pydantic objects if we didn't
            # update_data comes from product_update.dict(), so 'units' is a list of dicts.
            db_unit = models.ProductUnit(**unit, product_id=product_id)
            db.add(db_unit)

    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/{product_id}/rules", response_model=List[schemas.PriceRuleRead])
def read_price_rules(product_id: int, db: Session = Depends(get_db)):
    rules = db.query(models.PriceRule).filter(models.PriceRule.product_id == product_id).order_by(models.PriceRule.min_quantity).all()
    return rules

@router.post("/{product_id}/rules", response_model=schemas.PriceRuleRead)
def create_price_rule(product_id: int, rule: schemas.PriceRuleCreate, db: Session = Depends(get_db)):
    db_rule = models.PriceRule(**rule.dict())
    db_rule.product_id = product_id # Override with path param
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@router.delete("/rules/{rule_id}")
def delete_price_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(models.PriceRule).filter(models.PriceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"status": "success"}

@router.post("/sales/")
def create_sale(sale_data: schemas.SaleCreate, db: Session = Depends(get_db)):
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    # Credit Validation for Credit Sales
    if sale_data.is_credit and sale_data.customer_id:
        customer = db.query(models.Customer).filter(models.Customer.id == sale_data.customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # 1. Check if customer is blocked
        if customer.is_blocked:
            raise HTTPException(
                status_code=400,
                detail=f"Cliente '{customer.name}' está bloqueado por mora. No se pueden realizar ventas a crédito."
            )
        
        # 2. Check for overdue invoices
        overdue_count = db.query(models.Sale).filter(
            models.Sale.customer_id == sale_data.customer_id,
            models.Sale.is_credit == True,
            models.Sale.paid == False,
            models.Sale.due_date < datetime.now()
        ).count()
        
        if overdue_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cliente tiene {overdue_count} factura(s) vencida(s). Debe ponerse al día antes de nuevas ventas a crédito."
            )
        
        # 3. Check credit limit
        current_debt = db.query(func.sum(models.Sale.balance_pending)).filter(
            models.Sale.customer_id == sale_data.customer_id,
            models.Sale.is_credit == True,
            models.Sale.paid == False
        ).scalar() or 0.0
        
        if (current_debt + sale_data.total_amount) > customer.credit_limit:
            raise HTTPException(
                status_code=400,
                detail=f"Excede límite de crédito. Deuda actual: ${current_debt:.2f}, Límite: ${customer.credit_limit:.2f}, Disponible: ${(customer.credit_limit - current_debt):.2f}"
            )
    
    # 1. Create Sale Header
    total_bs = sale_data.total_amount * sale_data.exchange_rate
    
    # Calculate due date for credit sales
    due_date = None
    balance_pending = None
    if sale_data.is_credit and sale_data.customer_id:
        customer = db.query(models.Customer).filter(models.Customer.id == sale_data.customer_id).first()
        if customer:
            due_date = datetime.now() + timedelta(days=customer.payment_term_days)
            balance_pending = sale_data.total_amount
    
    new_sale = models.Sale(
        total_amount=sale_data.total_amount,
        payment_method=sale_data.payment_method,
        customer_id=sale_data.customer_id,
        is_credit=sale_data.is_credit,
        paid=not sale_data.is_credit, 
        currency=sale_data.currency,
        exchange_rate_used=sale_data.exchange_rate,
        total_amount_bs=total_bs,
        notes=sale_data.notes,
        due_date=due_date,
        balance_pending=balance_pending
    )
    db.add(new_sale)
    db.flush() # Get ID

    # 2. Process Items
    for item in sale_data.items:
        # Fetch Product
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        # Calculate base units to deduct using conversion_factor
        # item.quantity = how many of THIS unit (e.g., 2 Kilos)
        # item.conversion_factor = how many base units per unit (e.g., 1 Kilo = 1kg)
        # units_to_deduct = 2 * 1 = 2kg from stock
        units_to_deduct = item.quantity * item.conversion_factor
        
        # Check Stock
        if product.stock < units_to_deduct:
             raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")

        # Calculate subtotal (before discount)
        subtotal = item.unit_price_usd * item.quantity
        
        # Apply discount if any
        if item.discount > 0:
            if item.discount_type == "PERCENT":
                subtotal = subtotal * (1 - item.discount / 100)
            elif item.discount_type == "FIXED":
                subtotal = subtotal - item.discount
        
        # Create Sale Detail
        detail = models.SaleDetail(
            sale_id=new_sale.id,
            product_id=product.id,
            quantity=units_to_deduct,  # Store base units deducted
            unit_price=item.unit_price_usd,  # Store the price per unit sold
            subtotal=subtotal,
            is_box_sale=False,  # Deprecated, keeping for compatibility
            discount=item.discount,
            discount_type=item.discount_type
        )
        db.add(detail)

        # Update Stock
        product.stock -= units_to_deduct
        
        # Register Kardex Movement
        kardex_entry = models.Kardex(
            product_id=product.id,
            movement_type="SALE",
            quantity=-units_to_deduct,  # Negative for outgoing
            balance_after=product.stock,
            description=f"Sale #{new_sale.id}: Sold {item.quantity} units at ${item.unit_price_usd} each"
        )
        db.add(kardex_entry)

    # 3. Process Payments (New Multi-Payment Logic)
    if sale_data.payments:
        for p in sale_data.payments:
            new_payment = models.SalePayment(
                sale_id=new_sale.id,
                amount=p.amount,
                currency=p.currency,
                payment_method=p.payment_method,
                exchange_rate=p.exchange_rate
            )
            db.add(new_payment)
    else:
        # Fallback for legacy calls or single payment
        fallback_payment = models.SalePayment(
            sale_id=new_sale.id,
            amount=sale_data.total_amount,
            currency=sale_data.currency,
            payment_method=sale_data.payment_method,
            exchange_rate=sale_data.exchange_rate
        )
        db.add(fallback_payment)

    db.commit()
    return {"status": "success", "sale_id": new_sale.id}

@router.post("/sales/payments")
def register_sale_payment(
    payment_data: schemas.SalePaymentCreate,
    db: Session = Depends(get_db)
):
    """Register a payment (abono) for a credit sale"""
    # Verify sale exists
    sale = db.query(models.Sale).filter(models.Sale.id == payment_data.sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    # Create SalePayment record
    payment = models.SalePayment(
        sale_id=payment_data.sale_id,
        amount=payment_data.amount,
        currency=payment_data.currency,
        payment_method=payment_data.payment_method,
        exchange_rate=payment_data.exchange_rate
    )
    db.add(payment)
    db.commit()
    
    return {"status": "success", "payment_id": payment.id}

@router.put("/sales/{sale_id}")
def update_sale(
    sale_id: int,
    balance_pending: float = None,
    paid: bool = None,
    db: Session = Depends(get_db)
):
    """Update sale balance and paid status"""
    print(f"🔄 UPDATE SALE {sale_id}: balance_pending={balance_pending}, paid={paid}")
    
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    print(f"   Before: paid={sale.paid}, balance={sale.balance_pending}")
    
    if balance_pending is not None:
        sale.balance_pending = balance_pending
    
    if paid is not None:
        sale.paid = paid
    
    db.commit()
    db.refresh(sale)
    
    print(f"   After: paid={sale.paid}, balance={sale.balance_pending}")
    
    return {"status": "success", "sale": sale}

@router.post("/bulk", response_model=schemas.BulkImportResult)
def bulk_create_products(products: List[schemas.ProductCreate], db: Session = Depends(get_db)):
    # Initialize result using Pydantic model
    result = schemas.BulkImportResult(success_count=0, failed_count=0, errors=[])
    
    for p in products:
        try:
            # Use nested transaction (savepoint) to isolate each insertion
            with db.begin_nested():
                # Check for existing SKU to avoid generic IntegrityError if possible (optimization)
                # But begin_nested handles it safely.
                # db_product = models.Product(**p.dict()) 
                # p.dict() might invoke validations.
                
                # Manual mapping or dict unpacking
                db_product = models.Product(
                    name=p.name,
                    sku=p.sku,
                    price=p.price,
                    cost_price=p.cost_price,
                    stock=p.stock,
                    description=p.description,
                    min_stock=p.min_stock,
                    is_box=p.is_box,
                    conversion_factor=p.conversion_factor,
                    category_id=p.category_id,
                    supplier_id=p.supplier_id,
                    is_active=True # Default true for imports
                )
                db.add(db_product)
                db.flush() # Force SQL execution to catch constraints
            
            result.success_count += 1
        except Exception as e:
            result.failed_count += 1
            msg = str(e)
            if "UNIQUE constraint failed" in msg or "Duplicate entry" in msg:
                msg = f"SKU '{p.sku}' ya existe."
            result.errors.append(f"Producto '{p.name}': {msg}")
            
    db.commit()
    return result
