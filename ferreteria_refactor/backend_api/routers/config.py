from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..database.db import get_db
from ..models import models
from .. import schemas
from ..dependencies import admin_only

router = APIRouter(
    prefix="/config",
    tags=["config"]
)

# ========================================
# EXCHANGE RATE MANAGEMENT (NEW SYSTEM)
# ========================================

@router.get("/exchange-rates", response_model=List[schemas.ExchangeRateRead])
def get_exchange_rates(
    currency_code: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """Get all exchange rates, optionally filtered by currency or active status"""
    query = db.query(models.ExchangeRate)
    
    if currency_code:
        query = query.filter(models.ExchangeRate.currency_code == currency_code)
    if is_active is not None:
        query = query.filter(models.ExchangeRate.is_active == is_active)
    
    return query.order_by(models.ExchangeRate.currency_code, models.ExchangeRate.is_default.desc()).all()


@router.post("/exchange-rates", response_model=schemas.ExchangeRateRead)
def create_exchange_rate(
    rate_data: schemas.ExchangeRateCreate,
    db: Session = Depends(get_db),
    user: Any = Depends(admin_only)  # Protect mutation
):
    """Create a new exchange rate"""
    # Validate: If is_default=True, unset other defaults for same currency
    if rate_data.is_default:
        db.query(models.ExchangeRate).filter(
            models.ExchangeRate.currency_code == rate_data.currency_code,
            models.ExchangeRate.is_default == True
        ).update({"is_default": False})
    
    new_rate = models.ExchangeRate(**rate_data.dict())
    db.add(new_rate)
    db.commit()
    db.refresh(new_rate)
    return new_rate


@router.get("/exchange-rates/{id}", response_model=schemas.ExchangeRateRead)
def get_exchange_rate_by_id(id: int, db: Session = Depends(get_db)):
    """Get a specific exchange rate by ID"""
    rate = db.query(models.ExchangeRate).get(id)
    if not rate:
        raise HTTPException(status_code=404, detail="Exchange rate not found")
    return rate


@router.put("/exchange-rates/{id}", response_model=schemas.ExchangeRateRead)
def update_exchange_rate(
    id: int,
    rate_data: schemas.ExchangeRateUpdate,
    db: Session = Depends(get_db),
    user: Any = Depends(admin_only)  # Protect mutation
):
    """Update an exchange rate"""
    rate = db.query(models.ExchangeRate).get(id)
    if not rate:
        raise HTTPException(status_code=404, detail="Exchange rate not found")
    
    # Handle default flag
    if rate_data.is_default is not None and rate_data.is_default and not rate.is_default:
        # Unset other defaults for same currency
        db.query(models.ExchangeRate).filter(
            models.ExchangeRate.currency_code == rate.currency_code,
            models.ExchangeRate.id != id
        ).update({"is_default": False})
    
    # Update fields
    for key, value in rate_data.dict(exclude_unset=True).items():
        setattr(rate, key, value)
    
    db.commit()
    db.refresh(rate)
    return rate


@router.delete("/exchange-rates/{id}")
def delete_exchange_rate(
    id: int,
    db: Session = Depends(get_db),
    user: Any = Depends(admin_only)  # Protect mutation
):
    """Soft delete (deactivate) an exchange rate"""
    rate = db.query(models.ExchangeRate).get(id)
    if not rate:
        raise HTTPException(status_code=404, detail="Exchange rate not found")
    
    if rate.is_default:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete default rate. Set another rate as default first."
        )
    
    rate.is_active = False
    db.commit()
    return {"message": "Exchange rate deactivated successfully"}

# ========================================
# BUSINESS CONFIGURATION (GENERIC)
# ========================================

@router.get("/", response_model=List[schemas.BusinessConfigRead])
def get_all_configs(db: Session = Depends(get_db)):
    """Get all configuration entries"""
    return db.query(models.BusinessConfig).all()

@router.get("/dict", response_model=Dict[str, Any])
def get_all_configs_dict(db: Session = Depends(get_db)):
    """Get all configuration as a dictionary"""
    configs = db.query(models.BusinessConfig).all()
    return {c.key: c.value for c in configs}

# Helper endpoint for Legacy Exchange Rate compatibility
@router.get("/exchange-rate/current")
def get_legacy_exchange_rate(db: Session = Depends(get_db)):
    """Get current legacy exchange rate"""
    config = db.query(models.BusinessConfig).get("exchange_rate")
    if not config:
        return {"rate": 1.0}
    try:
        return {"rate": float(config.value)}
    except (ValueError, TypeError):
        return {"rate": 1.0}

# Currency Management Endpoints

@router.get("/currencies")
def get_currencies(db: Session = Depends(get_db)):
    """Get all currencies"""
    data = db.query(models.Currency).all()
    print(f"DEBUG: Returning {len(data)} currencies")
    return data

@router.post("/currencies", response_model=schemas.CurrencyRead)
def create_currency(currency: schemas.CurrencyCreate, db: Session = Depends(get_db)):
    """Create a new currency"""
    # If this is anchor, unset others
    if currency.is_anchor:
        db.query(models.Currency).update({models.Currency.is_anchor: False})
    
    db_currency = models.Currency(**currency.dict())
    db.add(db_currency)
    db.commit()
    db.refresh(db_currency)
    return db_currency

@router.put("/currencies/{currency_id}", response_model=schemas.CurrencyRead)
def update_currency(currency_id: int, currency: schemas.CurrencyUpdate, db: Session = Depends(get_db)):
    """Update a currency"""
    db_currency = db.query(models.Currency).get(currency_id)
    if not db_currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    
    update_data = currency.dict(exclude_unset=True)
    
    # If setting to anchor, unset others
    if update_data.get("is_anchor"):
        db.query(models.Currency).update({models.Currency.is_anchor: False})
        
    for key, value in update_data.items():
        setattr(db_currency, key, value)
        
    db.commit()
    db.refresh(db_currency)
    return db_currency

@router.delete("/currencies/{currency_id}")
def delete_currency(currency_id: int, db: Session = Depends(get_db)):
    """Delete a currency"""
    db_currency = db.query(models.Currency).get(currency_id)
    if not db_currency:
        raise HTTPException(status_code=404, detail="Currency not found")
        
    db.delete(db_currency)
    db.commit()
    return {"message": f"Deleted config key: {currency_id}"}


@router.get("/{key}", response_model=schemas.BusinessConfigRead)
def get_config(key: str, db: Session = Depends(get_db)):
    """Get specific configuration key"""
    config = db.query(models.BusinessConfig).get(key)
    if not config:
        # Return a dummy config object instead of 404 to suppress errors
        return models.BusinessConfig(key=key, value="")
    return config

@router.put("/{key}", response_model=schemas.BusinessConfigRead)
def set_config(
    key: str, 
    config_data: schemas.BusinessConfigCreate, 
    db: Session = Depends(get_db),
    user: Any = Depends(admin_only)  # Protect mutation
):
    """Set configuration value"""
    config = db.query(models.BusinessConfig).get(key)
    if not config:
        config = models.BusinessConfig(key=key, value=config_data.value)
        db.add(config)
    else:
        config.value = config_data.value
    
    db.commit()
    db.refresh(config)
    return config

@router.post("/batch")
def set_configs_batch(
    configs: Dict[str, str], 
    db: Session = Depends(get_db),
    user: Any = Depends(admin_only)  # Protect mutation
):
    """Set multiple configuration values at once"""
    results = {}
    for key, value in configs.items():
        config = db.query(models.BusinessConfig).get(key)
        if not config:
            config = models.BusinessConfig(key=key, value=str(value))
            db.add(config)
        else:
            config.value = str(value)
        results[key] = value
    
    db.commit()
    return {"message": "Configurations updated", "data": results}

def init_exchange_rates(db: Session):
    """Seed default exchange rates if table is empty"""
    existing_count = db.query(models.ExchangeRate).count()
    
    if existing_count > 0:
        print(f"✅ Exchange rates already seeded ({existing_count} rates found)")
        return
    
    print("🌱 Seeding default exchange rates...")
    
    default_rates = [
        models.ExchangeRate(
            name="USD Default",
            currency_code="USD",
            currency_symbol="$",
            rate=1.00,
            is_default=True,
            is_active=True
        ),
        models.ExchangeRate(
            name="BCV",
            currency_code="VES",
            currency_symbol="Bs",
            rate=45.00,
            is_default=True,
            is_active=True
        ),
        models.ExchangeRate(
            name="Paralelo",
            currency_code="VES",
            currency_symbol="Bs",
            rate=52.00,
            is_default=False,
            is_active=True
        ),
        models.ExchangeRate(
            name="TRM",
            currency_code="COP",
            currency_symbol="COP",
            rate=4200.00,
            is_default=True,
            is_active=True
        ),
        models.ExchangeRate(
            name="Euro",
            currency_code="EUR",
            currency_symbol="€",
            rate=0.92,
            is_default=True,
            is_active=False
        ),
    ]
    
    for rate in default_rates:
        db.add(rate)
    
    db.commit()
    print(f"✅ Seeded {len(default_rates)} default exchange rates")

def init_currencies(db: Session):
    """Seed default currencies if table is empty"""
    if db.query(models.Currency).first():
        return
    
    currencies = [
        {"name": "Dólar Americano", "symbol": "USD", "rate": 1.00, "is_anchor": True, "is_active": True},
        {"name": "Bolívar Venezolano", "symbol": "VES", "rate": 60.00, "is_anchor": False, "is_active": True},
        {"name": "Peso Colombiano", "symbol": "COP", "rate": 4200.00, "is_anchor": False, "is_active": True},
        {"name": "Euro", "symbol": "EUR", "rate": 1.10, "is_anchor": False, "is_active": False},
        {"name": "Peso Argentino", "symbol": "ARS", "rate": 1000.00, "is_anchor": False, "is_active": False},
        {"name": "Peso Mexicano", "symbol": "MXN", "rate": 17.00, "is_anchor": False, "is_active": False},
        {"name": "Sol Peruano", "symbol": "PEN", "rate": 3.70, "is_anchor": False, "is_active": False},
    ]
    
    for curr in currencies:
        db_curr = models.Currency(**curr)
        db.add(db_curr)
    
    db.commit()
    print("✅ Currencies seeded successfully")

@router.get("/debug/seed")
def debug_seed_currencies(db: Session = Depends(get_db)):
    """Force seed check and return status"""
    count_before = db.query(models.Currency).count()
    init_currencies(db)
    count_after = db.query(models.Currency).count()
    # Also return the actual data to see what the API sees
    data = db.query(models.Currency).all()
    return {
        "count_before": count_before,
        "count_after": count_after,
        "seeded": count_after > count_before,
        "data": data
    }
