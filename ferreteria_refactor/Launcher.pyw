import sys
import os
import json
import shutil
import zipfile
import urllib.request
import subprocess
from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox, QProgressBar, QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor

# CONFIGURATION
UPDATE_URL_JSON = "https://inventariosoft.netlify.app/version.json"

if getattr(sys, 'frozen', False):
    # Running as compiled exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path Logic:
# 1. Unified Compiled: BASE/Client/Ferreteria.exe
# 2. Legacy Compiled: BASE/frontend_caja/Ferreteria.exe
# 3. Dev Mode: BASE/frontend_caja/src/main.py

MAIN_EXE_UNIFIED = os.path.join(BASE_DIR, "Client", "Ferreteria.exe")
MAIN_EXE_LEGACY = os.path.join(BASE_DIR, "frontend_caja", "Ferreteria.exe")
SERVER_EXE = os.path.join(BASE_DIR, "Server", "Server.exe")
MAIN_SCRIPT_DEV = os.path.join(BASE_DIR, "frontend_caja", "src", "main.py")

LOCAL_VERSION_FILE = os.path.join(BASE_DIR, "version.json")

class UpdateThread(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def run(self):
        try:
            # 1. Check Remote Version
            self.status.emit("Buscando actualizaciones...")
            with urllib.request.urlopen(UPDATE_URL_JSON) as url:
                data = json.loads(url.read().decode())
                remote_version = data.get("version")
                download_url_rel = data.get("download_url")
                # Construct absolute URL assuming relative to JSON
                # If json is at domain.com/version.json, download is at domain.com/downloads/file.zip
                base_url = UPDATE_URL_JSON.rsplit('/', 1)[0]
                download_url = f"{base_url}/{download_url_rel}"

            # 2. Check Local Version
            local_version = "0.0.0"
            if os.path.exists(LOCAL_VERSION_FILE):
                try:
                    with open(LOCAL_VERSION_FILE, 'r') as f:
                        local_data = json.load(f)
                        local_version = local_data.get("version", "0.0.0")
                except:
                    pass

            if remote_version == local_version:
                self.status.emit("Sistema actualizado.")
                self.finished.emit(False, "No hay actualizaciones") # False means no update performed
                return

            self.status.emit(f"Actualizando a v{remote_version}...")
            
            # 3. Download Zip
            zip_path = os.path.join(BASE_DIR, "update_temp.zip")
            
            def report(blocknum, blocksize, totalsize):
                read = blocknum * blocksize
                if totalsize > 0:
                    percent = int(read * 100 / totalsize)
                    self.progress.emit(percent)
            
            urllib.request.urlretrieve(download_url, zip_path, report)
            
            # 4. Extract
            self.status.emit("Instalando actualización...")
            self.progress.emit(0)
            
            # Extract to BASE_DIR (Project Root)
            # Zip contains "Client/" and "Server/" folder structures AND "Launcher.exe"
            
            # 4. Extract
            self.status.emit("Instalando actualización...")
            self.progress.emit(0)
            
            # Extract to BASE_DIR (Project Root)
            import time
            
            # HANDLE SELF-UPDATE (Windows locking)
            launcher_path = os.path.join(BASE_DIR, "Launcher.exe")
            launcher_writable = True
            
            if os.path.exists(launcher_path):
                try:
                    old_launcher = launcher_path + ".old"
                    if os.path.exists(old_launcher):
                        os.remove(old_launcher)
                    
                    # Try rename
                    os.rename(launcher_path, old_launcher)
                    time.sleep(1.0) # Allow OS to release handle
                except Exception as e:
                    print(f"Warning: Could not rename Launcher: {e}")
                    launcher_writable = False
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Custom extraction to respect launcher locking
                file_list = zip_ref.namelist()
                for file_info in file_list:
                    # Skip Launcher.exe if we couldn't rename the running one
                    if file_info.lower() == "launcher.exe" and not launcher_writable:
                        print("Skipping Launcher.exe update (File locked)")
                        continue
                        
                    zip_ref.extract(file_info, BASE_DIR)
                
            # 5. Cleanup
            try:
                os.remove(zip_path)
            except:
                pass
            
            # 6. Update Local Version File
            with open(LOCAL_VERSION_FILE, 'w') as f:
                json.dump({"version": remote_version}, f)
                
            self.status.emit("Actualización completada.")
            self.finished.emit(True, f"Actualizado a v{remote_version}")
            
        except Exception as e:
            self.finished.emit(False, str(e))

class Launcher(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(400, 250)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Style
        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                border-radius: 10px;
                border: 2px solid #34495e;
            }
            QLabel { color: white; }
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        
        title = QLabel("INVENTARIOSOFT")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(title)
        
        # Determine current version
        local_version = "Detectando..."
        if os.path.exists(LOCAL_VERSION_FILE):
            try:
                with open(LOCAL_VERSION_FILE, 'r') as f:
                    local_version = json.load(f).get("version", "0.0.0")
            except:
                local_version = "E: Lectura"
        
        self.lbl_version = QLabel(f"Versión: {local_version}")
        self.lbl_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_version.setStyleSheet("color: #bdc3c7; font-size: 10px; margin-bottom: 5px;")
        layout.addWidget(self.lbl_version)
        
        self.status_label = QLabel("Iniciando...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.pbar = QProgressBar()
        layout.addWidget(self.pbar)
        
        layout.addStretch()
        
        # Cleanup old updates
        old_launcher = os.path.join(BASE_DIR, "Launcher.exe.old")
        if os.path.exists(old_launcher):
            try:
                os.remove(old_launcher)
            except:
                pass

        # Start Update Process
        self.thread = UpdateThread()
        self.thread.progress.connect(self.pbar.setValue)
        self.thread.status.connect(self.status_label.setText)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def on_finished(self, updated, msg):
        if "Error" in msg:
            if "HTTP Error 404" in str(msg):
                 # Network error or version check failed -> Launch anyway (offline mode possibility)
                 self.status_label.setText("Modo Offline / Error Update")
            else:
                QMessageBox.warning(self, "Error de Actualización", f"No se pudo actualizar: {msg}\nIniciando versión actual.")
        
        self.launch_app()

    def is_server_running(self):
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                return s.connect_ex(('127.0.0.1', 8000)) == 0
        except:
            return False

    def get_local_ip(self):
        import socket
        try:
            # Connect to an external server to know which interface is used
            # We don't actually send data
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def check_license_features(self):
        """Quick check of license file for WEB feature without full controller logic"""
        try:
            app_data = os.path.join(os.getenv('APPDATA'), 'InventarioSoft')
            license_file = os.path.join(app_data, 'license.dat')
            
            if os.path.exists(license_file):
                with open(license_file, 'r') as f:
                    data = json.load(f)
                    
                    # Check validation using a simplistic check or rely on file trust for launcher speed
                    # Ideally we should use the controller, but importing it might be complex if paths aren't set
                    # Let's trust the "features" key if present, assuming 'activate_license' wrote it.
                    # Security note: A user could edit the JSON, but the backend validates the key hash anyway.
                    # The Launcher is just a convenience UI.
                    features = data.get("features", [])
                    if "WEB" in features:
                        return True
        except:
            pass
        return False

    def get_python_command(self):
        """Get a valid python command. Avoids using sys.executable if it points to the frozen EXE."""
        if getattr(sys, 'frozen', False):
            # If frozen, we CANNOT use sys.executable because it is the Launcher.exe itself.
            # We must assume a python environment is available or bundled.
            # Strategy:
            # 1. Look for a 'runtime/python.exe' (bundled)
            # 2. Fallback to system 'python' command
            
            bundled_python = os.path.join(BASE_DIR, "runtime", "python.exe")
            if os.path.exists(bundled_python):
                return bundled_python
            
            # Fallback to PATH
            return "python"
        else:
            return sys.executable

    def launch_app(self):
        self.status_label.setText("Iniciando aplicación...")
        QApplication.processEvents()
        
        # --- WEB DASHBOARD LAUNCH LOGIC ---
        web_process = None
        web_enabled = self.check_license_features()
        
        if web_enabled:
            # Launch Streamlit
            try:
                self.status_label.setText("Iniciando Dashboard Web...")
                QApplication.processEvents()
                
                dashboard_path = os.path.join(BASE_DIR, "web_dashboard", "app.py")
                
                if not os.path.exists(dashboard_path):
                     # Log error but don't block
                     print(f"Error: No se encuentra {dashboard_path}")
                     self.status_label.setText("Error: falta carpeta web_dashboard")
                
                else:
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    
                    # USE SAFE COMMAND
                    py_cmd = self.get_python_command()
                    
                    cmd = [py_cmd, "-m", "streamlit", "run", dashboard_path, "--server.headless=true", "--server.address=0.0.0.0"]
                    
                    web_process = subprocess.Popen(
                        cmd,
                        cwd=BASE_DIR,
                        startupinfo=startupinfo,
                        shell=False
                    )
                    
                    ip = self.get_local_ip()
                    final_msg = f"Dashboard Activo: http://{ip}:8501"
                    self.status_label.setText(final_msg)
                    print(final_msg)

            except Exception as e:
                print(f"Error starting web dashboard: {e}")
                self.status_label.setText("Error al iniciar Web")
            except Exception as e:
                print(f"Error starting web dashboard: {e}")
                QMessageBox.critical(self, "Error Web", f"Excepción al iniciar dashboard:\n{str(e)}")

        # 0. Start Server (if needed)
        server_process = None
        server_managed = False  # Flag to know if WE started it
        
        if os.path.exists(SERVER_EXE):
            if self.is_server_running():
                if not web_enabled:
                    self.status_label.setText("Servidor ya activo...")
            else:
                self.status_label.setText("Iniciando Servidor...")
                QApplication.processEvents()
                try:
                    # Start Server silently (no window) WITHOUT shell=True to get real PID
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    server_dir = os.path.dirname(SERVER_EXE)
                    
                    server_process = subprocess.Popen(
                        [SERVER_EXE], 
                        cwd=server_dir,
                        startupinfo=startupinfo,
                        shell=False # Changed to False to own the PID directly
                    )
                    server_managed = True
                except Exception as e:
                    print(f"Error starting server: {e}")
        
        # Check Priorities
        client_process = None
        
        if os.path.exists(MAIN_EXE_UNIFIED):
             # Launch with Client/ as CWD so it finds .env
             client_dir = os.path.dirname(MAIN_EXE_UNIFIED)
             client_process = subprocess.Popen([MAIN_EXE_UNIFIED], cwd=client_dir)
             
        elif os.path.exists(MAIN_EXE_LEGACY):
             legacy_dir = os.path.dirname(MAIN_EXE_LEGACY)
             client_process = subprocess.Popen([MAIN_EXE_LEGACY], cwd=legacy_dir)
             
        elif os.path.exists(MAIN_SCRIPT_DEV):
            dev_dir = os.path.dirname(os.path.dirname(MAIN_SCRIPT_DEV))
            client_process = subprocess.Popen([sys.executable, MAIN_SCRIPT_DEV], cwd=dev_dir)
            
        else:
            QMessageBox.critical(self, "Error Fatal", f"No se encuentra el sistema principal:\nBuscado en:\n{MAIN_EXE_UNIFIED}")
            self.close()
            return
            
        # NOW: Wait for Client to Close
        if client_process:
            self.hide() # Hide Launcher but keep running
            
            # Wait for client to finish
            client_process.wait()
            
            # Client closed, kill Server IF we started it
            if server_managed and server_process:
                try:
                    # Robust Kill
                    self.status_label.setText("Cerrando servidor...")
                    import signal
                    server_process.terminate()
                    try:
                        server_process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        server_process.kill() # Force kill
                except Exception as e:
                    print(f"Error killing server: {e}")
            
            # Kill Web Dashboard
            if web_process:
                try:
                    web_process.terminate()
                except:
                    pass
                        
            self.close()
            sys.exit(0)
        else:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = Launcher()
    launcher.show()
    sys.exit(app.exec())
