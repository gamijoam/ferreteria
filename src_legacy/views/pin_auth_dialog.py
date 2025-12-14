from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from src.database.db import SessionLocal
from src.models.models import User

class PINAuthDialog(QDialog):
    """Dialog for PIN authorization"""
    
    def __init__(self, parent=None, action_description="realizar esta acción"):
        super().__init__(parent)
        self.setWindowTitle("Autorización Requerida")
        self.resize(350, 200)
        self.authorized_user = None
        self.action_description = action_description
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        lbl_title = QLabel(f"Se requiere autorización para {self.action_description}")
        lbl_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        lbl_title.setWordWrap(True)
        lbl_title.setStyleSheet("color: #d32f2f; padding: 10px;")
        layout.addWidget(lbl_title)
        
        # Username input
        layout.addWidget(QLabel("Usuario:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ingrese su usuario")
        layout.addWidget(self.username_input)
        
        # PIN input
        layout.addWidget(QLabel("PIN:"))
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setPlaceholderText("Ingrese su PIN")
        self.pin_input.setMaxLength(6)
        layout.addWidget(self.pin_input)
        
        # Info label
        lbl_info = QLabel("Solo usuarios autorizados (Admin/Manager) pueden aprobar esta acción")
        lbl_info.setStyleSheet("color: #666; font-size: 9pt; font-style: italic;")
        lbl_info.setWordWrap(True)
        layout.addWidget(lbl_info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_ok = QPushButton("Autorizar")
        btn_ok.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; font-weight: bold;")
        btn_ok.clicked.connect(self.validate_pin)
        btn_ok.setDefault(True)
        btn_layout.addWidget(btn_ok)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Focus on username
        self.username_input.setFocus()
    
    def validate_pin(self):
        """Validate PIN and authorize"""
        username = self.username_input.text().strip()
        pin = self.pin_input.text().strip()
        
        if not username or not pin:
            QMessageBox.warning(self, "Error", "Debe ingresar usuario y PIN")
            return
        
        # Validate PIN
        db = SessionLocal()
        try:
            user = db.query(User).filter(
                User.username == username,
                User.is_active == True
            ).first()
            
            if not user:
                QMessageBox.warning(self, "Error", "Usuario no encontrado o inactivo")
                return
            
            # Check if user has authorization role
            if user.role.value not in ["ADMIN", "MANAGER"]:
                QMessageBox.warning(self, "Error", "Este usuario no tiene permisos para autorizar descuentos")
                return
            
            # Check PIN
            if not user.pin:
                QMessageBox.warning(self, "Error", "Este usuario no tiene PIN configurado. Configure un PIN en Gestión de Usuarios")
                return
            
            if user.pin != pin:
                QMessageBox.warning(self, "Error", "PIN incorrecto")
                return
            
            # Authorization successful
            self.authorized_user = user
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al validar PIN: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    def request_authorization(parent=None, action_description="realizar esta acción"):
        """Static method to request authorization. Returns (authorized, user) tuple"""
        dialog = PINAuthDialog(parent, action_description)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            return True, dialog.authorized_user
        else:
            return False, None
