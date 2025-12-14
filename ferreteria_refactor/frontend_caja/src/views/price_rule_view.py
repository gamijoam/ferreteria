from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, 
    QComboBox, QFormLayout, QGroupBox
)
from src.utils.event_bus import event_bus
from frontend_caja.services.product_service import ProductService

class PriceRuleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Precios Mayoristas (Reglas) - Módulo 8")
        self.resize(1000, 600)
        
        self.product_service = ProductService()
        self.current_product = None
        self.products_map = {} # Cache products by ID
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        # Product selector
        selector_layout = QHBoxLayout()
        self.product_combo = QComboBox()
        self.product_combo.currentIndexChanged.connect(self.on_product_selected)
        
        selector_layout.addWidget(QLabel("Producto:"))
        selector_layout.addWidget(self.product_combo)
        self.layout.addLayout(selector_layout)
        
        # Product info
        self.lbl_base_price = QLabel("Precio Base: $0")
        self.lbl_base_price.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.layout.addWidget(self.lbl_base_price)
        
        # Add rule form
        form_group = QGroupBox("Nueva Regla de Precio")
        form_layout = QFormLayout()
        
        self.input_min_qty = QLineEdit()
        self.input_min_qty.setPlaceholderText("Ej: 10")
        
        self.input_price = QLineEdit()
        self.input_price.setPlaceholderText("Ej: 90")
        
        btn_add = QPushButton("Agregar Regla")
        btn_add.clicked.connect(self.add_rule)
        
        form_layout.addRow("Cantidad Mínima:", self.input_min_qty)
        form_layout.addRow("Precio Especial:", self.input_price)
        form_layout.addRow(btn_add)
        
        form_group.setLayout(form_layout)
        self.layout.addWidget(form_group)
        
        # Rules table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Cantidad Mínima", "Precio", "Eliminar"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)

    def load_products(self):
        self.product_combo.blockSignals(True)
        self.product_combo.clear()
        self.product_combo.addItem("Seleccione un producto...", None)
        
        try:
            products = self.product_service.get_all_products()
            # products is a list of dicts now
            for p in products:
                # Store in map for quick access
                self.products_map[p['id']] = p
                self.product_combo.addItem(f"{p['name']} (${p['price']:,.2f})", p['id'])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando productos: {str(e)}")
            
        self.product_combo.blockSignals(False)

    def on_product_selected(self):
        product_id = self.product_combo.currentData()
        if not product_id:
            self.current_product = None
            self.table.setRowCount(0)
            self.lbl_base_price.setText("Precio Base: $0.00")
            return
            
        self.current_product = self.products_map.get(product_id)
        if self.current_product:
            self.lbl_base_price.setText(f"Precio Base: ${self.current_product['price']:,.2f}")
            self.load_rules()

    def load_rules(self):
        if not self.current_product:
            return
            
        try:
            rules = self.product_service.get_price_rules(self.current_product['id'])
            
            self.table.setRowCount(0)
            for i, rule in enumerate(rules):
                self.table.insertRow(i)
                self.table.setRowHeight(i, 50) 
                self.table.setItem(i, 0, QTableWidgetItem(str(rule['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(str(rule['min_quantity'])))
                self.table.setItem(i, 2, QTableWidgetItem(f"${rule['price']:,.2f}"))
                
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
                # rule['id'] is correct for dict access
                btn_del.clicked.connect(lambda checked, rid=rule['id']: self.delete_rule(rid))
                self.table.setCellWidget(i, 3, btn_del)
        except Exception as e:
             QMessageBox.critical(self, "Error", f"Error cargando reglas: {str(e)}")

    def add_rule(self):
        if not self.current_product:
            QMessageBox.warning(self, "Error", "Seleccione un producto primero")
            return
            
        try:
            min_qty = float(self.input_min_qty.text())
            price = float(self.input_price.text())
            
            if min_qty <= 0 or price <= 0:
                raise ValueError("Los valores deben ser mayores a 0")
                
            self.product_service.add_price_rule(
                self.current_product['id'],
                min_quantity=min_qty,
                price=price
            )
            
            QMessageBox.information(self, "Éxito", "Regla agregada")
            self.load_rules()
            self.input_min_qty.clear()
            self.input_price.clear()
            
        except ValueError as e:
             # Handle int conversion error or logical error
             QMessageBox.warning(self, "Error", "Valores inválidos. " + str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_rule(self, rule_id):
        reply = QMessageBox.question(
            self, "Confirmar", 
            "¿Eliminar esta regla de precio?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.product_service.delete_price_rule(rule_id)
                self.load_rules()
            except Exception as e:
                 QMessageBox.critical(self, "Error", str(e))

    def closeEvent(self, event):
        event.accept()
