from fastapi import FastAPI
from .models import models
from .database.db import engine
from .routers import products

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ferreteria API Refactor", version="1.0.0")

app.include_router(products.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Ferreteria API Refactor"}
