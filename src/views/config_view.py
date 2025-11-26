from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, 
    QMessageBox, QLabel, QGroupBox
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
        
        form_layout.addRow("Nombre del Negocio:", self.name_input)
        form_layout.addRow("RIF / NIT:", self.rif_input)
        form_layout.addRow("Dirección:", self.address_input)
        form_layout.addRow("Teléfono:", self.phone_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
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
            
            QMessageBox.information(self, "Éxito", "Configuración guardada correctamente.\nReinicie la aplicación para ver algunos cambios.")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def closeEvent(self, event):
        self.db.close()
        event.accept()
