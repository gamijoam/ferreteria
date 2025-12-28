from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..config import settings

# Hybrid Database Support
# If DB_TYPE is 'sqlite' or DATABASE_URL contains 'sqlite', we adapt.
import os

DB_TYPE = os.getenv("DB_TYPE", "postgres")
DATABASE_URL = settings.DATABASE_URL

if DB_TYPE == "sqlite" or "sqlite" in str(DATABASE_URL):
    # Desktop App Mode
    if DB_TYPE == "sqlite":
        db_name = os.getenv("SQLITE_DB_NAME", "ferreteria.db")
        DATABASE_URL = f"sqlite:///./{db_name}"
        
    connect_args = {"check_same_thread": False}
    pool_config = {} # SQLite doesn't use the same pool config as Postgres
else:
    # VPS/Docker Mode (Postgres)
    connect_args = {}
    pool_config = {
        "pool_size": 20,        # Mantener 20 conexiones listas
        "max_overflow": 10,     # Permitir 10 extra en picos
        "pool_timeout": 30,     # Esperar 30s antes de dar error
        "pool_recycle": 1800,   # Reciclar conexiones cada 30 min
        "pool_pre_ping": True   # Verificar conexión antes de usarla
    }

engine = create_engine(
    DATABASE_URL,
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
