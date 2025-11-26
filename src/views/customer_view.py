from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, 
    QTabWidget, QFormLayout, QGroupBox, QComboBox, QInputDialog
)
from src.database.db import SessionLocal
from src.controllers.customer_controller import CustomerController

class CustomerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Clientes - Módulo 7")
        self.resize(900, 600)
        
        self.db = SessionLocal()
        self.controller = CustomerController(self.db)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.setup_customer_tab()
        self.setup_debt_tab()

    def setup_customer_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Form
        form_group = QGroupBox("Nuevo Cliente")
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()
        
        btn_add = QPushButton("Agregar Cliente")
        btn_add.clicked.connect(self.add_customer)
        
        form_layout.addRow("Nombre:", self.name_input)
        form_layout.addRow("Teléfono:", self.phone_input)
        form_layout.addRow("Dirección:", self.address_input)
        form_layout.addRow(btn_add)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Table
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(4)
        self.customer_table.setHorizontalHeaderLabels(["ID", "Nombre", "Teléfono", "Dirección"])
        self.customer_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.customer_table)
        
        btn_refresh = QPushButton("Actualizar Lista")
        btn_refresh.clicked.connect(self.load_customers)
        layout.addWidget(btn_refresh)
        
        self.tabs.addTab(tab, "Clientes")
        self.load_customers()

    def setup_debt_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Customer selector
        selector_layout = QHBoxLayout()
        self.debt_customer_combo = QComboBox()
        self.load_customers_combo()
        
        btn_check = QPushButton("Ver Deuda")
        btn_check.clicked.connect(self.check_debt)
        
        selector_layout.addWidget(QLabel("Cliente:"))
        selector_layout.addWidget(self.debt_customer_combo)
        selector_layout.addWidget(btn_check)
        layout.addLayout(selector_layout)
        
        # Debt display
        self.lbl_debt = QLabel("Deuda Actual: $0")
        self.lbl_debt.setStyleSheet("font-size: 20px; font-weight: bold; color: red;")
        layout.addWidget(self.lbl_debt)
        
        # Payment
        btn_pay = QPushButton("Registrar Pago")
        btn_pay.setStyleSheet("background-color: green; color: white; padding: 10px;")
        btn_pay.clicked.connect(self.record_payment)
        layout.addWidget(btn_pay)
        
        layout.addStretch()
        
        self.tabs.addTab(tab, "Cuentas Corrientes")

    def add_customer(self):
        try:
            name = self.name_input.text()
            phone = self.phone_input.text()
            address = self.address_input.text()
            
            self.controller.create_customer(name, phone, address)
            QMessageBox.information(self, "Éxito", "Cliente agregado")
            self.load_customers()
            self.load_customers_combo()
            
            self.name_input.clear()
            self.phone_input.clear()
            self.address_input.clear()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def load_customers(self):
        customers = self.controller.get_all_customers()
        self.customer_table.setRowCount(0)
        
        for i, c in enumerate(customers):
            self.customer_table.insertRow(i)
            self.customer_table.setItem(i, 0, QTableWidgetItem(str(c.id)))
            self.customer_table.setItem(i, 1, QTableWidgetItem(c.name))
            self.customer_table.setItem(i, 2, QTableWidgetItem(c.phone or ""))
            self.customer_table.setItem(i, 3, QTableWidgetItem(c.address or ""))

    def load_customers_combo(self):
        self.debt_customer_combo.clear()
        customers = self.controller.get_all_customers()
        for c in customers:
            self.debt_customer_combo.addItem(c.name, c.id)

    def check_debt(self):
        customer_id = self.debt_customer_combo.currentData()
        if not customer_id:
            return
            
        debt = self.controller.get_customer_debt(customer_id)
        self.lbl_debt.setText(f"Deuda Actual: ${debt:,.0f}")

    def record_payment(self):
        customer_id = self.debt_customer_combo.currentData()
        if not customer_id:
            QMessageBox.warning(self, "Error", "Seleccione un cliente")
            return
            
        amount, ok = QInputDialog.getDouble(self, "Registrar Pago", "Monto del pago:")
        if ok and amount > 0:
            try:
                self.controller.record_payment(customer_id, amount)
                QMessageBox.information(self, "Éxito", "Pago registrado")
                self.check_debt()  # Refresh
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def closeEvent(self, event):
        self.db.close()
        event.accept()
