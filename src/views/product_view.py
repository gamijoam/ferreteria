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
        self.resize(1200, 750)
        
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
        self.price_input.textChanged.connect(self.calculate_margin)
        self.cost_input = QLineEdit()  # NEW: Cost price
        self.cost_input.setPlaceholderText("Precio de costo")
        self.cost_input.textChanged.connect(self.calculate_margin)
        self.margin_label = QLabel("Margen: -")  # NEW: Margin display
        self.margin_label.setStyleSheet("font-weight: bold; color: green;")
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
        form_layout.addRow("Precio Costo:", self.cost_input)
        form_layout.addRow("Precio Venta:", self.price_input)
        form_layout.addRow("", self.margin_label)
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
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "SKU", "Costo", "Precio", "Margen%", "Stock", "Es Caja?", "Factor"
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
            self.table.setItem(row, 3, QTableWidgetItem(f"${prod.cost_price:,.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"${prod.price:,.2f}"))
            
            # Calculate margin
            if prod.price > 0:
                margin = ((prod.price - prod.cost_price) / prod.price) * 100
                margin_item = QTableWidgetItem(f"{margin:.1f}%")
                if margin < 0:
                    margin_item.setForeground(Qt.GlobalColor.red)
                else:
                    margin_item.setForeground(Qt.GlobalColor.darkGreen)
                self.table.setItem(row, 5, margin_item)
            else:
                self.table.setItem(row, 5, QTableWidgetItem("-"))
            
            self.table.setItem(row, 6, QTableWidgetItem(str(prod.stock)))
            self.table.setItem(row, 7, QTableWidgetItem("Sí" if prod.is_box else "No"))
            self.table.setItem(row, 8, QTableWidgetItem(str(prod.conversion_factor)))

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
                cost_price=float(self.cost_input.text() or 0),
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

    def calculate_margin(self):
        """Calculate and display profit margin"""
        try:
            cost = float(self.cost_input.text() or 0)
            price = float(self.price_input.text() or 0)
            
            if price > 0:
                margin = ((price - cost) / price) * 100
                if margin < 0:
                    self.margin_label.setText(f"Margen: {margin:.1f}% (PÉRDIDA)")
                    self.margin_label.setStyleSheet("font-weight: bold; color: red;")
                else:
                    self.margin_label.setText(f"Margen: {margin:.1f}%")
                    self.margin_label.setStyleSheet("font-weight: bold; color: green;")
            else:
                self.margin_label.setText("Margen: -")
                self.margin_label.setStyleSheet("font-weight: bold; color: gray;")
        except:
            self.margin_label.setText("Margen: -")
    
    def clear_form(self):
        self.name_input.clear()
        self.sku_input.clear()
        self.price_input.clear()
        self.cost_input.clear()
        self.stock_input.clear()
        self.is_box_check.setChecked(False)
        self.conversion_factor_input.setText("1")
        self.margin_label.setText("Margen: -")

    def closeEvent(self, event):
        self.db.close()
        event.accept()
