from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Importamos tus módulos existentes
from .models import models
from .database.db import engine
from .routers import (
    products, customers, quotes, cash, suppliers, 
    inventory, returns, reports, purchases, users, 
    config, auth, categories, websocket
)

# Crear tablas (si no existen)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ferreteria API", version="2.0.0")

# --- MIDDLEWARES ---
@app.middleware("http")
async def log_requests(request, call_next):
    # Log simple para ver tráfico en consola
    # print(f"📡 {request.method} {request.url}") 
    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API ROUTERS (Prefijo /api/v1) ---
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

# --- STARTUP EVENTS ---
@app.on_event("startup")
def startup_event():
    from .database.db import SessionLocal
    from .routers.auth import init_admin_user
    from .routers.config import init_exchange_rates
    db = SessionLocal()
    try:
        init_admin_user(db)
        init_exchange_rates(db)
        print("✅ Inicialización de sistema completa")
    except Exception as e:
        print(f"⚠️ Error en inicialización: {e}")
    finally:
        db.close()

# --- SERVIR FRONTEND REACT (MODO HÍBRIDO) ---
# Buscamos la carpeta 'dist' subiendo 2 niveles desde este archivo
current_dir = os.path.dirname(os.path.abspath(__file__))
# Ajuste de ruta: backend_api -> ferreteria_refactor -> frontend_web -> dist
frontend_dist = os.path.join(current_dir, "..", "frontend_web", "dist")

if os.path.exists(frontend_dist):
    print(f"🖥️  Frontend detectado en: {frontend_dist}")
    
    # 1. Montar assets estáticos (JS, CSS, Imágenes)
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    # 2. Ruta raíz y Catch-All para React Router (SPA)
    # Cualquier ruta que NO sea /api/... será manejada por React
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            # Dejar pasar errores 404 de API reales
            return {"error": "Endpoint not found"}
        
        # Servir index.html para todo lo demás (Dashboard, Login, etc)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    print(f"⚠️ AVISO: No se encontró carpeta 'dist' en {frontend_dist}")
    print("   El sistema funcionará solo como API Backend.")

@app.get("/")
def read_root():
    # Si existe el frontend, esta ruta será sobreescrita por el catch-all de arriba,
    # pero si no existe, mostramos este mensaje.
    return {"message": "Ferreteria API Running (Frontend not found)"}