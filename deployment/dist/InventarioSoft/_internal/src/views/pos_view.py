from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QFrame, QComboBox, QCompleter, QDoubleSpinBox,
    QGroupBox, QFormLayout
)
from PyQt6.QtGui import QKeySequence, QFont, QShortcut
from PyQt6.QtCore import Qt
from src.database.db import SessionLocal
from src.controllers.pos_controller import POSController
from src.controllers.customer_controller import CustomerController
from src.controllers.quote_controller import QuoteController
from src.controllers.config_controller import ConfigController

class POSWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Punto de Venta (POS) - Módulo 3")
        self.resize(1200, 750)
        
        self.db = SessionLocal()
        self.controller = POSController(self.db)
        self.customer_controller = CustomerController(self.db)
        self.quote_controller = QuoteController(self.db)
        self.config_controller = ConfigController(self.db)
        
        # Get exchange rate
        self.exchange_rate = self.config_controller.get_exchange_rate()
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        # Main horizontal layout: Left (search + table) | Right (controls)
        main_layout = QHBoxLayout()
        
        # LEFT PANEL: Search and Table
        left_panel = QVBoxLayout()
        
        # Search Bar (now with more space)
        search_frame = QFrame()
        search_layout = QVBoxLayout()
        search_frame.setLayout(search_layout)
        search_frame.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
        
        lbl_scan = QLabel("🔍 Buscar Producto (F1):")
        lbl_scan.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        search_layout.addWidget(lbl_scan)
        
        self.input_scan = QLineEdit()
        self.input_scan.setFont(QFont("Arial", 16))
        self.input_scan.setPlaceholderText("Ingrese SKU o Nombre del Producto...")
        self.input_scan.returnPressed.connect(self.handle_add_item)
        self.input_scan.setMinimumHeight(45)
        search_layout.addWidget(self.input_scan)
        
        # Setup autocomplete
        self.setup_autocomplete()
        
        left_panel.addWidget(search_frame)
        
        # RIGHT PANEL: Controls
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)
        
        # Control Group 1: Sale Mode
        mode_group = QGroupBox("Modo de Venta")
        mode_layout = QVBoxLayout()
        
        self.check_box_mode = QCheckBox("Vender por Caja (F2)")
        self.check_box_mode.setFont(QFont("Arial", 11))
        mode_layout.addWidget(self.check_box_mode)
        
        mode_group.setLayout(mode_layout)
        right_panel.addWidget(mode_group)
        
        # Control Group 2: Currency
        currency_group = QGroupBox("Moneda")
        currency_layout = QFormLayout()
        
        self.currency_combo = QComboBox()
        self.currency_combo.setFont(QFont("Arial", 11))
        self.currency_combo.addItems(["USD", "Bs"])
        self.currency_combo.setCurrentIndex(1)  # Default to Bs
        self.currency_combo.currentTextChanged.connect(self.on_currency_changed)
        
        currency_layout.addRow("Venta en:", self.currency_combo)
        currency_group.setLayout(currency_layout)
        right_panel.addWidget(currency_group)
        
        # Control Group 3: Payment Method
        payment_group = QGroupBox("Método de Pago")
        payment_layout = QVBoxLayout()
        
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.setFont(QFont("Arial", 11))
        self.payment_method_combo.addItems([
            "Efectivo Bs",
            "Efectivo USD",
            "Transferencia Bs / Pago Móvil",
            "Transferencia USD",
            "Tarjeta Débito/Crédito",
            "Crédito (Fiado)"
        ])
        self.payment_method_combo.currentTextChanged.connect(self.on_payment_method_changed)
        payment_layout.addWidget(self.payment_method_combo)
        
        # Credit Checkbox (Restored)
        self.credit_check = QCheckBox("Venta a Crédito")
        self.credit_check.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.credit_check.setStyleSheet("color: #d32f2f;")
        self.credit_check.toggled.connect(self.on_credit_check_toggled)
        payment_layout.addWidget(self.credit_check)
        
        payment_group.setLayout(payment_layout)
        right_panel.addWidget(payment_group)
        
        # Control Group 4: Customer
        customer_group = QGroupBox("Cliente (Opcional)")
        customer_layout = QVBoxLayout()
        
        self.customer_combo = QComboBox()
        self.customer_combo.setFont(QFont("Arial", 10))
        self.customer_combo.setVisible(True)
        self.load_customers()
        customer_layout.addWidget(self.customer_combo)
        
        customer_group.setLayout(customer_layout)
        right_panel.addWidget(customer_group)
        
        # Exchange Rate Info
        self.lbl_rate = QLabel(f"Tasa: 1 USD = {self.exchange_rate:.2f} Bs")
        self.lbl_rate.setFont(QFont("Arial", 10))
        self.lbl_rate.setStyleSheet("color: #666; padding: 5px; background-color: #fff3cd; border-radius: 3px;")
        self.lbl_rate.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(self.lbl_rate)
        
        right_panel.addStretch()
        
        # Table (in left panel)
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Producto", "Cant.", "Tipo", "Precio Unit.", "Subtotal", "Eliminar"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setFont(QFont("Arial", 12))
        
        # Connect cell change signal
        self.table.cellChanged.connect(self.on_cell_changed)
        
        left_panel.addWidget(self.table)
        
        # Bottom: Total & Actions (in left panel)
        bottom_frame = QFrame()
        bottom_layout = QHBoxLayout()
        bottom_frame.setLayout(bottom_layout)
        
        self.lbl_total = QLabel(f"Total: $0 / Bs 0")
        self.lbl_total.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.lbl_total.setStyleSheet("color: green;")
        
        btn_pay = QPushButton("COBRAR (F12)")
        btn_pay.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        btn_pay.setStyleSheet("background-color: #28a745; color: white; padding: 15px; border-radius: 5px;")
        btn_pay.clicked.connect(self.handle_payment)
        
        btn_quote = QPushButton("GUARDAR COTIZACIÓN (F4)")
        btn_quote.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        btn_quote.setStyleSheet("background-color: #ff9800; color: white; padding: 15px; border-radius: 5px;")
        btn_quote.clicked.connect(self.save_as_quote)
        
        bottom_layout.addWidget(self.lbl_total)
        bottom_layout.addStretch()
        bottom_layout.addWidget(btn_quote)
        bottom_layout.addWidget(btn_pay)
        
        left_panel.addWidget(bottom_frame)
        
        # Add panels to main layout
        main_layout.addLayout(left_panel, 3)  # 75% width
        main_layout.addLayout(right_panel, 1)  # 25% width
        
        self.layout.addLayout(main_layout)
        
        # Focus input initially
        self.input_scan.setFocus()

    def setup_shortcuts(self):
        QShortcut(QKeySequence("F1"), self, self.focus_input)
        QShortcut(QKeySequence("F2"), self, self.toggle_box_mode)
        QShortcut(QKeySequence("F3"), self, self.toggle_credit)
        QShortcut(QKeySequence("F4"), self, self.save_as_quote)
        QShortcut(QKeySequence("F12"), self, self.handle_payment)
        QShortcut(QKeySequence("Del"), self, self.remove_selected_item)

    def focus_input(self):
        self.input_scan.setFocus()
        self.input_scan.selectAll()

    def toggle_box_mode(self):
        self.check_box_mode.setChecked(not self.check_box_mode.isChecked())
        self.focus_input()

    def toggle_credit(self):
        self.check_credit.setChecked(not self.check_credit.isChecked())
        self.focus_input()

    def toggle_credit_mode(self, checked):
        self.customer_combo.setVisible(checked)
        if checked:
            self.load_customers()

    def load_customers(self):
        self.customer_combo.clear()
        self.customer_combo.addItem("Seleccione Cliente...", None)
        customers = self.customer_controller.get_all_customers()
        for c in customers:
            self.customer_combo.addItem(c.name, c.id)
    
    def setup_autocomplete(self):
        """Setup autocomplete for product search"""
        from src.models.models import Product
        
        # Get all active products
        products = self.db.query(Product).filter(Product.is_active == True).all()
        
        # Create list of suggestions: "Name - SKU - $Price"
        suggestions = []
        for p in products:
            sku_part = f" - {p.sku}" if p.sku else ""
            suggestion = f"{p.name}{sku_part} - ${p.price:,.2f}"
            suggestions.append(suggestion)
        
        # Create completer
        completer = QCompleter(suggestions)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        
        # Set completer to input
        self.input_scan.setCompleter(completer)

    def handle_add_item(self):
        text = self.input_scan.text().strip()
        if not text:
            return
        
        # If text contains " - $" it's from autocomplete, extract the product name/SKU
        if " - $" in text:
            # Format is "Name - SKU - $Price" or "Name - $Price"
            # Extract just the name part (before first " - ")
            text = text.split(" - ")[0].strip()
            
        is_box = self.check_box_mode.isChecked()
        qty = 1.0 
        
        success, msg = self.controller.add_to_cart(text, qty, is_box)
        
        if success:
            self.refresh_table()
            self.input_scan.clear()
        else:
            QMessageBox.warning(self, "Alerta", msg)
        
        self.focus_input()

    def refresh_table(self):
        # Block signals to prevent infinite loop when setting items
        self.table.blockSignals(True)
        
        self.table.setRowCount(0)
        total = 0
        for i, item in enumerate(self.controller.cart):
            self.table.insertRow(i)
            
            # Product Name (Not editable)
            name_item = QTableWidgetItem(item["name"])
            name_item.setFlags(name_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, name_item)
            
            # Quantity (Editable)
            qty_item = QTableWidgetItem(str(item["quantity"]))
            self.table.setItem(i, 1, qty_item)
            
            # Type (Not editable) - Show unit type (Kg, Metro, etc.) or CAJA
            if item["is_box"]:
                type_text = "CAJA"
            else:
                type_text = item.get("unit_type", "Unidad")
            type_item = QTableWidgetItem(type_text)
            type_item.setFlags(type_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 2, type_item)
            
            # Unit Price (Not editable)
            price_item = QTableWidgetItem(f"${item['unit_price']:,.2f}")
            price_item.setFlags(price_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 3, price_item)
            
            # Subtotal (Not editable)
            subtotal_item = QTableWidgetItem(f"${item['subtotal']:,.2f}")
            subtotal_item.setFlags(subtotal_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 4, subtotal_item)
            
            # Delete Button
            btn_del = QPushButton("Eliminar")
            btn_del.setFixedWidth(70)
            btn_del.setStyleSheet("""
                QPushButton {
                    background-color: #F44336;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #D32F2F;
                }
            """)
            btn_del.clicked.connect(lambda checked, idx=i: self.remove_item(idx))
            self.table.setCellWidget(i, 5, btn_del)
            
            total += item["subtotal"]
            
        # Calculate total in Bs
        total_bs = total * self.exchange_rate
        
        self.lbl_total.setText(f"Total: ${total:,.2f} / Bs {total_bs:,.2f}")
        
        self.table.blockSignals(False)
    
    def on_currency_changed(self, currency):
        """Handle currency selection change"""
        # Refresh display to show prices in selected currency
        self.refresh_table()

    def on_cell_changed(self, row, column):
        # Column 1 is Quantity
        if column == 1:
            try:
                new_qty_str = self.table.item(row, column).text()
                try:
                    new_qty = float(new_qty_str)
                except ValueError:
                    raise ValueError("Debe ser un número válido")
                
                if new_qty <= 0:
                    raise ValueError("Debe ser mayor a 0")
                
                # Update Controller
                success, msg = self.controller.update_quantity(row, new_qty)
                
                if not success:
                    QMessageBox.warning(self, "Stock Insuficiente", msg)
                    # Revert change (refresh table from controller state)
                    self.refresh_table()
                else:
                    # Refresh to update subtotal and total
                    self.refresh_table()
                    
            except ValueError:
                QMessageBox.warning(self, "Error", "Ingrese una cantidad válida")
                self.refresh_table()
        
        self.focus_input()

    def remove_item(self, index):
        self.controller.remove_from_cart(index)
        self.refresh_table()
        self.focus_input()

    def remove_selected_item(self):
        row = self.table.currentRow()
        if row >= 0:
            self.remove_item(row)

    def handle_payment(self):
        if not self.controller.cart:
            return
        
        payment_method = self.payment_method_combo.currentText()
        is_credit = self.credit_check.isChecked() # Use checkbox as truth
        # Optional: Save customer for all sales if selected
        customer_id = self.customer_combo.currentData()
        
        if is_credit:
            if not customer_id:
                QMessageBox.warning(self, "Error", "Debe seleccionar un cliente para venta a crédito")
                return
            
        reply = QMessageBox.question(
            self, "Confirmar Venta", 
            f"¿Procesar venta por {self.lbl_total.text()}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Get currency and exchange rate
            currency = self.currency_combo.currentText()
            
            success, msg, ticket = self.controller.finalize_sale(
                payment_method=payment_method,
                customer_id=customer_id,
                is_credit=is_credit,
                currency=currency,
                exchange_rate=self.exchange_rate
            )
            if success:
                if is_credit:
                    QMessageBox.information(self, "Venta a Crédito Exitosa", 
                                          f"Venta registrada a crédito.\\n\\n{ticket}")
                else:
                    QMessageBox.information(self, "Venta Exitosa", f"Ticket generado:\\n\\n{ticket}")
                self.refresh_table()
                self.payment_method_combo.setCurrentIndex(0)  # Reset to Efectivo
            else:
                QMessageBox.critical(self, "Error", msg)
        
        self.focus_input()

    def on_payment_method_changed(self, text):
        # Sync checkbox with combo
        is_credit = (text == "Crédito (Fiado)")
        self.credit_check.blockSignals(True)
        self.credit_check.setChecked(is_credit)
        self.credit_check.blockSignals(False)
        
        # Show/Hide customer requirement
        if is_credit:
            self.customer_combo.setStyleSheet("background-color: #ffebee; border: 1px solid red;")
        else:
            self.customer_combo.setStyleSheet("")

    def on_credit_check_toggled(self, checked):
        # Sync combo with checkbox
        self.payment_method_combo.blockSignals(True)
        if checked:
            index = self.payment_method_combo.findText("Crédito (Fiado)")
            if index >= 0:
                self.payment_method_combo.setCurrentIndex(index)
        else:
            # Revert to default or first option if uncheck
            if self.payment_method_combo.currentText() == "Crédito (Fiado)":
                self.payment_method_combo.setCurrentIndex(0) # Efectivo Bs
        self.payment_method_combo.blockSignals(False)
        
        # Trigger logic
        self.on_payment_method_changed(self.payment_method_combo.currentText())

    def save_as_quote(self):
        """Save current cart as a quote (F4)"""
        if not self.controller.cart:
            QMessageBox.warning(self, "Alerta", "El carrito está vacío")
            return
        
        from PyQt6.QtWidgets import QInputDialog
        
        # Ask for customer (optional)
        customer_id = None
        if self.customer_combo.count() > 1:  # Has customers
            customer_name, ok = QInputDialog.getItem(
                self, "Cliente", 
                "Seleccione cliente (opcional):",
                [self.customer_combo.itemText(i) for i in range(self.customer_combo.count())],
                0, False
            )
            if ok and customer_name != "Seleccione Cliente...":
                customer_id = self.customer_combo.findText(customer_name)
                if customer_id > 0:
                    customer_id = self.customer_combo.itemData(customer_id)
        
        # Ask for notes
        notes, ok = QInputDialog.getText(
            self, "Notas", 
            "Notas de la cotización (opcional):"
        )
        if not ok:
            return
        
        try:
            quote = self.quote_controller.save_quote(
                self.controller.cart, 
                customer_id=customer_id, 
                notes=notes
            )
            QMessageBox.information(
                self, "Éxito", 
                f"Cotización #{quote.id} guardada exitosamente"
            )
            self.controller.cart.clear()
            self.refresh_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def closeEvent(self, event):
        self.db.close()
        event.accept()
