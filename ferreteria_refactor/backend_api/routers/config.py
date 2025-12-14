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

@router.get("/", response_model=List[schemas.BusinessConfigRead])
def get_all_configs(db: Session = Depends(get_db)):
    """Get all configuration entries"""
    return db.query(models.BusinessConfig).all()

@router.get("/dict", response_model=Dict[str, Any])
def get_all_configs_dict(db: Session = Depends(get_db)):
    """Get all configuration as a dictionary"""
    configs = db.query(models.BusinessConfig).all()
    return {c.key: c.value for c in configs}

@router.get("/{key}", response_model=schemas.BusinessConfigRead)
def get_config(key: str, db: Session = Depends(get_db)):
    """Get specific configuration key"""
    config = db.query(models.BusinessConfig).get(key)
    if not config:
        # Return default or 404? 
        # Return 404 to be safe
        raise HTTPException(status_code=404, detail="Config key not found")
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

# Helper endpoint for Exchange Rate
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
