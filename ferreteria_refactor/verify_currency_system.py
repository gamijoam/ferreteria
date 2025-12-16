from ferreteria_refactor.backend_api.database.db import SessionLocal, engine
from ferreteria_refactor.backend_api.models.models import Currency, ExchangeRate, Base

# Create tables if they don't exist (just in case)
Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    print("--- VERIFICACIÓN DE BASE DE DATOS ---")
    
    # Check Currencies
    currencies = db.query(Currency).all()
    print(f"\nMonedas encontradas ({len(currencies)}):")
    for c in currencies:
        print(f" - {c.code}: {c.name} ({c.symbol})")
        
    if len(currencies) == 0:
        print("⚠️  ALERTA: No hay monedas en la base de datos.")
    
    # Check Exchange Rates
    rates = db.query(ExchangeRate).all()
    print(f"\nTasas encontradas ({len(rates)}):")
    for r in rates:
        print(f" - {r.name}: {r.rate} (Base: {r.currency_code}) Active={r.is_active}")

finally:
    db.close()
