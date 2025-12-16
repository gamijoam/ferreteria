from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDoubleSpinBox, QGroupBox, QCheckBox, QRadioButton, QButtonGroup, QFrame,
    QWidget, QSplitter, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon

class UnitManagementDialog(QDialog):
    """
    CRUD Dialog for Product Units with Split View (List | Form).
    """
    
    def __init__(self, parent=None, product_id=None, controller=None, base_unit_name="UNIDAD", base_price=0.0):
        super().__init__(parent)
        self.product_id = product_id
        self.controller = controller
        self.base_unit_name = base_unit_name
        self.base_price = base_price
        self.current_unit_id = None # Check this to determine Create vs Update
        self.loaded_units = []

        self.setWindowTitle("Administrador de Presentaciones (CRUD)")
        self.resize(1000, 600)
        self.setModal(True)
        
        self.setStyleSheet("""
            QDialog { background-color: #f5f5f5; }
            QGroupBox { font-weight: bold; border: 1px solid #ccc; border-radius: 6px; margin-top: 10px; background-color: white; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #1976D2; }
            QTableWidget { border: 1px solid #ddd; background-color: white; }
            QHeaderView::section { font-weight: bold; background-color: #f0f0f0; border: 1px solid #ddd; }
        """)
        
        self.setup_ui()
        
        if self.product_id:
            self.load_units()
        else:
            QMessageBox.critical(self, "Error", "Producto no definido. Guarde el producto primero.")
            self.close()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Header
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        title = QLabel(f"Gestión de Presentaciones: {self.base_unit_name}")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #1565C0;")
        header_layout.addWidget(title)
        
        # Price Info
        if self.base_price > 0:
            price_info = QLabel(f"Precio Base: ${self.base_price:,.2f}")
            price_info.setStyleSheet("background: #E3F2FD; color: #1565C0; padding: 4px 8px; border-radius: 4px; font-weight: bold;")
            header_layout.addWidget(price_info)
            
        main_layout.addWidget(header_container)
        
        # Splitter (Left: List, Right: Form)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        
        # --- LEFT PANEL (LIST) ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0,0,5,0)
        
        self.units_table = QTableWidget()
        self.units_table.setColumnCount(3)
        self.units_table.setHorizontalHeaderLabels(["Nombre", "Factor", "Código"])
        self.units_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.units_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.units_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.units_table.cellClicked.connect(self.on_table_click)
        left_layout.addWidget(self.units_table)
        
        btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("✚ Nuevo / Limpiar")
        self.btn_new.clicked.connect(self.reset_form)
        self.btn_new.setStyleSheet("background-color: #2196F3; color: white; padding: 6px; font-weight: bold;")
        
        self.btn_delete = QPushButton("🗑 Eliminar")
        self.btn_delete.clicked.connect(self.delete_current)
        self.btn_delete.setStyleSheet("background-color: #ef5350; color: white; padding: 6px; font-weight: bold;")
        
        btn_layout.addWidget(self.btn_new)
        btn_layout.addWidget(self.btn_delete)
        left_layout.addLayout(btn_layout)
        
        splitter.addWidget(left_widget)
        
        # --- RIGHT PANEL (FORM WITH SCROLL) ---
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        right_scroll_content = QWidget()
        right_layout = QVBoxLayout(right_scroll_content)
        right_layout.setContentsMargins(5,0,0,0)
        
        form_group = QGroupBox("Detalles de la Presentación")
        form_layout = QVBoxLayout()
        
        # Edit/Create Indicator
        self.mode_label = QLabel("MODO: CREAR")
        self.mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mode_label.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; border-radius: 4px; padding: 4px;")
        form_layout.addWidget(self.mode_label)

        # 1. Basic Data
        input_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Caja, Saco, Gramo")
        self.barcode_input = QLineEdit()
        
        input_layout.addRow("Nombre:", self.name_input)
        input_layout.addRow("Código Barras:", self.barcode_input)
        form_layout.addLayout(input_layout)
        
        # 2. Logic Type (Radio)
        type_group = QGroupBox("Tipo de Relación")
        type_layout = QVBoxLayout()
        
        self.radio_pack = QRadioButton("Empaque / Mayor (Ej: 1 Caja = 12 Unidades)")
        self.radio_fraction = QRadioButton("Fracción / Menor (Ej: 1000 Gramos = 1 Kilo)")
        self.radio_pack.setChecked(True)
        
        self.btn_group_type = QButtonGroup()
        self.btn_group_type.addButton(self.radio_pack)
        self.btn_group_type.addButton(self.radio_fraction)
        self.btn_group_type.buttonClicked.connect(self.update_logic_ui)
        
        type_layout.addWidget(self.radio_pack)
        type_layout.addWidget(self.radio_fraction)
        form_group.setLayout(form_layout) 
        
        # 3. Factor Input
        self.lbl_question = QLabel("¿Cuántas Unidades Base trae?")
        self.lbl_question.setStyleSheet("font-weight: bold; margin-top: 10px;")
        type_layout.addWidget(self.lbl_question)
        
        input_h = QHBoxLayout()
        self.spin_factor_input = QDoubleSpinBox()
        self.spin_factor_input.setRange(0.0001, 999999)
        self.spin_factor_input.setDecimals(3)
        self.spin_factor_input.setValue(1)
        self.spin_factor_input.valueChanged.connect(self.calculate_preview)
        
        input_h.addWidget(self.spin_factor_input)
        type_layout.addLayout(input_h)
        
        # Preview Box
        self.lbl_preview = QLabel()
        self.lbl_preview.setWordWrap(True)
        self.lbl_preview.setStyleSheet("background: #f1f8e9; color: #33691e; padding: 8px; border: 1px solid #AED581; border-radius: 4px;")
        type_layout.addWidget(self.lbl_preview)

        # Price Sim
        self.lbl_price_sim = QLabel()
        self.lbl_price_sim.setWordWrap(True)
        self.lbl_price_sim.setStyleSheet("color: #0277BD; font-weight: bold; font-style: italic;")
        type_layout.addWidget(self.lbl_price_sim)
        
        type_group.setLayout(type_layout)
        form_layout.addWidget(type_group)
        
        # 4. Optional Price
        price_group = QGroupBox("Estrategia de Precio")
        price_layout = QVBoxLayout()
        
        # Override Checkbox
        self.check_override_price = QCheckBox("Permitir precio manual (Sobrescribir matemática)")
        self.check_override_price.toggled.connect(self.toggle_price_override)
        price_layout.addWidget(self.check_override_price)
        
        # Price Input Row
        price_row = QHBoxLayout()
        self.spin_price = QDoubleSpinBox()
        self.spin_price.setPrefix("$ ")
        self.spin_price.setRange(0, 999999)
        self.spin_price.setValue(0)
        self.spin_price.setEnabled(False) # Locked by default for safety
        
        price_row.addWidget(QLabel("Precio de Venta:"))
        price_row.addWidget(self.spin_price)
        price_layout.addLayout(price_row)
        
        self.check_default = QCheckBox("Es venta predeterminada")
        price_layout.addWidget(self.check_default)
        
        price_group.setLayout(price_layout)
        form_layout.addWidget(price_group)
        
        form_layout.addStretch()
        
        # Save Button
        self.btn_save = QPushButton("💾 Guardar Cambios")
        self.btn_save.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold; font-size: 11pt;")
        self.btn_save.clicked.connect(self.save_unit)
        form_layout.addWidget(self.btn_save)
        
        form_group.setLayout(form_layout)
        
        # Add form group to Scroll Content Layout
        right_layout.addWidget(form_group)
        
        # Finalize Scroll Area
        right_scroll.setWidget(right_scroll_content)
        splitter.addWidget(right_scroll)
        
        # Set splitter sizes (35% List, 65% Form)
        splitter.setSizes([350, 650])
        splitter.setCollapsible(0, False)
        
        main_layout.addWidget(splitter)
        
        self.update_logic_ui()

    def toggle_price_override(self, checked):
        """Enable/Disable manual price input"""
        self.spin_price.setEnabled(checked)
        if not checked:
            # Revert to mathematical price
            self.calculate_preview()

    def update_logic_ui(self):
        """Update labels based on radio selection"""
        if self.radio_pack.isChecked():
            # CASE A: Pack
            self.lbl_question.setText(f"¿Cuántos {self.base_unit_name} trae este empaque?")
            self.spin_factor_input.setSuffix(f" {self.base_unit_name}")
        else:
            # CASE B: Fraction
            self.lbl_question.setText(f"¿Cuántas de estas unidades hacen 1 {self.base_unit_name}?")
            self.spin_factor_input.setSuffix(" Unidades")
            
        self.calculate_preview()

    def calculate_preview(self):
        val = self.spin_factor_input.value()
        if val <= 0: return
        
        name = self.name_input.text() or "Nueva Unidad"
        factor = 1.0
        
        if self.radio_pack.isChecked():
            # Factor = val
            factor = val
            self.lbl_preview.setText(f"✅ 1 {name} = {val} {self.base_unit_name}")
        else:
            # Factor = 1 / val
            factor = 1.0 / val
            self.lbl_preview.setText(f"✅ Factor Interno: {factor:.6f}\n(Se necesitan {val} {name} para hacer 1 {self.base_unit_name})")
            
        # Price Calculation Safety Logic
        if self.base_price > 0:
            suggested_price = self.base_price * factor
            self.lbl_price_sim.setText(f"💰 Precio Calculado (Matemático): ${suggested_price:,.2f}")
            
            # Auto-update spinner if not overridden
            if not self.check_override_price.isChecked():
                self.spin_price.setValue(suggested_price)
        else:
            self.lbl_price_sim.setText("")

    def load_units(self):
        try:
            self.units_table.setRowCount(0)
            self.loaded_units = self.controller.get_product_units(self.product_id)
            for row, unit in enumerate(self.loaded_units):
                self.units_table.insertRow(row)
                self.units_table.setItem(row, 0, QTableWidgetItem(unit.get('name', '')))
                self.units_table.setItem(row, 1, QTableWidgetItem(f"{unit.get('conversion_factor', 1):.4f}"))
                self.units_table.setItem(row, 2, QTableWidgetItem(unit.get('barcode') or '-'))
        except Exception as e:
            print(e)

    def on_table_click(self, row, col):
        if row < 0 or row >= len(self.loaded_units): return
        
        unit = self.loaded_units[row]
        self.current_unit_id = unit.get('id')
        self.mode_label.setText("MODO: EDITAR")
        self.mode_label.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; border-radius: 4px; padding: 4px;")
        
        self.name_input.setText(unit.get('name'))
        self.barcode_input.setText(unit.get('barcode') or "")
        
        factor = unit.get('conversion_factor', 1.0)
        
        # Reverse Logic to determine Radio State
        if factor >= 1:
            self.radio_pack.setChecked(True)
            self.spin_factor_input.setValue(factor)
        else:
            self.radio_fraction.setChecked(True)
            # If factor = 0.001 (1/1000), input should satisfy 1/input = factor => input = 1/factor
            self.spin_factor_input.setValue(1.0 / factor)
            
        stored_price = unit.get('price') or 0.0
        
        # Check if price is custom (Manual Override)
        math_price = self.base_price * factor
        is_custom = abs(math_price - stored_price) > 0.01
        
        self.check_override_price.setChecked(is_custom)
        self.spin_price.setEnabled(is_custom)
        self.spin_price.setValue(stored_price)
        
        self.check_default.setChecked(unit.get('is_default_sale', False))
        
        self.update_logic_ui()

    def reset_form(self):
        self.current_unit_id = None
        self.mode_label.setText("MODO: CREAR")
        self.mode_label.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; border-radius: 4px; padding: 4px;")
        
        self.name_input.clear()
        self.barcode_input.clear()
        self.radio_pack.setChecked(True)
        self.spin_factor_input.setValue(1)
        self.spin_price.setValue(0)
        self.check_default.setChecked(False)
        self.update_logic_ui()
        self.units_table.clearSelection()

    def delete_current(self):
        row = self.units_table.currentRow()
        if row < 0: return
        
        unit = self.loaded_units[row]
        reply = QMessageBox.question(self, "Confirmar", f"¿Eliminar {unit.get('name')}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.controller.delete_product_unit(unit.get('id'))
                self.load_units()
                self.reset_form()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def save_unit(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
            
        val = self.spin_factor_input.value()
        if self.radio_pack.isChecked():
            final_factor = val
        else:
            final_factor = 1.0 / val
            
        data = {
            "product_id": self.product_id,
            "name": name,
            "conversion_factor": final_factor,
            "barcode": self.barcode_input.text().strip() or None,
            "price": self.spin_price.value() if self.spin_price.value() > 0 else None,
            "is_default_sale": self.check_default.isChecked(),
            "is_active": True
        }
        
        try:
            if self.current_unit_id:
                # Update
                self.controller.update_product_unit(self.current_unit_id, data)
                QMessageBox.information(self, "Éxito", "Presentación actualizada")
            else:
                # Create
                self.controller.create_product_unit(data)
                QMessageBox.information(self, "Éxito", "Presentación creada")
            
            self.load_units()
            self.reset_form()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
