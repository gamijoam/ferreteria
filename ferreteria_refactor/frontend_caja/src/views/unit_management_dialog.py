from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDoubleSpinBox, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

class UnitManagementDialog(QDialog):
    """Dialog for managing product presentations/units (Saco, Caja, Pallet, etc.)"""
    
    def __init__(self, parent=None, product_id=None, controller=None, base_unit_name="UNIDAD"):
        super().__init__(parent)
        self.product_id = product_id
        self.controller = controller
        self.base_unit_name = base_unit_name
        
        self.setWindowTitle("Gestionar Presentaciones del Producto")
        self.resize(800, 600)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 6px;
                margin-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #1976D2;
            }
            QLabel {
                font-size: 11pt;
            }
        """)
        
        self.setup_ui()
        
        if self.product_id:
            self.load_units()
        else:
            QMessageBox.warning(
                self, 
                "Advertencia", 
                "Debe guardar el producto primero antes de gestionar presentaciones."
            )
            self.close()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        self.setLayout(main_layout)
        
        # Header
        header_layout = QHBoxLayout()
        header = QLabel("📦 Presentaciones y Unidades")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #1565C0;")
        header_layout.addWidget(header)
        main_layout.addLayout(header_layout)
        
        # Helper text
        info = QLabel(
            f"Defina presentaciones alternativas para este producto. la unidad base es: <b>{self.base_unit_name}</b>"
        )
        info.setStyleSheet("color: #555;")
        main_layout.addWidget(info)
        
        # === TOP SECTION: FORM ===
        form_group = QGroupBox("➕ Nueva Presentación")
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Saco 50kg, Caja x12, Pallet")
        self.name_input.setMinimumHeight(35)
        self.name_input.textChanged.connect(self.update_explanation)
        form_layout.addRow("Nombre Presentación:", self.name_input)
        
        # Factor
        self.factor_input = QDoubleSpinBox()
        self.factor_input.setRange(0.001, 999999.99)
        self.factor_input.setDecimals(3)
        self.factor_input.setValue(1.0)
        self.factor_input.setMinimumHeight(35)
        self.factor_input.valueChanged.connect(self.update_explanation)
        form_layout.addRow("Factor de Conversión:", self.factor_input)
        
        # EXPLANATION LABEL (The core requirement)
        self.explanation_label = QLabel(f"1 [Presentación] = 1.00 {self.base_unit_name}")
        self.explanation_label.setStyleSheet("""
            background-color: #E3F2FD;
            color: #0D47A1;
            padding: 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 10pt;
        """)
        form_layout.addRow("", self.explanation_label)
        
        # Barcode
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Código de barras específico para esta unidad")
        self.barcode_input.setMinimumHeight(35)
        form_layout.addRow("Código de Barras:", self.barcode_input)
        
        # Price (Optional)
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 999999.99)
        self.price_input.setDecimals(2)
        self.price_input.setPrefix("$ ")
        self.price_input.setMinimumHeight(35)
        self.price_input.setToolTip("Dejar en 0 para calcular automáticamente base * factor")
        form_layout.addRow("Precio Fijo (Opcional):", self.price_input)
        
        # Is Default Checkbox
        self.is_default_check = QCheckBox("Predeterminado para Venta")
        self.is_default_check.setToolTip("Marcar para que el POS sugiera esta unidad por defecto")
        self.is_default_check.setStyleSheet("font-weight: bold; color: #2E7D32;")
        form_layout.addRow("", self.is_default_check)
        
        # Add Button
        add_btn = QPushButton("Guardar Presentación")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        add_btn.clicked.connect(self.add_unit)
        form_layout.addRow("", add_btn)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        # === BOTTOM SECTION: TABLE ===
        table_group = QGroupBox("📋 Presentaciones Actuales")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(5, 10, 5, 10)  # Reduced margins
        
        self.units_table = QTableWidget()
        self.units_table.setColumnCount(6)
        self.units_table.setHorizontalHeaderLabels([
            "Nombre", "Factor", "Código", "Precio", "Default", "Acciones"
        ])
        
        # FIX: Apply Stretch to improve readability
        header = self.units_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Optional: Optimize specific columns if needed, but basic Stretch ensures visibility
        # header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents) 
        
        self.units_table.setMinimumHeight(250)  # Ensure minimum height
        
        self.units_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #eee;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
        """)
        
        table_layout.addWidget(self.units_table)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)
        
        # Footer
        close_btn = QPushButton("Cerrar")
        close_btn.setFixedSize(100, 35)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575; 
                color: white; 
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        close_btn.clicked.connect(self.accept)
        
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        footer_layout.addWidget(close_btn)
        main_layout.addLayout(footer_layout)

    def update_explanation(self):
        """Update the logic explanation label directly"""
        name = self.name_input.text().strip() or "[Presentación]"
        factor = self.factor_input.value()
        
        # Example: 1 Saco = 20.00 KG
        self.explanation_label.setText(
            f"✅ Entendido: 1 {name} contiene {factor:.2f} {self.base_unit_name}"
        )
        self.explanation_label.setStyleSheet("""
            background-color: #E8F5E9;
            color: #2E7D32;
            padding: 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 10pt;
            border: 1px solid #C8E6C9;
        """)

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
                name_item = QTableWidgetItem(unit.get('name', ''))
                name_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
                self.units_table.setItem(row, 0, name_item)
                
                # Factor
                factor = unit.get('conversion_factor', 1.0)
                # Show nicely formatted factor
                self.units_table.setItem(row, 1, QTableWidgetItem(f"{factor:.3f}"))
                
                # Barcode
                barcode = unit.get('barcode', '') or '-'
                self.units_table.setItem(row, 2, QTableWidgetItem(barcode))
                
                # Price
                price = unit.get('price', 0) or 0
                price_text = f"${price:,.2f}" if price > 0 else "(Auto)"
                self.units_table.setItem(row, 3, QTableWidgetItem(price_text))
                
                # Is Default?
                is_default = unit.get('is_default_sale', False)
                default_text = "✅ SÍ" if is_default else "-"
                default_item = QTableWidgetItem(default_text)
                if is_default:
                   default_item.setForeground(QColor("green"))
                   default_item.setFont(QFont("Arial", 9, QFont.Weight.Bold))
                self.units_table.setItem(row, 4, default_item)
                
                # Delete button
                delete_btn = QPushButton("🗑")
                delete_btn.setToolTip("Eliminar presentación")
                delete_btn.setFixedSize(30, 30)
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffebee;
                        color: #c62828;
                        border: 1px solid #ffcdd2;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #ffcdd2;
                    }
                """)
                unit_id = unit.get('id')
                delete_btn.clicked.connect(lambda checked, uid=unit_id: self.delete_unit(uid))
                
                container = QDialog() # Dummy widget for layout
                # layout = QHBoxLayout(container)
                # layout.setContentsMargins(0,0,0,0)
                # layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                # layout.addWidget(delete_btn)
                
                self.units_table.setCellWidget(row, 5, delete_btn)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar presentaciones: {str(e)}")
    
    def add_unit(self):
        """Add new unit presentation"""
        name = self.name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Error", "El nombre de la presentación es obligatorio")
            return
        
        if not self.controller or not self.product_id:
            QMessageBox.warning(self, "Error", "Error de control de estado. No se puede guardar.")
            return
        
        try:
            unit_data = {
                'product_id': self.product_id,
                'name': name,
                'conversion_factor': self.factor_input.value(),
                'barcode': self.barcode_input.text().strip() or None,
                'price': self.price_input.value() if self.price_input.value() > 0 else None,
                'is_active': True,
                'is_default_sale': self.is_default_check.isChecked()
            }
            
            self.controller.create_product_unit(unit_data)
            
            # Clear form
            self.name_input.clear()
            self.factor_input.setValue(1.0)
            self.barcode_input.clear()
            self.price_input.setValue(0)
            self.is_default_check.setChecked(False)
            
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
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar: {str(e)}")
