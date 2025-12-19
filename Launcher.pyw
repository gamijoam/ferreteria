#!/usr/bin/env python3
import sys
import os
import traceback
import tempfile
from datetime import datetime

# --- CONFIGURACION DE LOGGING ULTRA-ROBUSTA ---
# Usamos carpeta temporal para evitar problemas de permisos
LOG_PATH = os.path.join(tempfile.gettempdir(), "ferreteria_launcher.log")

def setup_logging():
    try:
        # Abrir archivo en modo append
        log_file = open(LOG_PATH, "a", encoding="utf-8")
        
        # Redirigir siempre, no solo si es None
        sys.stdout = log_file
        sys.stderr = log_file
        
        print(f"\n{'='*50}")
        print(f"LAUNCHER STARTED AT: {datetime.now()}")
        print(f"PYTHON EXECUTABLE: {sys.executable}")
        print(f"CWD: {os.getcwd()}")
        print(f"LOG FILE: {LOG_PATH}")
        print(f"{'='*50}\n")
        return log_file
    except Exception as e:
        # Si falla configurar log, intentar mostrar error visual como ultimo recurso
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error Fatal", f"No se pudo iniciar el logging:\n{e}")
        except:
            pass
        sys.exit(1)

# Iniciar logging inmediatamente
log_file = setup_logging()

# --- BLOQUE PRINCIPAL PROTEGIDO ---
try:
    print("[*] Iniciando importaciones...")
    import subprocess
    import webbrowser
    import time
    import tkinter as tk
    from tkinter import messagebox, simpledialog
    from pathlib import Path
    import uuid
    
    # Imports externos que podrian fallar
    print("[*] Importando librerias externas...")
    try:
        from jose import jwt, JWTError
    except ImportError as e:
        print(f"[ERROR] Falta libreria 'python-jose': {e}")
        raise
    
    # --- CONFIGURACION ---
    try:
        BASE_DIR = Path(__file__).parent
    except NameError:
        BASE_DIR = Path(os.getcwd())
        
    LICENSE_FILE = BASE_DIR / "license.key"
    BACKEND_DIR = BASE_DIR / "ferreteria_refactor" / "backend_api" # Ajustar ruta segun estructura
    # Ajuste: Si backend_api esta en ferreteria_refactor/backend_api
    if not BACKEND_DIR.exists():
        # Intentar ruta alternativa
        BACKEND_DIR = BASE_DIR / "backend_api"
        
    APP_HOST = "127.0.0.1"
    APP_PORT = 8000
    PACKAGE_NAME = "ferreteria_refactor"

    print(f"[*] BASE_DIR: {BASE_DIR}")
    print(f"[*] LICENSE_FILE: {LICENSE_FILE}")
    print(f"[*] BACKEND_DIR: {BACKEND_DIR}")

    # Clave publica RSA
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
        print("[*] Validando licencia...")
        if not LICENSE_FILE.exists():
            print("   -> No existe archivo licencia")
            return False, "No se encontro archivo de licencia", None
        
        try:
            with open(LICENSE_FILE, 'r') as f:
                token = f.read().strip()
        except Exception as e:
            print(f"   -> Error lectura: {e}")
            return False, f"Error al leer licencia: {str(e)}", None
        
        try:
            payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
        except JWTError as e:
            print(f"   -> Error JWT: {e}")
            return False, f"Licencia invalida: {str(e)}", None
        
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            exp_date = datetime.fromtimestamp(exp_timestamp)
            if datetime.utcnow() > exp_date:
                print("   -> Licencia expirada")
                return False, f"Licencia expirada el {exp_date.strftime('%Y-%m-%d')}", None
        
        license_type = payload.get("type", "FULL")
        if license_type == "FULL":
            license_hw_id = payload.get("hw_id")
            current_hw_id = get_machine_id()
            if license_hw_id and license_hw_id != current_hw_id:
                print(f"   -> HW Mismatch: {license_hw_id} != {current_hw_id}")
                return False, "Esta licencia no es valida para este equipo", None
        
        print("   -> Licencia OK")
        return True, "Licencia valida", payload

    def save_license(license_key):
        try:
            print(f"[*] Guardando licencia en {LICENSE_FILE}")
            with open(LICENSE_FILE, 'w') as f:
                f.write(license_key.strip())
            return True
        except Exception as e:
            print(f"[ERROR] Guardando licencia: {e}")
            messagebox.showerror("Error", f"No se pudo guardar la licencia:\n{str(e)}")
            return False

    def check_license():
        valid, message, payload = validate_license()
        
        if not valid:
            print(f"[!] Licencia invalida: {message}")
            root = tk.Tk()
            root.withdraw() 
            
            machine_id = get_machine_id()
            msg = (
                f"No se detecto una licencia valida.\n"
                f"Error: {message}\n\n"
                f"Machine ID: {machine_id}\n\n"
                f"Ingrese su código:"
            )
            
            # Asegurar que el dialogo modal aparezca encima
            root.attributes("-topmost", True)
            license_key = simpledialog.askstring(
                "Activacion Requerida", 
                msg, 
                parent=root
            )
            
            if license_key:
                license_key = license_key.strip()
                if save_license(license_key):
                    valid, message, payload = validate_license()
                    if valid:
                        messagebox.showinfo("Exito", "Licencia activada correctamente.")
                        root.destroy()
                        return 
                    else:
                        messagebox.showerror("Error", f"La licencia no es valida:\n{message}")
                        root.destroy()
                        sys.exit(1)
                else:
                    root.destroy()
                    sys.exit(1)
            else:
                root.destroy()
                sys.exit(1)

    def start_backend():
        print("[*] Iniciando Backend...")
        
        # Detectar rutas correctas
        backend_module = f"{PACKAGE_NAME}.backend_api.main:app"
        
        # Verificar si existe el paquete ferreteria_refactor en CWD
        possible_pkg = BASE_DIR / PACKAGE_NAME
        if not possible_pkg.exists():
            print(f"[WARN] No se encuentra {possible_pkg}, intentando ajustar PYTHONPATH")
        
        env = os.environ.copy()
        env["PYTHONPATH"] = str(BASE_DIR) + os.pathsep + env.get("PYTHONPATH", "")
        
        cmd = [
            sys.executable, "-m", "uvicorn", 
            backend_module,
            "--host", APP_HOST, 
            "--port", str(APP_PORT)
        ]
        
        print(f"   CMD: {' '.join(cmd)}")
        
        # IMPORTANTE: No usar subprocess.PIPE si queremos ver output en el log global
        # Usamos sys.stdout que ya esta redirigido al archivo
        process = subprocess.Popen(
            cmd,
            cwd=BASE_DIR,
            env=env,
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        return process

    def main():
        print("[*] Entrando a main()")
        check_license()
        
        server_process = start_backend()
        
        print("[*] Esperando 5s para abrir navegador...")
        time.sleep(5)
        url = f"http://{APP_HOST}:{APP_PORT}"
        print(f"[*] Abriendo navegador: {url}")
        webbrowser.open(url)
        
        try:
            print("[*] Launcher corriendo. Presione Ctrl+C en consola o cierre ventana para salir.")
            server_process.wait()
        except KeyboardInterrupt:
            print("[*] Interrupcion de teclado. Cerrando...")
            server_process.terminate()

    if __name__ == "__main__":
        main()

except Exception as e:
    print(f"\n{'#'*50}")
    print("FATAL ERROR NO MANEJADO:")
    print(f"{e}")
    traceback.print_exc()
    print(f"{'#'*50}\n")
    
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error Fatal en Launcher", f"Ocurrio un error critico:\n{e}\n\nRevise el log en:\n{LOG_PATH}")
    except:
        pass
    
    sys.exit(1)
finally:
    if 'log_file' in locals() and log_file:
        log_file.close()
