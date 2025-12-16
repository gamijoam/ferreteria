from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDoubleSpinBox, QGroupBox, QCheckBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

class UnitManagementDialog(QDialog):
    """Dialog for managing product presentations/units (Saco, Caja, Pallet, etc.)"""
    
    def __init__(self, parent=None, product_id=None, controller=None, base_unit_name="UNIDAD", base_price=0.0):
        super().__init__(parent)
        self.product_id = product_id
        self.controller = controller
        self.base_unit_name = base_unit_name
        self.base_price = base_price
        
        self.setWindowTitle("Gestionar Presentaciones del Producto")
        self.resize(850, 700)
        
        self.setStyleSheet("""
            QDialog { background-color: #f5f5f5; }
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
        """)
        
        self.setup_ui()
        
        if self.product_id:
            self.load_units()
        else:
            QMessageBox.warning(self, "Advertencia", "Debe guardar el producto primero.")
            self.close()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        self.setLayout(main_layout)
        
        # --- Header ---
        header = QLabel("📦 Configuración de Presentaciones")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #1565C0; padding: 5px;")
        main_layout.addWidget(header)
        
        info = QLabel(f"Defina cómo se vende este producto. La unidad base es: <b>{self.base_unit_name}</b>")
        info.setStyleSheet("color: #666; padding-bottom: 10px;")
        main_layout.addWidget(info)
        
        # --- FORM SECTION ---
        # We split the form into logical groups for better UX
        
        # 1. Identity Group
        identity_group = QGroupBox("1. Identificación")
        identity_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Saco 50kg, Caja x12, Gramo")
        self.name_input.textChanged.connect(self.update_logic_preview)
        identity_layout.addRow("Nombre de Presentación:", self.name_input)
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Código de barras (Opcional)")
        identity_layout.addRow("Código de Barras:", self.barcode_input)
        
        identity_group.setLayout(identity_layout)
        main_layout.addWidget(identity_group)
        
        # 2. Relation Type Group (The Core UX Change)
        relation_group = QGroupBox("2. Tipo de Relación")
        relation_layout = QVBoxLayout()
        
        # Radio Buttons
        self.radio_pack = QRadioButton(f"Es un Empaque / Agrupación (Ej: Saco, Caja)")
        self.radio_pack.setToolTip(f"Contiene varios {self.base_unit_name}")
        self.radio_pack.setChecked(True)
        
        self.radio_fraction = QRadioButton(f"Es una Fracción / Sub-unidad (Ej: Gramo from Kilo)")
        self.radio_fraction.setToolTip(f"Es más pequeño que un {self.base_unit_name}")
        
        self.type_group = QButtonGroup()
        self.type_group.addButton(self.radio_pack)
        self.type_group.addButton(self.radio_fraction)
        self.type_group.buttonClicked.connect(self.update_input_label)
        
        relation_layout.addWidget(self.radio_pack)
        relation_layout.addWidget(self.radio_fraction)
        
        # Value Input Section
        value_container = QHBoxLayout()
        self.dynamic_question_label = QLabel(f"¿Cuántos {self.base_unit_name} contiene este empaque?:")
        self.dynamic_question_label.setStyleSheet("font-weight: bold; color: #333;")
        
        self.relation_value_input = QDoubleSpinBox()
        self.relation_value_input.setRange(0.0001, 999999.99)
        self.relation_value_input.setDecimals(3)
        self.relation_value_input.setValue(1.0)
        self.relation_value_input.setFixedWidth(120)
        self.relation_value_input.valueChanged.connect(self.update_logic_preview)
        
        value_container.addWidget(self.dynamic_question_label)
        value_container.addWidget(self.relation_value_input)
        value_container.addStretch()
        
        relation_layout.addLayout(value_container)
        
        # Logic Preview (Green Box)
        self.preview_label = QLabel("✅ Análisis de Lógica...")
        self.preview_label.setStyleSheet("""
            background-color: #E8F5E9; color: #2E7D32; 
            padding: 10px; border-radius: 4px; font-weight: bold; border: 1px solid #C8E6C9;
        """)
        self.preview_label.setWordWrap(True)
        relation_layout.addWidget(self.preview_label)
        
        # Price Simulation Label (NEW)
        self.price_simulation_label = QLabel("")
        self.price_simulation_label.setStyleSheet("""
            color: #1565C0; font-style: italic; font-weight: bold;
            margin-top: 5px; font-size: 10pt;
        """)
        self.price_simulation_label.setWordWrap(True)
        relation_layout.addWidget(self.price_simulation_label)
        
        relation_group.setLayout(relation_layout)
        main_layout.addWidget(relation_group)
        
        # 3. Attributes Group
        attr_group = QGroupBox("3. Atributos Adicionales")
        attr_layout = QHBoxLayout()
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setPrefix("$ ")
        self.price_input.setRange(0, 999999)
        self.price_input.setDecimals(2)
        
        self.is_default_check = QCheckBox("Predeterminado")
        self.is_default_check.setStyleSheet("color: #2E7D32; font-weight: bold;")
        
        attr_layout.addWidget(QLabel("Precio Fijo (Opcional):"))
        attr_layout.addWidget(self.price_input)
        attr_layout.addSpacing(20)
        attr_layout.addWidget(self.is_default_check)
        attr_layout.addStretch()
        
        attr_group.setLayout(attr_layout)
        main_layout.addWidget(attr_group)
        
        # Add Button
        add_btn = QPushButton("✚ Guardar Presentación")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; color: white; padding: 12px;
                font-size: 11pt; font-weight: bold; border-radius: 6px;
            }
            QPushButton:hover { background-color: #43A047; }
        """)
        add_btn.clicked.connect(self.add_unit)
        main_layout.addWidget(add_btn)
        
        # --- TABLE SECTION ---
        table_group = QGroupBox("📋 Lista de Presentaciones")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(5, 10, 5, 10)
        
        self.units_table = QTableWidget()
        self.units_table.setColumnCount(6)
        self.units_table.setHorizontalHeaderLabels(["Nombre", "Factor", "Código", "Precio", "Default", "Acciones"])
        
        # Visual fixes preserved
        header = self.units_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.units_table.setMinimumHeight(200)
        self.units_table.setStyleSheet("QTableWidget { border: 1px solid #ddd; } QHeaderView::section { font-weight: bold; background-color: #f0f0f0; }")
        
        table_layout.addWidget(self.units_table)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)
        
        # Close Button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        close_layout.addWidget(close_btn)
        main_layout.addLayout(close_layout)
        
        # Initialize labels
        self.update_input_label()
        
    def update_input_label(self):
        """Updates the question and visual cues based on Pack vs Fraction mode."""
        if self.radio_pack.isChecked():
            # Mode: PACK
            self.dynamic_question_label.setText(f"¿Cuántos {self.base_unit_name} contiene este empaque?:")
            self.relation_value_input.setSuffix(f" {self.base_unit_name}")
            self.relation_value_input.setDecimals(2)
        else:
            # Mode: FRACTION
            self.dynamic_question_label.setText(f"¿Cuántas de estas unidades hacen 1 {self.base_unit_name}(s)?:")
            self.relation_value_input.setSuffix("")
            self.relation_value_input.setDecimals(0) # Usually integers like 1000g = 1kg
            
        self.update_logic_preview()

    def update_logic_preview(self):
        """Calculates factor in real-time and shows green confirmation."""
        name = self.name_input.text().strip() or "Nueva Unidad"
        user_val = self.relation_value_input.value()
        
        if user_val <= 0:
            self.preview_label.setText("⚠️ El valor debe ser mayor a 0")
            self.preview_label.setStyleSheet("background-color: #ffebee; color: #c62828; padding: 10px; border-radius: 4px;")
            self.price_simulation_label.setText("")
            return

        factor = 1.0
        msg = ""

        if self.radio_pack.isChecked():
            # Factor = Value (e.g. 1 Sack = 50 Kg)
            factor = user_val
            msg = f"✅ Entendido: 1 {name} contiene {factor:g} {self.base_unit_name}."
        else:
            # Factor = 1 / Value (e.g. 1000g = 1Kg -> 1g = 0.001 Kg)
            factor = 1 / user_val
            msg = f"✅ Correcto: 1 {self.base_unit_name} contiene {user_val:g} de estas unidades ({name}).\n(Factor interno: {factor:.6f})"
            
        self.preview_label.setText(msg)
        self.preview_label.setStyleSheet("background-color: #E8F5E9; color: #2E7D32; padding: 10px; border-radius: 4px; border: 1px solid #C8E6C9; font-weight: bold;")

        # Price Simulation
        if self.base_price > 0:
            simulated_price = self.base_price * factor
            self.price_simulation_label.setText(
                f"💰 Ejemplo: Si el {self.base_unit_name} cuesta ${self.base_price:,.2f}, "
                f"esta unidad ({name}) costaría automáticante ${simulated_price:,.2f}"
            )
        else:
            self.price_simulation_label.setText("💡 Ingrese un precio en el producto principal para ver la simulación de costos.")

    def add_unit(self):
        """Add unit with computed conversion factor"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
            
        user_val = self.relation_value_input.value()
        if user_val <= 0:
            QMessageBox.warning(self, "Error", "El valor debe ser positivo")
            return
            
        # Compute Factor
        if self.radio_pack.isChecked():
            factor = user_val
        else:
            factor = 1.0 / user_val
            
        try:
            unit_data = {
                'product_id': self.product_id,
                'name': name,
                'conversion_factor': factor,
                'barcode': self.barcode_input.text().strip() or None,
                'price': self.price_input.value() if self.price_input.value() > 0 else None,
                'is_active': True,
                'is_default_sale': self.is_default_check.isChecked()
            }
            
            self.controller.create_product_unit(unit_data)
            
            # Reset Form
            self.name_input.clear()
            self.barcode_input.clear()
            self.price_input.setValue(0)
            self.is_default_check.setChecked(False)
            self.relation_value_input.setValue(1.0)
            self.radio_pack.setChecked(True)
            self.update_input_label()
            
            self.load_units()
            QMessageBox.information(self, "Éxito", "Presentación agregada")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def load_units(self):
        # ... (Preserve existing logic for basic loading but update table columns if needed)
        # Using previous implementation logic
        if not self.controller or not self.product_id: return
        try:
            units = self.controller.get_product_units(self.product_id)
            self.units_table.setRowCount(0)
            for unit in units:
                row = self.units_table.rowCount()
                self.units_table.insertRow(row)
                
                self.units_table.setItem(row, 0, QTableWidgetItem(unit.get('name','')))
                self.units_table.setItem(row, 1, QTableWidgetItem(f"{unit.get('conversion_factor',1):.4f}"))
                self.units_table.setItem(row, 2, QTableWidgetItem(unit.get('barcode','') or '-'))
                
                p = unit.get('price', 0) or 0
                self.units_table.setItem(row, 3, QTableWidgetItem(f"${p:,.2f}" if p>0 else "Auto"))
                
                is_def = unit.get('is_default_sale', False)
                def_item = QTableWidgetItem("✅ SÍ" if is_def else "-")
                if is_def: def_item.setForeground(QColor("green"))
                self.units_table.setItem(row, 4, def_item)
                
                # Delete Btn
                del_btn = QPushButton("🗑")
                del_btn.setStyleSheet("background-color: #ffebee; color: #c62828; border-radius: 4px;")
                del_btn.setFixedSize(30, 30)
                del_btn.clicked.connect(lambda ch, uid=unit.get('id'): self.delete_unit(uid))
                self.units_table.setCellWidget(row, 5, del_btn)
        except Exception as e:
            print(e)

    def delete_unit(self, unit_id):
        # (Preserve existing logic)
        reply = QMessageBox.question(self, "Confirmar", "¿Eliminar presentación?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.controller.delete_product_unit(unit_id)
                self.load_units()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
