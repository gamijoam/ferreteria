from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, 
    QComboBox, QFormLayout, QGroupBox
)
from src.database.db import SessionLocal
from src.models.models import Product, PriceRule

class PriceRuleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Precios Mayoristas - Módulo 8")
        self.resize(1200, 750)
        
        self.db = SessionLocal()
        self.current_product = None
        
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
        self.product_combo.clear()
        self.product_combo.addItem("Seleccione un producto...", None)
        products = self.db.query(Product).filter(Product.is_active == True).all()
        for p in products:
            self.product_combo.addItem(f"{p.name} (${p.price:,.2f})", p.id)

    def on_product_selected(self):
        product_id = self.product_combo.currentData()
        if not product_id:
            self.current_product = None
            self.table.setRowCount(0)
            self.lbl_base_price.setText("Precio Base: $0.00")
            return
            
        self.current_product = self.db.query(Product).get(product_id)
        self.lbl_base_price.setText(f"Precio Base: ${self.current_product.price:,.2f}")
        self.load_rules()

    def load_rules(self):
        if not self.current_product:
            return
            
        rules = self.db.query(PriceRule).filter(
            PriceRule.product_id == self.current_product.id
        ).order_by(PriceRule.min_quantity).all()
        
        self.table.setRowCount(0)
        for i, rule in enumerate(rules):
            self.table.insertRow(i)
            self.table.setRowHeight(i, 50)  # Set row height for better button visibility
            self.table.setItem(i, 0, QTableWidgetItem(str(rule.id)))
            self.table.setItem(i, 1, QTableWidgetItem(str(rule.min_quantity)))
            self.table.setItem(i, 2, QTableWidgetItem(f"${rule.price:,.2f}"))
            
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
            btn_del.clicked.connect(lambda checked, r=rule: self.delete_rule(r))
            self.table.setCellWidget(i, 3, btn_del)

    def add_rule(self):
        if not self.current_product:
            QMessageBox.warning(self, "Error", "Seleccione un producto primero")
            return
            
        try:
            min_qty = int(self.input_min_qty.text())
            price = float(self.input_price.text())
            
            if min_qty <= 0 or price <= 0:
                raise ValueError("Los valores deben ser mayores a 0")
                
            new_rule = PriceRule(
                product_id=self.current_product.id,
                min_quantity=min_qty,
                price=price
            )
            self.db.add(new_rule)
            self.db.commit()
            
            QMessageBox.information(self, "Éxito", "Regla agregada")
            self.load_rules()
            self.input_min_qty.clear()
            self.input_price.clear()
            
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_rule(self, rule):
        reply = QMessageBox.question(
            self, "Confirmar", 
            f"¿Eliminar regla: {rule.min_quantity}+ unidades a ${rule.price}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete(rule)
            self.db.commit()
            self.load_rules()

    def closeEvent(self, event):
        self.db.close()
        event.accept()
