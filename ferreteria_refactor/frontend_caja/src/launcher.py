
import os
import sys
import json
import subprocess
import shutil
import zipfile
import time
import ctypes
import threading
import tkinter as tk
from tkinter import messagebox

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

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Iniciando Sistema...")
        self.root.geometry("400x250")
        self.root.configure(bg="#2c3e50")
        self.root.overrideredirect(True) # Quitar bordes de ventana

        # Centrar ventana
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - 200
        y = (screen_height // 2) - 125
        self.root.geometry(f"400x250+{x}+{y}")

        # UI Elements
        self.lbl_title = tk.Label(root, text="Ferretería POS", font=("Segoe UI", 20, "bold"), fg="white", bg="#2c3e50")
        self.lbl_title.pack(pady=(30, 10))

        self.lbl_status = tk.Label(root, text="Iniciando...", font=("Segoe UI", 10), fg="#bdc3c7", bg="#2c3e50")
        self.lbl_status.pack(pady=10)

        self.progress = tk.Frame(root, width=300, height=5, bg="#34495e")
        self.progress.pack(pady=20)
        self.progress_bar = tk.Frame(self.progress, width=0, height=5, bg="#3498db")
        self.progress_bar.place(x=0, y=0)

        # Version info
        current_config = self.load_local_version()
        ver = current_config.get("version", "...")
        self.lbl_ver = tk.Label(root, text=f"v{ver}", font=("Segoe UI", 8), fg="#7f8c8d", bg="#2c3e50")
        self.lbl_ver.pack(side="bottom", pady=10)

        # Start process
        self.root.after(1000, self.start_update_thread)

    def set_status(self, text):
        self.lbl_status.config(text=text)
    
    def set_progress(self, percent):
        width = int(300 * (percent / 100))
        self.progress_bar.config(width=width)

    def load_local_version(self):
        try:
            if os.path.exists(LOCAL_VERSION_PATH):
                with open(LOCAL_VERSION_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def get_usb_drives(self):
        drives = []
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for letter in range(65, 91):
            if bitmask & 1:
                drive_path = chr(letter) + ":\\"
                if drive_path != "C:\\":
                     drives.append(drive_path)
            bitmask >>= 1
        return drives

    def update_from_zip(self, zip_path):
        try:
            self.set_status("Descomprimiendo archivos...")
            temp_dir = os.path.join(BASE_DIR, "temp_update")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            self.set_status("Instalando actualización...")
            # Detectar estructura
            items = os.listdir(temp_dir)
            if len(items) == 1 and os.path.isdir(os.path.join(temp_dir, items[0])) and items[0] == APP_DIR_NAME:
                # Caso: zip/InventarioSoft/...
                source_root = temp_dir
            else:
                # Caso: zip/archivos...
                source_root = temp_dir

            for root, dirs, files in os.walk(source_root):
                for file in files:
                    if file == UPDATE_PKG_NAME: continue
                    
                    src_file = os.path.join(root, file)
                    rel_path = os.path.relpath(src_file, source_root)
                    
                    # Si source_root es temp_dir y dentro hay InventarioSoft, 
                    # queremos copiar InventarioSoft/file a BASE_DIR/InventarioSoft/file
                    # adjustments logic
                    final_dest = os.path.join(BASE_DIR, rel_path)
                    
                    os.makedirs(os.path.dirname(final_dest), exist_ok=True)
                    shutil.copy2(src_file, final_dest)

            shutil.rmtree(temp_dir)
            return True
        except Exception as e:
            print(f"Update error: {e}")
            return False

    def start_update_thread(self):
        thread = threading.Thread(target=self.run_update_logic)
        thread.daemon = True
        thread.start()

    def run_update_logic(self):
        try:
            self.set_status("Buscando actualizaciones...")
            current_config = self.load_local_version()
            current_version = current_config.get("version", "0.0.0")
            
            # 1. USB Check
            usb_found = False
            drives = self.get_usb_drives()
            for drive in drives:
                candidate = os.path.join(drive, UPDATE_PKG_NAME)
                if os.path.exists(candidate):
                    self.set_status(f"USB Detectado: {drive}")
                    self.set_progress(50)
                    if self.update_from_zip(candidate):
                        usb_found = True
                        self.set_status("Actualización USB completada")
                    break
            
            # 2. Online Check
            if not usb_found and requests:
                update_url = current_config.get("update_url")
                if update_url:
                    try:
                        self.set_status("Conectando con servidor...")
                        resp = requests.get(update_url, timeout=5)
                        if resp.status_code == 200:
                            remote_data = resp.json()
                            remote_ver = remote_data.get("version", "0.0.0")
                            
                            if remote_ver > current_version:
                                self.set_status(f"Nueva versión {remote_ver} encontrada")
                                zip_url = remote_data.get("download_url")
                                if not zip_url.startswith("http"):
                                    zip_url = f"{os.path.dirname(update_url)}/{zip_url}"
                                
                                self.set_status("Descargando...")
                                local_zip = os.path.join(BASE_DIR, "temp_update.zip")
                                
                                with requests.get(zip_url, stream=True) as r:
                                    r.raise_for_status()
                                    total_length = r.headers.get('content-length')
                                    
                                    with open(local_zip, 'wb') as f:
                                        if total_length is None: # no content length header
                                            f.write(r.content)
                                        else:
                                            dl = 0
                                            total_length = int(total_length)
                                            for chunk in r.iter_content(chunk_size=8192):
                                                dl += len(chunk)
                                                f.write(chunk)
                                                done = int(50 * dl / total_length)
                                                # Update UI from thread (simple implementation)
                                                # In complex apps invoke() is needed, here risky but usually works 
                                                # or use polling. For simple splash it's okay.
                                
                                self.set_status("Instalando...")
                                if self.update_from_zip(local_zip):
                                    remote_data["update_url"] = update_url
                                    with open(LOCAL_VERSION_PATH, 'w') as f:
                                        json.dump(remote_data, f, indent=4)
                                
                                if os.path.exists(local_zip):
                                    os.remove(local_zip)
                    except Exception as e:
                        print(f"Network error: {e}")

        except Exception as e:
            print(f"Global error: {e}")
        
        self.set_status("Iniciando aplicación...")
        self.set_progress(100)
        time.sleep(0.5)
        self.launch_main_app()

    def launch_main_app(self):
        if not os.path.exists(MAIN_APP_PATH):
            alt_path = os.path.join(BASE_DIR, MAIN_EXECUTABLE)
            if os.path.exists(alt_path):
                 subprocess.Popen([alt_path], cwd=BASE_DIR)
                 self.root.quit()
                 return
            
            messagebox.showerror("Error", f"No se encuentra la aplicación:\n{MAIN_APP_PATH}")
            self.root.quit()
            return
        
        try:
            subprocess.Popen([MAIN_APP_PATH], cwd=APP_PATH)
        except Exception as e:
             messagebox.showerror("Error", f"Fallo al iniciar:\n{e}")
        
        self.root.quit()

def main():
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
