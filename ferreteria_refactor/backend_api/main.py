from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import models
from .database.db import engine
from .routers import products, customers, quotes, cash, suppliers, inventory, returns, reports, purchases, users, config, auth

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ferreteria API", version="1.0.0")

@app.middleware("http")
async def log_requests(request, call_next):
    import sys
    print(f"[REQUEST] {request.method} {request.url}")
    auth = request.headers.get("Authorization", "None")
    print(f"[AUTH] HEADER AUTH: {auth[:20]}..." if auth else "[AUTH] HEADER AUTH: Missing")
    
    response = await call_next(request)
    print(f"[RESPONSE] STATUS: {response.status_code}")
    return response

# CORS setup (Allow all for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/api/v1")
# Sales endpoints are inside products router currently
app.include_router(customers.router, prefix="/api/v1")
app.include_router(quotes.router, prefix="/api/v1")
app.include_router(cash.router, prefix="/api/v1")
app.include_router(suppliers.router, prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")
app.include_router(returns.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(purchases.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(config.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")

@app.on_event("startup")
def startup_event():
    from .database.db import SessionLocal
    from .routers.auth import init_admin_user
    from .database.init_currencies import init_currency_system
    
    db = SessionLocal()
    try:
        init_admin_user(db)
        init_currency_system(db)  # Initialize multi-currency system
    except Exception as e:
        print(f"[ERROR] Error during startup initialization: {e}")
    finally:
        db.close()
