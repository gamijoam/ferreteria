from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QColor
from src.database.db import SessionLocal
from src.controllers.auth_controller import AuthController
import os

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("InventarioSoft - Inicio de Sesión")
        self.setFixedSize(1200, 600)
        
        self.db = SessionLocal()
        self.auth_controller = AuthController(self.db)
        self.user = None
        
        # Set background gradient
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f2027, stop:0.5 #203a43, stop:1 #2c5364);
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # LEFT SIDE - Branding
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
            }
        """)
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.setLayout(left_layout)
        
        # Logo
        from src.controllers.config_controller import ConfigController
        config_ctrl = ConfigController(self.db)
        logo_path = config_ctrl.get_config("business_logo_path", "")
        
        if logo_path and os.path.exists(logo_path):
            lbl_logo = QLabel()
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl_logo.setPixmap(scaled_pixmap)
            lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            left_layout.addWidget(lbl_logo)
        
        # Brand name
        business_info = config_ctrl.get_business_info()
        brand_title = QLabel(f"{business_info['name']}")
        brand_title.setStyleSheet("""
            color: white;
            font-size: 32pt;
            font-weight: bold;
            letter-spacing: 2px;
        """)
        brand_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(brand_title)
        
        # Tagline
        tagline = QLabel("Sistema de Gestión Empresarial")
        tagline.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 13pt;
            margin-top: 10px;
        """)
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(tagline)
        
        left_layout.addSpacing(40)
        
        # Features
        features = [
            "✓ Control de Inventario",
            "✓ Punto de Venta",
            "✓ Reportes en Tiempo Real",
            "✓ Gestión de Clientes"
        ]
        
        for feature in features:
            feat_label = QLabel(feature)
            feat_label.setStyleSheet("""
                color: rgba(255, 255, 255, 0.85);
                font-size: 11pt;
                padding: 5px;
            """)
            feat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            left_layout.addWidget(feat_label)
        
        # RIGHT SIDE - Login Form
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
            }
        """)
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(60, 80, 60, 80)
        right_layout.setSpacing(25)
        right_panel.setLayout(right_layout)
        
        # Welcome text
        welcome = QLabel("Bienvenido")
        welcome.setStyleSheet("""
            color: #2c3e50;
            font-size: 28pt;
            font-weight: bold;
        """)
        welcome.setAlignment(Qt.AlignmentFlag.AlignLeft)
        right_layout.addWidget(welcome)
        
        subtitle = QLabel("Ingrese sus credenciales para continuar")
        subtitle.setStyleSheet("""
            color: #7f8c8d;
            font-size: 11pt;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignLeft)
        right_layout.addWidget(subtitle)
        
        right_layout.addSpacing(20)
        
        # Username field
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Usuario")
        self.input_username.setFont(QFont("Arial", 12))
        self.input_username.setMinimumHeight(50)
        self.input_username.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 2px solid #bdc3c7;
                background-color: transparent;
                padding: 10px 5px;
                color: #2c3e50;
                font-size: 13pt;
            }
            QLineEdit:focus {
                border-bottom: 2px solid #3498db;
            }
        """)
        right_layout.addWidget(self.input_username)
        
        right_layout.addSpacing(15)
        
        # Password field
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Contraseña")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setFont(QFont("Arial", 12))
        self.input_password.setMinimumHeight(50)
        self.input_password.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 2px solid #bdc3c7;
                background-color: transparent;
                padding: 10px 5px;
                color: #2c3e50;
                font-size: 13pt;
            }
            QLineEdit:focus {
                border-bottom: 2px solid #3498db;
            }
        """)
        self.input_password.returnPressed.connect(self.handle_login)
        right_layout.addWidget(self.input_password)
        
        right_layout.addSpacing(30)
        
        # Login button
        btn_login = QPushButton("INICIAR SESIÓN")
        btn_login.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        btn_login.setMinimumHeight(55)
        btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_login.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 8px;
                letter-spacing: 2px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2980b9, stop:1 #1f6fa8);
            }
            QPushButton:pressed {
                background: #1f6fa8;
            }
        """)
        btn_login.clicked.connect(self.handle_login)
        
        # Add shadow to button
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(52, 152, 219, 100))
        shadow.setOffset(0, 4)
        btn_login.setGraphicsEffect(shadow)
        
        right_layout.addWidget(btn_login)
        
        right_layout.addSpacing(20)
        
        # Default credentials hint
        '''hint = QLabel("Credenciales por defecto: admin / admin123")
        hint.setStyleSheet("""
            color: #95a5a6;
            font-size: 9pt;
            font-style: italic;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
        """)
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(hint)'''
        
        right_layout.addStretch()
        
        # Version footer
        version = QLabel("v1.0.2")
        version.setStyleSheet("""
            color: #bdc3c7;
            font-size: 8pt;
        """)
        version.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_layout.addWidget(version)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 3)
        
        self.setLayout(main_layout)
        
        # Focus on username
        self.input_username.setFocus()
        
    def handle_login(self):
        username = self.input_username.text().strip()
        password = self.input_password.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Por favor ingrese usuario y contraseña")
            return
        
        user = self.auth_controller.login(username, password)
        
        if user:
            self.user = user
            self.accept()
        else:
            QMessageBox.critical(self, "Error de Autenticación", 
                               "Usuario o contraseña incorrectos.\nPor favor, verifique sus credenciales.")
            self.input_password.clear()
            self.input_password.setFocus()
    
    def closeEvent(self, event):
        self.db.close()
        event.accept()
