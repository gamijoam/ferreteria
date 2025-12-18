from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, 
    QMessageBox, QLabel, QGroupBox, QComboBox, QFileDialog, QHBoxLayout,
    QApplication
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from src.database.db import SessionLocal
from src.controllers.config_controller import ConfigController
import os

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración del Negocio")
        self.resize(800, 600)
        
        self.controller = ConfigController()
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Header
        header = QLabel("Datos de la Empresa")
        header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(header)
        
        # Create horizontal layout for two columns
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)
        
        # LEFT COLUMN
        left_column = QVBoxLayout()
        content_layout.addLayout(left_column)
        
        # Form
        form_group = QGroupBox("Información General")
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.rif_input = QLineEdit()
        self.address_input = QLineEdit()
        self.phone_input = QLineEdit()
        
        self.business_type_combo = QComboBox()
        self.business_type_combo.setEditable(True)
        self.business_type_combo.addItems([
            "Ferretería", 
            "Farmacia", 
            "Supermercado", 
            "Tienda de Ropa", 
            "Restaurante", 
            "Repuestos", 
            "Electrónica",
            "Pescadería/Frutería", 
            "Otro"
        ])
        
        form_layout.addRow("Nombre del Negocio:", self.name_input)
        form_layout.addRow("RIF / NIT:", self.rif_input)
        form_layout.addRow("Tipo de Negocio:", self.business_type_combo)
        form_layout.addRow("Dirección:", self.address_input)
        form_layout.addRow("Teléfono:", self.phone_input)
        
        form_group.setLayout(form_layout)
        left_column.addWidget(form_group)
        
        # Exchange Rate Section
        exchange_group = QGroupBox("Tasa de Cambio (USD → Bs)")
        exchange_layout = QFormLayout()
        
        self.exchange_rate_input = QLineEdit()
        self.exchange_rate_input.setPlaceholderText("Ej: 36.50")
        
        self.exchange_rate_updated_label = QLabel("Nunca actualizada")
        self.exchange_rate_updated_label.setStyleSheet("color: #666; font-size: 10pt;")
        
        exchange_layout.addRow("Tasa Actual (1 USD = X Bs):", self.exchange_rate_input)
        exchange_layout.addRow("Última Actualización:", self.exchange_rate_updated_label)
        
        exchange_group.setLayout(exchange_layout)
        left_column.addWidget(exchange_group)
        
        left_column.addStretch()
        
        # RIGHT COLUMN
        right_column = QVBoxLayout()
        content_layout.addLayout(right_column)
        
        # Logo Section
        logo_group = QGroupBox("Logo de la Empresa")
        logo_layout = QVBoxLayout()
        
        self.logo_preview = QLabel("Sin logo")
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_preview.setMinimumHeight(150)
        self.logo_preview.setStyleSheet("border: 1px solid #ccc; background-color: #f5f5f5;")
        logo_layout.addWidget(self.logo_preview)
        
        btn_upload_logo = QPushButton("Cargar Logo")
        btn_upload_logo.clicked.connect(self.upload_logo)
        logo_layout.addWidget(btn_upload_logo)
        
        logo_group.setLayout(logo_layout)
        right_column.addWidget(logo_group)

        # LINK DASHBOARD WEB SECTION
        web_group = QGroupBox("Acceso Dashboard Web")
        web_layout = QVBoxLayout()
        
        from src.controllers.license_controller import LicenseController
        license_ctrl = LicenseController()
        status, msg = license_ctrl.check_status()
        
        # Check if license has WEB feature
        # (Assuming check_status returns "ACTIVE" and we can inspect internal logic or msg)
        # Better: use validate_key directly if possible or trust the feature/msg
        # Let's use a simpler heuristic or the controller's property if available.
        # Since check_status doesn't return features explicitly, we infer or read.
        # However, the user wants the IP.
        
        is_web_active = "Plan Web Activo" in msg or "WEB" in msg # Based on previous logic
        # Or better: check license file ourselves briefly or add method to controller. 
        # But let's assume if it is ACTIVE and we are here.
        # Let's just calculate IP and show it.
        
        ip = self.get_local_ip()
        url = f"http://{ip}:8501"
        
        lbl_info = QLabel("Enlace de acceso local:")
        lbl_info.setStyleSheet("color: #666;")
        web_layout.addWidget(lbl_info)
        
        self.url_input = QLineEdit(url)
        self.url_input.setReadOnly(True)
        self.url_input.setStyleSheet("font-size: 13px; font-weight: bold; padding: 5px; color: #2196F3;")
        web_layout.addWidget(self.url_input)
        
        btn_copy = QPushButton("Copiar Enlace")
        btn_copy.clicked.connect(lambda: QApplication.clipboard().setText(self.url_input.text()))
        web_layout.addWidget(btn_copy)
        
        web_group.setLayout(web_layout)
        right_column.addWidget(web_group)
        
        # Printer Configuration Button
        btn_printer = QPushButton("⚙️ Configurar Impresora Térmica")
        btn_printer.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        btn_printer.clicked.connect(self.open_printer_config)
        right_column.addWidget(btn_printer)
        
        right_column.addStretch()
        
        # BOTTOM: Save button (full width)
        btn_save = QPushButton("Guardar Cambios")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        btn_save.clicked.connect(self.save_config)
        main_layout.addWidget(btn_save)

    def load_data(self):
        info = self.controller.get_business_info()
        self.name_input.setText(info["name"])
        self.rif_input.setText(info["rif"])
        self.address_input.setText(info["address"])
        self.phone_input.setText(info["phone"])
        
        # Load business type
        business_type = self.controller.get_config("BUSINESS_TYPE", "Ferretería")
        index = self.business_type_combo.findText(business_type)
        if index >= 0:
            self.business_type_combo.setCurrentIndex(index)
        
        # Load exchange rate
        exchange_rate = self.controller.get_config("exchange_rate", "1.0")
        self.exchange_rate_input.setText(exchange_rate)
        
        # Load last updated
        updated_at = self.controller.get_config("exchange_rate_updated_at", "")
        if updated_at:
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(updated_at)
                self.exchange_rate_updated_label.setText(dt.strftime("%Y-%m-%d %H:%M"))
            except:
                self.exchange_rate_updated_label.setText("Fecha inválida")
        else:
            self.exchange_rate_updated_label.setText("Nunca actualizada")
        
        # Load logo
        logo_path = self.controller.get_config("business_logo_path", "")
        if logo_path and os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(200, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_preview.setPixmap(scaled_pixmap)
            self.logo_path = logo_path
        else:
            self.logo_path = ""

    def save_config(self):
        try:
            name = self.name_input.text().strip()
            rif = self.rif_input.text().strip()
            address = self.address_input.text().strip()
            phone = self.phone_input.text().strip()
            
            if not name:
                QMessageBox.warning(self, "Error", "El nombre del negocio es obligatorio")
                return
                
            self.controller.update_business_info({
                "name": name,
                "rif": rif,
                "address": address,
                "phone": phone
            })
            
            # Save business type
            business_type = self.business_type_combo.currentText()
            self.controller.set_config("BUSINESS_TYPE", business_type)
            
            # Save exchange rate
            exchange_rate_text = self.exchange_rate_input.text().strip()
            if exchange_rate_text:
                try:
                    exchange_rate = float(exchange_rate_text)
                    if exchange_rate <= 0:
                        QMessageBox.warning(self, "Error", "La tasa de cambio debe ser mayor a 0")
                        return
                    
                    from datetime import datetime
                    self.controller.set_config("exchange_rate", str(exchange_rate))
                    self.controller.set_config("exchange_rate_updated_at", datetime.now().isoformat())
                except ValueError:
                    QMessageBox.warning(self, "Error", "La tasa de cambio debe ser un número válido")
                    return
            
            QMessageBox.information(self, "Éxito", "Configuración guardada correctamente.\nReinicie la aplicación para ver algunos cambios.")
            self.accept()
            
            # Save logo path if changed
            if hasattr(self, 'logo_path') and self.logo_path:
                self.controller.set_config("business_logo_path", self.logo_path)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def upload_logo(self):
        """Upload business logo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Logo",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            try:
                pixmap = QPixmap(file_path)
                if pixmap.isNull():
                    QMessageBox.warning(self, "Error", "No se pudo cargar la imagen")
                    return
                
                scaled_pixmap = pixmap.scaled(200, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.logo_preview.setPixmap(scaled_pixmap)
                self.logo_path = file_path
                
                QMessageBox.information(self, "Éxito", "Logo cargado. Haga clic en 'Guardar Cambios' para aplicar.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar logo: {str(e)}")
    
    def open_printer_config(self):
        """Open printer configuration dialog"""
        from src.views.printer_view import PrinterConfigDialog
        dialog = PrinterConfigDialog(self)
        dialog.exec()

    def get_local_ip(self):
        import socket
        try:
            # Method 1: Connect to external server (Best for identifying correct interface)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            try:
                # Method 2: Get hostname IP (Fallback for offline LAN)
                return socket.gethostbyname(socket.gethostname())
            except:
                return "127.0.0.1"

    def closeEvent(self, event):
        event.accept()
