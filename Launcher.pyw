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
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvvRgZK4BaGKv0t270yQb
baE3rNTL7Uy6JbRjPqU8L4m3qQRdgSCSlMFEE/nIRpxqSlDeTRPMHtaYH53rAfuo
kUrUxxTwiU2aFvRhdd9WHo9HGzmutboeQIJny6ReLp9TOrS/rGdIkMd4A8gEDWWZ
gjhhZlUxoJZHdINu42wqi9WBpXQrbcTc0jkAnpZisjzs9+Pxp5TiDm9vOl4BEGbf
/uo88o2DUwvB8OSn1T74mt3uN7JbKf4TBWtMmJoHFLuMe35MLO5tkUsyWW7v5ogs
ILvS1VdBdvWNOsZdpA8L/k78e2UG7ppkg0YiXbBFtLsxpYMb6Q6bQ09AVgfXvgFO
MwIDAQAB
-----END PUBLIC KEY-----"""

    def get_machine_id():
        return str(uuid.getnode())

    def validate_license():
        log("Validando licencia...")
        
        # 1. Verificar existencia
        if not LICENSE_FILE.exists():
            log("   -> Archivo license.key no encontrado.")
            return False, "Archivo license.key no encontrado", None
        
        # 2. Leer archivo
        try:
            with open(LICENSE_FILE, 'r') as f:
                token = f.read().strip()
            log(f"   -> Token leido: {token[:15]}...") 
        except Exception as e:
            log(f"   -> Error leyendo licencia: {e}")
            return False, f"Error leyendo archivo: {e}", None
        
        # 3. Decodificar JWT (Verifica firma y estructura)
        try:
            # IMPORTANTE: python-jose verifica 'exp' automaticamente por defecto.
            # Sin embargo, agregamos logs para depuracion manual.
            payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
            log("   -> Firma JWT valida.")
        except jwt.ExpiredSignatureError:
            log("   -> ERROR: Token expirado (detectado por libreria).")
            return False, "Licencia expirada.", None
        except Exception as e:
            log(f"   -> Error decodificando JWT: {e}")
            return False, f"Token invalido: {e}", None
            
        # 4. Verificacion Manual de Expiracion (Doble chequeo UTC)
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            # Convertir timestamp (que es UTC) a objeto datetime UTC
            exp_date = datetime.utcfromtimestamp(exp_timestamp)
            now_utc = datetime.utcnow()
            
            log(f"   -> Expiracion (UTC): {exp_date}")
            log(f"   -> Actual (UTC):     {now_utc}")
            
            if now_utc > exp_date:
                log("   -> ERROR: Licencia expirada (Chequeo manual).")
                return False, f"Licencia expirada el {exp_date.strftime('%Y-%m-%d %H:%M:%S')} UTC", None
            else:
                days = (exp_date - now_utc).days
                log(f"   -> Validez OK. Dias restantes: {days}")
                
        # 5. Validar Hardware ID (Solo FULL)
        l_type = payload.get("type", "UNKNOWN")
        log(f"   -> Tipo Licencia: {l_type}")
        
        if l_type == "FULL":
            hw_id = payload.get("hw_id")
            my_id = get_machine_id()
            log(f"   -> HW Check: Licencia={hw_id} vs Maquina={my_id}")
            
            if hw_id != my_id:
                log("   -> ERROR: Hardware Mismatch")
                return False, f"Hardware ID invalido. Licencia para: {hw_id}, Esta PC: {my_id}", None
                
        log("   -> Licencia TOTALMENTE VALIDA.")
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

    def start_hardware_bridge():
        """Inicia el Hardware Bridge para impresora térmica y cajón."""
        log("Iniciando Hardware Bridge...")
        
        # Verificar que existe el archivo
        bridge_file = BASE_DIR / "hardware_bridge.py"
        if not bridge_file.exists():
            log(f"   -> WARN: hardware_bridge.py no encontrado en {bridge_file}")
            log("   -> Impresión térmica NO estará disponible")
            return None
        
        # Comando para ejecutar hardware_bridge
        cmd = [sys.executable, str(bridge_file)]
        
        log(f"Comando: {' '.join(cmd)}")
        
        # Entorno
        env = os.environ.copy()
        env["PYTHONPATH"] = str(BASE_DIR) + os.pathsep + env.get("PYTHONPATH", "")
        
        # Redirigir salida según disponibilidad de consola
        stdout_dest = None if HAS_CONSOLE else subprocess.DEVNULL
        stderr_dest = None if HAS_CONSOLE else subprocess.DEVNULL
        
        try:
            process = subprocess.Popen(
                cmd, 
                cwd=BASE_DIR, 
                env=env, 
                stdout=stdout_dest, 
                stderr=stderr_dest
            )
            log(f"   -> Hardware Bridge iniciado (PID: {process.pid})")
            return process
        except Exception as e:
            log(f"   -> ERROR iniciando Hardware Bridge: {e}")
            log("   -> Impresión térmica NO estará disponible")
            return None

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
        backend_proc = start_backend()
        
        # Check inmediato si murio
        try:
            code = backend_proc.wait(timeout=2)
            # Si retorna, murio
            log(f"FATAL: El backend se cerro inmediatamente con codigo {code}")
            messagebox.showerror("Error Critico", f"El servidor backend fallo al iniciar.\nCodigo: {code}\n\nRevise la consola o launcher.log")
            return
        except subprocess.TimeoutExpired:
            log("Backend parece estar corriendo (Timeout de 2s superado)")
        
        # 2.5. Start Hardware Bridge (opcional, no bloquea si falla)
        bridge_proc = start_hardware_bridge()
        
        # 3. Web
        time.sleep(3)
        url = f"http://{APP_HOST}:{APP_PORT}"
        log(f"Abriendo {url}")
        webbrowser.open(url)
        
        # 4. Wait loop
        try:
            log("Launcher esperando terminacion del backend...")
            backend_proc.wait()
            log(f"Backend termino con codigo {backend_proc.returncode}")
        except KeyboardInterrupt:
            log("Interrumpido por usuario")
            backend_proc.terminate()
            if bridge_proc:
                log("Terminando Hardware Bridge...")
                bridge_proc.terminate()
        finally:
            # Asegurar que ambos procesos terminen
            if bridge_proc and bridge_proc.poll() is None:
                log("Cerrando Hardware Bridge...")
                bridge_proc.terminate()

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
