import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QFormLayout, QGroupBox, QDialog, QDoubleSpinBox
)
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt, QLocale
from src.database.db import SessionLocal
from src.controllers.product_controller import ProductController

class ProductFormDialog(QDialog):
    """Dialog for creating/editing products"""
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle("Editar Producto" if product else "Nuevo Producto")
        self.resize(500, 600)
        
        self.setup_ui()
        
        if product:
            self.populate_form(product)
    
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Form
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.sku_input = QLineEdit()
        self.price_input = QLineEdit()
        self.price_input.textChanged.connect(self.calculate_margin)
        self.cost_input = QLineEdit()
        self.cost_input.setPlaceholderText("Precio de costo")
        self.cost_input.textChanged.connect(self.calculate_margin)
        self.margin_label = QLabel("Margen: -")
        self.margin_label.setStyleSheet("font-weight: bold; color: green;")
        
        self.stock_input = QDoubleSpinBox()
        self.stock_input.setRange(0, 1000000)
        self.stock_input.setDecimals(3)
        self.stock_input.setSingleStep(1)
        # Force dot as decimal separator
        self.stock_input.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        
        self.min_stock_input = QDoubleSpinBox()
        self.min_stock_input.setRange(0, 1000000)
        self.min_stock_input.setDecimals(3)
        self.min_stock_input.setSingleStep(1)
        self.min_stock_input.setValue(5.0)
        self.min_stock_input.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        
        self.is_box_check = QCheckBox("Es Caja / Pack")
        self.is_box_check.toggled.connect(self.toggle_box_fields)
        
        self.conversion_factor_input = QLineEdit()
        self.conversion_factor_input.setPlaceholderText("Ej: 50 (Unidades por caja)")
        self.conversion_factor_input.setEnabled(False)
        self.conversion_factor_input.setText("1")
        
        self.unit_type_combo = QComboBox()
        self.unit_type_combo.addItems(["Unidad", "Metro", "Kilo", "Litro"])
        
        form_layout.addRow("Nombre:*", self.name_input)
        form_layout.addRow("SKU / Código:", self.sku_input)
        form_layout.addRow("Precio Costo:", self.cost_input)
        form_layout.addRow("Precio Venta:", self.price_input)
        form_layout.addRow("", self.margin_label)
        form_layout.addRow("Stock:", self.stock_input)
        form_layout.addRow("Stock Mínimo (Alerta):", self.min_stock_input)
        form_layout.addRow("Tipo Unidad:", self.unit_type_combo)
        form_layout.addRow("", self.is_box_check)
        form_layout.addRow("Factor Conversión:", self.conversion_factor_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("Guardar")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-size: 12pt;")
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet("background-color: #f44336; color: white; padding: 10px; font-size: 12pt;")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
    
    def toggle_box_fields(self, checked):
        self.conversion_factor_input.setEnabled(checked)
        if not checked:
            self.conversion_factor_input.setText("1")
    
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
    
    def populate_form(self, product):
        """Fill form with product data"""
        self.name_input.setText(product.name)
        self.sku_input.setText(product.sku or "")
        self.price_input.setText(str(product.price))
        self.cost_input.setText(str(product.cost_price))
        self.stock_input.setValue(float(product.stock))
        self.min_stock_input.setValue(float(product.min_stock if hasattr(product, 'min_stock') else 5.0))
        self.is_box_check.setChecked(product.is_box)
        self.conversion_factor_input.setText(str(product.conversion_factor))
        self.unit_type_combo.setCurrentText(product.unit_type)
        self.calculate_margin()
    
    def get_data(self):
        """Get form data as dict"""
        return {
            "name": self.name_input.text().strip(),
            "sku": self.sku_input.text().strip() or None,
            "price": float(self.price_input.text() or 0),
            "cost_price": float(self.cost_input.text() or 0),
            "stock": self.stock_input.value(),
            "min_stock": self.min_stock_input.value(),
            "is_box": self.is_box_check.isChecked(),
            "conversion_factor": int(self.conversion_factor_input.text() or 1),
            "unit_type": self.unit_type_combo.currentText()
        }


class ProductWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Productos")
        self.resize(1200, 750)
        
        self.db = SessionLocal()
        self.controller = ProductController(self.db)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        # Header with title and new button
        header_layout = QHBoxLayout()
        
        title = QLabel("📦 GESTIÓN DE PRODUCTOS")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #1976D2; padding: 10px;")
        
        new_btn = QPushButton("+ Nuevo Producto")
        new_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px 24px;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        new_btn.clicked.connect(self.open_new_product_dialog)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(new_btn)
        self.layout.addLayout(header_layout)
        
        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Buscar:")
        search_label.setFont(QFont("Arial", 11))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o código...")
        self.search_input.setFont(QFont("Arial", 11))
        self.search_input.textChanged.connect(self.filter_products)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        self.layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "SKU", "Costo", "Precio", "Margen%", "Stock", "Min.", "Es Caja?", "Factor", "Editar", "Eliminar"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setFont(QFont("Arial", 10))
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:alternate {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #1976D2;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)
        
        self.layout.addWidget(self.table)

    def open_new_product_dialog(self):
        """Open dialog to create new product"""
        dialog = ProductFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                data = dialog.get_data()
                if not data["name"]:
                    QMessageBox.warning(self, "Error", "El nombre es obligatorio")
                    return
                
                self.controller.create_product(**data)
                QMessageBox.information(self, "Éxito", "Producto creado correctamente")
                self.load_products()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al crear producto: {str(e)}")

    def open_edit_product_dialog(self, product_id):
        """Open dialog to edit product"""
        product = self.controller.get_product_by_id(product_id)
        if not product:
            return
        
        dialog = ProductFormDialog(self, product)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                data = dialog.get_data()
                if not data["name"]:
                    QMessageBox.warning(self, "Error", "El nombre es obligatorio")
                    return
                
                self.controller.update_product(product_id, **data)
                QMessageBox.information(self, "Éxito", "Producto actualizado correctamente")
                self.load_products()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al actualizar: {str(e)}")

    def load_products(self):
        self.table.setRowCount(0)
        products = self.controller.get_active_products()
        
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
                    margin_item.setForeground(QColor("red"))
                else:
                    margin_item.setForeground(QColor("green"))
                self.table.setItem(row, 5, margin_item)
            else:
                self.table.setItem(row, 5, QTableWidgetItem("-"))
            
            stock_item = QTableWidgetItem(str(prod.stock))
            min_stock = prod.min_stock if hasattr(prod, 'min_stock') else 5.0
            
            if prod.stock <= min_stock:
                stock_item.setForeground(QColor("red"))
                stock_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
                stock_item.setBackground(QColor("#FFEBEE")) # Light red background
            
            self.table.setItem(row, 6, stock_item)
            self.table.setItem(row, 7, QTableWidgetItem(str(min_stock)))
            self.table.setItem(row, 8, QTableWidgetItem("Sí" if prod.is_box else "No"))
            self.table.setItem(row, 9, QTableWidgetItem(str(prod.conversion_factor)))
            
            # Edit Button
            btn_edit = QPushButton("✏ Editar")
            btn_edit.setStyleSheet("background-color: #2196F3; color: white; padding: 6px; border-radius: 4px;")
            btn_edit.clicked.connect(lambda checked, pid=prod.id: self.open_edit_product_dialog(pid))
            self.table.setCellWidget(row, 10, btn_edit)
            
            # Delete Button
            btn_delete = QPushButton("🗑 Eliminar")
            btn_delete.setStyleSheet("background-color: #F44336; color: white; padding: 6px; border-radius: 4px;")
            btn_delete.clicked.connect(lambda checked, pid=prod.id: self.delete_product(pid))
            self.table.setCellWidget(row, 11, btn_delete)

    def filter_products(self):
        """Filter products based on search text"""
        search_text = self.search_input.text().lower()
        
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 1).text().lower()
            sku = self.table.item(row, 2).text().lower()
            
            if search_text in name or search_text in sku:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def delete_product(self, product_id):
        reply = QMessageBox.question(
            self, "Confirmar Eliminación",
            "¿Está seguro de eliminar este producto?\n\nEl producto quedará inactivo pero se preservará el historial de ventas.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.controller.delete_product(product_id)
                QMessageBox.information(self, "Éxito", "Producto eliminado correctamente")
                self.load_products()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def closeEvent(self, event):
        self.db.close()
        event.accept()
