from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from src.database.db import SessionLocal
from src.controllers.auth_controller import AuthController

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iniciar Sesión")
        self.resize(300, 150)
        
        self.db = SessionLocal()
        self.auth = AuthController(self.db)
        self.user = None
        
        # Ensure admin exists
        self.auth.init_admin()
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuario")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.handle_login)
        
        btn_login = QPushButton("Entrar")
        btn_login.clicked.connect(self.handle_login)
        
        self.layout.addWidget(QLabel("Bienvenido al Sistema"))
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(btn_login)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        user = self.auth.login(username, password)
        if user:
            self.user = user
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Credenciales incorrectas")

    def closeEvent(self, event):
        self.db.close()
        event.accept()
