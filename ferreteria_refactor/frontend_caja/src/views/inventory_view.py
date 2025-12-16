from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QGroupBox, QFormLayout, QTabWidget, QCompleter, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QLocale
from PyQt6.QtGui import QColor
from src.database.db import SessionLocal
from src.models.models import Product
from src.controllers.inventory_controller import InventoryController
from src.utils.event_bus import event_bus

class InventoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Inventario (Bodega) - Módulo 2")
        self.resize(1200, 750)
        
        # self.db = SessionLocal() # Removed
        self.controller = InventoryController() # No DB needed
        from src.controllers.product_controller import ProductController
        self.product_controller = ProductController()
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.setup_ui()
        
        # Debounce timer
        from PyQt6.QtCore import QTimer
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(500)
        self.update_timer.timeout.connect(self.refresh_current_stock)
        
        # Connect signals
        event_bus.products_updated.connect(self.setup_product_autocomplete)
        event_bus.products_updated.connect(self.setup_stock_out_product_autocomplete)
        event_bus.inventory_updated.connect(self.schedule_refresh)

    def schedule_refresh(self):
        self.update_timer.start()

    def refresh_current_stock(self):
        if self.selected_product_id:
            self.on_product_selected()
        if self.selected_out_product_id:
            self.on_stock_out_product_selected()
        if self.selected_history_product_id:
            self.load_kardex()
        
        # Refresh stock table if it exists
        if hasattr(self, 'stock_table'):
            self.load_stock_table()

    def setup_ui(self):
        # Tabs for Entry and History
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.stock_tab = QWidget() # NEW TAB
        self.entry_tab = QWidget()
        self.stock_out_tab = QWidget()
        self.history_tab = QWidget()
        
        self.tabs.addTab(self.stock_tab, "📦 Stock Actual")
        self.tabs.addTab(self.entry_tab, "Entrada de Mercancía")
        self.tabs.addTab(self.stock_out_tab, "Salida / Ajuste")
        self.tabs.addTab(self.history_tab, "Kardex / Historial")
        
        self.setup_stock_tab() # NEW SETUP
        self.setup_entry_tab()
        self.setup_stock_out_tab()
        self.setup_history_tab()

    def setup_stock_tab(self):
        layout = QVBoxLayout()
        self.stock_tab.setLayout(layout)
        
        # Filter Layout
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Buscar Producto:"))
        
        self.stock_search_input = QLineEdit()
        self.stock_search_input.setPlaceholderText("Filtrar por nombre, SKU...")
        self.stock_search_input.textChanged.connect(self.filter_stock_table)
        filter_layout.addWidget(self.stock_search_input)
        
        btn_refresh = QPushButton("🔄 Actualizar")
        btn_refresh.clicked.connect(self.load_stock_table)
        filter_layout.addWidget(btn_refresh)
        
        layout.addLayout(filter_layout)
        
        # Table
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(5)
        self.stock_table.setHorizontalHeaderLabels([
            "Código/SKU", "Producto", "Ubicación", "Stock Base", "Visualización Inteligente"
        ])
        self.stock_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.stock_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.stock_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.stock_table)
        
        # Load initial data
        self.load_stock_table()

    def load_stock_table(self):
        self.stock_table.setRowCount(0)
        
        # Use ProductController to fetch products
        products = self.product_controller.get_active_products()
        
        # Store for filtering
        self.all_inventory_products = products
        
        self.populate_stock_table(products)

    def populate_stock_table(self, products):
        self.stock_table.setRowCount(0)
        
        for row, p in enumerate(products):
            self.stock_table.insertRow(row)
            
            # SKU
            self.stock_table.setItem(row, 0, QTableWidgetItem(p.sku or ""))
            
            # Name
            item_name = QTableWidgetItem(p.name)
            item_name.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.stock_table.setItem(row, 1, item_name)
            
            # Location
            self.stock_table.setItem(row, 2, QTableWidgetItem(p.location or "-"))
            
            # Stock Base
            base_unit = getattr(p, 'unit_type', 'UNIDAD')
            self.stock_table.setItem(row, 3, QTableWidgetItem(f"{p.stock} {base_unit}"))
            
            # SMART COLUMN
            # Need to get units for this product to calculate
            # Optimization: If many products, this is slow. But for <100 items ok.
            # Ideally fetch units in bulk or lazy load.
            units = self.product_controller.get_product_units(p.id)
            smart_display = self.format_stock_display(p.stock, units, base_unit)
            
            smart_item = QTableWidgetItem(smart_display)
            smart_item.setForeground(QColor("blue"))
            smart_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.stock_table.setItem(row, 4, smart_item)

    def filter_stock_table(self):
        query = self.stock_search_input.text().lower()
        if not hasattr(self, 'all_inventory_products'):
            return
            
        filtered = [
            p for p in self.all_inventory_products 
            if query in p.name.lower() or (p.sku and query in p.sku.lower())
        ]
        self.populate_stock_table(filtered)

    def format_stock_display(self, total_qty, units, base_unit="UNIDAD"):
        """
        Calculates smart display string.
        total_qty: float (Real stock in base units)
        units: list of dicts (ProductUnit)
        base_unit: str
        """
        if not units or total_qty == 0:
            return f"{total_qty} {base_unit}"
        
        # Sort units by conversion factor (Descending) to use largest first
        # Filter active units
        active_units = [u for u in units if u.get('is_active', True) and u.get('conversion_factor', 0) > 0]
        sorted_units = sorted(active_units, key=lambda x: x['conversion_factor'], reverse=True)
        
        if not sorted_units:
             return f"{total_qty} {base_unit}"
        
        parts = []
        remaining = total_qty
        
        # Use the LARGEST unit primarily
        largest_unit = sorted_units[0]
        factor = largest_unit['conversion_factor']
        unit_name = largest_unit['name']
        
        if factor > 1:
            main_count = int(remaining // factor)
            if main_count > 0:
                parts.append(f"{main_count} {unit_name}")
                remaining %= factor
        
        # Remainder in base unit
        # Round logic to avoid floating point errors (e.g. 0.0000001)
        remaining = round(remaining, 3)
        
        if remaining > 0:
            parts.append(f"{remaining} {base_unit}")
            
        final_str = ", ".join(parts)
        if not final_str:
            final_str = f"0 {base_unit}"
            
        # Add total reference
        return f"{final_str} ({total_qty} {base_unit})"

    def setup_entry_tab(self):
        layout = QVBoxLayout()
        self.entry_tab.setLayout(layout)
        
        form_group = QGroupBox("Registrar Compra / Entrada")
        form_layout = QFormLayout()
        
        # Product search with autocomplete
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Buscar producto por nombre o código...")
        self.setup_product_autocomplete()
        self.product_search.returnPressed.connect(self.on_product_selected)
        
        self.selected_product_id = None
        self.selected_product_label = QLabel("Ningún producto seleccionado")
        self.selected_product_label.setStyleSheet("font-weight: bold; color: #666;")
        
        self.qty_input = QDoubleSpinBox()
        self.qty_input.setRange(0, 1000000)
        self.qty_input.setDecimals(3)
        self.qty_input.setSingleStep(1)
        self.qty_input.setValue(1)
        # Force dot as decimal separator
        self.qty_input.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        
        self.is_box_check = QCheckBox("Es Caja / Pack")
        self.is_box_check.setEnabled(False) # Will enable if product allows
        
        self.current_stock_label = QLabel("Stock Actual: -")
        
        btn_add = QPushButton("Registrar Entrada")
        btn_add.clicked.connect(self.handle_add_stock)
        
        form_layout.addRow("Producto:", self.product_search)
        form_layout.addRow("", self.selected_product_label)
        form_layout.addRow("Stock Actual:", self.current_stock_label)
        form_layout.addRow("Cantidad:", self.qty_input)
        form_layout.addRow("", self.is_box_check)
        form_layout.addRow(btn_add)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        layout.addStretch()

    def setup_history_tab(self):
        layout = QVBoxLayout()
        self.history_tab.setLayout(layout)
        
        # Filter
        filter_layout = QHBoxLayout()
        
        self.history_product_search = QLineEdit()
        self.history_product_search.setPlaceholderText("Buscar producto por nombre o código...")
        self.setup_history_product_autocomplete()
        self.history_product_search.returnPressed.connect(self.on_history_product_selected)
        
        self.selected_history_product_id = None
        
        btn_refresh = QPushButton("Ver Historial")
        btn_refresh.clicked.connect(self.load_kardex)
        
        btn_all = QPushButton("Ver Todos")
        btn_all.clicked.connect(self.load_all_kardex)
        
        filter_layout.addWidget(QLabel("Producto:"))
        filter_layout.addWidget(self.history_product_search)
        filter_layout.addWidget(btn_refresh)
        filter_layout.addWidget(btn_all)
        layout.addLayout(filter_layout)
        
        # Table with improved layout
        self.kardex_table = QTableWidget()
        self.kardex_table.setColumnCount(6)
        self.kardex_table.setHorizontalHeaderLabels([
            "Fecha", "Producto", "Tipo", "Cantidad", "Saldo", "Descripción"
        ])
        
        # Set specific column widths for better visibility
        self.kardex_table.setColumnWidth(0, 140)  # Fecha
        self.kardex_table.setColumnWidth(1, 200)  # Producto
        self.kardex_table.setColumnWidth(2, 110)  # Tipo
        self.kardex_table.setColumnWidth(3, 90)   # Cantidad
        self.kardex_table.setColumnWidth(4, 90)   # Saldo
        # Description column will stretch to fill remaining space
        self.kardex_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        
        # Enable word wrap for better text display
        self.kardex_table.setWordWrap(True)
        
        layout.addWidget(self.kardex_table)

    def setup_product_autocomplete(self):
        """Setup autocomplete for product search in entry tab"""
        # products = self.db.query(Product).filter(Product.is_active == True).all()
        # Use ProductService directly or Controller
        # Since we don't have ProductController passed in, let's instantiate one or use Service
        from src.controllers.product_controller import ProductController
        self.product_controller = ProductController()
        products = self.product_controller.get_active_products()
        
        # Create list of suggestions with product data
        self.product_map = {}  # Map suggestion text to product
        suggestions = []
        for p in products:
            # p is a MockProduct object
            sku = getattr(p, 'sku', '')
            name = getattr(p, 'name', '')
            sku_part = f" - {sku}" if sku else ""
            suggestion = f"{name}{sku_part}"
            suggestions.append(suggestion)
            self.product_map[suggestion] = p
        
        # Create completer
        completer = QCompleter(suggestions)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.product_search.setCompleter(completer)
    
    def on_product_selected(self):
        """Handle product selection from autocomplete"""
        text = self.product_search.text().strip()
        if not text:
            return
        
        # Find product in map
        product = self.product_map.get(text)
        # Fallback search if not in map (e.g. typed manually) not strictly needed if completer works well
        # but for robustness:
        if not product:
             # Try API search? For now assume map covers active products loaded
             pass
        
        if product:
            self.selected_product_id = getattr(product, 'id', None)
            name = getattr(product, 'name', 'Desconocido')
            self.selected_product_label.setText(f"✓ {name}")
            self.selected_product_label.setStyleSheet("font-weight: bold; color: green;")
            stock = getattr(product, 'stock', 0)
            unit = getattr(product, 'unit_type', 'Unidad')
            self.current_stock_label.setText(f"Stock Actual: {stock} {unit}")
            
            if getattr(product, 'is_box', False):
                self.is_box_check.setEnabled(True)
                factor = getattr(product, 'conversion_factor', 1)
                self.is_box_check.setText(f"Es Caja (x{factor} {unit})")
            else:
                self.is_box_check.setEnabled(False)
                self.is_box_check.setChecked(False)
                self.is_box_check.setText("Es Caja / Pack")
        else:
            self.selected_product_id = None
            self.selected_product_label.setText("Producto no encontrado")
            self.selected_product_label.setStyleSheet("font-weight: bold; color: red;")
    
    def load_products_combo(self):
        # This method is no longer used but kept for compatibility
        pass
    
    def handle_add_stock(self):
        try:
            if not self.selected_product_id:
                QMessageBox.warning(self, "Error", "Seleccione un producto primero")
                return
            
            qty = self.qty_input.value()
            
            if qty <= 0:
                QMessageBox.warning(self, "Error", "Ingrese una cantidad válida")
                return
                
            is_box = self.is_box_check.isChecked()
            
            self.controller.add_stock(self.selected_product_id, qty, is_box)
            
            QMessageBox.information(self, "Éxito", "Stock actualizado correctamente")
            self.qty_input.setValue(1)
            self.product_search.clear()
            self.selected_product_id = None
            self.selected_product_label.setText("Ningún producto seleccionado")
            self.selected_product_label.setStyleSheet("font-weight: bold; color: #666;")
            self.current_stock_label.setText("Stock Actual: -")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def setup_stock_out_tab(self):
        layout = QVBoxLayout()
        self.stock_out_tab.setLayout(layout)
        
        form_group = QGroupBox("Registrar Salida / Ajuste / Merma")
        form_layout = QFormLayout()
        
        # Product search
        self.out_product_search = QLineEdit()
        self.out_product_search.setPlaceholderText("Buscar producto por nombre o código...")
        self.setup_stock_out_product_autocomplete()
        self.out_product_search.returnPressed.connect(self.on_stock_out_product_selected)
        
        self.selected_out_product_id = None
        self.selected_out_product_label = QLabel("Ningún producto seleccionado")
        self.selected_out_product_label.setStyleSheet("font-weight: bold; color: #666;")
        
        self.out_current_stock_label = QLabel("Stock Actual: -")
        
        self.out_qty_input = QDoubleSpinBox()
        self.out_qty_input.setRange(0, 1000000)
        self.out_qty_input.setDecimals(3)
        self.out_qty_input.setSingleStep(1)
        self.out_qty_input.setValue(1)
        self.out_qty_input.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        
        self.out_reason_combo = QComboBox()
        self.out_reason_combo.addItems(["Ajuste de Inventario", "Merma / Dañado", "Donación", "Uso Interno", "Otro"])
        self.out_reason_combo.setEditable(True)
        
        btn_remove = QPushButton("Registrar Salida")
        btn_remove.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold;")
        btn_remove.clicked.connect(self.handle_remove_stock)
        
        form_layout.addRow("Producto:", self.out_product_search)
        form_layout.addRow("", self.selected_out_product_label)
        form_layout.addRow("Stock Actual:", self.out_current_stock_label)
        form_layout.addRow("Cantidad a Retirar:", self.out_qty_input)
        form_layout.addRow("Motivo:", self.out_reason_combo)
        form_layout.addRow(btn_remove)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        layout.addStretch()

    def setup_stock_out_product_autocomplete(self):
        # products = self.db.query(Product).filter(Product.is_active == True).all()
        # Ensure controller exists
        if not hasattr(self, 'product_controller'):
             from src.controllers.product_controller import ProductController
             self.product_controller = ProductController()
             
        products = self.product_controller.get_active_products()
        
        self.out_product_map = {}
        suggestions = []
        for p in products:
            sku = getattr(p, 'sku', '')
            name = getattr(p, 'name', '')
            sku_part = f" - {sku}" if sku else ""
            suggestion = f"{name}{sku_part}"
            suggestions.append(suggestion)
            self.out_product_map[suggestion] = p
        
        completer = QCompleter(suggestions)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.out_product_search.setCompleter(completer)

    def on_stock_out_product_selected(self):
        text = self.out_product_search.text().strip()
        if not text:
            return
            
        product = self.out_product_map.get(text)
        # Fallback removed as DB is gone
        
        if product:
            self.selected_out_product_id = getattr(product, 'id', None)
            name = getattr(product, 'name', 'Desconocido')
            self.selected_out_product_label.setText(f"✓ {name}")
            self.selected_out_product_label.setStyleSheet("font-weight: bold; color: green;")
            stock = getattr(product, 'stock', 0)
            unit = getattr(product, 'unit_type', 'Unidad')
            self.out_current_stock_label.setText(f"Stock Actual: {stock} {unit}")
        else:
            self.selected_out_product_id = None
            self.selected_out_product_label.setText("Producto no encontrado")
            self.selected_out_product_label.setStyleSheet("font-weight: bold; color: red;")

    def handle_remove_stock(self):
        try:
            if not self.selected_out_product_id:
                QMessageBox.warning(self, "Error", "Seleccione un producto primero")
                return
            
            qty = self.out_qty_input.value()
            if qty <= 0:
                QMessageBox.warning(self, "Error", "Ingrese una cantidad válida")
                return
                
            reason = self.out_reason_combo.currentText()
            if not reason:
                QMessageBox.warning(self, "Error", "Ingrese un motivo")
                return
            
            self.controller.remove_stock(self.selected_out_product_id, qty, reason)
            
            QMessageBox.information(self, "Éxito", "Salida de stock registrada correctamente")
            self.out_qty_input.setValue(1)
            self.out_product_search.clear()
            self.selected_out_product_id = None
            self.selected_out_product_label.setText("Ningún producto seleccionado")
            self.selected_out_product_label.setStyleSheet("font-weight: bold; color: #666;")
            self.out_current_stock_label.setText("Stock Actual: -")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def setup_history_product_autocomplete(self):
        """Setup autocomplete for product search in history tab"""
        # products = self.db.query(Product).filter(Product.is_active == True).all()
        if not hasattr(self, 'product_controller'):
             from src.controllers.product_controller import ProductController
             self.product_controller = ProductController()
        
        products = self.product_controller.get_active_products()
        
        # Reuse the same map logic or create new one
        self.history_product_map = {}
        suggestions = []
        for p in products:
            sku = getattr(p, 'sku', '')
            name = getattr(p, 'name', '')
            sku_part = f" - {sku}" if sku else ""
            suggestion = f"{name}{sku_part}"
            suggestions.append(suggestion)
            self.history_product_map[suggestion] = p
        
        completer = QCompleter(suggestions)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.history_product_search.setCompleter(completer)

    def on_history_product_selected(self):
        text = self.history_product_search.text().strip()
        if not text:
            return
            
        product = self.history_product_map.get(text)
        # Fallback removed
            
        if product:
            self.selected_history_product_id = getattr(product, 'id', None)
            self.load_kardex()
        else:
            self.selected_history_product_id = None
            QMessageBox.warning(self, "Error", "Producto no encontrado")

    def load_history_products(self):
        pass

    def load_all_kardex(self):
        self.history_product_search.clear()
        self.selected_history_product_id = None
        self.load_kardex()

    def load_kardex(self):
        # Allow loading all history if no product selected
        product_id = self.selected_history_product_id
        
        self.kardex_table.setRowCount(0)
        
        movements = self.controller.get_kardex(product_id)
        
        for row, mov in enumerate(movements):
            self.kardex_table.insertRow(row)
            
            # Date
            date_item = QTableWidgetItem(mov.date.strftime("%Y-%m-%d %H:%M"))
            self.kardex_table.setItem(row, 0, date_item)
            
            # Product Name
            product_name = mov.product.name if mov.product else "Desconocido"
            self.kardex_table.setItem(row, 1, QTableWidgetItem(product_name))
            
            # Type - with color coding
            type_item = QTableWidgetItem(mov.movement_type.value)
            if mov.movement_type.value == "PURCHASE":
                type_item.setBackground(QColor("#c8e6c9"))  # Light green
            elif mov.movement_type.value == "SALE":
                type_item.setBackground(QColor("#ffcdd2"))  # Light red
            elif mov.movement_type.value == "ADJUSTMENT":
                type_item.setBackground(QColor("#fff9c4"))  # Light yellow
            self.kardex_table.setItem(row, 2, type_item)
            
            # Quantity - with color and sign
            qty_text = f"+{mov.quantity}" if mov.quantity > 0 else str(mov.quantity)
            qty_item = QTableWidgetItem(qty_text)
            if mov.quantity > 0:
                qty_item.setForeground(Qt.GlobalColor.green)
            else:
                qty_item.setForeground(Qt.GlobalColor.red)
            self.kardex_table.setItem(row, 3, qty_item)
            
            # Balance
            self.kardex_table.setItem(row, 4, QTableWidgetItem(f"{mov.balance_after:.2f}"))
            
            # Description
            self.kardex_table.setItem(row, 5, QTableWidgetItem(mov.description or ""))
            
            # Set row height for better readability
            self.kardex_table.setRowHeight(row, 50)

    def closeEvent(self, event):
        # self.db.close()
        event.accept()
