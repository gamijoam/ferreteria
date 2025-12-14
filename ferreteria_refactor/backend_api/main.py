from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import models
from .database.db import engine
from .routers import products, customers, quotes, cash, suppliers, inventory, returns

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ferreteria API", version="1.0.0")

# CORS setup (Allow all for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")
app.include_router(quotes.router, prefix="/api/v1")
app.include_router(cash.router, prefix="/api/v1")
app.include_router(suppliers.router, prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")
app.include_router(returns.router, prefix="/api/v1")
