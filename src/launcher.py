
import os
import sys
import json
import subprocess
import shutil
import zipfile
import time
import ctypes
import traceback

# Intenta importar requests, si falla, usaremos la app sin actualizar (Fail-Safe)
try:
    import requests
except ImportError:
    requests = None

# --- CONFIGURACIÓN ---
APP_DIR_NAME = "InventarioSoft"
MAIN_EXECUTABLE = "InventarioSoft.exe" 
VERSION_FILE = "version.json"
UPDATE_PKG_NAME = "update_ferreteria.zip"

def get_base_dir():
    """Retorna el directorio donde corre el ejecutable o script."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
APP_PATH = os.path.join(BASE_DIR, APP_DIR_NAME)
MAIN_APP_PATH = os.path.join(APP_PATH, MAIN_EXECUTABLE)
LOCAL_VERSION_PATH = os.path.join(BASE_DIR, VERSION_FILE)

def show_error(title, message):
    """Muestra un mensaje nativo de Windows (sin librerías pesadas)."""
    try:
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x10) # 0x10 = MB_ICONERROR
    except:
        print(f"[{title}] {message}")

def launch_main_app():
    """Lanza la aplicación principal e ignora este proceso."""
    if not os.path.exists(MAIN_APP_PATH):
        # Fallback: Intentar buscar en la raíz si la estructura cambió
        alt_path = os.path.join(BASE_DIR, MAIN_EXECUTABLE)
        if os.path.exists(alt_path):
            subprocess.Popen([alt_path], cwd=BASE_DIR)
            sys.exit(0)
        
        show_error("Error Fatal", f"No se encuentra la aplicación en:\n{MAIN_APP_PATH}")
        sys.exit(1)
    
    try:
        # Popen permite que el launcher se cierre y la app siga
        subprocess.Popen([MAIN_APP_PATH], cwd=APP_PATH)
        sys.exit(0)
    except Exception as e:
        show_error("Error de Lanzamiento", f"No se pudo iniciar la aplicación:\n{e}")
        # Intentar lanzar de todas formas por shell
        try:
            os.startfile(MAIN_APP_PATH)
        except:
            sys.exit(1)

def get_usb_drives():
    """Retorna una lista de letras de unidad disponibles (ej: ['D:\\', 'E:\\'])."""
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in range(65, 91):  # A-Z
        if bitmask & 1:
            drive_path = chr(letter) + ":\\"
            if drive_path != "C:\\": # Ignorar C:
                 drives.append(drive_path)
        bitmask >>= 1
    return drives

def load_local_version():
    try:
        if os.path.exists(LOCAL_VERSION_PATH):
            with open(LOCAL_VERSION_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {}

def update_from_zip(zip_path):
    """Extrae el ZIP y sobrescribe la app 'InventarioSoft'."""
    try:
        # Extraer en carpeta temporal primero
        temp_dir = os.path.join(BASE_DIR, "temp_update")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Mover archivos: Se espera que el ZIP contenga la carpeta 'InventarioSoft' o los archivos directos
        # Si tiene carpeta contenedora, identificarla.
        # Estrategia: Copiar todo contenido de temp_dir a BASE_DIR (mezclando/sobrescribiendo)
        
        # Detectar estructura del ZIP
        items = os.listdir(temp_dir)
        source_dir = temp_dir
        if len(items) == 1 and os.path.isdir(os.path.join(temp_dir, items[0])):
            # Si el zip tiene una carpeta raiz (ej: InventarioSoft/), entramos
            if items[0] == APP_DIR_NAME:
                source_dir = os.path.join(temp_dir, items[0])
                target_root = APP_PATH
            else:
                 # Caso genérico, asumimos que va a la raíz
                 pass

        # Copiar recursivamente (simulación de overwrite)
        # shutil.copytree(source_dir, APP_PATH, dirs_exist_ok=True) no está en Python < 3.8
        # Hacemos una copia manual robusta
        
        for root, dirs, files in os.walk(temp_dir):
            rel_path = os.path.relpath(root, temp_dir)
            dest_dir = os.path.join(BASE_DIR, rel_path)
            
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                
            for file in files:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest_dir, file)
                # Ignorar el propio zip si está ahí
                if file == UPDATE_PKG_NAME: 
                    continue
                    
                shutil.copy2(src_file, dest_file)

        # Limpieza
        shutil.rmtree(temp_dir)
        return True
    except Exception as e:
        print(f"Error actualizando: {e}")
        # No mostrar error crítico al usuario para no bloquear venta, loggear si es posible
        return False

def check_usb_update():
    """Busca update_ferreteria.zip en drives USB."""
    drives = get_usb_drives()
    for drive in drives:
        candidate = os.path.join(drive, UPDATE_PKG_NAME)
        if os.path.exists(candidate):
            return candidate
    return None

def main():
    try:
        current_config = load_local_version()
        current_version = current_config.get("version", "0.0.0")
        download_url = current_config.get("download_url")

        # 1. Chequeo USB (Prioridad)
        usb_zip = check_usb_update()
        if usb_zip:
            if update_from_zip(usb_zip):
                # Opcional: Borrar zip o renombrar para no instalar loop
                pass
                
        # 2. Chequeo Online
        update_url = current_config.get("update_url") # URL directa al version.json remoto
        
        if requests and update_url:
            try:
                # Timeout corto para no retrasar inicio
                resp = requests.get(update_url, timeout=3)
                if resp.status_code == 200:
                    remote_data = resp.json()
                    remote_ver = remote_data.get("version", "0.0.0")
                    
                    if remote_ver > current_version:
                        # Descargar ZIP
                        zip_url = remote_data.get("download_url")
                        # Si la URL es relativa, construirla en base al update_url
                        if not zip_url.startswith("http"):
                             base_remote = os.path.dirname(update_url)
                             zip_url = f"{base_remote}/{zip_url}"

                        local_zip = os.path.join(BASE_DIR, "temp_update.zip")
                        
                        with requests.get(zip_url, stream=True) as r:
                            r.raise_for_status()
                            with open(local_zip, 'wb') as f:
                                for chunk in r.iter_content(chunk_size=8192): 
                                    f.write(chunk)
                                    
                        if update_from_zip(local_zip):
                            # Actualizar version.json local (Manteniendo la update_url)
                            remote_data["update_url"] = update_url 
                            with open(LOCAL_VERSION_PATH, 'w') as f:
                                json.dump(remote_data, f, indent=4)
                        
                        if os.path.exists(local_zip):
                            os.remove(local_zip)

            except Exception:
                # Fallos de red ignorados silenciosamente
                pass

    except Exception as e:
        # Logging silencioso (podría ser un archivo log)
        with open("launcher_error.log", "a") as log:
            log.write(f"{e}\n")
    
    # SIEMPRE lanzar la app
    launch_main_app()

if __name__ == "__main__":
    main()
