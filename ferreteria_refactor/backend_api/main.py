from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .models import models
from .database.db import engine
from .routers import (
    products, customers, quotes, cash, suppliers, 
    inventory, returns, reports, purchases, users, 
    config, auth, categories, websocket
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ferreteria API", version="2.0.0")

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
app.include_router(reports.router, prefix="/api/v1")
app.include_router(purchases.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(config.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(websocket.router, prefix="/api/v1")

@app.on_event("startup")
def startup_event():
    from .database.db import SessionLocal
    from .routers.auth import init_admin_user
    from .routers.config import init_exchange_rates
    db = SessionLocal()
    try:
        init_admin_user(db)
        init_exchange_rates(db)
        print("✅ Inicialización completa")
    except Exception as e:
        print(f"⚠️ Error startup: {e}")
    finally:
        db.close()

# --- SERVIR FRONTEND ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# SUBIR SOLO UN NIVEL (CORREGIDO)
frontend_dist = os.path.join(current_dir, "..", "frontend_web", "dist")

if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        if full_path.startswith("api"):
            return {"error": "Endpoint not found"}
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    print(f"⚠️ NO SE ENCUENTRA EL FRONTEND EN: {frontend_dist}")

@app.get("/")
def read_root():
    return {"message": "API Running - Frontend not found"}