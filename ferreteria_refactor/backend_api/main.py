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
    config, auth, categories, websocket, audit, system
)
from .middleware.license_guard import LicenseGuardMiddleware

# models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ferretería Enterprise API",
    description="""API profesional para la gestión integral de ferretería.
    
    Módulos incluidos:
    * **Inventario**: Gestión de productos, SKUs, categorías y control de stock.
    * **Ventas (POS)**: Punto de venta con soporte de concurrencia, pagos múltiples y caja.
    * **Usuarios**: Control de acceso basado en roles (RBAC).
    * **Caja**: Apertura y cierre de sesiones de caja con auditoría.
    """,
    version="2.1.0",
    contact={
        "name": "Soporte Técnico",
        "email": "admin@ferreteria.local",
    },
)

from .config import settings

@app.on_event("startup")
async def startup_event():
    print("\n" + "="*60)
    print("🚀 FERRETERÍA API INICIADA")
    
    # Mostrar URL de base de datos (ocultando password)
    db_url = settings.DATABASE_URL
    safe_msg = ""
    
    if "sqlite" in db_url:
        safe_msg = f"SQLite: {db_url.replace('sqlite:///', '')}"
    elif "@" in db_url:
        try:
            safe_msg = f"PostgreSQL: {db_url.split('@')[1]}"
        except:
            safe_msg = db_url
    else:
        safe_msg = db_url
        
    print(f"📊 CONECTADO A BASE DE DATOS: {safe_msg}")
    
    # DEBUG: Print all routes
    print("\n🛣️ RUTAS REGISTRADAS:")
    for route in app.routes:
        if hasattr(route, "path"):
            print(f"  - {route.path} [{','.join(route.methods) if hasattr(route, 'methods') else ''}]")
            
    print("="*60 + "\n")

# License Guard Middleware (DEBE IR PRIMERO)
app.add_middleware(LicenseGuardMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTERS ---
app.include_router(products.router, prefix="/api/v1", tags=["Inventario"])
app.include_router(customers.router, prefix="/api/v1", tags=["Clientes"])
app.include_router(quotes.router, prefix="/api/v1", tags=["Presupuestos"])
app.include_router(cash.router, prefix="/api/v1", tags=["Caja"])
app.include_router(suppliers.router, prefix="/api/v1", tags=["Proveedores"])
app.include_router(inventory.router, prefix="/api/v1", tags=["Inventario (Operaciones)"])
app.include_router(returns.router, prefix="/api/v1", tags=["Devoluciones"])
app.include_router(reports.router, prefix="/api/v1", tags=["Reportes"])
app.include_router(purchases.router, prefix="/api/v1", tags=["Compras"])
app.include_router(users.router, prefix="/api/v1", tags=["Usuarios"])
app.include_router(config.router, prefix="/api/v1", tags=["Configuración"])
app.include_router(auth.router, prefix="/api/v1", tags=["Autenticación"])
app.include_router(categories.router, prefix="/api/v1", tags=["Categorías"])
app.include_router(websocket.router, prefix="/api/v1", tags=["WebSocket Events"])
app.include_router(audit.router, prefix="/api/v1", tags=["Auditoría"])
app.include_router(system.router, prefix="/api/v1", tags=["Sistema y Licencias"])

def run_migrations():
    """Run Alembic migrations programmatically on startup."""
    from alembic import command
    from alembic.config import Config
    
    print("🔄 Checking database migrations...")
    try:
        # Determine paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        alembic_ini_path = os.path.join(base_dir, "alembic.ini")
        
        if not os.path.exists(alembic_ini_path):
            print(f"⚠️ Warning: alembic.ini not found at {alembic_ini_path}. Skipping migrations.")
            return

        # Create Alembic configuration object
        alembic_cfg = Config(alembic_ini_path)
        # Ensure script location is absolute/correct relative to ini
        alembic_cfg.set_main_option("script_location", os.path.join(base_dir, "alembic"))
        
        # Run upgrade head
        command.upgrade(alembic_cfg, "head")
        print("✅ Database migrations applied successfully.")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        # Optional: raise e # Force crash if migration fails


@app.on_event("startup")
def startup_event():
    # 1. Run Migrations
    run_migrations()
    
    # 1.5 ENSURE ALL TABLES EXIST (for fresh databases)
    print("🔧 Ensuring all database tables exist...")
    try:
        from .database.db import Base
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables verified/created successfully.")
    except Exception as e:
        print(f"⚠️ Error ensuring tables: {e}")

    # 2. Existing startup items
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

# --- SERVIR FRONTEND REACT (MODO HÍBRIDO CON DEBUG) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# Calculamos la ruta base subiendo un nivel
base_path = os.path.abspath(os.path.join(current_dir, ".."))
frontend_dist = os.path.join(base_path, "frontend_web", "dist")

# IMPRIMIMOS EL DIAGNÓSTICO EN CONSOLA
print("\n" + "="*40)
print("DIAGNOSTICO DE RUTAS DE FRONTEND")
print("="*40)
print(f"1. Archivo main.py en: {current_dir}")
print(f"2. Base del proyecto:   {base_path}")
print(f"3. Buscando 'dist' en:  {frontend_dist}")

if os.path.exists(frontend_dist):
    print("CARPETA ENCONTRADA!")
    try:
        contenido = os.listdir(frontend_dist)
        print(f"   Contenido: {contenido}")
    except:
        print("   (No se pudo leer contenido)")

    # Montar assets (Intentar método estándar)
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    # Check what files are actually in assets
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        print(f"Archivos en assets detectados: {os.listdir(assets_dir)}")
    else:
        print("Carpeta assets no encontrada en dist!")

    # Catch-all para React
    from fastapi import Request
    from fastapi.responses import JSONResponse
    import mimetypes
    
    # Fix for Windows Registry MIME types issues
    mimetypes.init()
    mimetypes.add_type('application/javascript', '.js')
    mimetypes.add_type('text/css', '.css')

    @app.exception_handler(404)
    async def custom_404_handler(request: Request, exc):
        path = request.url.path
        
        # Debug logging (visible in console)
        if path.startswith("/assets"):
            print(f"404 Asset: {path} - Checking manually...")
            # Fallback manual para assets (por si StaticFiles falla)
            asset_filename = path.replace("/assets/", "")
            asset_path = os.path.join(frontend_dist, "assets", asset_filename)
            if os.path.exists(asset_path):
                print(f"   Asset encontrado manualmente: {asset_path}")
                media_type, _ = mimetypes.guess_type(asset_path)
                return FileResponse(asset_path, media_type=media_type)
            else:
                print(f"   Asset NO encontrado en disco: {asset_path}")
            
        # Si es una llamada a la API, retornar JSON 404 real
        if path.startswith("/api") or path.startswith("/docs") or path.startswith("/openapi"):
            return JSONResponse(status_code=404, content={"detail": "Endpoint not found"})
        
        # Para todo lo demás (SPA routing), devolver index.html
        return FileResponse(os.path.join(frontend_dist, "index.html"))

else:
    print("❌ CARPETA NO ENCONTRADA")
    print(f"   Intentando listar {base_path}:")
    try:
        print(f"   {os.listdir(base_path)}")
    except Exception as e:
        print(f"   Error listando directorio base: {e}")

print("="*40 + "\n")


@app.get("/")
def read_root():
    # Attempt to serve index.html if it exists
    index_path = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
        
    # Fallback to JSON if frontend is not built
    return {
        "message": "Ferreteria API Running (Frontend not found)",
        "debug_info": {
            "frontend_found": os.path.exists(frontend_dist),
            "searched_path": frontend_dist,
            "base_path_content": os.listdir(base_path) if os.path.exists(base_path) else "Error reading base"
        }
    }