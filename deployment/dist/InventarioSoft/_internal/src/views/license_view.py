from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from src.controllers.license_controller import LicenseController

class LicenseDialog(QDialog):
    def __init__(self, controller: LicenseController, status, message):
        super().__init__()
        self.controller = controller
        self.status = status
        self.message = message
        
        self.setWindowTitle("Activación de Producto - InventarioSoft")
        self.setFixedSize(500, 400)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        title = QLabel("🔐 Activación Requerida")
        title.setStyleSheet("font-size: 22pt; font-weight: bold; color: #c0392b;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Status Message
        msg_label = QLabel(self.message)
        msg_label.setStyleSheet("font-size: 12pt; color: #7f8c8d;")
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label)
        
        # Hardware ID Box
        id_frame = QFrame()
        id_frame.setStyleSheet("background-color: #ecf0f1; border-radius: 5px; padding: 10px;")
        id_layout = QVBoxLayout()
        id_frame.setLayout(id_layout)
        
        lbl_id = QLabel("Tu ID de Hardware:")
        lbl_id.setStyleSheet("font-weight: bold; color: #2c3e50;")
        id_layout.addWidget(lbl_id)
        
        self.hw_id_display = QLineEdit(self.controller.get_hardware_id())
        self.hw_id_display.setReadOnly(True)
        self.hw_id_display.setStyleSheet("font-size: 14pt; border: none; background: transparent; font-family: monospace;")
        self.hw_id_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        id_layout.addWidget(self.hw_id_display)
        
        lbl_copy = QLabel("(Envía este ID al proveedor para obtener tu licencia)")
        lbl_copy.setStyleSheet("font-size: 9pt; color: #95a5a6; font-style: italic;")
        lbl_copy.setAlignment(Qt.AlignmentFlag.AlignCenter)
        id_layout.addWidget(lbl_copy)
        
        layout.addWidget(id_frame)
        
        # License Key Input
        self.input_key = QLineEdit()
        self.input_key.setPlaceholderText("Ingresa tu clave de licencia aquí...")
        self.input_key.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.input_key)
        
        # Buttons
        btn_activate = QPushButton("ACTIVAR LICENCIA")
        btn_activate.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        btn_activate.clicked.connect(self.activate)
        layout.addWidget(btn_activate)
        
        btn_exit = QPushButton("Salir")
        btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_exit.clicked.connect(self.reject)
        layout.addWidget(btn_exit)
        
        self.setLayout(layout)
        
    def activate(self):
        key = self.input_key.text().strip()
        if not key:
            QMessageBox.warning(self, "Error", "Ingresa una clave")
            return
            
        success, msg = self.controller.activate_license(key)
        if success:
            QMessageBox.information(self, "Éxito", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", msg)
