from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QFrame, QComboBox, QCompleter, QDoubleSpinBox,
    QGroupBox, QFormLayout, QDialog, QRadioButton, QButtonGroup
)
from PyQt6.QtGui import QKeySequence, QFont, QShortcut, QColor
from PyQt6.QtCore import Qt, QLocale
# from src.database.db import SessionLocal
from src.controllers.pos_controller import POSController
from src.controllers.customer_controller import CustomerController
from src.controllers.quote_controller import QuoteController
from src.controllers.config_controller import ConfigController
from frontend_caja.services.cash_service import CashService
from src.utils.event_bus import event_bus

class POSWindow(QWidget):
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.setWindowTitle("Punto de Venta (POS) - Módulo 3")
        self.showMaximized()  # Maximize window instead of fixed size
        
        self.db = None        # Controllers
        self.controller = POSController(db=None) 
        self.config_controller = ConfigController(db=None)
        self.quote_controller = QuoteController(db=None) # Service-based now
        self.customer_controller = CustomerController(db=None)
        self.cash_service = CashService()
        
        # Get exchange rate
        self.exchange_rate = self.config_controller.get_exchange_rate()
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.setup_ui()
        self.setup_shortcuts()
        
        # Connect signals
        event_bus.products_updated.connect(self.setup_autocomplete)
        event_bus.customers_updated.connect(self.load_customers)

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
        

        # Price Tier Group
        tier_group = QGroupBox("Nivel de Precio")
        tier_layout = QVBoxLayout()
        
        self.price_tier_combo = QComboBox()
        self.price_tier_combo.addItem("Precio Detal", "price")
        self.price_tier_combo.addItem("Mayorista 1", "price_mayor_1")
        self.price_tier_combo.addItem("Mayorista 2", "price_mayor_2")
        self.price_tier_combo.setFont(QFont("Arial", 11))
        tier_layout.addWidget(self.price_tier_combo)
        
        tier_group.setLayout(tier_layout)
        right_panel.addWidget(tier_group)
        
        # Credit Sale Checkbox
        credit_group = QGroupBox("Tipo de Venta")
        credit_layout = QVBoxLayout()
        
        self.credit_check = QCheckBox("Venta a Crédito (Fiado)")
        self.credit_check.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.credit_check.setStyleSheet("color: #d32f2f;")
        credit_layout.addWidget(self.credit_check)
        
        credit_group.setLayout(credit_layout)
        right_panel.addWidget(credit_group)
        
        # Control Group 4: Customer
        customer_group = QGroupBox("Cliente (Opcional)")
        customer_layout = QVBoxLayout()
        
        self.customer_input = QLineEdit()
        self.customer_input.setPlaceholderText("Buscar cliente por nombre o cédula...")
        self.customer_input.setFont(QFont("Arial", 10))
        self.setup_customer_autocomplete()
        self.customer_input.returnPressed.connect(self.on_customer_selected)
        customer_layout.addWidget(self.customer_input)
        
        self.selected_customer_id = None
        self.lbl_selected_customer = QLabel("Ninguno seleccionado")
        self.lbl_selected_customer.setStyleSheet("color: #666; font-style: italic;")
        customer_layout.addWidget(self.lbl_selected_customer)
        
        customer_group.setLayout(customer_layout)
        right_panel.addWidget(customer_group)
        
        # Exchange Rate Info
        self.lbl_rate = QLabel(f"Tasa: 1 USD = {self.exchange_rate:.2f} Bs")
        self.lbl_rate.setFont(QFont("Arial", 10))
        self.lbl_rate.setStyleSheet("color: #666; padding: 5px; background-color: #fff3cd; border-radius: 3px;")
        self.lbl_rate.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(self.lbl_rate)
        

        
        # Discount Buttons
        discount_group = QGroupBox("Descuentos")
        discount_layout = QVBoxLayout()
        
        btn_item_discount = QPushButton("Descuento por Item")
        btn_item_discount.setStyleSheet("background-color: #9C27B0; color: white; padding: 8px;")
        btn_item_discount.clicked.connect(self.apply_item_discount)
        discount_layout.addWidget(btn_item_discount)
        
        btn_global_discount = QPushButton("Descuento Global")
        btn_global_discount.setStyleSheet("background-color: #673AB7; color: white; padding: 8px;")
        btn_global_discount.clicked.connect(self.apply_global_discount_dialog)
        discount_layout.addWidget(btn_global_discount)
        
        btn_quick_discount = QPushButton("⚡ Ajustar Total")
        btn_quick_discount.setStyleSheet("background-color: #FF5722; color: white; padding: 8px; font-weight: bold;")
        btn_quick_discount.clicked.connect(self.apply_quick_discount)
        discount_layout.addWidget(btn_quick_discount)
        
        discount_group.setLayout(discount_layout)
        right_panel.addWidget(discount_group)
        
        right_panel.addStretch()
        
        # Wrap right panel in scroll area
        from PyQt6.QtWidgets import QScrollArea
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(right_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setMaximumWidth(400)  # Limit width
        
        # Table (in left panel)
        self.table = QTableWidget()
        self.table.setColumnCount(9)  # Increased from 7 to 9
        self.table.setHorizontalHeaderLabels([
            "Producto", "Presentación", "Cant.", "Precio ($)", "Tasa", "Precio (Bs)", "Subtotal ($)", "Subtotal (Bs)", "Eliminar"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setFont(QFont("Arial", 11))  # Slightly smaller font
        
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
        main_layout.addWidget(scroll_area, 1)  # 25% width with scroll
        
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
        self.customer_input.setVisible(checked)
        self.lbl_selected_customer.setVisible(checked)
        if checked:
            self.load_customers()

    def load_customers(self):
        # Refresh autocomplete data
        self.setup_customer_autocomplete()
        
    def setup_customer_autocomplete(self):
        """Setup autocomplete for customer search"""
        customers = self.customer_controller.get_all_customers()
        
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
        self.customer_input.setCompleter(completer)

    def on_customer_selected(self):
        text = self.customer_input.text().strip()
        if not text:
            self.selected_customer_id = None
            self.lbl_selected_customer.setText("Ninguno seleccionado")
            return
            
        customer = self.customer_map.get(text)
        if not customer:
            # Try finding by name match
            for name, c in self.customer_map.items():
                if text.lower() in name.lower():
                    customer = c
                    break
        
        if customer:
            self.selected_customer_id = customer.id
            self.lbl_selected_customer.setText(f"Seleccionado: {customer.name}")
            self.lbl_selected_customer.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.selected_customer_id = None
            self.lbl_selected_customer.setText("Cliente no encontrado")
            self.lbl_selected_customer.setStyleSheet("color: red;")
    
    def setup_autocomplete(self):
        """Setup autocomplete for product search"""
        # from src.models.models import Product
        
        # Get all active products FROM CONTROLLER CACHE (API)
        # products = self.db.query(Product).filter(Product.is_active == True).all()
        products = self.controller.cached_products
        
        # Create list of suggestions: "Name - SKU - $Price"
        suggestions = []
        for p in products:
            # Handle dict access since it's now a list of dicts from API
            p_sku = p.get('sku', '')
            p_loc = p.get('location', '')
            p_name = p.get('name', 'Unknown')
            p_price = p.get('price', 0.0)

            sku_part = f" - {p_sku}" if p_sku else ""
            loc_part = f" (Ubic: {p_loc})" if p_loc else ""
            suggestion = f"{p_name}{sku_part} - ${p_price:,.2f}{loc_part}"
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
        tier = self.price_tier_combo.currentData()
        qty = 1.0 
        
        # Try to add to cart
        success, msg = self.controller.add_to_cart(text, qty, is_box, price_tier=tier)
        
        # Check for Selection Needed (msg will be a dict)
        if not success and isinstance(msg, dict) and msg.get('status') == 'SELECTION_NEEDED':
            # Open Selection Dialog
            from src.views.dialogs.unit_selection_dialog import UnitSelectionDialog
            
            dialog = UnitSelectionDialog(
                parent=self,
                product=msg['product'],
                units=msg['units'],
                exchange_rate=self.exchange_rate
            )
            
            if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_unit:
                # Add specific unit
                success_final, msg_final = self.controller.add_to_cart(
                    sku_or_name=text,
                    quantity=qty,
                    is_box=is_box,
                    price_tier=tier,
                    unit_data=dialog.selected_unit,
                    product_id=msg['product']['id'] # Pass ID to avoid re-search ambiguity
                )
                
                if success_final:
                    self.refresh_table()
                else:
                    QMessageBox.warning(self, "Alerta", msg_final)
            
            # Clear input regardless
            self.input_scan.clear()
            self.focus_input()
            return
        
        # Standard Success/Fail
        if success:
            self.refresh_table()
        else:
            # Regular error message
            QMessageBox.warning(self, "Alerta", str(msg))
        
        self.input_scan.clear()
        # Force clear again just in case completer interferes
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(10, self.input_scan.clear)
        
        self.focus_input()

    def refresh_table(self):
        # Block signals to prevent infinite loop when setting items
        self.table.blockSignals(True)
        
        self.table.setRowCount(0)
        total_usd = 0
        total_bs = 0
        
        for i, item in enumerate(self.controller.cart):
            self.table.insertRow(i)
            
            # Column 0: Product Name (Not editable)
            name_item = QTableWidgetItem(item["name"])
            name_item.setFlags(name_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, name_item)
            
            # Column 1: Presentación (Not editable)
            presentation = item.get("unit_name", item.get("unit_type", "Unidad"))
            pres_item = QTableWidgetItem(presentation)
            pres_item.setFlags(pres_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 1, pres_item)
            
            # Column 2: Quantity (Editable)
            qty_item = QTableWidgetItem(str(item["quantity"]))
            self.table.setItem(i, 2, qty_item)
            
            # Column 3: Precio ($) - Base price in USD (Not editable)
            price_usd = item.get("base_price_usd", item.get("unit_price", 0))
            price_usd_item = QTableWidgetItem(f"${price_usd:,.2f}")
            price_usd_item.setFlags(price_usd_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 3, price_usd_item)
            
            # Column 4: Tasa (Not editable)
            rate_name = item.get("rate_name", "Estándar")
            rate_value = item.get("rate_value", self.exchange_rate)
            rate_item = QTableWidgetItem(f"{rate_name} ({rate_value:.2f})")
            rate_item.setFlags(rate_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 4, rate_item)
            
            # Column 5: Precio (Bs) - Price in Bs (Not editable)
            price_bs = price_usd * rate_value
            price_bs_item = QTableWidgetItem(f"Bs {price_bs:,.2f}")
            price_bs_item.setFlags(price_bs_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 5, price_bs_item)
            
            # Column 6: Subtotal ($) (Not editable)
            subtotal_usd = item["subtotal"]
            subtotal_usd_item = QTableWidgetItem(f"${subtotal_usd:,.2f}")
            subtotal_usd_item.setFlags(subtotal_usd_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 6, subtotal_usd_item)
            
            # Column 7: Subtotal (Bs) (Not editable)
            subtotal_bs = subtotal_usd * rate_value
            subtotal_bs_item = QTableWidgetItem(f"Bs {subtotal_bs:,.2f}")
            subtotal_bs_item.setFlags(subtotal_bs_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 7, subtotal_bs_item)
            
            # Column 8: Delete Button
            btn_del = QPushButton("🗑")
            btn_del.setFixedWidth(50)
            btn_del.setStyleSheet("""
                QPushButton {
                    background-color: #F44336;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 14pt;
                }
                QPushButton:hover {
                    background-color: #D32F2F;
                }
            """)
            btn_del.clicked.connect(lambda checked, idx=i: self.remove_item(idx))
            self.table.setCellWidget(i, 8, btn_del)
            
            total_usd += subtotal_usd
            total_bs += subtotal_bs
        
        # Update total label with LARGE Bs display and small USD display
        self.lbl_total.setText(f"TOTAL: Bs {total_bs:,.2f}  (${total_usd:,.2f})")
        self.lbl_total.setStyleSheet("color: #1976D2; font-size: 24px; font-weight: bold;")
        
        self.table.blockSignals(False)
    
    def on_currency_changed(self, currency):
        """Handle currency selection change"""
        # Refresh display to show prices in selected currency
        self.refresh_table()

    def on_cell_changed(self, row, column):
        # Column 2 is Quantity (changed from 1)
        if column == 2:
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

    def validate_session(self):
        """Check if user has an open cash session"""
        if not self.user: # Dev/Mock
            return True
            
        try:
            # Check Global Session (Any open box)
            session = self.cash_service.get_active_session_global()
            if not session or session.get("status") != "OPEN":
                QMessageBox.warning(self, "Caja Cerrada", "Debe abrir una sesión de caja antes de realizar ventas.\nVaya al módulo de Control de Caja.")
                return False
            return True
        except Exception as e:
            print(f"Error checking session: {e}")
            # Fail safe: Block if unsure? Or allow? Assuming block.
            return False

    def handle_payment(self):
        if not self.validate_session():
            return

        if not self.controller.cart:
            return
        
        is_credit = self.credit_check.isChecked()
        customer_id = self.selected_customer_id
        
        if is_credit:
            if not customer_id:
                QMessageBox.warning(self, "Error", "Debe seleccionar un cliente para venta a crédito")
                return
            # For credit sales, skip payment dialog
            self.process_sale(payments=None, is_credit=True, customer_id=customer_id)
        else:
            # Show mixed payment dialog
            self.show_mixed_payment_dialog()
        
        self.focus_input()
    
    def show_mixed_payment_dialog(self):
        """Show dialog for mixed payment entry"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QRadioButton, QButtonGroup
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Forma de Pago")
        dialog.resize(600, 450)
        
        layout = QVBoxLayout()
        
        # Total display
        total_usd = self.controller.get_total()
        total_bs = total_usd * self.exchange_rate
        
        lbl_total = QLabel(f"TOTAL A PAGAR: ${total_usd:,.2f} USD / Bs {total_bs:,.2f}")
        lbl_total.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        lbl_total.setStyleSheet("color: green; padding: 10px; background-color: #e8f5e9; border-radius: 5px;")
        layout.addWidget(lbl_total)
        
        # Payments table
        layout.addWidget(QLabel("Métodos de Pago:"))
        payments_table = QTableWidget()
        payments_table.setColumnCount(3)
        payments_table.setHorizontalHeaderLabels(["Método", "Monto", "Eliminar"])
        payments_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(payments_table)
        
        # Payment list storage
        payment_list = []
        
        def refresh_payments_table():
            payments_table.setRowCount(0)
            total_paid_usd = 0
            
            for i, p in enumerate(payment_list):
                payments_table.insertRow(i)
                payments_table.setItem(i, 0, QTableWidgetItem(p["method"]))
                
                # Display amount in original currency
                amount_display = f"{p['amount']:.2f} {p['currency']}"
                payments_table.setItem(i, 1, QTableWidgetItem(amount_display))
                
                btn_del = QPushButton("X")
                btn_del.setStyleSheet("background-color: #f44336; color: white;")
                btn_del.clicked.connect(lambda checked, idx=i: remove_payment(idx))
                payments_table.setCellWidget(i, 2, btn_del)
                
                # Convert to USD for total calculation
                if p["currency"] == "USD":
                    total_paid_usd += p["amount"]
                else:  # Bs
                    total_paid_usd += p["amount"] / self.exchange_rate
            
            remaining_usd = total_usd - total_paid_usd
            remaining_bs = remaining_usd * self.exchange_rate
            
            lbl_remaining.setText(f"Restante: ${remaining_usd:,.2f} USD / Bs {remaining_bs:,.2f}")
            if remaining_usd <= 0.01:  # Allow small rounding
                lbl_remaining.setStyleSheet("color: green; font-weight: bold;")
            else:
                lbl_remaining.setStyleSheet("color: red; font-weight: bold;")
        
        def remove_payment(idx):
            payment_list.pop(idx)
            refresh_payments_table()
        
        # Remaining label
        lbl_remaining = QLabel(f"Restante: ${total_usd:,.2f} USD / Bs {total_bs:,.2f}")
        lbl_remaining.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(lbl_remaining)
        
        # Add payment controls
        add_layout = QVBoxLayout()
        
        # Method selector
        method_layout = QHBoxLayout()
        method_combo = QComboBox()
        method_combo.addItems([
            "Efectivo",
            "Transferencia / Pago Móvil",
            "Tarjeta Débito/Crédito",
            "Zelle"
        ])
        method_layout.addWidget(QLabel("Método:"))
        method_layout.addWidget(method_combo)
        add_layout.addLayout(method_layout)
        
        # Currency selector
        currency_layout = QHBoxLayout()
        currency_layout.addWidget(QLabel("Moneda:"))
        
        btn_group = QButtonGroup(dialog)
        rb_bs = QRadioButton("Bs")
        rb_usd = QRadioButton("USD")
        rb_bs.setChecked(True)
        btn_group.addButton(rb_bs)
        btn_group.addButton(rb_usd)
        
        currency_layout.addWidget(rb_bs)
        currency_layout.addWidget(rb_usd)
        add_layout.addLayout(currency_layout)
        
        # Amount input
        amount_layout = QHBoxLayout()
        amount_input = QDoubleSpinBox()
        amount_input.setRange(0, 1000000)
        amount_input.setDecimals(2)
        amount_input.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        amount_input.setValue(total_bs)
        amount_layout.addWidget(QLabel("Monto:"))
        amount_layout.addWidget(amount_input)
        add_layout.addLayout(amount_layout)
        
        # Update amount when currency changes
        def on_currency_changed():
            # Calculate current remaining
            total_paid_usd = sum(
                p["amount"] if p["currency"] == "USD" else p["amount"] / self.exchange_rate 
                for p in payment_list
            )
            remaining_usd = total_usd - total_paid_usd
            
            if rb_bs.isChecked():
                amount_input.setValue(remaining_usd * self.exchange_rate)
            else:
                amount_input.setValue(remaining_usd)
        
        rb_bs.toggled.connect(on_currency_changed)
        rb_usd.toggled.connect(on_currency_changed)
        
        def add_payment():
            method = method_combo.currentText()
            amount = amount_input.value()
            currency = "USD" if rb_usd.isChecked() else "Bs"
            
            if amount <= 0:
                QMessageBox.warning(dialog, "Error", "El monto debe ser mayor a 0")
                return
            
            payment_list.append({
                "method": f"{method} {currency}",
                "amount": amount,
                "currency": currency
            })
            refresh_payments_table()
            
            # Calculate remaining and update amount input
            on_currency_changed()
        
        btn_add = QPushButton("Agregar Pago")
        btn_add.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; font-weight: bold;")
        btn_add.clicked.connect(add_payment)
        add_layout.addWidget(btn_add)
        
        layout.addLayout(add_layout)
        
        # Bottom buttons
        btn_layout = QHBoxLayout()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_ok = QPushButton("PROCESAR VENTA")
        btn_ok.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold;")
        btn_ok.clicked.connect(dialog.accept)
        btn_layout.addWidget(btn_ok)
        
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if not payment_list:
                QMessageBox.warning(self, "Error", "Debe agregar al menos un método de pago")
                return
            
            # Calculate total paid in USD
            total_paid_usd = sum(
                p["amount"] if p["currency"] == "USD" else p["amount"] / self.exchange_rate 
                for p in payment_list
            )
            
            if abs(total_paid_usd - total_usd) > 0.01:
                QMessageBox.warning(self, "Error", 
                    f"El total pagado (${total_paid_usd:.2f}) no coincide con el total (${total_usd:.2f})")
                return
            
            self.process_sale(payments=payment_list, is_credit=False, customer_id=self.selected_customer_id)
    
    def process_sale(self, payments, is_credit, customer_id):
        """Process the sale with given payments"""
        
        # Capture cart items for picking list before they are cleared
        cart_snapshot = list(self.controller.cart)
        
        # Determine currency from payments (use first payment's currency)
        primary_currency = "USD"
        if payments and len(payments) > 0:
            primary_currency = payments[0]["currency"]
        
        success, msg, ticket = self.controller.finalize_sale(
            payments=payments,
            customer_id=customer_id,
            is_credit=is_credit,
            currency=primary_currency,
            exchange_rate=self.exchange_rate,
            notes=""  # Notes field removed from UI
        )
        if success:
            if is_credit:
                QMessageBox.information(self, "Venta a Crédito Exitosa", 
                                      f"Venta registrada a crédito.\n\n{ticket}")
            else:
                QMessageBox.information(self, "Venta Exitosa", f"Ticket generado:\n\n{ticket}")
            
            # Show Picking List / Locations
            self.show_picking_list(cart_snapshot)
            
            self.refresh_table()
            # payment_method_combo removed - no longer needed
        else:
            QMessageBox.critical(self, "Error", msg)

    # on_payment_method_changed and on_credit_check_toggled removed
    # Payment methods now handled in payment dialog



    def save_as_quote(self):
        # Quotes might not strictly require open cash (no money moves), 
        # but user likely wants consistency. Optional. I will NOT block quotes for now unless requested.
        # IF user said "ventas", quotes are pre-sales.
        # But checking session is good practice.
        # if not self.validate_session(): return
        
        if not self.controller.cart:
            QMessageBox.warning(self, "Alerta", "El carrito está vacío")
            return
        
        from PyQt6.QtWidgets import QInputDialog
        
        # Ask for customer (optional)
        customer_id = self.selected_customer_id
        if not customer_id:
            # Try to get from input if not confirmed
            self.on_customer_selected()
            customer_id = self.selected_customer_id
        
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

    def apply_item_discount(self):
        """Apply discount to selected item"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Alerta", "Seleccione un producto de la tabla")
            return
        
        # Request PIN authorization
        from src.views.pin_auth_dialog import PINAuthDialog
        authorized, auth_user = PINAuthDialog.request_authorization(self, "aplicar descuento por ítem")
        
        if not authorized:
            return
        
        from PyQt6.QtWidgets import QInputDialog, QDialog, QVBoxLayout, QRadioButton, QButtonGroup
        
        # Create custom dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Aplicar Descuento")
        dialog.resize(300, 150)
        
        layout = QVBoxLayout()
        
        # Radio buttons for discount type
        layout.addWidget(QLabel("Tipo de descuento:"))
        btn_group = QButtonGroup(dialog)
        rb_percent = QRadioButton("Porcentaje (%)")
        rb_fixed = QRadioButton("Monto Fijo ($)")
        rb_percent.setChecked(True)
        btn_group.addButton(rb_percent)
        btn_group.addButton(rb_fixed)
        layout.addWidget(rb_percent)
        layout.addWidget(rb_fixed)
        
        # Input
        layout.addWidget(QLabel("Valor:"))
        input_value = QDoubleSpinBox()
        input_value.setMinimum(0)
        input_value.setMaximum(100)
        input_value.setValue(10)
        layout.addWidget(input_value)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("Aplicar")
        btn_cancel = QPushButton("Cancelar")
        btn_ok.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            discount_value = input_value.value()
            discount_type = "PERCENT" if rb_percent.isChecked() else "FIXED"
            
            success, msg = self.controller.apply_discount(row, discount_value, discount_type)
            if success:
                self.refresh_table()
                QMessageBox.information(self, "Éxito", msg)
            else:
                QMessageBox.warning(self, "Error", msg)

    def apply_global_discount_dialog(self):
        """Apply discount to entire sale"""
        if not self.controller.cart:
            QMessageBox.warning(self, "Alerta", "El carrito está vacío")
            return
        
        # Request PIN authorization
        from src.views.pin_auth_dialog import PINAuthDialog
        authorized, auth_user = PINAuthDialog.request_authorization(self, "aplicar descuento global")
        
        if not authorized:
            return
        
        from PyQt6.QtWidgets import QInputDialog, QDialog, QVBoxLayout, QRadioButton, QButtonGroup
        
        # Create custom dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Descuento Global")
        dialog.resize(300, 150)
        
        layout = QVBoxLayout()
        
        # Radio buttons for discount type
        layout.addWidget(QLabel("Tipo de descuento:"))
        btn_group = QButtonGroup(dialog)
        rb_percent = QRadioButton("Porcentaje (%)")
        rb_fixed = QRadioButton("Monto Fijo ($)")
        rb_percent.setChecked(True)
        btn_group.addButton(rb_percent)
        btn_group.addButton(rb_fixed)
        layout.addWidget(rb_percent)
        layout.addWidget(rb_fixed)
        
        # Input
        layout.addWidget(QLabel("Valor:"))
        input_value = QDoubleSpinBox()
        input_value.setMinimum(0)
        input_value.setMaximum(1000)
        input_value.setValue(5)
        layout.addWidget(input_value)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("Aplicar")
        btn_cancel = QPushButton("Cancelar")
        btn_ok.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            discount_value = input_value.value()
            discount_type = "PERCENT" if rb_percent.isChecked() else "FIXED"
            
            success, msg = self.controller.apply_global_discount(discount_value, discount_type)
            if success:
                self.refresh_table()
                QMessageBox.information(self, "Éxito", msg)
            else:
                QMessageBox.warning(self, "Error", msg)

    def apply_quick_discount(self):
        """Quick discount - adjust total to a specific amount"""
        if not self.controller.cart:
            QMessageBox.warning(self, "Alerta", "El carrito está vacío")
            return
        
        # Request PIN authorization
        from src.views.pin_auth_dialog import PINAuthDialog
        authorized, auth_user = PINAuthDialog.request_authorization(self, "ajustar total (descuento rápido)")
        
        if not authorized:
            return
        
        from PyQt6.QtWidgets import QInputDialog, QDialog, QVBoxLayout, QHBoxLayout, QRadioButton, QButtonGroup, QLabel, QPushButton
        
        current_total_usd = self.controller.get_total()
        current_total_bs = current_total_usd * self.exchange_rate
        
        # Create custom dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajustar Total")
        dialog.resize(350, 200)
        
        layout = QVBoxLayout()
        
        # Show current total
        lbl_current = QLabel(f"Total actual:\n${current_total_usd:,.2f} USD / Bs {current_total_bs:,.2f}")
        lbl_current.setFont(QFont("Arial", 11))
        lbl_current.setStyleSheet("padding: 10px; background-color: #e3f2fd; border-radius: 5px;")
        layout.addWidget(lbl_current)
        
        # Currency selector
        currency_layout = QHBoxLayout()
        currency_layout.addWidget(QLabel("Moneda:"))
        
        btn_group = QButtonGroup(dialog)
        rb_bs = QRadioButton("Bs")
        rb_usd = QRadioButton("USD")
        rb_bs.setChecked(True)
        btn_group.addButton(rb_bs)
        btn_group.addButton(rb_usd)
        
        currency_layout.addWidget(rb_bs)
        currency_layout.addWidget(rb_usd)
        layout.addLayout(currency_layout)
        
        # Amount input
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("Nuevo total:"))
        
        amount_input = QDoubleSpinBox()
        amount_input.setRange(0, 1000000)
        amount_input.setDecimals(2)
        amount_input.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        amount_input.setValue(current_total_bs)
        amount_layout.addWidget(amount_input)
        layout.addLayout(amount_layout)
        
        # Update amount when currency changes
        def on_currency_changed():
            if rb_bs.isChecked():
                amount_input.setValue(current_total_bs)
            else:
                amount_input.setValue(current_total_usd)
        
        rb_bs.toggled.connect(on_currency_changed)
        rb_usd.toggled.connect(on_currency_changed)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(dialog.reject)
        btn_ok = QPushButton("Aplicar")
        btn_ok.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
        btn_ok.clicked.connect(dialog.accept)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_total = amount_input.value()
            currency = "USD" if rb_usd.isChecked() else "Bs"
            
            # Convert to USD for calculation
            if currency == "USD":
                new_total_usd = new_total
                if new_total_usd >= current_total_usd:
                    QMessageBox.information(self, "Info", "El nuevo total debe ser menor al actual")
                    return
            else:  # Bs
                new_total_usd = new_total / self.exchange_rate
                if new_total >= current_total_bs:
                    QMessageBox.information(self, "Info", "El nuevo total debe ser menor al actual")
                    return
            
            # Calculate discount amount in USD
            discount_amount_usd = current_total_usd - new_total_usd
            
            # Apply as fixed discount in USD
            success, msg = self.controller.apply_global_discount(discount_amount_usd, "FIXED")
            if success:
                self.refresh_table()
                QMessageBox.information(self, "Éxito", 
                    f"Total ajustado a {new_total:,.2f} {currency}\nDescuento aplicado: ${discount_amount_usd:,.2f}")
            else:
                QMessageBox.warning(self, "Error", msg)

    def show_picking_list(self, items):
        """Show dialog with items and locations for warehouse/picking"""
        if not items:
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("📋 Ubicación de Productos")
        dialog.resize(700, 500)
        
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        # Header
        lbl_title = QLabel("📦 Lista de Recogida / Ubicaciones")
        lbl_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #1976D2; margin-bottom: 10px;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)
        
        # Info
        lbl_info = QLabel("Entregue estos productos al cliente:")
        lbl_info.setFont(QFont("Arial", 12))
        layout.addWidget(lbl_info)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Producto", "Cantidad", "Ubicación Estante"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        table.setStyleSheet("font-size: 14pt;")
        
        table.setRowCount(len(items))
        
        for i, item in enumerate(items):
            # Name
            name_item = QTableWidgetItem(item.get("name", ""))
            table.setItem(i, 0, name_item)
            
            # Quantity + Type
            qty = item.get("quantity", 0)
            is_box = item.get("is_box", False)
            type_str = "CAJA" if is_box else "UNID"
            qty_item = QTableWidgetItem(f"{qty} {type_str}")
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(i, 1, qty_item)
            
            # Location
            location = "-"
            # Try to get from product_obj
            if "product_obj" in item and hasattr(item["product_obj"], "location"):
                location = item["product_obj"].location or "-"
            
            loc_item = QTableWidgetItem(location)
            loc_item.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            loc_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if location != "-":
                loc_item.setForeground(QColor("blue"))
                loc_item.setBackground(QColor("#E3F2FD")) # Light blue bg
            else:
                loc_item.setForeground(QColor("gray"))
                
            table.setItem(i, 2, loc_item)
            
        layout.addWidget(table)
        
        # Button
        btn_close = QPushButton("Listo / Cerrar (Enter)")
        btn_close.setStyleSheet("background-color: #4CAF50; color: white; padding: 15px; font-weight: bold; font-size: 14pt;")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close)
        
        dialog.exec()

    def show_picking_list(self, items):
        """Show dialog with items and locations for warehouse/picking"""
        if not items:
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("📋 Ubicación de Productos")
        dialog.resize(700, 500)
        
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        # Header
        lbl_title = QLabel("📦 Lista de Recogida / Ubicaciones")
        lbl_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #1976D2; margin-bottom: 10px;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)
        
        # Info
        lbl_info = QLabel("Entregue estos productos al cliente:")
        lbl_info.setFont(QFont("Arial", 12))
        layout.addWidget(lbl_info)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Producto", "Cantidad", "Ubicación Estante"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        table.setStyleSheet("font-size: 14pt;")
        
        table.setRowCount(len(items))
        
        for i, item in enumerate(items):
            # Name
            name_item = QTableWidgetItem(item.get("name", ""))
            table.setItem(i, 0, name_item)
            
            # Quantity + Type
            qty = item.get("quantity", 0)
            is_box = item.get("is_box", False)
            type_str = "CAJA" if is_box else "UNID"
            qty_item = QTableWidgetItem(f"{qty} {type_str}")
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(i, 1, qty_item)
            
            # Location
            location = item.get("location")
            
            if not location or location == "-":
                 if "product_obj" in item:
                     p_obj = item["product_obj"]
                     # Handle as dict (API response) or object (Database model)
                     if isinstance(p_obj, dict):
                         location = p_obj.get("location")
                     elif hasattr(p_obj, "location"):
                         location = p_obj.location
            
            location = location or "-"
            
            loc_item = QTableWidgetItem(location)
            loc_item.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            loc_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if location != "-":
                loc_item.setForeground(QColor("blue"))
                loc_item.setBackground(QColor("#E3F2FD")) # Light blue bg
            else:
                loc_item.setForeground(QColor("gray"))
                
            table.setItem(i, 2, loc_item)
            
        layout.addWidget(table)
        
        # Button
        btn_close = QPushButton("Listo / Cerrar (Enter)")
        btn_close.setStyleSheet("background-color: #4CAF50; color: white; padding: 15px; font-weight: bold; font-size: 14pt;")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close)
        
        dialog.exec()

    def closeEvent(self, event):
        # self.db.close()
        event.accept()
