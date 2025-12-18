import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

# --- CONFIGURACIÓN ---
# Cambia esto por la URL de tu repositorio real
REPO_URL = "https://github.com/gamijoam/ferreteria.git" 
BRANCH = "main"
APP_HOST = "127.0.0.1"
APP_PORT = 8000

# Nombre de la carpeta del paquete python (donde está backend_api)
PACKAGE_NAME = "ferreteria_refactor"

def git_update():
    """Intenta actualizar el código usando Git"""
    if not os.path.exists(".git"):
        print("⚠️ No se detectó repositorio Git. Omitiendo actualización.")
        return

    print("🔄 Buscando actualizaciones en la nube...")
    try:
        # Fetch: Traer info sin tocar nada
        subprocess.run(["git", "fetch", "origin", BRANCH], check=True, timeout=15)
        
        # Reset Hard: Forzar que el código local sea idéntico a la nube
        # ¡OJO! Esto borra cambios locales no guardados (ideal para clientes)
        subprocess.run(["git", "reset", "--hard", f"origin/{BRANCH}"], check=True, timeout=15)
        print("✅ Sistema actualizado a la última versión.")
    except Exception as e:
        print(f"⚠️ No se pudo actualizar (¿Sin internet?): {e}")
        print("   Iniciando versión actual...")

def start_backend():
    """Inicia el servidor Uvicorn"""
    print(f"🚀 Iniciando servidor en http://{APP_HOST}:{APP_PORT}...")
    
    # Comando: python -m uvicorn ferreteria_refactor.backend_api.main:app
    cmd = [
        sys.executable, "-m", "uvicorn", 
        f"{PACKAGE_NAME}.backend_api.main:app", 
        "--host", APP_HOST, 
        "--port", str(APP_PORT)
    ]
    
    # En Windows, usamos flags para ocultar la ventana negra si ejecutamos pyw
    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = subprocess.CREATE_NO_WINDOW

    # Lanzamos el proceso
    process = subprocess.Popen(
        cmd,
        cwd=os.path.dirname(os.path.abspath(__file__)), # Ejecutar desde la raíz
        creationflags=creation_flags
    )
    return process

def main():
    # 1. Intentar Auto-Update
    git_update()
    
    # 2. Iniciar el Backend (+ Frontend servido)
    server_process = start_backend()
    
    # 3. Esperar un momento a que el servidor arranque
    print("⏳ Esperando arranque del sistema...")
    time.sleep(4)
    
    # 4. Abrir el navegador del cliente
    url = f"http://{APP_HOST}:{APP_PORT}"
    print(f"🌍 Abriendo {url}")
    webbrowser.open(url)
    
    # 5. Mantener el script vivo mientras el servidor funcione
    try:
        server_process.wait()
    except KeyboardInterrupt:
        print("🛑 Deteniendo servidor...")
        server_process.terminate()

if __name__ == "__main__":
    main()