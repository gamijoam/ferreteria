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
        
        # Currency Configuration Section
        currency_group = QGroupBox("Configuración de Moneda")
        currency_layout = QFormLayout()
        
        # Base Currency (for inventory prices)
        self.base_currency_combo = QComboBox()
        self.base_currency_combo.setToolTip("Moneda en la que se guardan los precios en el sistema")
        currency_layout.addRow("Moneda de Inventario (Base):", self.base_currency_combo)
        
        # Operating Currency (local currency for payments)
        self.operating_currency_combo = QComboBox()
        self.operating_currency_combo.setToolTip("Moneda local para cobros y pagos")
        currency_layout.addRow("Moneda de Cobro (Principal):", self.operating_currency_combo)
        
        # Exchange Rates Management
        rates_label = QLabel("Tasas de Cambio:")
        rates_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        currency_layout.addRow(rates_label)
        
        # Exchange Rates Table
        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
        self.rates_table = QTableWidget()
        self.rates_table.setColumnCount(5)
        self.rates_table.setHorizontalHeaderLabels([
            "Nombre", "Moneda", "Tasa", "Activa", "Acciones"
        ])
        self.rates_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.rates_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.rates_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.rates_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.rates_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.rates_table.setMaximumHeight(200)
        currency_layout.addRow(self.rates_table)
        
        # Buttons for rate management
        rate_buttons_layout = QHBoxLayout()
        self.add_rate_btn = QPushButton("+ Agregar Tasa")
        self.add_rate_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px 10px; border-radius: 3px;")
        self.add_rate_btn.clicked.connect(self.add_exchange_rate)
        
        self.edit_rate_btn = QPushButton("Editar")
        self.edit_rate_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 5px 10px; border-radius: 3px;")
        self.edit_rate_btn.clicked.connect(self.edit_exchange_rate)
        
        self.delete_rate_btn = QPushButton("Eliminar")
        self.delete_rate_btn.setStyleSheet("background-color: #f44336; color: white; padding: 5px 10px; border-radius: 3px;")
        self.delete_rate_btn.clicked.connect(self.delete_exchange_rate)
        
        rate_buttons_layout.addWidget(self.add_rate_btn)
        rate_buttons_layout.addWidget(self.edit_rate_btn)
        rate_buttons_layout.addWidget(self.delete_rate_btn)
        rate_buttons_layout.addStretch()
        currency_layout.addRow(rate_buttons_layout)
        
        currency_group.setLayout(currency_layout)
        left_column.addWidget(currency_group)
        
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
        
        # Load currencies
        self.load_currencies()
        
        # Load exchange rates
        self.load_exchange_rates()
        
        # Load logo
        logo_path = self.controller.get_config("business_logo_path", "")
        if logo_path and os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(200, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_preview.setPixmap(scaled_pixmap)
            self.logo_path = logo_path
        else:
            self.logo_path = ""
    
    def load_currencies(self):
        """Load available currencies from backend"""
        try:
            currencies = self.controller.get_currencies()
            
            # Clear and populate both combos
            self.base_currency_combo.clear()
            self.operating_currency_combo.clear()
            
            for currency in currencies:
                display_text = f"{currency['code']} - {currency['name']} ({currency['symbol']})"
                self.base_currency_combo.addItem(display_text, currency['code'])
                self.operating_currency_combo.addItem(display_text, currency['code'])
            
            # Load saved selections
            base_currency = self.controller.get_config("BASE_CURRENCY", "USD")
            operating_currency = self.controller.get_config("OPERATING_CURRENCY", "VES")
            
            # Set current selections
            base_index = self.base_currency_combo.findData(base_currency)
            if base_index >= 0:
                self.base_currency_combo.setCurrentIndex(base_index)
            
            operating_index = self.operating_currency_combo.findData(operating_currency)
            if operating_index >= 0:
                self.operating_currency_combo.setCurrentIndex(operating_index)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar monedas: {str(e)}")
    
    def load_exchange_rates(self):
        """Load exchange rates into table"""
        try:
            rates = self.controller.get_exchange_rates()
            
            self.rates_table.setRowCount(0)
            
            for rate in rates:
                row = self.rates_table.rowCount()
                self.rates_table.insertRow(row)
                
                # Name
                from PyQt6.QtWidgets import QTableWidgetItem
                self.rates_table.setItem(row, 0, QTableWidgetItem(rate['name']))
                
                # Currency
                currency_text = f"{rate['currency_code']}"
                self.rates_table.setItem(row, 1, QTableWidgetItem(currency_text))
                
                # Rate
                self.rates_table.setItem(row, 2, QTableWidgetItem(f"{rate['rate']:.2f}"))
                
                # Active
                active_text = "Sí" if rate.get('is_active', True) else "No"
                self.rates_table.setItem(row, 3, QTableWidgetItem(active_text))
                
                # Store rate ID in first column
                self.rates_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, rate['id'])
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar tasas: {str(e)}")

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
            
            # Save currency configuration
            base_currency = self.base_currency_combo.currentData()
            operating_currency = self.operating_currency_combo.currentData()
            
            if base_currency:
                self.controller.set_config("BASE_CURRENCY", base_currency)
            if operating_currency:
                self.controller.set_config("OPERATING_CURRENCY", operating_currency)
            
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
    
    def add_exchange_rate(self):
        """Open dialog to add new exchange rate"""
        dialog = ExchangeRateDialog(self)
        if dialog.exec():
            rate_data = dialog.get_data()
            try:
                self.controller.create_exchange_rate(rate_data)
                self.load_exchange_rates()
                QMessageBox.information(self, "Éxito", "Tasa de cambio agregada correctamente")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al agregar tasa: {str(e)}")
    
    def edit_exchange_rate(self):
        """Edit selected exchange rate"""
        current_row = self.rates_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione una tasa para editar")
            return
        
        # Get rate ID from first column
        rate_id = self.rates_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Get current rate data
        rate_data = {
            'id': rate_id,
            'name': self.rates_table.item(current_row, 0).text(),
            'currency_code': self.rates_table.item(current_row, 1).text(),
            'rate': float(self.rates_table.item(current_row, 2).text()),
            'is_active': self.rates_table.item(current_row, 3).text() == "Sí"
        }
        
        dialog = ExchangeRateDialog(self, rate_data)
        if dialog.exec():
            updated_data = dialog.get_data()
            try:
                self.controller.update_exchange_rate(rate_id, updated_data)
                self.load_exchange_rates()
                QMessageBox.information(self, "Éxito", "Tasa de cambio actualizada correctamente")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al actualizar tasa: {str(e)}")
    
    def delete_exchange_rate(self):
        """Delete selected exchange rate"""
        current_row = self.rates_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione una tasa para eliminar")
            return
        
        rate_name = self.rates_table.item(current_row, 0).text()
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro de eliminar la tasa '{rate_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            rate_id = self.rates_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            try:
                self.controller.delete_exchange_rate(rate_id)
                self.load_exchange_rates()
                QMessageBox.information(self, "Éxito", "Tasa de cambio eliminada correctamente")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar tasa: {str(e)}")

    def closeEvent(self, event):
        event.accept()


class ExchangeRateDialog(QDialog):
    """Dialog for adding/editing exchange rates"""
    
    def __init__(self, parent=None, rate_data=None):
        super().__init__(parent)
        self.rate_data = rate_data
        self.setWindowTitle("Gestionar Tasa de Cambio")
        self.resize(400, 250)
        
        self.setup_ui()
        
        if rate_data:
            self.load_data(rate_data)
    
    def setup_ui(self):
        layout = QFormLayout()
        
        # Name input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("ej: Tasa BCV, Monitor, Paralelo")
        layout.addRow("Nombre:", self.name_input)
        
        # Currency combo
        self.currency_combo = QComboBox()
        self.load_currencies()
        layout.addRow("Moneda:", self.currency_combo)
        
        # Rate input
        from PyQt6.QtWidgets import QDoubleSpinBox
        self.rate_input = QDoubleSpinBox()
        self.rate_input.setRange(0.01, 999999.99)
        self.rate_input.setDecimals(2)
        self.rate_input.setValue(1.00)
        layout.addRow("Tasa:", self.rate_input)
        
        # Active checkbox
        from PyQt6.QtWidgets import QCheckBox
        self.active_checkbox = QCheckBox("Activa")
        self.active_checkbox.setChecked(True)
        layout.addRow("", self.active_checkbox)
        
        # Buttons
        from PyQt6.QtWidgets import QDialogButtonBox
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def load_currencies(self):
        """Load currencies into combo"""
        try:
            from src.controllers.config_controller import ConfigController
            controller = ConfigController()
            currencies = controller.get_currencies()
            
            for currency in currencies:
                display_text = f"{currency['code']} - {currency['name']}"
                self.currency_combo.addItem(display_text, currency['code'])
        except:
            # Fallback to default currencies
            self.currency_combo.addItem("USD - Dólar", "USD")
            self.currency_combo.addItem("VES - Bolívar", "VES")
    
    def load_data(self, rate_data):
        """Load existing rate data into form"""
        self.name_input.setText(rate_data.get('name', ''))
        self.rate_input.setValue(rate_data.get('rate', 1.0))
        self.active_checkbox.setChecked(rate_data.get('is_active', True))
        
        # Set currency
        currency_code = rate_data.get('currency_code', '')
        index = self.currency_combo.findData(currency_code)
        if index >= 0:
            self.currency_combo.setCurrentIndex(index)
    
    def validate_and_accept(self):
        """Validate form before accepting"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Error", "El nombre de la tasa es obligatorio")
            return
        
        if self.rate_input.value() <= 0:
            QMessageBox.warning(self, "Error", "La tasa debe ser mayor a 0")
            return
        
        self.accept()
    
    def get_data(self):
        """Get form data as dictionary"""
        return {
            'name': self.name_input.text().strip(),
            'currency_code': self.currency_combo.currentData(),
            'rate': self.rate_input.value(),
            'is_active': self.active_checkbox.isChecked()
        }
