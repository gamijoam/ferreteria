from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
import sys

# --- DIAGNÓSTICO DE INICIO ---
print("🔍 Verificando entorno Python...", flush=True)
try:
    import aiofiles
    print("✅ aiofiles está instalado y disponible.", flush=True)
except ImportError as e:
    print(f"❌ ERROR CRÍTICO: aiofiles NO está instalado: {e}", flush=True)

from .models import models
from .database.db import engine
from .routers import (
    products, customers, quotes, cash, suppliers, 
    inventory, returns, reports, purchases, users, 
    config, auth, categories, websocket, audit, system
)
from .routers.hardware_bridge import router as hardware_bridge_router  # WebSocket router
from .middleware.license_guard import LicenseGuardMiddleware

app = FastAPI(
    title="Ferretería Enterprise API",
    description="API profesional para la gestión integral de ferretería.",
    version="2.2.0",
)

from .config import settings

@app.on_event("startup")
async def startup_event_async():
    print("\n" + "="*60)
    print("🚀 FERRETERÍA API INICIADA (Modo Docker SaaS v2)")
    print("="*60 + "\n")

# --- SEGURIDAD HÍBRIDA (License Guard) ---
if not os.getenv("DOCKER_CONTAINER"):
    # Modo Local (PC Cliente)
    app.add_middleware(LicenseGuardMiddleware)
    print("🔒 MODO LOCAL: License Guard ACTIVADO")
else:
    # Modo SaaS (VPS)
    print("☁️ MODO SAAS: License Guard DESACTIVADO (Gestión Centralizada)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTERS API (Prioridad Alta) ---
app.include_router(products, prefix="/api/v1", tags=["Inventario"])
app.include_router(customers, prefix="/api/v1", tags=["Clientes"])
app.include_router(quotes, prefix="/api/v1", tags=["Presupuestos"])
app.include_router(cash, prefix="/api/v1", tags=["Caja"])
app.include_router(suppliers, prefix="/api/v1", tags=["Proveedores"])
app.include_router(inventory, prefix="/api/v1", tags=["Inventario (Operaciones)"])
app.include_router(returns, prefix="/api/v1", tags=["Devoluciones"])
app.include_router(reports, prefix="/api/v1", tags=["Reportes"])
app.include_router(purchases, prefix="/api/v1", tags=["Compras"])
app.include_router(users, prefix="/api/v1", tags=["Usuarios"])
app.include_router(config, prefix="/api/v1", tags=["Configuración"])
app.include_router(auth, prefix="/api/v1", tags=["Autenticación"])
app.include_router(categories, prefix="/api/v1", tags=["Categorías"])
app.include_router(websocket, prefix="/api/v1", tags=["WebSocket Events"])
app.include_router(audit, prefix="/api/v1", tags=["Auditoría"])
app.include_router(system, prefix="/api/v1", tags=["Sistema y Licencias"])
app.include_router(hardware_bridge_router, prefix="/api/v1", tags=["Hardware Bridge"])

# --- LÓGICA DE INICIALIZACIÓN ---
def run_migrations():
    from alembic import command
    from alembic.config import Config
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        alembic_ini_path = os.path.join(base_dir, "alembic.ini")
        if os.path.exists(alembic_ini_path):
            alembic_cfg = Config(alembic_ini_path)
            alembic_cfg.set_main_option("script_location", os.path.join(base_dir, "alembic"))
            command.upgrade(alembic_cfg, "head")
            print("✅ Migraciones aplicadas correctamente.")
    except Exception as e:
        print(f"⚠️ Nota sobre migraciones: {e}")

@app.on_event("startup")
def startup_event():
    run_migrations()
    try:
        from .database.db import Base
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"⚠️ Error verificando tablas: {e}")

    # Seed Data
    from .database.db import SessionLocal
    from .routers.auth import init_admin_user
    from .routers.config import init_exchange_rates
    db = SessionLocal()
    try:
        init_admin_user(db)
        init_exchange_rates(db)
    except Exception as e:
        print(f"⚠️ Nota de Inicialización: {e}")
    finally:
        db.close()

# --- SERVIR FRONTEND (SPA) - CONFIGURACIÓN CRÍTICA ---
static_dir = "/app/static"

# Definimos la función de respuesta raíz explícitamente fuera del if para asegurar registro
async def serve_index():
    if os.path.exists(os.path.join(static_dir, "index.html")):
        return FileResponse(os.path.join(static_dir, "index.html"))
    return JSONResponse(status_code=404, content={"detail": "Frontend index.html not found"})

if os.path.exists(static_dir):
    print(f"📂 FRONTEND ENCONTRADO en: {static_dir}")
    
    # 1. Montar Assets
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    
    # 2. RUTA RAÍZ (Registrada explícitamente)
    app.add_api_route("/", serve_index, methods=["GET"], include_in_schema=False)

    # 3. Catch-All para React Router
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # 🛡️ ESCUDO DE API: Si la ruta empieza con 'api', devolver 404 JSON real
        if full_path.startswith("api"):
            return JSONResponse(status_code=404, content={"detail": "Endpoint not found"})

        file_path = os.path.join(static_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return await serve_index() # Fallback a index.html

else:
    print("⚠️ FRONTEND NO ENCONTRADO. Iniciando en modo API-Only.")
    @app.get("/")
    def root():
        return {"message": "Ferreteria API (Backend Only)"}