from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database.db import get_db
from ..models import models
from .. import schemas

router = APIRouter(
    prefix="/suppliers",
    tags=["suppliers"]
)

@router.get("/", response_model=List[schemas.SupplierRead])
def read_suppliers(
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = True,
    q: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Supplier)
    
    if active_only:
        query = query.filter(models.Supplier.is_active == True)
        
    if q:
        search = f"%{q}%"
        query = query.filter(models.Supplier.name.ilike(search))
        
    return query.order_by(models.Supplier.name).offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.SupplierRead)
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):
    # Check duplicate name
    exists = db.query(models.Supplier).filter(models.Supplier.name.ilike(supplier.name)).first()
    if exists:
        raise HTTPException(status_code=400, detail="Supplier with this name already exists")
        
    db_supplier = models.Supplier(**supplier.model_dump())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@router.get("/{supplier_id}", response_model=schemas.SupplierRead)
def read_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@router.put("/{supplier_id}", response_model=schemas.SupplierRead)
def update_supplier(supplier_id: int, supplier_update: schemas.SupplierCreate, db: Session = Depends(get_db)):
    db_supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
        
    for key, value in supplier_update.model_dump(exclude_unset=True).items():
        setattr(db_supplier, key, value)
        
    db.commit()
    db.refresh(db_supplier)
    return db_supplier
