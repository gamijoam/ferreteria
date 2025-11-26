from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QGroupBox, QFormLayout, QTabWidget, QCompleter
)
from PyQt6.QtCore import Qt
from src.database.db import SessionLocal
from src.models.models import Product
from src.controllers.inventory_controller import InventoryController

class InventoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Inventario (Bodega) - Módulo 2")
        self.resize(1200, 750)
        
        self.db = SessionLocal()
        self.controller = InventoryController(self.db)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.setup_ui()

    def setup_ui(self):
        # Tabs for Entry and History
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.entry_tab = QWidget()
        self.history_tab = QWidget()
        
        self.tabs.addTab(self.entry_tab, "Entrada de Mercancía")
        self.tabs.addTab(self.history_tab, "Kardex / Historial")
        
        self.setup_entry_tab()
        self.setup_history_tab()

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
        
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Cantidad")
        
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
        
        filter_layout.addWidget(QLabel("Producto:"))
        filter_layout.addWidget(self.history_product_search)
        filter_layout.addWidget(btn_refresh)
        layout.addLayout(filter_layout)
        
        # Table
        self.kardex_table = QTableWidget()
        self.kardex_table.setColumnCount(5)
        self.kardex_table.setHorizontalHeaderLabels([
            "Fecha", "Tipo", "Cantidad", "Saldo", "Descripción"
        ])
        self.kardex_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.kardex_table)

    def setup_product_autocomplete(self):
        """Setup autocomplete for product search in entry tab"""
        products = self.db.query(Product).filter(Product.is_active == True).all()
        
        # Create list of suggestions with product data
        self.product_map = {}  # Map suggestion text to product
        suggestions = []
        for p in products:
            sku_part = f" - {p.sku}" if p.sku else ""
            suggestion = f"{p.name}{sku_part}"
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
        if not product:
            # Try to find by name or SKU
            product = self.db.query(Product).filter(
                (Product.name.ilike(f"%{text}%")) | (Product.sku == text),
                Product.is_active == True
            ).first()
        
        if product:
            self.selected_product_id = product.id
            self.selected_product_label.setText(f"✓ {product.name}")
            self.selected_product_label.setStyleSheet("font-weight: bold; color: green;")
            self.current_stock_label.setText(f"Stock Actual: {product.stock} {product.unit_type}")
            
            if product.is_box:
                self.is_box_check.setEnabled(True)
                self.is_box_check.setText(f"Es Caja (x{product.conversion_factor} {product.unit_type})")
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
                QMessageBox.warning(self, "Error", "Por favor seleccione un producto primero")
                return
            
            qty_text = self.qty_input.text()
            
            if not qty_text.isdigit():
                QMessageBox.warning(self, "Error", "Ingrese una cantidad válida")
                return
                
            qty = int(qty_text)
            is_box = self.is_box_check.isChecked()
            
            self.controller.add_stock(self.selected_product_id, qty, is_box)
            
            QMessageBox.information(self, "Éxito", "Stock actualizado correctamente")
            self.qty_input.clear()
            self.product_search.clear()
            self.selected_product_id = None
            self.selected_product_label.setText("Ningún producto seleccionado")
            self.selected_product_label.setStyleSheet("font-weight: bold; color: #666;")
            self.current_stock_label.setText("Stock Actual: -")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def setup_history_product_autocomplete(self):
        """Setup autocomplete for product search in history tab"""
        products = self.db.query(Product).filter(Product.is_active == True).all()
        
        # Reuse the same map logic or create new one
        self.history_product_map = {}
        suggestions = []
        for p in products:
            sku_part = f" - {p.sku}" if p.sku else ""
            suggestion = f"{p.name}{sku_part}"
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
        if not product:
            product = self.db.query(Product).filter(
                (Product.name.ilike(f"%{text}%")) | (Product.sku == text),
                Product.is_active == True
            ).first()
            
        if product:
            self.selected_history_product_id = product.id
            self.load_kardex()
        else:
            self.selected_history_product_id = None
            QMessageBox.warning(self, "Error", "Producto no encontrado")

    def load_history_products(self):
        pass

    def load_kardex(self):
        if not self.selected_history_product_id:
            return

        self.kardex_table.setRowCount(0)
        
        movements = self.controller.get_kardex(self.selected_history_product_id)
        
        for row, mov in enumerate(movements):
            self.kardex_table.insertRow(row)
            self.kardex_table.setItem(row, 0, QTableWidgetItem(mov.date.strftime("%Y-%m-%d %H:%M")))
            self.kardex_table.setItem(row, 1, QTableWidgetItem(mov.movement_type.value))
            
            qty_item = QTableWidgetItem(str(mov.quantity))
            if mov.quantity > 0:
                qty_item.setForeground(Qt.GlobalColor.green)
            else:
                qty_item.setForeground(Qt.GlobalColor.red)
            self.kardex_table.setItem(row, 2, qty_item)
            
            self.kardex_table.setItem(row, 3, QTableWidgetItem(str(mov.balance_after)))
            self.kardex_table.setItem(row, 4, QTableWidgetItem(mov.description or ""))

    def closeEvent(self, event):
        self.db.close()
        event.accept()
