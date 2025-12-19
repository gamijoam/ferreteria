#!/usr/bin/env python3
import sys
import os
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from datetime import datetime
import traceback

# --- CONFIGURACION DE LOGGING (CRITICO: ANTES DE TODO) ---
try:
    BASE_DIR = Path(__file__).parent
except NameError:
    BASE_DIR = Path(os.getcwd())

LOG_FILE = BASE_DIR / "launcher.log"

# Redirigir stdout/stderr a archivo si no hay consola (doble click)
if sys.stdout is None or sys.stderr is None:
    sys.stdout = open(LOG_FILE, "a")
    sys.stderr = open(LOG_FILE, "a")

print(f"\n--- Launcher Iniciado: {datetime.now()} ---")
print(f"CWD: {os.getcwd()}")

# --- IMPORTACIONES PROTEGIDAS ---
try:
    import subprocess
    import webbrowser
    import time
    from tkinter import simpledialog
    from jose import jwt, JWTError
    import uuid
except ImportError as e:
    print(f"FATAL ERROR: Falta una dependencia: {e}")
    traceback.print_exc()
    # Intentar mostrar error grafico
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error Fatal", f"Faltan dependencias:\n{e}\n\nConsulte launcher.log")
    except:
        pass
    sys.exit(1)
except Exception as e:
    print(f"FATAL ERROR en imports: {e}")
    traceback.print_exc()
    sys.exit(1)

# --- CONFIGURACION ---
REPO_URL = "https://github.com/gamijoam/ferreteria.git" 
BRANCH = "main"
APP_HOST = "127.0.0.1"
APP_PORT = 8000
PACKAGE_NAME = "ferreteria_refactor"

# --- CONFIGURACION DE LICENCIAS ---
LICENSE_FILE = BASE_DIR / "license.key"

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
    """Obtiene el ID de hardware de la maquina."""
    return str(uuid.getnode())

def validate_license():
    """Valida la licencia JWT."""
    print("Validando licencia...")
    if not LICENSE_FILE.exists():
        print("No existe archivo de licencia")
        return False, "No se encontro archivo de licencia", None
    
    try:
        with open(LICENSE_FILE, 'r') as f:
            token = f.read().strip()
    except Exception as e:
        print(f"Error leyendo licencia: {e}")
        return False, f"Error al leer licencia: {str(e)}", None
    
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
    except JWTError as e:
        print(f"Error decodificando JWT: {e}")
        return False, f"Licencia invalida: {str(e)}", None
    
    exp_timestamp = payload.get("exp")
    if exp_timestamp:
        exp_date = datetime.fromtimestamp(exp_timestamp)
        if datetime.utcnow() > exp_date:
            print("Licencia expirada")
            return False, f"Licencia expirada el {exp_date.strftime('%Y-%m-%d')}", None
    
    license_type = payload.get("type", "FULL")
    if license_type == "FULL":
        license_hw_id = payload.get("hw_id")
        current_hw_id = get_machine_id()
        if license_hw_id and license_hw_id != current_hw_id:
            print(f"Hardware mismatch: {license_hw_id} vs {current_hw_id}")
            return False, "Esta licencia no es valida para este equipo", None
    
    return True, "Licencia valida", payload

def save_license(license_key):
    """Guarda la licencia."""
    try:
        with open(LICENSE_FILE, 'w') as f:
            f.write(license_key.strip())
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar la licencia:\n{str(e)}")
        return False

def check_license():
    """Verifica la licencia con UI simplificada."""
    try:
        valid, message, payload = validate_license()
        
        if not valid:
            print(f"Licencia invalida: {message}")
            
            # UI Simplificada
            root = tk.Tk()
            root.withdraw() 
            
            machine_id = get_machine_id()
            msg = (
                f"No se detecto una licencia valida.\n"
                f"Error: {message}\n\n"
                f"Machine ID de este equipo: {machine_id}\n\n"
                f"Por favor, ingrese su codigo de licencia a continuacion:"
            )
            
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
                        messagebox.showerror("Error", f"La licencia ingresada no es valida:\n{message}")
                        root.destroy()
                        sys.exit(1)
                else:
                    root.destroy()
                    sys.exit(1)
            else:
                messagebox.showinfo(
                    "Cancelado",
                    f"Inicio cancelado.\n\n"
                    f"Si tiene problemas, puede crear manualmente 'license.key' "
                    f"en {BASE_DIR}."
                )
                root.destroy()
                sys.exit(1)

        print("Licencia OK")
    except Exception as e:
        print(f"Error en check_license: {e}")
        traceback.print_exc()
        messagebox.showerror("Error", f"Error verificando licencia: {e}\nRevise launcher.log")
        sys.exit(1)

def start_backend():
    """Inicia el servidor backend."""
    print(f"Iniciando servidor en http://{APP_HOST}:{APP_PORT}...")
    cmd = [
        sys.executable, "-m", "uvicorn", 
        f"{PACKAGE_NAME}.backend_api.main:app", 
        "--host", APP_HOST, 
        "--port", str(APP_PORT)
    ]
    
    # IMPORTANTE: En Windows sin consola, necesitamos PIPE o redirigir a archivo
    # Si pasamos stdout=sys.stdout y sys.stdout es un archivo, funciona.
    process = subprocess.Popen(
        cmd,
        cwd=BASE_DIR,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    return process

def main():
    try:
        check_license()
        
        server_process = start_backend()
        
        time.sleep(4)
        url = f"http://{APP_HOST}:{APP_PORT}"
        print(f"Abriendo navegador: {url}")
        webbrowser.open(url)
        
        try:
            server_process.wait()
        except KeyboardInterrupt:
            server_process.terminate()
            
    except Exception as e:
        print(f"Error FATAL en main: {e}")
        traceback.print_exc()
        try:
            messagebox.showerror("Error Fatal", f"Ocurrio un error inesperado:\n{str(e)}\nRevise launcher.log")
        except:
            pass

if __name__ == "__main__":
    main()
