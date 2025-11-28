from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap
from src.database.db import SessionLocal
from src.controllers.auth_controller import AuthController
from src.controllers.config_controller import ConfigController
import os

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iniciar Sesión")
        self.resize(400, 500)
        self.setStyleSheet("background-color: #f5f5f5;")
        
        self.db = SessionLocal()
        self.auth = AuthController(self.db)
        self.config_controller = ConfigController(self.db)
        self.user = None
        
        # Ensure admin exists
        self.auth.init_admin()
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        self.setLayout(layout)
        
        # Get business info
        info = self.config_controller.get_business_info()
        
        # Logo
        logo_path = self.config_controller.get_config("business_logo_path", "")
        if logo_path and os.path.exists(logo_path):
            lbl_logo = QLabel()
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(200, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl_logo.setPixmap(scaled_pixmap)
            lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl_logo)
        
        # Business Name
        lbl_title = QLabel(info["name"])
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 5px;")
        layout.addWidget(lbl_title)
        
        # RIF
        if info["rif"]:
            lbl_rif = QLabel(f"RIF: {info['rif']}")
            lbl_rif.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_rif.setStyleSheet("font-size: 14px; color: #666; margin-bottom: 20px;")
            layout.addWidget(lbl_rif)
        
        # Login Container
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #ddd;
            }
        """)
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(20, 30, 20, 30)
        container_layout.setSpacing(15)
        container.setLayout(container_layout)
        
        # Welcome text
        lbl_welcome = QLabel("Bienvenido")
        lbl_welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_welcome.setStyleSheet("font-size: 18px; color: #444; border: none;")
        container_layout.addWidget(lbl_welcome)
        
        # Inputs
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuario")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        self.password_input.returnPressed.connect(self.handle_login)
        
        container_layout.addWidget(self.username_input)
        container_layout.addWidget(self.password_input)
        
        # Button
        btn_login = QPushButton("INGRESAR")
        btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_login.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 12px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        btn_login.clicked.connect(self.handle_login)
        container_layout.addWidget(btn_login)
        
        layout.addWidget(container)
        layout.addStretch()
        
        # Footer
        lbl_footer = QLabel("Sistema de Gestión v1.0")
        lbl_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_footer.setStyleSheet("color: #999; font-size: 12px;")
        layout.addWidget(lbl_footer)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Por favor ingrese usuario y contraseña")
            return
        
        user = self.auth.login(username, password)
        if user:
            self.user = user
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Credenciales incorrectas")

    def closeEvent(self, event):
        self.db.close()
        event.accept()
