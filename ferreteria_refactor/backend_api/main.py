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

# --- ROUTERS ---
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

# --- SERVIR FRONTEND REACT (MODO HÍBRIDO CON DEBUG) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# Calculamos la ruta base subiendo un nivel
base_path = os.path.abspath(os.path.join(current_dir, ".."))
frontend_dist = os.path.join(base_path, "frontend_web", "dist")

# IMPRIMIMOS EL DIAGNÓSTICO EN CONSOLA
print("\n" + "="*40)
print("🔍 DIAGNÓSTICO DE RUTAS DE FRONTEND")
print("="*40)
print(f"1. Archivo main.py en: {current_dir}")
print(f"2. Base del proyecto:   {base_path}")
print(f"3. Buscando 'dist' en:  {frontend_dist}")

if os.path.exists(frontend_dist):
    print(f"✅ ¡CARPETA ENCONTRADA!")
    try:
        contenido = os.listdir(frontend_dist)
        print(f"   Contenido: {contenido}")
    except:
        print("   (No se pudo leer contenido)")

    # Montar assets
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    # Catch-all para React
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # Si es una llamada a la API, dejarla pasar (retornar 404 de API si no existe)
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi"):
            return {"error": "Endpoint not found"}
        # Para todo lo demás, devolver index.html
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
    return {
        "message": "Ferreteria API Running",
        "debug_info": {
            "frontend_found": os.path.exists(frontend_dist),
            "searched_path": frontend_dist,
            "base_path_content": os.listdir(base_path) if os.path.exists(base_path) else "Error reading base"
        }
    }