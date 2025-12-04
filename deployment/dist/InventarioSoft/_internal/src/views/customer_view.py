from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
    QMessageBox, QFormLayout, QTabWidget, QCompleter, QDialog, QDoubleSpinBox,
    QGroupBox
)
from PyQt6.QtCore import Qt
from src.database.db import SessionLocal
from src.controllers.customer_controller import CustomerController
from src.controllers.config_controller import ConfigController

class CustomerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Clientes - Módulo 7")
        self.resize(1200, 750)
        
        self.db = SessionLocal()
        self.controller = CustomerController(self.db)
        self.config_controller = ConfigController(self.db)
        
        # Get exchange rate
        self.exchange_rate = self.config_controller.get_exchange_rate()
        
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
        self.id_number_input = QLineEdit()
        self.id_number_input.setPlaceholderText("Cédula o RIF")
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()
        
        btn_add = QPushButton("Agregar Cliente")
        btn_add.clicked.connect(self.add_customer)
        
        form_layout.addRow("Nombre:", self.name_input)
        form_layout.addRow("Cédula/RIF:", self.id_number_input)
        form_layout.addRow("Teléfono:", self.phone_input)
        form_layout.addRow("Dirección:", self.address_input)
        form_layout.addRow(btn_add)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Table
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(5)
        self.customer_table.setHorizontalHeaderLabels(["ID", "Nombre", "Cédula/RIF", "Teléfono", "Dirección"])
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
        
        self.customer_search = QLineEdit()
        self.customer_search.setPlaceholderText("Buscar cliente por nombre o cédula...")
        self.setup_customer_autocomplete()
        self.customer_search.returnPressed.connect(self.on_customer_selected)
        
        self.selected_customer_id = None
        
        btn_check = QPushButton("Ver Deuda")
        btn_check.clicked.connect(self.check_debt)
        
        selector_layout.addWidget(QLabel("Cliente:"))
        selector_layout.addWidget(self.customer_search)
        selector_layout.addWidget(btn_check)
        layout.addLayout(selector_layout)
        
        # Debt display
        self.lbl_debt = QLabel("Deuda Actual: $0 / Bs 0")
        self.lbl_debt.setStyleSheet("font-size: 18px; font-weight: bold; color: red;")
        layout.addWidget(self.lbl_debt)
        
        # Exchange rate info
        self.lbl_rate = QLabel(f"Tasa: 1 USD = {self.exchange_rate:.2f} Bs")
        self.lbl_rate.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(self.lbl_rate)
        
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
            id_number = self.id_number_input.text()
            phone = self.phone_input.text()
            address = self.address_input.text()
            
            self.controller.create_customer(name, id_number, phone, address)
            QMessageBox.information(self, "Éxito", "Cliente agregado")
            self.load_customers()
            self.load_customers_combo()
            
            self.name_input.clear()
            self.id_number_input.clear()
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
            self.customer_table.setItem(i, 2, QTableWidgetItem(c.id_number or ""))
            self.customer_table.setItem(i, 3, QTableWidgetItem(c.phone or ""))
            self.customer_table.setItem(i, 4, QTableWidgetItem(c.address or ""))

    def load_customers_combo(self):
        # Kept for compatibility
        pass

    def setup_customer_autocomplete(self):
        """Setup autocomplete for customer search"""
        customers = self.controller.get_all_customers()
        
        self.customer_map = {}
        suggestions = []
        for c in customers:
            # Add both name and id_number as searchable
            suggestion = c.name
            suggestions.append(suggestion)
            self.customer_map[suggestion] = c
            
            if c.id_number:
                suggestions.append(c.id_number)
                self.customer_map[c.id_number] = c
            
        completer = QCompleter(suggestions)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.customer_search.setCompleter(completer)

    def on_customer_selected(self):
        text = self.customer_search.text().strip()
        if not text:
            return
            
        customer = self.customer_map.get(text)
        if not customer:
            # Try finding by name
            # Note: This is a simple check, could be improved
            for name, c in self.customer_map.items():
                if text.lower() in name.lower():
                    customer = c
                    break
        
        if customer:
            self.selected_customer_id = customer.id
            self.check_debt()
        else:
            self.selected_customer_id = None
            QMessageBox.warning(self, "Error", "Cliente no encontrado")

    def check_debt(self):
        if not self.selected_customer_id:
            return
            
        debt = self.controller.get_customer_debt(self.selected_customer_id)
        debt_bs = debt * self.exchange_rate
        self.lbl_debt.setText(f"Deuda Actual: ${debt:,.2f} / Bs {debt_bs:,.2f}")

    def record_payment(self):
        if not self.selected_customer_id:
            QMessageBox.warning(self, "Error", "Seleccione un cliente")
            return
        
        # Get current debt
        current_debt = self.controller.get_customer_debt(self.selected_customer_id)
        
        # Create custom dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Registrar Pago")
        dialog.setMinimumWidth(350)
        
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        # Show current debt in both currencies
        debt_bs = current_debt * self.exchange_rate
        debt_label = QLabel(f"Deuda Actual:\n${current_debt:,.2f} / Bs {debt_bs:,.2f}")
        debt_label.setStyleSheet("font-size: 16px; font-weight: bold; color: red; padding: 10px;")
        layout.addWidget(debt_label)
        
        # Currency selector
        from PyQt6.QtWidgets import QRadioButton, QButtonGroup
        currency_group = QButtonGroup(dialog)
        
        radio_usd = QRadioButton("Pagar en USD")
        radio_bs = QRadioButton("Pagar en Bs")
        radio_usd.setChecked(True)
        
        currency_group.addButton(radio_usd, 0)
        currency_group.addButton(radio_bs, 1)
        
        layout.addWidget(radio_usd)
        layout.addWidget(radio_bs)
        
        # Payment input with QDoubleSpinBox
        form_layout = QFormLayout()
        amount_spin = QDoubleSpinBox()
        amount_spin.setRange(0.01, 999999.99)
        amount_spin.setDecimals(2)
        amount_spin.setSingleStep(0.50)
        amount_spin.setValue(current_debt if current_debt > 0 else 0.01)
        amount_spin.setPrefix("$ ")
        amount_spin.setStyleSheet("font-size: 18px; padding: 5px;")
        
        # Force dot as decimal separator (not comma)
        from PyQt6.QtCore import QLocale
        amount_spin.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        
        # Function to update currency display
        def update_currency_display():
            if radio_usd.isChecked():
                amount_spin.setPrefix("$ ")
                amount_spin.setValue(current_debt if current_debt > 0 else 0.01)
            else:
                amount_spin.setPrefix("Bs ")
                amount_spin.setValue(debt_bs if debt_bs > 0 else 0.01)
                
        radio_usd.toggled.connect(update_currency_display)
        radio_bs.toggled.connect(update_currency_display)
        
        amount_spin.selectAll()
        
        form_layout.addRow("Monto del Pago:", amount_spin)
        layout.addLayout(form_layout)
        
        # Instructions
        instructions = QLabel("Use las flechas ↑↓ o escriba el monto.\nEjemplo: 1.50 para un peso cincuenta centavos")
        instructions.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")
        layout.addWidget(instructions)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("Registrar Pago")
        btn_ok.setStyleSheet("background-color: green; color: white; padding: 10px; font-size: 12px;")
        btn_ok.clicked.connect(dialog.accept)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet("background-color: gray; color: white; padding: 10px; font-size: 12px;")
        btn_cancel.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        layout.addLayout(btn_layout)
        
        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            amount = amount_spin.value()
            
            # Get selected currency
            currency = "USD" if radio_usd.isChecked() else "Bs"
            
            # Convert to USD if paying in Bs
            amount_usd = amount
            if currency == "Bs":
                amount_usd = amount / self.exchange_rate
            
            if amount_usd <= 0:
                QMessageBox.warning(self, "Error", "El monto debe ser mayor a 0")
                return
            
            try:
                # Record payment in USD (always store in USD)
                self.controller.add_payment(
                    self.selected_customer_id, 
                    amount_usd,
                    f"Pago en {currency}: {amount:,.2f}"
                )
                
                # Calculate remaining debt
                remaining_debt = self.controller.get_customer_debt(self.selected_customer_id)
                remaining_bs = remaining_debt * self.exchange_rate
                
                if remaining_debt < 0:
                    QMessageBox.information(
                        self, 
                        "Pago Registrado", 
                        f"Pago registrado exitosamente.\n\n"
                        f"CRÉDITO A FAVOR: ${abs(remaining_debt):,.2f} / Bs {abs(remaining_bs):,.2f}"
                    )
                elif remaining_debt == 0:
                    QMessageBox.information(
                        self, 
                        "Pago Registrado", 
                        "Pago registrado exitosamente.\n\nDeuda saldada completamente."
                    )
                else:
                    QMessageBox.information(
                        self, 
                        "Pago Registrado", 
                        f"Pago registrado exitosamente.\n\n"
                        f"Deuda Restante: ${remaining_debt:,.2f} / Bs {remaining_bs:,.2f}"
                    )
                
                self.check_debt()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def closeEvent(self, event):
        self.db.close()
        event.accept()
