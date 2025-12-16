"""
Initialization script for Currency and ExchangeRate tables.
This module is called during application startup to populate
the database with base currencies and default exchange rates.
"""

from sqlalchemy.orm import Session
from ..models.models import Currency, ExchangeRate
import datetime


def init_currencies(db: Session):
    """Initialize base currencies if they don't exist"""
    
    # Check if currencies already exist
    existing_count = db.query(Currency).count()
    if existing_count > 0:
        print(f"[OK] Currencies already initialized ({existing_count} found)")
        return
    
    print("[INIT] Initializing currencies...")
    
    # Create base currencies
    currencies = [
        Currency(code="USD", name="Dólar Estadounidense", symbol="$"),
        Currency(code="VES", name="Bolívar Venezolano", symbol="Bs"),
    ]
    
    for currency in currencies:
        db.add(currency)
    
    db.commit()
    print(f"[OK] Created {len(currencies)} currencies: USD, VES")


def init_exchange_rates(db: Session):
    """Initialize default exchange rates if they don't exist"""
    
    # Check if rates already exist
    existing_count = db.query(ExchangeRate).count()
    if existing_count > 0:
        print(f"[OK] Exchange rates already initialized ({existing_count} found)")
        return
    
    print("[INIT] Initializing exchange rates...")
    
    # Create default exchange rates for VES
    rates = [
        ExchangeRate(
            name="Tasa BCV",
            currency_code="VES",
            rate=45.00,
            is_active=True,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        ),
        ExchangeRate(
            name="Tasa Monitor/Paralelo",
            currency_code="VES",
            rate=50.00,
            is_active=True,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        ),
        ExchangeRate(
            name="Tasa Interna",
            currency_code="VES",
            rate=52.00,
            is_active=True,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        ),
    ]
    
    for rate in rates:
        db.add(rate)
    
    db.commit()
    print(f"[OK] Created {len(rates)} exchange rates: BCV (45.00), Monitor (50.00), Interna (52.00)")


def init_currency_system(db: Session):
    """Initialize complete currency system (currencies + exchange rates)"""
    print("\n" + "="*60)
    print("[CURRENCY] INITIALIZING MULTI-CURRENCY SYSTEM")
    print("="*60)
    
    try:
        init_currencies(db)
        init_exchange_rates(db)
        print("="*60)
        print("[OK] Multi-currency system initialized successfully!")
        print("="*60 + "\n")
    except Exception as e:
        print(f"[ERROR] Error initializing currency system: {e}")
        db.rollback()
        raise
