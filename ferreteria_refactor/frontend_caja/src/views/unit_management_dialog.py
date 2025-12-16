from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDoubleSpinBox, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class UnitManagementDialog(QDialog):
    """Dialog for managing product presentations/units (Saco, Caja, Pallet, etc.)"""
    
    def __init__(self, parent=None, product_id=None, controller=None):
        super().__init__(parent)
        self.product_id = product_id
        self.controller = controller
        
        self.setWindowTitle("Gestionar Presentaciones del Producto")
        self.resize(700, 500)
        self.setMinimumHeight(400)
        
        self.setup_ui()
        
        if self.product_id:
            self.load_units()
        else:
            QMessageBox.warning(
                self, 
                "Advertencia", 
                "Debe guardar el producto primero antes de gestionar presentaciones."
            )
            self.accept()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Header
        header = QLabel("📦 Presentaciones del Producto")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #1976D2; padding: 10px;")
        main_layout.addWidget(header)
        
        # Info label
        info_label = QLabel(
            "Las presentaciones permiten vender el mismo producto en diferentes formatos.\n"
            "Ejemplo: Cemento en Sacos de 42.5kg, Sacos de 25kg, o por Kilogramo."
        )
        info_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # Table of existing units
        table_group = QGroupBox("Presentaciones Actuales")
        table_layout = QVBoxLayout()
        
        self.units_table = QTableWidget()
        self.units_table.setColumnCount(5)
        self.units_table.setHorizontalHeaderLabels([
            "Nombre", "Factor", "Código Barras", "Precio", "Acciones"
        ])
        self.units_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.units_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.units_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.units_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.units_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.units_table.setAlternatingRowColors(True)
        
        table_layout.addWidget(self.units_table)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)
        
        # Form to add new unit
        form_group = QGroupBox("Agregar Nueva Presentación")
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Saco 42.5kg, Caja x12, Pallet")
        form_layout.addRow("Nombre:", self.name_input)
        
        self.factor_input = QDoubleSpinBox()
        self.factor_input.setRange(0.01, 999999.99)
        self.factor_input.setDecimals(2)
        self.factor_input.setValue(1.0)
        self.factor_input.setToolTip("Cuántas unidades base contiene esta presentación")
        form_layout.addRow("Factor de Conversión:", self.factor_input)
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Código de barras único (opcional)")
        form_layout.addRow("Código de Barras:", self.barcode_input)
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 999999.99)
        self.price_input.setDecimals(2)
        self.price_input.setPrefix("$ ")
        self.price_input.setToolTip("Precio específico para esta presentación (opcional)")
        form_layout.addRow("Precio (Opcional):", self.price_input)
        
        # Add button
        add_btn = QPushButton("➕ Agregar Presentación")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_btn.clicked.connect(self.add_unit)
        form_layout.addRow("", add_btn)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        # Close button
        close_btn = QPushButton("Cerrar")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        close_btn.clicked.connect(self.accept)
        main_layout.addWidget(close_btn)
    
    def load_units(self):
        """Load existing units from database"""
        if not self.controller or not self.product_id:
            return
        
        try:
            units = self.controller.get_product_units(self.product_id)
            
            self.units_table.setRowCount(0)
            
            for unit in units:
                row = self.units_table.rowCount()
                self.units_table.insertRow(row)
                
                # Name
                self.units_table.setItem(row, 0, QTableWidgetItem(unit.get('name', '')))
                
                # Factor
                factor = unit.get('conversion_factor', 1.0)
                self.units_table.setItem(row, 1, QTableWidgetItem(f"{factor:.2f}"))
                
                # Barcode
                barcode = unit.get('barcode', '') or '-'
                self.units_table.setItem(row, 2, QTableWidgetItem(barcode))
                
                # Price
                price = unit.get('price', 0) or 0
                price_text = f"${price:.2f}" if price > 0 else "Auto"
                self.units_table.setItem(row, 3, QTableWidgetItem(price_text))
                
                # Delete button
                delete_btn = QPushButton("🗑 Eliminar")
                delete_btn.setStyleSheet("background-color: #f44336; color: white; padding: 4px 8px; border-radius: 3px;")
                unit_id = unit.get('id')
                delete_btn.clicked.connect(lambda checked, uid=unit_id: self.delete_unit(uid))
                self.units_table.setCellWidget(row, 4, delete_btn)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar presentaciones: {str(e)}")
    
    def add_unit(self):
        """Add new unit presentation"""
        name = self.name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Error", "El nombre de la presentación es obligatorio")
            return
        
        if not self.controller or not self.product_id:
            QMessageBox.warning(self, "Error", "No se puede agregar presentación sin producto guardado")
            return
        
        try:
            unit_data = {
                'product_id': self.product_id,
                'name': name,
                'conversion_factor': self.factor_input.value(),
                'barcode': self.barcode_input.text().strip() or None,
                'price': self.price_input.value() if self.price_input.value() > 0 else None,
                'is_active': True,
                'is_default_sale': False
            }
            
            self.controller.create_product_unit(unit_data)
            
            # Clear form
            self.name_input.clear()
            self.factor_input.setValue(1.0)
            self.barcode_input.clear()
            self.price_input.setValue(0)
            
            # Reload table
            self.load_units()
            
            QMessageBox.information(self, "Éxito", "Presentación agregada correctamente")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al agregar presentación: {str(e)}")
    
    def delete_unit(self, unit_id):
        """Delete unit presentation"""
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            "¿Está seguro de eliminar esta presentación?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.controller.delete_product_unit(unit_id)
                self.load_units()
                QMessageBox.information(self, "Éxito", "Presentación eliminada correctamente")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar: {str(e)}")
