import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QFormLayout, QGroupBox
)
from PyQt6.QtCore import Qt
from src.database.db import SessionLocal
from src.models.models import Product, Category, Supplier

class ProductWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Productos - Módulo 1")
        self.resize(1000, 600)
        
        self.db = SessionLocal()
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        # Form Area
        form_group = QGroupBox("Nuevo Producto")
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.sku_input = QLineEdit()
        self.price_input = QLineEdit()
        self.stock_input = QLineEdit()
        self.stock_input.setPlaceholderText("Cantidad inicial (Unidades base)")
        
        self.is_box_check = QCheckBox("Es Caja / Pack")
        self.is_box_check.toggled.connect(self.toggle_box_fields)
        
        self.conversion_factor_input = QLineEdit()
        self.conversion_factor_input.setPlaceholderText("Ej: 50 (Unidades por caja)")
        self.conversion_factor_input.setEnabled(False)
        self.conversion_factor_input.setText("1")
        
        self.unit_type_combo = QComboBox()
        self.unit_type_combo.addItems(["Unidad", "Metro", "Kilo", "Litro"])
        
        form_layout.addRow("Nombre:", self.name_input)
        form_layout.addRow("SKU / Código:", self.sku_input)
        form_layout.addRow("Precio Venta:", self.price_input)
        form_layout.addRow("Stock Inicial:", self.stock_input)
        form_layout.addRow("Tipo Unidad:", self.unit_type_combo)
        form_layout.addRow("", self.is_box_check)
        form_layout.addRow("Factor Conversión:", self.conversion_factor_input)
        
        save_btn = QPushButton("Guardar Producto")
        save_btn.clicked.connect(self.save_product)
        form_layout.addRow(save_btn)
        
        form_group.setLayout(form_layout)
        self.layout.addWidget(form_group)
        
        # Table Area
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "SKU", "Precio", "Stock", "Es Caja?", "Factor"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)

    def toggle_box_fields(self, checked):
        self.conversion_factor_input.setEnabled(checked)
        if not checked:
            self.conversion_factor_input.setText("1")

    def load_products(self):
        self.table.setRowCount(0)
        products = self.db.query(Product).all()
        
        for row, prod in enumerate(products):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(prod.id)))
            self.table.setItem(row, 1, QTableWidgetItem(prod.name))
            self.table.setItem(row, 2, QTableWidgetItem(prod.sku or ""))
            self.table.setItem(row, 3, QTableWidgetItem(str(prod.price)))
            self.table.setItem(row, 4, QTableWidgetItem(str(prod.stock)))
            self.table.setItem(row, 5, QTableWidgetItem("Sí" if prod.is_box else "No"))
            self.table.setItem(row, 6, QTableWidgetItem(str(prod.conversion_factor)))

    def save_product(self):
        try:
            name = self.name_input.text()
            sku = self.sku_input.text()
            price = float(self.price_input.text() or 0)
            stock = int(self.stock_input.text() or 0)
            is_box = self.is_box_check.isChecked()
            factor = int(self.conversion_factor_input.text() or 1)
            unit_type = self.unit_type_combo.currentText()
            
            if not name:
                QMessageBox.warning(self, "Error", "El nombre es obligatorio")
                return

            new_product = Product(
                name=name,
                sku=sku,
                price=price,
                stock=stock,
                is_box=is_box,
                conversion_factor=factor,
                unit_type=unit_type
            )
            
            self.db.add(new_product)
            self.db.commit()
            
            self.load_products()
            self.clear_form()
            QMessageBox.information(self, "Éxito", "Producto guardado correctamente")
            
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Error", f"Error al guardar: {str(e)}")

    def clear_form(self):
        self.name_input.clear()
        self.sku_input.clear()
        self.price_input.clear()
        self.stock_input.clear()
        self.is_box_check.setChecked(False)
        self.conversion_factor_input.setText("1")

    def closeEvent(self, event):
        self.db.close()
        event.accept()
