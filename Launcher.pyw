#!/usr/bin/env python3
import sys
import os
import traceback
import tempfile
import subprocess
from datetime import datetime

# --- CONFIGURACION DE LOGGING ---
# Detectamos si hay consola disponible
HAS_CONSOLE = True
try:
    if sys.stdout is None or not sys.stdout.isatty():
        HAS_CONSOLE = False
except AttributeError:
    HAS_CONSOLE = False

# Archivo de log siempre util para debug
LOG_PATH = os.path.join(tempfile.gettempdir(), "ferreteria_launcher.log")

def log(msg):
    """Escribe en consola si existe, y SIEMPRE al archivo de log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    
    # 1. Escribir en archivo (append)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except:
        pass # No podemos hacer nada si falla el log
        
    # 2. Escribir en consola si existe
    if HAS_CONSOLE:
        print(formatted)

# Redirigir sys.stdout/stderr solo si NO hay consola
if not HAS_CONSOLE:
    # Hack simple para capturar print() nativos si los hubiera
    # (aunque usaremos la funcion log())
    sys.stdout = open(LOG_PATH, "a", encoding="utf-8")
    sys.stderr = sys.stdout

log(f"{'='*50}")
log(f"LAUNCHER INICIADO")
log(f"CWD: {os.getcwd()}")
log(f"LOG PATH: {LOG_PATH}")
log(f"TIENE CONSOLA: {HAS_CONSOLE}")
log(f"{'='*50}")

# --- BLOQUE PRINCIPAL ---
try:
    log("Importando dependencias...")
    import webbrowser
    import time
    import tkinter as tk
    from tkinter import messagebox, simpledialog
    from pathlib import Path
    import uuid
    from jose import jwt, JWTError # Dependencia critica

    # Configuracion de Rutas
    try:
        BASE_DIR = Path(__file__).parent
    except NameError:
        BASE_DIR = Path(os.getcwd())
        
    # Ajuste para backend_api
    PACKAGE_NAME = "ferreteria_refactor"
    BACKEND_DIR = BASE_DIR / PACKAGE_NAME / "backend_api"
    
    # Fallback si estamos dentro de la carpeta
    if not BACKEND_DIR.exists():
         BACKEND_DIR = BASE_DIR / "backend_api"
         log(f" WARN: Backend dir ajustado a {BACKEND_DIR}")

    LICENSE_FILE = BASE_DIR / "license.key"
    APP_HOST = "127.0.0.1"
    APP_PORT = 8000
    
    # PUBLIC KEY
    PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0wnnOdeEW3b181oL2KC9
1lZFKhVOLPiohBL69d6qLSsYJNuv3SIVf6jD+khFZMgAXcIT87Bgov614SKk/IPN
Uip6zEUPWWsATQqIEsK0dchsgaHZYb0/fUOu7NK3Xi2PHvtUE66YgKYEbBbxVlXW
ocGWhyfgUBZWgboG8Ehhe0s/74SKSc+5n7DVKIHm6bwqRhzfANCdaD349sB9HS34
iPS2uot2kBNfNTCuLaxWMhDwvsyEVy75PqRiJj76cbD6PE1N/BRx4U2N8NIy4wyG
rRNtqsPUITYZVaFO/97jS4cLE0pbxxMENM3BzqAJiPL+59IPkyAk9JJDsMHbjXlj
TQIDAQAB
-----END PUBLIC KEY-----"""

    def get_machine_id():
        return str(uuid.getnode())

    def validate_license():
        log("Validando licencia...")
        if not LICENSE_FILE.exists():
            return False, "Archivo license.key no encontrado", None
        
        try:
            with open(LICENSE_FILE, 'r') as f:
                token = f.read().strip()
        except Exception as e:
            return False, f"Error leyendo: {e}", None
        
        try:
            payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
        except Exception as e:
            return False, f"Token invalido: {e}", None
            
        # Validar Hardware ID
        l_type = payload.get("type")
        if l_type == "FULL":
            hw_id = payload.get("hw_id")
            my_id = get_machine_id()
            if hw_id != my_id:
                return False, f"ID Hardware incorrecto ({hw_id} != {my_id})", None
                
        return True, "OK", payload

    def input_license_gui(error_msg):
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        
        mid = get_machine_id()
        key = simpledialog.askstring(
            "Activar Licencia", 
            f"Error: {error_msg}\n\nMachine ID: {mid}\n\nIngrese licencia:",
            parent=root
        )
        root.destroy()
        return key

    def save_license(key):
        try:
            with open(LICENSE_FILE, "w") as f:
                f.write(key.strip())
            return True
        except Exception as e:
            log(f"Error guardando licencia: {e}")
            return False

    def start_backend():
        log("Iniciando proceso Backend...")
        
        # Comando para uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn",
            f"{PACKAGE_NAME}.backend_api.main:app",
            "--host", APP_HOST,
            "--port", str(APP_PORT)
        ]
        
        log(f"Comando: {' '.join(cmd)}")
        
        # Entorno
        env = os.environ.copy()
        env["PYTHONPATH"] = str(BASE_DIR) + os.pathsep + env.get("PYTHONPATH", "")
        
        # IMPORTANTE: Si hay consola, que el backend herede stdout/stderr para ver errores
        # Si NO hay consola, redirigir a DEVNULL para evitar cierres, o al log
        stdout_dest = None if HAS_CONSOLE else subprocess.DEVNULL
        stderr_dest = None if HAS_CONSOLE else subprocess.DEVNULL
        
        process = subprocess.Popen(cmd, cwd=BASE_DIR, env=env, stdout=stdout_dest, stderr=stderr_dest)
        return process

    def git_update():
        """Intenta actualizar el repositorio."""
        log("Chequeando actualizaciones...")
        try:
            # Verificar si git esta instalado
            subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
            # Hacer git pull
            log("Ejecutando git pull...")
            result = subprocess.run(
                ["git", "pull"], 
                cwd=BASE_DIR,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                log(f"Git pull exitoso: {result.stdout}")
                if "Already up to date." not in result.stdout:
                    log("Actualizacion detectada. Reiniciando...")
                    # Reiniciar script
                    os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                log(f"Git pull fallo: {result.stderr}")
                
        except FileNotFoundError:
            log("Git no encontrado en PATH. Saltando actualizacion.")
        except Exception as e:
            log(f"Error en auto-update: {e}")

    def main():
        # 0. Auto-update
        git_update()

        # 1. Licencia
        ok, msg, _ = validate_license()
        if not ok:
            log(f"Licencia no valida: {msg}")
            new_key = input_license_gui(msg)
            if new_key and save_license(new_key):
                ok, msg, _ = validate_license()
                if not ok:
                    messagebox.showerror("Error", "Licencia invalida.")
                    return
            else:
                log("Usuario cancelo o fallo guardado.")
                return

        log("Licencia correcta. Arrancando servicios...")
        
        # 2. Start Backend
        proc = start_backend()
        
        # Check inmediato si murio
        try:
            code = proc.wait(timeout=2)
            # Si retorna, murio
            log(f"FATAL: El backend se cerro inmediatamente con codigo {code}")
            messagebox.showerror("Error Critico", f"El servidor backend fallo al iniciar.\nCodigo: {code}\n\nRevise la consola o launcher.log")
            return
        except subprocess.TimeoutExpired:
            log("Backend parece estar corriendo (Timeout de 2s superado)")
        
        # 3. Web
        time.sleep(3)
        url = f"http://{APP_HOST}:{APP_PORT}"
        log(f"Abriendo {url}")
        webbrowser.open(url)
        
        # 4. Wait loop
        try:
            log("Launcher esperando terminacion del backend...")
            proc.wait()
            log(f"Backend termino con codigo {proc.returncode}")
        except KeyboardInterrupt:
            log("Interrumpido por usuario")
            proc.terminate()

    if __name__ == "__main__":
        main()

except Exception as e:
    log(f"CRASH NO MANEJADO: {e}")
    traceback.print_exc()
    if not HAS_CONSOLE:
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Crash", f"Error fatal: {e}")
        except: pass
