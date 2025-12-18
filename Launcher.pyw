import os
import sys
import subprocess
import time
import webbrowser
import tkinter as tk
from tkinter import messagebox, simpledialog
from pathlib import Path
from jose import jwt, JWTError
from datetime import datetime
import uuid

# --- CONFIGURACION ---
REPO_URL = "https://github.com/gamijoam/ferreteria.git" 
BRANCH = "main"
APP_HOST = "127.0.0.1"
APP_PORT = 8000
PACKAGE_NAME = "ferreteria_refactor"

# --- CONFIGURACION DE LICENCIAS ---
try:
    BASE_DIR = Path(__file__).parent
except NameError:
    BASE_DIR = Path(os.getcwd())

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
    if not LICENSE_FILE.exists():
        return False, "No se encontro archivo de licencia", None
    
    try:
        with open(LICENSE_FILE, 'r') as f:
            token = f.read().strip()
    except Exception as e:
        return False, f"Error al leer licencia: {str(e)}", None
    
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
    except JWTError as e:
        return False, f"Licencia invalida: {str(e)}", None
    
    exp_timestamp = payload.get("exp")
    if exp_timestamp:
        exp_date = datetime.fromtimestamp(exp_timestamp)
        if datetime.utcnow() > exp_date:
            return False, f"Licencia expirada el {exp_date.strftime('%Y-%m-%d')}", None
    
    license_type = payload.get("type", "FULL")
    if license_type == "FULL":
        license_hw_id = payload.get("hw_id")
        current_hw_id = get_machine_id()
        if license_hw_id and license_hw_id != current_hw_id:
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
    print("Verificando licencia...")
    valid, message, payload = validate_license()
    
    if not valid:
        print(f"Licencia invalida: {message}")
        print(f"Machine ID: {get_machine_id()}")
        
        # UI Simplificada
        root = tk.Tk()
        root.withdraw() # Ocultar ventana principal
        
        machine_id = get_machine_id()
        msg = (
            f"No se detecto una licencia valida.\n"
            f"Error: {message}\n\n"
            f"Machine ID de este equipo: {machine_id}\n\n"
            f"Por favor, ingrese su codigo de licencia a continuacion:"
        )
        
        # Usar simpledialog que es mas robusto
        license_key = simpledialog.askstring(
            "Activacion Requerida", 
            msg, 
            parent=root
        )
        
        if license_key:
            # Intentar activar
            license_key = license_key.strip()
            # Guardar temporalmente para validar
            if save_license(license_key):
                valid, message, payload = validate_license()
                if valid:
                    messagebox.showinfo("Exito", "Licencia activada correctamente.")
                    return # Exito
                else:
                    messagebox.showerror("Error", f"La licencia ingresada no es valida:\n{message}")
                    sys.exit(1)
            else:
                sys.exit(1)
        else:
            # Usuario cancelo
            # Ultimo recurso: Instrucciones manuales
            messagebox.showinfo(
                "Cancelado",
                f"Inicio cancelado.\n\n"
                f"Si tiene problemas, puede crear manualmente un archivo llamado 'license.key' "
                f"en la carpeta {BASE_DIR} y pegar su licencia dentro."
            )
            sys.exit(1)

    # Si llegamos aqui, la licencia es valida
    print("Licencia valida.")

def start_backend():
    """Inicia el servidor backend."""
    print(f"Iniciando servidor en http://{APP_HOST}:{APP_PORT}...")
    cmd = [
        sys.executable, "-m", "uvicorn", 
        f"{PACKAGE_NAME}.backend_api.main:app", 
        "--host", APP_HOST, 
        "--port", str(APP_PORT)
    ]
    # Creation flags para ocultar consola si es posible
    process = subprocess.Popen(
        cmd,
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    return process

def main():
    try:
        check_license()
        
        # git_update() # Desactivado
        
        server_process = start_backend()
        
        time.sleep(4)
        url = f"http://{APP_HOST}:{APP_PORT}"
        webbrowser.open(url)
        
        try:
            server_process.wait()
        except KeyboardInterrupt:
            server_process.terminate()
            
    except Exception as e:
        # Catch-all para errores
        try:
            messagebox.showerror("Error Fatal", f"Ocurrio un error inesperado:\n{str(e)}")
        except:
            print(f"Error fatal: {e}")

if __name__ == "__main__":
    main()
