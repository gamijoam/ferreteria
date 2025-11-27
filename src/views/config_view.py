from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, 
    QMessageBox, QLabel, QGroupBox, QComboBox
)
from src.database.db import SessionLocal
from src.controllers.config_controller import ConfigController

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración del Negocio")
        self.resize(400, 300)
        
        self.db = SessionLocal()
        self.controller = ConfigController(self.db)
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header
        header = QLabel("Datos de la Empresa")
        header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Form
        form_group = QGroupBox("Información General")
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.rif_input = QLineEdit()
        self.address_input = QLineEdit()
        self.phone_input = QLineEdit()
        
        self.business_type_combo = QComboBox()
        self.business_type_combo.addItems(["Ferretería", "Pescadería/Frutería", "Otro"])
        
        form_layout.addRow("Nombre del Negocio:", self.name_input)
        form_layout.addRow("RIF / NIT:", self.rif_input)
        form_layout.addRow("Tipo de Negocio:", self.business_type_combo)
        form_layout.addRow("Dirección:", self.address_input)
        form_layout.addRow("Teléfono:", self.phone_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
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
        layout.addWidget(exchange_group)
        
        # Buttons
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
        layout.addWidget(btn_save)
        
        layout.addStretch()

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

    def save_config(self):
        try:
            name = self.name_input.text().strip()
            rif = self.rif_input.text().strip()
            address = self.address_input.text().strip()
            phone = self.phone_input.text().strip()
            
            if not name:
                QMessageBox.warning(self, "Error", "El nombre del negocio es obligatorio")
                return
                
            self.controller.update_business_info(name, rif, address, phone)
            
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
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def closeEvent(self, event):
        self.db.close()
        event.accept()
