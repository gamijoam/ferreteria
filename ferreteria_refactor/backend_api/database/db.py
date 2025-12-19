from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..config import settings

# Configuración inteligente: Si es SQLite usa una config, si es Postgres usa Pool
connect_args = {}
pool_config = {}

if "sqlite" in settings.DATABASE_URL:
    connect_args = {"check_same_thread": False}
else:
    # CONFIGURACIÓN PROD PARA POSTGRESQL
    pool_config = {
        "pool_size": 20,        # Mantener 20 conexiones listas
        "max_overflow": 10,     # Permitir 10 extra en picos
        "pool_timeout": 30,     # Esperar 30s antes de dar error
        "pool_recycle": 1800,   # Reciclar conexiones cada 30 min
        "pool_pre_ping": True   # Verificar conexión antes de usarla
    }

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **pool_config
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
