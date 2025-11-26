from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QGroupBox, QFormLayout, QTabWidget
)
from src.database.db import SessionLocal
from src.models.models import Product
from src.controllers.inventory_controller import InventoryController

class InventoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Inventario (Bodega) - Módulo 2")
        self.resize(1000, 700)
        
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
        
        self.product_combo = QComboBox()
        self.load_products_combo()
        self.product_combo.currentIndexChanged.connect(self.on_product_select)
        
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Cantidad")
        
        self.is_box_check = QCheckBox("Es Caja / Pack")
        self.is_box_check.setEnabled(False) # Will enable if product allows
        
        self.current_stock_label = QLabel("Stock Actual: -")
        
        btn_add = QPushButton("Registrar Entrada")
        btn_add.clicked.connect(self.handle_add_stock)
        
        form_layout.addRow("Producto:", self.product_combo)
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
        self.history_product_combo = QComboBox()
        self.history_product_combo.addItem("Seleccione Producto...", None)
        self.load_history_products()
        
        btn_refresh = QPushButton("Ver Historial")
        btn_refresh.clicked.connect(self.load_kardex)
        
        filter_layout.addWidget(QLabel("Producto:"))
        filter_layout.addWidget(self.history_product_combo)
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

    def load_products_combo(self):
        self.product_combo.clear()
        products = self.db.query(Product).all()
        for p in products:
            self.product_combo.addItem(f"{p.name} (SKU: {p.sku})", p.id)

    def load_history_products(self):
        # Same list but for the history tab
        products = self.db.query(Product).all()
        for p in products:
            self.history_product_combo.addItem(f"{p.name}", p.id)

    def on_product_select(self):
        product_id = self.product_combo.currentData()
        if product_id:
            product = self.db.query(Product).get(product_id)
            self.current_stock_label.setText(f"Stock Actual: {product.stock} {product.unit_type}")
            
            if product.is_box:
                self.is_box_check.setEnabled(True)
                self.is_box_check.setText(f"Es Caja (x{product.conversion_factor} {product.unit_type})")
            else:
                self.is_box_check.setEnabled(False)
                self.is_box_check.setChecked(False)
                self.is_box_check.setText("Es Caja / Pack")

    def handle_add_stock(self):
        try:
            product_id = self.product_combo.currentData()
            qty_text = self.qty_input.text()
            
            if not qty_text.isdigit():
                QMessageBox.warning(self, "Error", "Ingrese una cantidad válida")
                return
                
            qty = int(qty_text)
            is_box = self.is_box_check.isChecked()
            
            self.controller.add_stock(product_id, qty, is_box)
            
            QMessageBox.information(self, "Éxito", "Stock actualizado correctamente")
            self.qty_input.clear()
            self.on_product_select() # Refresh label
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def load_kardex(self):
        product_id = self.history_product_combo.currentData()
        if not product_id:
            return
            
        records = self.controller.get_kardex(product_id)
        self.kardex_table.setRowCount(0)
        
        for row, rec in enumerate(records):
            self.kardex_table.insertRow(row)
            self.kardex_table.setItem(row, 0, QTableWidgetItem(str(rec.date)))
            self.kardex_table.setItem(row, 1, QTableWidgetItem(rec.movement_type.value))
            self.kardex_table.setItem(row, 2, QTableWidgetItem(str(rec.quantity)))
            self.kardex_table.setItem(row, 3, QTableWidgetItem(str(rec.balance_after)))
            self.kardex_table.setItem(row, 4, QTableWidgetItem(rec.description))

    def closeEvent(self, event):
        self.db.close()
        event.accept()
