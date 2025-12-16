from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..database.db import get_db
from ..models import models
from .. import schemas

router = APIRouter(
    prefix="/config",
    tags=["config"]
)

# =============================================================================================
# Helper endpoint for Exchange Rate - MOVED UP
# =============================================================================================
@router.get("/exchange-rate/current")
def get_exchange_rate(db: Session = Depends(get_db)):
    """Get current exchange rate"""
    config = db.query(models.BusinessConfig).get("exchange_rate")
    if not config:
        return {"rate": 1.0}
    try:
        return {"rate": float(config.value)}
    except (ValueError, TypeError):
        return {"rate": 1.0}

# =============================================================================================
# Currencies endpoints - MOVED UP
# =============================================================================================
@router.get("/currencies")
def get_currencies(db: Session = Depends(get_db)):
    """Get all available currencies"""
    try:
        # Currency model doesn't have is_active, return all
        currencies = db.query(models.Currency).all()
        return [{"id": 0, "code": c.code, "name": c.name, "symbol": c.symbol} for c in currencies]
    except Exception as e:
        # Fallback if Currency table doesn't exist
        return [
            {"id": 1, "code": "USD", "name": "Dólar Estadounidense", "symbol": "$"},
            {"id": 2, "code": "VES", "name": "Bolívar", "symbol": "Bs"},
            {"id": 3, "code": "EUR", "name": "Euro", "symbol": "€"}
        ]

# =============================================================================================
# Exchange Rates endpoints - MOVED UP
# =============================================================================================
@router.get("/exchange-rates")
def get_exchange_rates(db: Session = Depends(get_db)):
    """Get all exchange rates"""
    try:
        rates = db.query(models.ExchangeRate).all()
        return [{
            "id": r.id,
            "name": r.name,
            "currency_code": r.currency_code,
            "rate": r.rate,
            "is_active": r.is_active,
            "created_at": r.created_at.isoformat() if hasattr(r, 'created_at') else None
        } for r in rates]
    except Exception as e:
        print(f"Error getting exchange rates: {e}")
        return []

@router.post("/exchange-rates")
def create_exchange_rate(rate_data: dict, db: Session = Depends(get_db)):
    """Create new exchange rate"""
    try:
        new_rate = models.ExchangeRate(**rate_data)
        db.add(new_rate)
        db.commit()
        db.refresh(new_rate)
        return {
            "id": new_rate.id,
            "name": new_rate.name,
            "currency_code": new_rate.currency_code,
            "rate": new_rate.rate,
            "is_active": new_rate.is_active
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/exchange-rates/{rate_id}")
def update_exchange_rate(rate_id: int, rate_data: dict, db: Session = Depends(get_db)):
    """Update exchange rate"""
    try:
        rate = db.query(models.ExchangeRate).filter(models.ExchangeRate.id == rate_id).first()
        if not rate:
            raise HTTPException(status_code=404, detail="Exchange rate not found")
        
        for key, value in rate_data.items():
            setattr(rate, key, value)
        
        db.commit()
        db.refresh(rate)
        return {
            "id": rate.id,
            "name": rate.name,
            "currency_code": rate.currency_code,
            "rate": rate.rate,
            "is_active": rate.is_active
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/exchange-rates/{rate_id}")
def delete_exchange_rate(rate_id: int, db: Session = Depends(get_db)):
    """Delete exchange rate (soft delete)"""
    try:
        rate = db.query(models.ExchangeRate).filter(models.ExchangeRate.id == rate_id).first()
        if not rate:
            raise HTTPException(status_code=404, detail="Exchange rate not found")
        
        rate.is_active = False
        db.commit()
        return {"status": "success", "message": "Exchange rate deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================================================
# General Config Endpoints - MOVED TO BOTTOM (GENERIC ROUTES LAST)
# =============================================================================================

@router.get("/", response_model=List[schemas.BusinessConfigRead])
def get_all_configs(db: Session = Depends(get_db)):
    """Get all configuration entries"""
    return db.query(models.BusinessConfig).all()

@router.get("/dict", response_model=Dict[str, Any])
def get_all_configs_dict(db: Session = Depends(get_db)):
    """Get all configuration as a dictionary"""
    configs = db.query(models.BusinessConfig).all()
    return {c.key: c.value for c in configs}

@router.post("/batch")
def set_configs_batch(configs: Dict[str, str], db: Session = Depends(get_db)):
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

# GENERIC CATCH-ALL ROUTE MUST BE LAST
@router.get("/{key}", response_model=schemas.BusinessConfigRead)
def get_config(key: str, db: Session = Depends(get_db)):
    """Get specific configuration key"""
    config = db.query(models.BusinessConfig).get(key)
    if not config:
        # Return a dummy config object instead of 404 to suppress errors
        return models.BusinessConfig(key=key, value="")
    return config

@router.put("/{key}", response_model=schemas.BusinessConfigRead)
def set_config(key: str, config_data: schemas.BusinessConfigCreate, db: Session = Depends(get_db)):
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
