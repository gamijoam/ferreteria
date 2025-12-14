from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget,
    QFormLayout, QGroupBox, QTextEdit
)
from src.database.db import SessionLocal
from src.controllers.supplier_controller import SupplierController

class SupplierWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Proveedores - Módulo 14")
        self.resize(1200, 750)
        
        self.db = SessionLocal()
        self.controller = SupplierController(self.db)
        self.current_supplier = None
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.setup_list_tab()
        self.setup_form_tab()

    def setup_list_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        layout.addWidget(QLabel("Lista de Proveedores"))
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Contacto", "Teléfono", "Email", "Acciones"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        btn_refresh = QPushButton("Actualizar")
        btn_refresh.clicked.connect(self.load_suppliers)
        layout.addWidget(btn_refresh)
        
        self.tabs.addTab(tab, "Proveedores")
        self.load_suppliers()

    def setup_form_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        form_group = QGroupBox("Crear/Editar Proveedor")
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(80)
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        
        form_layout.addRow("Nombre*:", self.name_input)
        form_layout.addRow("Persona Contacto:", self.contact_input)
        form_layout.addRow("Teléfono:", self.phone_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Dirección:", self.address_input)
        form_layout.addRow("Notas:", self.notes_input)
        
        btn_save = QPushButton("Guardar Proveedor")
        btn_save.clicked.connect(self.save_supplier)
        btn_save.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        form_layout.addRow(btn_save)
        
        btn_clear = QPushButton("Limpiar Formulario")
        btn_clear.clicked.connect(self.clear_form)
        form_layout.addRow(btn_clear)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        self.lbl_mode = QLabel("Modo: Crear Nuevo Proveedor")
        self.lbl_mode.setStyleSheet("font-weight: bold; color: blue;")
        layout.addWidget(self.lbl_mode)
        
        layout.addStretch()
        self.tabs.addTab(tab, "Crear/Editar")

    def load_suppliers(self):
        suppliers = self.controller.get_all_suppliers(active_only=False)
        self.table.setRowCount(0)
        
        for i, supplier in enumerate(suppliers):
            self.table.insertRow(i)
            self.table.setRowHeight(i, 50)
            
            self.table.setItem(i, 0, QTableWidgetItem(str(supplier.id)))
            self.table.setItem(i, 1, QTableWidgetItem(supplier.name))
            self.table.setItem(i, 2, QTableWidgetItem(supplier.contact_person or ""))
            self.table.setItem(i, 3, QTableWidgetItem(supplier.phone or ""))
            self.table.setItem(i, 4, QTableWidgetItem(supplier.email or ""))
            
            # Action buttons
            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(0, 0, 0, 0)
            
            btn_edit = QPushButton("Editar")
            btn_edit.setFixedWidth(60)
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            btn_edit.clicked.connect(lambda checked, s=supplier: self.edit_supplier(s))
            
            btn_toggle = QPushButton("Activar" if not supplier.is_active else "Desact.")
            btn_toggle.setFixedWidth(60)
            btn_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                }
            """)
            btn_toggle.clicked.connect(lambda checked, s=supplier: self.toggle_supplier(s))
            
            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_toggle)
            btn_widget.setLayout(btn_layout)
            
            self.table.setCellWidget(i, 5, btn_widget)

    def save_supplier(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        
        contact = self.contact_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        address = self.address_input.toPlainText().strip()
        notes = self.notes_input.toPlainText().strip()
        
        if self.current_supplier:
            # Update
            success, msg = self.controller.update_supplier(
                self.current_supplier.id,
                name=name,
                contact_person=contact,
                phone=phone,
                email=email,
                address=address,
                notes=notes
            )
        else:
            # Create
            supplier, msg = self.controller.create_supplier(
                name, contact, phone, email, address, notes
            )
            success = supplier is not None
        
        if success:
            QMessageBox.information(self, "Éxito", "Proveedor guardado correctamente")
            self.clear_form()
            self.load_suppliers()
            self.tabs.setCurrentIndex(0)
        else:
            QMessageBox.critical(self, "Error", msg)

    def edit_supplier(self, supplier):
        self.current_supplier = supplier
        self.name_input.setText(supplier.name)
        self.contact_input.setText(supplier.contact_person or "")
        self.phone_input.setText(supplier.phone or "")
        self.email_input.setText(supplier.email or "")
        self.address_input.setPlainText(supplier.address or "")
        self.notes_input.setPlainText(supplier.notes or "")
        
        self.lbl_mode.setText(f"Modo: Editando '{supplier.name}'")
        self.lbl_mode.setStyleSheet("font-weight: bold; color: orange;")
        self.tabs.setCurrentIndex(1)

    def clear_form(self):
        self.current_supplier = None
        self.name_input.clear()
        self.contact_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.address_input.clear()
        self.notes_input.clear()
        self.lbl_mode.setText("Modo: Crear Nuevo Proveedor")
        self.lbl_mode.setStyleSheet("font-weight: bold; color: blue;")

    def toggle_supplier(self, supplier):
        action = "activar" if not supplier.is_active else "desactivar"
        reply = QMessageBox.question(
            self, "Confirmar",
            f"¿Está seguro de {action} al proveedor '{supplier.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if supplier.is_active:
                success, msg = self.controller.deactivate_supplier(supplier.id)
            else:
                success, msg = self.controller.activate_supplier(supplier.id)
            
            if success:
                QMessageBox.information(self, "Éxito", msg)
                self.load_suppliers()
            else:
                QMessageBox.critical(self, "Error", msg)

    def closeEvent(self, event):
        self.db.close()
        event.accept()
