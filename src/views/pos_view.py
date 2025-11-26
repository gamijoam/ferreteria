from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QFrame, QComboBox, QCompleter
)
from PyQt6.QtGui import QKeySequence, QFont, QShortcut
from PyQt6.QtCore import Qt
from src.database.db import SessionLocal
from src.controllers.pos_controller import POSController
from src.controllers.customer_controller import CustomerController
from src.controllers.quote_controller import QuoteController

class POSWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Punto de Venta (POS) - Módulo 3")
        self.resize(1200, 750)
        
        self.db = SessionLocal()
        self.controller = POSController(self.db)
        self.customer_controller = CustomerController(self.db)
        self.quote_controller = QuoteController(self.db)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        # Top Bar: Input
        top_frame = QFrame()
        top_layout = QHBoxLayout()
        top_frame.setLayout(top_layout)
        
        lbl_scan = QLabel("Escanear / Código (F1):")
        lbl_scan.setFont(QFont("Arial", 14))
        
        self.input_scan = QLineEdit()
        self.input_scan.setFont(QFont("Arial", 16))
        self.input_scan.setPlaceholderText("Ingrese SKU o Nombre y presione ENTER")
        self.input_scan.returnPressed.connect(self.handle_add_item)
        
        # Setup autocomplete
        self.setup_autocomplete()
        
        self.check_box_mode = QCheckBox("Vender por Caja (F2)")
        self.check_box_mode.setFont(QFont("Arial", 12))
        
        # Credit Sale
        self.check_credit = QCheckBox("Venta a Crédito (F3)")
        self.check_credit.setFont(QFont("Arial", 12))
        self.check_credit.toggled.connect(self.toggle_credit_mode)
        
        self.customer_combo = QComboBox()
        self.customer_combo.setVisible(False)
        self.load_customers()
        
        top_layout.addWidget(lbl_scan)
        top_layout.addWidget(self.input_scan)
        top_layout.addWidget(self.check_box_mode)
        top_layout.addWidget(self.check_credit)
        top_layout.addWidget(self.customer_combo)
        
        self.layout.addWidget(top_frame)
        
        # Center: Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Producto", "Cant.", "Tipo", "Precio Unit.", "Subtotal", "Eliminar"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setFont(QFont("Arial", 12))
        
        # Connect cell change signal
        self.table.cellChanged.connect(self.on_cell_changed)
        
        self.layout.addWidget(self.table)
        
        # Bottom: Total & Actions
        bottom_frame = QFrame()
        bottom_layout = QHBoxLayout()
        bottom_frame.setLayout(bottom_layout)
        
        self.lbl_total = QLabel("Total: $0")
        self.lbl_total.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.lbl_total.setStyleSheet("color: green;")
        
        btn_pay = QPushButton("COBRAR (F12)")
        btn_pay.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        btn_pay.setStyleSheet("background-color: #007bff; color: white; padding: 10px;")
        btn_pay.clicked.connect(self.handle_payment)
        
        btn_quote = QPushButton("GUARDAR COTIZACIÓN (F4)")
        btn_quote.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        btn_quote.setStyleSheet("background-color: #ff9800; color: white; padding: 10px;")
        btn_quote.clicked.connect(self.save_as_quote)
        
        bottom_layout.addWidget(self.lbl_total)
        bottom_layout.addStretch()
        bottom_layout.addWidget(btn_quote)
        bottom_layout.addWidget(btn_pay)
        
        self.layout.addWidget(bottom_frame)
        
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
            suggestion = f"{p.name}{sku_part} - ${p.price:,.0f}"
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
        qty = 1 
        
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
            
            # Type (Not editable)
            type_item = QTableWidgetItem("CAJA" if item["is_box"] else "UNID")
            type_item.setFlags(type_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 2, type_item)
            
            # Unit Price (Not editable)
            price_item = QTableWidgetItem(f"${item['unit_price']:,.0f}")
            price_item.setFlags(price_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 3, price_item)
            
            # Subtotal (Not editable)
            subtotal_item = QTableWidgetItem(f"${item['subtotal']:,.0f}")
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
            
        self.lbl_total.setText(f"Total: ${total:,.0f}")
        
        self.table.blockSignals(False)

    def on_cell_changed(self, row, column):
        # Column 1 is Quantity
        if column == 1:
            try:
                new_qty_str = self.table.item(row, column).text()
                if not new_qty_str.isdigit():
                    raise ValueError("Debe ser un número")
                
                new_qty = int(new_qty_str)
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
        
        is_credit = self.check_credit.isChecked()
        customer_id = None
        
        if is_credit:
            customer_id = self.customer_combo.currentData()
            if not customer_id:
                QMessageBox.warning(self, "Error", "Debe seleccionar un cliente para venta a crédito")
                return
            
        reply = QMessageBox.question(
            self, "Confirmar Venta", 
            f"¿Procesar venta por {self.lbl_total.text()}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, msg, ticket = self.controller.finalize_sale(
                payment_method="Credito" if is_credit else "Efectivo",
                customer_id=customer_id,
                is_credit=is_credit
            )
            if success:
                if is_credit:
                    QMessageBox.information(self, "Venta a Crédito Exitosa", 
                                          f"Venta registrada a crédito.\\n\\n{ticket}")
                else:
                    QMessageBox.information(self, "Venta Exitosa", f"Ticket generado:\\n\\n{ticket}")
                self.refresh_table()
                self.check_credit.setChecked(False)  # Reset
            else:
                QMessageBox.critical(self, "Error", msg)
        
        self.focus_input()

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
