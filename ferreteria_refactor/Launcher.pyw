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
            
            # HANDLE SELF-UPDATE (Windows locking)
            launcher_path = os.path.join(BASE_DIR, "Launcher.exe")
            if os.path.exists(launcher_path):
                try:
                    # Rename running exe to allow overwrite
                    old_launcher = launcher_path + ".old"
                    if os.path.exists(old_launcher):
                        os.remove(old_launcher)
                    os.rename(launcher_path, old_launcher)
                except Exception as e:
                    print(f"Warning: Could not rename Launcher for update: {e}")
                    # Continue anyway, extraction might fail for Launcher.exe but succeed for others
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(BASE_DIR)
                
            # 5. Cleanup
            os.remove(zip_path)
            
            # 6. Update Local Version File
            with open(LOCAL_VERSION_FILE, 'w') as f:
                json.dump({"version": remote_version}, f)
                
            self.status.emit("Actualización completada.")
            self.finished.emit(True, "Actualizado")
            
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

    def launch_app(self):
        self.status_label.setText("Iniciando aplicación...")
        QApplication.processEvents()
        
        # Check Priorities
        if os.path.exists(MAIN_EXE_UNIFIED):
             # Launch with Client/ as CWD so it finds .env
             client_dir = os.path.dirname(MAIN_EXE_UNIFIED)
             subprocess.Popen([MAIN_EXE_UNIFIED], cwd=client_dir)
             self.close()
        elif os.path.exists(MAIN_EXE_LEGACY):
             legacy_dir = os.path.dirname(MAIN_EXE_LEGACY)
             subprocess.Popen([MAIN_EXE_LEGACY], cwd=legacy_dir)
             self.close()
        elif os.path.exists(MAIN_SCRIPT_DEV):
            # Launch without blocking
            # Dev mode usually expects cwd at root of frontend_caja? Or root of repo?
            # src code expects frontend_caja as root or ferreteria_refactor?
            # Let's set it to frontend_caja
            dev_dir = os.path.dirname(os.path.dirname(MAIN_SCRIPT_DEV))
            subprocess.Popen([sys.executable, MAIN_SCRIPT_DEV], cwd=dev_dir)
            self.close()
        else:
            QMessageBox.critical(self, "Error Fatal", f"No se encuentra el sistema principal:\nBuscado en:\n{MAIN_EXE_UNIFIED}")
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = Launcher()
    launcher.show()
    sys.exit(app.exec())
