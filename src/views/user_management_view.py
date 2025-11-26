from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, 
    QTabWidget, QFormLayout, QGroupBox, QComboBox, QCheckBox
)
from src.database.db import SessionLocal
from src.controllers.auth_controller import AuthController
from src.models.models import UserRole

class UserManagementWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Usuarios - Módulo 11")
        self.resize(900, 600)
        
        self.db = SessionLocal()
        self.controller = AuthController(self.db)
        self.current_user = None
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.setup_user_list_tab()
        self.setup_user_form_tab()

    def setup_user_list_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        layout.addWidget(QLabel("Lista de Usuarios del Sistema"))
        
        # Table
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels([
            "ID", "Usuario", "Rol", "Estado", "Acciones"
        ])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.user_table)
        
        # Refresh button
        btn_refresh = QPushButton("Actualizar Lista")
        btn_refresh.clicked.connect(self.load_users)
        layout.addWidget(btn_refresh)
        
        self.tabs.addTab(tab, "Usuarios")
        self.load_users()

    def setup_user_form_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Form
        form_group = QGroupBox("Crear/Editar Usuario")
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.role_combo = QComboBox()
        self.role_combo.addItem("Administrador", UserRole.ADMIN)
        self.role_combo.addItem("Cajero", UserRole.CASHIER)
        self.role_combo.addItem("Bodeguero", UserRole.WAREHOUSE)
        
        self.active_checkbox = QCheckBox("Usuario Activo")
        self.active_checkbox.setChecked(True)
        
        btn_save = QPushButton("Guardar Usuario")
        btn_save.clicked.connect(self.save_user)
        btn_save.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        
        btn_clear = QPushButton("Limpiar Formulario")
        btn_clear.clicked.connect(self.clear_form)
        
        form_layout.addRow("Nombre de Usuario:", self.username_input)
        form_layout.addRow("Contraseña:", self.password_input)
        form_layout.addRow("Rol:", self.role_combo)
        form_layout.addRow("", self.active_checkbox)
        form_layout.addRow(btn_save)
        form_layout.addRow(btn_clear)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Info label
        self.lbl_form_mode = QLabel("Modo: Crear Nuevo Usuario")
        self.lbl_form_mode.setStyleSheet("font-weight: bold; color: blue;")
        layout.addWidget(self.lbl_form_mode)
        
        layout.addStretch()
        
        self.tabs.addTab(tab, "Crear/Editar")

    def load_users(self):
        users = self.controller.get_all_users()
        self.user_table.setRowCount(0)
        
        for i, user in enumerate(users):
            self.user_table.insertRow(i)
            self.user_table.setItem(i, 0, QTableWidgetItem(str(user.id)))
            self.user_table.setItem(i, 1, QTableWidgetItem(user.username))
            self.user_table.setItem(i, 2, QTableWidgetItem(user.role.value))
            self.user_table.setItem(i, 3, QTableWidgetItem("Activo" if user.is_active else "Inactivo"))
            
            # Action buttons
            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(0, 0, 0, 0)
            
            btn_edit = QPushButton("Editar")
            btn_edit.clicked.connect(lambda checked, u=user: self.edit_user(u))
            
            btn_deactivate = QPushButton("Desactivar" if user.is_active else "Activar")
            btn_deactivate.clicked.connect(lambda checked, u=user: self.toggle_user_status(u))
            
            btn_password = QPushButton("Cambiar Contraseña")
            btn_password.clicked.connect(lambda checked, u=user: self.change_password(u))
            
            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_deactivate)
            btn_layout.addWidget(btn_password)
            btn_widget.setLayout(btn_layout)
            
            self.user_table.setCellWidget(i, 4, btn_widget)

    def save_user(self):
        try:
            username = self.username_input.text().strip()
            password = self.password_input.text()
            role = self.role_combo.currentData()
            is_active = self.active_checkbox.isChecked()
            
            if not username:
                raise ValueError("El nombre de usuario es obligatorio")
            
            if self.current_user:
                # Update existing user
                self.controller.update_user(
                    self.current_user.id,
                    username=username,
                    role=role,
                    is_active=is_active
                )
                
                # Change password if provided
                if password:
                    self.controller.change_password(self.current_user.id, password)
                
                QMessageBox.information(self, "Éxito", "Usuario actualizado correctamente")
            else:
                # Create new user
                if not password:
                    raise ValueError("La contraseña es obligatoria para nuevos usuarios")
                
                self.controller.create_user(username, password, role)
                QMessageBox.information(self, "Éxito", "Usuario creado correctamente")
            
            self.clear_form()
            self.load_users()
            self.tabs.setCurrentIndex(0)  # Switch to user list
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def edit_user(self, user):
        self.current_user = user
        self.username_input.setText(user.username)
        self.password_input.clear()
        
        # Set role
        for i in range(self.role_combo.count()):
            if self.role_combo.itemData(i) == user.role:
                self.role_combo.setCurrentIndex(i)
                break
        
        self.active_checkbox.setChecked(user.is_active)
        self.lbl_form_mode.setText(f"Modo: Editando usuario '{user.username}'")
        self.lbl_form_mode.setStyleSheet("font-weight: bold; color: orange;")
        
        self.tabs.setCurrentIndex(1)  # Switch to form

    def clear_form(self):
        self.current_user = None
        self.username_input.clear()
        self.password_input.clear()
        self.role_combo.setCurrentIndex(0)
        self.active_checkbox.setChecked(True)
        self.lbl_form_mode.setText("Modo: Crear Nuevo Usuario")
        self.lbl_form_mode.setStyleSheet("font-weight: bold; color: blue;")

    def toggle_user_status(self, user):
        action = "desactivar" if user.is_active else "activar"
        reply = QMessageBox.question(
            self, "Confirmar", 
            f"¿Está seguro de {action} al usuario '{user.username}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.controller.update_user(user.id, is_active=not user.is_active)
                QMessageBox.information(self, "Éxito", f"Usuario {action}do correctamente")
                self.load_users()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def change_password(self, user):
        from PyQt6.QtWidgets import QInputDialog
        
        new_password, ok = QInputDialog.getText(
            self, "Cambiar Contraseña", 
            f"Nueva contraseña para '{user.username}':",
            QLineEdit.EchoMode.Password
        )
        
        if ok and new_password:
            try:
                self.controller.change_password(user.id, new_password)
                QMessageBox.information(self, "Éxito", "Contraseña cambiada correctamente")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def closeEvent(self, event):
        self.db.close()
        event.accept()
