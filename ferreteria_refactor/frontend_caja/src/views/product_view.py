import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QFormLayout, QGroupBox, QDialog, QDoubleSpinBox, QGridLayout,
    QScrollArea  # Added for scrollable dialogs
)
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt, QLocale
# from src.database.db import SessionLocal
from src.controllers.product_controller import ProductController
from src.utils.event_bus import event_bus

class ProductFormDialog(QDialog):
    """Dialog for creating/editing products with multi-currency and multi-unit support"""
    def __init__(self, parent=None, product=None, controller=None):
        super().__init__(parent)
        self.product = product
        self.controller = controller
        self.product_id = product.id if product else None
        
        self.setWindowTitle("Editar Producto" if product else "Nuevo Producto")
        self.resize(700, 600)  # Larger for new sections
        self.setMinimumHeight(500)
        
        self.setup_ui()
        
        if product:
            self.populate_form(product)
    
    def setup_ui(self):
        # Imports needed locally if not at top, but better to rely on class imports if updated. 
        # I will update imports in the file replacement if possible, but here I can just use QtWidgets.
        from PyQt6.QtWidgets import QTabWidget
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Get base currency
        self.base_currency, self.currency_symbol = self.get_base_currency()
        
        # TAB WIDGET
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #CCC; background-color: white; border-radius: 4px; }
            QTabBar::tab { background-color: #f0f0f0; padding: 10px 15px; border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px; }
            QTabBar::tab:selected { background-color: white; font-weight: bold; color: #1565C0; border-bottom: 2px solid #1565C0; }
            QLineEdit, QComboBox, QDoubleSpinBox { padding: 6px; font-size: 10pt; border: 1px solid #ccc; border-radius: 4px; }
            QLabel { font-size: 10pt; color: #333; }
        """)
        
        # --- TAB 1: INFORMACIÓN BÁSICA ---
        tab_basic = QWidget()
        form_basic = QFormLayout()
        form_basic.setSpacing(15)
        form_basic.setContentsMargins(20, 20, 20, 20)
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Cemento Gris Tipo 1")
        self.name_input.setStyleSheet("font-size: 11pt; font-weight: bold;")
        self.name_input.setMinimumHeight(40)
        form_basic.addRow("📝 Nombre del Producto:", self.name_input)
        
        # SKU
        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText("Código de barras o referencia")
        form_basic.addRow("🔢 SKU / Código:", self.sku_input)
        
        # Category
        self.category_combo = QComboBox()
        self.load_categories()
        form_basic.addRow("📂 Categoría:", self.category_combo)
        
        # Unit Type (Legacy)
        self.unit_type_combo = QComboBox()
        self.unit_type_combo.addItems(["Unidad", "Metro", "Kilo", "Litro", "Servicio"])
        form_basic.addRow("🏷️ Tipo (Legacy):", self.unit_type_combo)
        
        tab_basic.setLayout(form_basic)
        self.tabs.addTab(tab_basic, "📝 Información Básica")
        
        # --- TAB 2: PRECIOS Y COSTOS ---
        tab_prices = QWidget()
        layout_prices = QVBoxLayout()
        layout_prices.setSpacing(20)
        layout_prices.setContentsMargins(20, 20, 20, 20)
        
        # Grid for Cost/Price
        price_grid = QGridLayout()
        price_grid.setHorizontalSpacing(30)
        
        # Cost
        self.cost_input = QLineEdit()
        self.cost_input.setPlaceholderText("0.00")
        self.cost_input.textChanged.connect(self.calculate_margin)
        price_grid.addWidget(QLabel("📉 Costo de Compra:"), 0, 0)
        price_grid.addWidget(self.cost_input, 1, 0)
        
        # Price
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("0.00")
        self.price_input.textChanged.connect(self.calculate_margin)
        self.price_input.textChanged.connect(self.update_converted_price)
        price_grid.addWidget(QLabel("📈 Precio de Venta:"), 0, 1)
        price_grid.addWidget(self.price_input, 1, 1)
        
        layout_prices.addLayout(price_grid)
        
        # Margin Bar/Label
        self.margin_label = QLabel("Margen Calculado: -")
        self.margin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.margin_label.setStyleSheet("font-size: 12pt; font-weight: bold; background-color: #f9f9f9; padding: 10px; border-radius: 6px; border: 1px dashed #ccc;")
        layout_prices.addWidget(self.margin_label)
        
        # Tax (IVA) - Mock
        self.tax_combo = QComboBox()
        self.tax_combo.addItems(["Exento (0%)", "IVA General (16%)", "IVA Reducido (8%)"])
        form_tax = QFormLayout()
        form_tax.addRow("🏛️ Impuesto Aplicable:", self.tax_combo)
        layout_prices.addLayout(form_tax)
        
        # Reference Rates
        group_rates = QGroupBox("Conversión de Moneda Reference")
        layout_rates = QFormLayout()
        self.reference_rate_combo = QComboBox()
        self.load_exchange_rates()
        self.reference_rate_combo.currentIndexChanged.connect(self.update_converted_price)
        
        self.converted_price_label = QLabel("≈ 0.00")
        self.converted_price_label.setStyleSheet("color: #1976D2; font-weight: bold;")
        
        layout_rates.addRow("Tasa Referencia:", self.reference_rate_combo)
        layout_rates.addRow("Precio Convertido:", self.converted_price_label)
        group_rates.setLayout(layout_rates)
        
        layout_prices.addWidget(group_rates)
        layout_prices.addStretch() # Push Up
        
        tab_prices.setLayout(layout_prices)
        self.tabs.addTab(tab_prices, "💰 Precios y Costos")
        
        # --- TAB 3: INVENTARIO Y UNIDADES ---
        tab_inv = QWidget()
        layout_inv = QVBoxLayout()
        layout_inv.setContentsMargins(20, 20, 20, 20)
        
        # Base Unit
        form_inv = QFormLayout()
        self.base_unit_combo = QComboBox()
        self.base_unit_combo.addItems(["UNIDAD", "KG", "METRO", "LITRO", "GRAMO"])
        self.base_unit_combo.currentTextChanged.connect(self.update_stock_label)
        form_inv.addRow("📏 Unidad Base:", self.base_unit_combo)
        
        # Stock with Calculator
        stock_container = QHBoxLayout()
        self.stock_input = QDoubleSpinBox()
        self.stock_input.setRange(0, 1000000)
        self.stock_input.setDecimals(2)
        
        btn_calc = QPushButton("🖩")
        btn_calc.setFixedSize(40, 30)
        btn_calc.clicked.connect(self.open_stock_calculator)
        
        stock_container.addWidget(self.stock_input)
        stock_container.addWidget(btn_calc)
        
        self.stock_label = QLabel("Stock Actual:") # Kept reference for update_stock_label
        form_inv.addRow(self.stock_label, stock_container)
        
        # Min Stock
        self.min_stock_input = QDoubleSpinBox()
        self.min_stock_input.setRange(0, 100000)
        self.min_stock_input.setValue(5)
        form_inv.addRow("⚠️ Stock Mínimo:", self.min_stock_input)
        
        # Location
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Pasillo A, Estante 2...")
        form_inv.addRow("📍 Ubicación:", self.location_input)
        
        layout_inv.addLayout(form_inv)
        
        # Manage Allocations/Units Button
        self.manage_units_btn = QPushButton("📦 Gestionar Presentaciones Extras")
        self.manage_units_btn.setMinimumHeight(45)
        self.manage_units_btn.setStyleSheet("""
            QPushButton { background-color: #FF9800; color: white; font-weight: bold; font-size: 11pt; border-radius: 6px; }
            QPushButton:hover { background-color: #F57C00; }
        """)
        self.manage_units_btn.clicked.connect(self.open_unit_management)
        layout_inv.addWidget(self.manage_units_btn)
        
        # Legacy Box Fields (Hidden/Small)
        legacy_group = QGroupBox("Opciones Avanzadas / Legacy")
        legacy_group.setCheckable(True)
        legacy_group.setChecked(False)
        legacy_layout = QFormLayout()
        
        self.is_box_check = QCheckBox("Es Caja/Pack (Legacy Mode)")
        self.is_box_check.toggled.connect(self.toggle_box_fields)
        self.conversion_factor_input = QLineEdit("1")
        self.conversion_factor_input.setEnabled(False)
        
        legacy_layout.addRow(self.is_box_check)
        legacy_layout.addRow("Factor Legacy:", self.conversion_factor_input)
        legacy_group.setLayout(legacy_layout)
        
        layout_inv.addWidget(legacy_group)
        layout_inv.addStretch()
        
        tab_inv.setLayout(layout_inv)
        self.tabs.addTab(tab_inv, "🏗️ Inventario y Unidades")
        
        main_layout.addWidget(self.tabs)
        
        # Buttons Footer
        footer = QHBoxLayout()
        footer.addStretch()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setFixedSize(120, 40)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Guardar Producto")
        save_btn.setFixedSize(160, 40)
        save_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; border-radius: 4px;")
        save_btn.clicked.connect(self.accept)
        
        footer.addWidget(cancel_btn)
        footer.addWidget(save_btn)
        main_layout.addLayout(footer)
    
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
        self.location_input.setText(product.location or "")
        
        # Populate Category
        if hasattr(product, 'category_id') and product.category_id:
            index = self.category_combo.findData(product.category_id)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

        # Populate Default Rate
        if hasattr(product, 'default_rate_id') and product.default_rate_id:
            # Iterate to find item with matching dictionary data 'id'
            for i in range(self.reference_rate_combo.count()):
                data = self.reference_rate_combo.itemData(i)
                if data and data.get('id') == product.default_rate_id:
                    self.reference_rate_combo.setCurrentIndex(i)
                    break
        
        # Populate Base Unit (Fix)
        if hasattr(product, 'base_unit') and product.base_unit:
            self.base_unit_combo.setCurrentText(product.base_unit)
        
        self.calculate_margin()
    
    def get_base_currency(self):
        """Get base currency from configuration"""
        try:
            from src.controllers.config_controller import ConfigController
            controller = ConfigController()
            base_currency = controller.get_config("BASE_CURRENCY", "USD")
            
            # Map currency codes to symbols
            currency_symbols = {
                "USD": "$",
                "VES": "Bs",
                "EUR": "€",
                "MXN": "$"
            }
            
            return base_currency, currency_symbols.get(base_currency, "$")
        except:
            return "USD", "$"
    
    def load_exchange_rates(self):
        """Load active exchange rates into combo"""
        try:
            from src.controllers.config_controller import ConfigController
            controller = ConfigController()
            rates = controller.get_exchange_rates()
            
            self.reference_rate_combo.clear()
            self.reference_rate_combo.addItem("-- Seleccione tasa --", None)
            
            for rate in rates:
                if rate.get('is_active', True):
                    display_text = f"{rate['name']} ({rate['currency_code']}: {rate['rate']:.2f})"
                    self.reference_rate_combo.addItem(display_text, rate)
        except Exception as e:
            # Fallback if API fails
            self.reference_rate_combo.addItem("-- Sin tasas disponibles --", None)
    
    def update_converted_price(self):
        """Calculate and display converted price in real-time"""
        try:
            price_text = self.price_input.text().strip()
            if not price_text:
                self.converted_price_label.setText("")
                return
            
            price = float(price_text)
            rate_data = self.reference_rate_combo.currentData()
            
            if rate_data and price > 0:
                rate_value = rate_data['rate']
                currency_code = rate_data['currency_code']
                rate_name = rate_data['name']
                
                converted = price * rate_value
                
                # Get symbol for target currency
                currency_symbols = {"USD": "$", "VES": "Bs", "EUR": "€", "MXN": "$"}
                symbol = currency_symbols.get(currency_code, currency_code)
                
                self.converted_price_label.setText(
                    f"≈ {symbol} {converted:,.2f}\n(Calculado con {rate_name})"
                )
            else:
                self.converted_price_label.setText("")
        except ValueError:
            self.converted_price_label.setText("")
    
    def load_categories(self):
        """Load product categories from backend"""
        try:
            if self.controller:
                categories = self.controller.get_categories()
                
                self.category_combo.clear()
                self.category_combo.addItem("-- Sin categoría --", None)
                
                for category in categories:
                    self.category_combo.addItem(category['name'], category['id'])
            else:
                # Fallback if no controller
                self.category_combo.addItem("General", None)
        except Exception as e:
            # Fallback categories
            self.category_combo.addItem("General", None)
            self.category_combo.addItem("Construcción", None)
            self.category_combo.addItem("Herramientas", None)
    
    def open_unit_management(self):
        """Open unit management dialog"""
        if not self.product_id:
            QMessageBox.warning(
                self,
                "Advertencia",
                "Debe guardar el producto primero antes de gestionar presentaciones.\n\n"
                "Haga clic en 'Guardar Producto' y luego podrá agregar presentaciones."
            )
            return
        
        try:
            from src.views.unit_management_dialog import UnitManagementDialog
            
            base_unit = self.base_unit_combo.currentText()
            try:
                current_price = float(self.price_input.text() or 0)
            except:
                current_price = 0.0

            dialog = UnitManagementDialog(
                parent=self,
                product_id=self.product_id,
                controller=self.controller,
                base_unit_name=base_unit,
                base_price=current_price
            )
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al abrir gestor de presentaciones: {str(e)}"
            )
    
    def get_data(self):
        """Get form data as dict"""
        # Get selected rate ID
        rate_data = self.reference_rate_combo.currentData()
        default_rate_id = rate_data.get('id') if rate_data else None
        
        return {
            "name": self.name_input.text().strip(),
            "sku": self.sku_input.text().strip() or None,
            "price": float(self.price_input.text() or 0),
            "cost_price": float(self.cost_input.text() or 0),
            "stock": self.stock_input.value(),
            "min_stock": self.min_stock_input.value(),
            "location": self.location_input.text().strip() or None,
            
            # Multi-Currency
            "default_rate_id": default_rate_id,
            
            # Multi-Unit (New System)
            "category_id": self.category_combo.currentData(),
            "base_unit": self.base_unit_combo.currentText(),
            
            # Legacy fields (backward compatibility)
            "is_box": self.is_box_check.isChecked(),
            "conversion_factor": int(self.conversion_factor_input.text() or 1),
            "unit_type": self.unit_type_combo.currentText(),
        }

    def update_stock_label(self, text):
        """Update stock label based on selected unit"""
        if text:
            self.stock_label.setText(f"Stock Total en {text}:")
            self.stock_label.setStyleSheet("color: #1976D2; font-weight: bold;")
        else:
            self.stock_label.setText("Stock Actual:")

    def open_stock_calculator(self):
        """Open conversational stock assistant"""
        base_unit = self.base_unit_combo.currentText()
        dialog = StockCalculatorDialog(self, self.controller, self.product_id, base_unit)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            total = dialog.get_total()
            current_val = self.stock_input.value()
            # Ask if add or replace? Usually calculators replace or add. 
            # "Se agregarán..." implies adding to logic, but here we set the input value.
            # The user prompt says "Confirmar y Actualizar Stock" -> likely updating the field.
            # I will set the value. If they want to add to existing, they can do math. 
            # But "Se agregarán X al inventario" implies X is the increment?
            # If the user counts 10 sacks, that's their stock. They usually want to set Total Stock = 10 sacks.
            # So I will set the text field to the calculated total.
            self.stock_input.setValue(total)


class StockCalculatorDialog(QDialog):
    def __init__(self, parent=None, controller=None, product_id=None, base_unit="UNIDAD"):
        super().__init__(parent)
        self.controller = controller
        self.product_id = product_id
        self.base_unit = base_unit
        self.factor = 1.0
        
        self.setWindowTitle("Asistente de Ingreso de Stock")
        self.resize(450, 400)
        self.setStyleSheet("""
            QDialog { background-color: white; }
            QLabel { color: #333; font-family: 'Segoe UI', Arial; }
            QComboBox { 
                padding: 10px; font-size: 12pt; border: 2px solid #ddd; border-radius: 6px; 
                background-color: #f9f9f9;
            }
            QDoubleSpinBox { 
                padding: 10px; font-size: 16pt; font-weight: bold; 
                border: 2px solid #1976D2; border-radius: 6px; 
            }
            QPushButton {
                background-color: #1976D2; color: white; border-radius: 6px;
                padding: 12px; font-size: 11pt; font-weight: bold;
            }
            QPushButton:hover { background-color: #1565C0; }
        """)
        
        self.setup_ui()
        self.load_units()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        self.setLayout(layout)
        
        # Header
        title = QLabel("📦 Asistente de Conteo")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #1976D2;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Step 1
        lbl_q1 = QLabel("1. ¿Qué estás contando?")
        lbl_q1.setStyleSheet("font-size: 12pt; font-weight: bold;")
        layout.addWidget(lbl_q1)
        
        self.unit_combo = QComboBox()
        self.unit_combo.currentIndexChanged.connect(self.calculate)
        layout.addWidget(self.unit_combo)
        
        # Step 2
        lbl_q2 = QLabel("2. ¿Cuántos tienes físicamente?")
        lbl_q2.setStyleSheet("font-size: 12pt; font-weight: bold;")
        layout.addWidget(lbl_q2)
        
        self.qty_input = QDoubleSpinBox()
        self.qty_input.setRange(0, 999999)
        self.qty_input.setDecimals(2)
        self.qty_input.setValue(1)
        self.qty_input.valueChanged.connect(self.calculate)
        layout.addWidget(self.qty_input)
        
        # Result Visual
        self.result_container = QGroupBox()
        self.result_container.setStyleSheet("background-color: #E3F2FD; border: none; border-radius: 8px;")
        res_layout = QVBoxLayout()
        
        self.math_label = QLabel("0 Unidades x 1 = 0 Total")
        self.math_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.math_label.setStyleSheet("font-size: 11pt; color: #555;")
        
        self.total_label = QLabel("Total: 0.00")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2E7D32;")
        
        self.summary_label = QLabel(f"Se establecerá este inventario en {self.base_unit}")
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.summary_label.setStyleSheet("color: #1976D2; font-style: italic;")
        
        res_layout.addWidget(self.math_label)
        res_layout.addWidget(self.total_label)
        res_layout.addWidget(self.summary_label)
        self.result_container.setLayout(res_layout)
        
        layout.addWidget(self.result_container)
        layout.addStretch()
        
        # Button
        self.btn_confirm = QPushButton("Confirmar y Actualizar Stock")
        self.btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirm.clicked.connect(self.accept)
        layout.addWidget(self.btn_confirm)

    def load_units(self):
        """Load presentations + base unit"""
        self.unit_combo.clear()
        
        # Base Unit
        self.unit_combo.addItem(f"🔹 {self.base_unit} (Sueltos)", 1.0)
        
        # Load from DB if product exists
        if self.controller and self.product_id:
            try:
                units = self.controller.get_product_units(self.product_id)
                for unit in units:
                    name = unit.get('name', 'Unidad')
                    factor = unit.get('conversion_factor', 1.0)
                    self.unit_combo.addItem(f"📦 {name} (x{factor:g} {self.base_unit})", factor)
            except Exception as e:
                print(f"Error loading units for calc: {e}")
        
        # Trigger calc
        self.calculate()

    def calculate(self):
        try:
            qty = self.qty_input.value()
            factor = self.unit_combo.currentData() or 1.0
            unit_name = self.unit_combo.currentText()
            
            total = qty * factor
            
            self.math_label.setText(f"{qty:g} {unit_name.split('(')[0].strip()} × {factor:g}")
            self.total_label.setText(f"{total:,.2f} {self.base_unit}")
            self.summary_label.setText(f"Se ingresarán {total:,.2f} {self.base_unit} al sistema")
            
        except Exception:
            pass

    def get_total(self):
        qty = self.qty_input.value()
        factor = self.unit_combo.currentData() or 1.0
        return qty * factor


class ProductWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Productos")
        # self.resize(1200, 750)
        self.showMaximized()
        
        self.db = None # SessionLocal()
        self.controller = ProductController(self.db)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.setup_ui()
        
        # Pagination state
        self.current_page = 1
        self.page_size = 50
        self.total_pages = 1
        
        self.load_products()
        
        # Debounce timer
        from PyQt6.QtCore import QTimer
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(500) # 500ms delay
        self.update_timer.timeout.connect(self.load_products)
        
        # Connect signals
        event_bus.products_updated.connect(self.schedule_refresh)
        event_bus.inventory_updated.connect(self.schedule_refresh)

    def schedule_refresh(self):
        self.update_timer.start()

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
        self.table.setColumnCount(13)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "SKU", "Ubicación", "Costo", "Precio", "Margen%", "Stock", "Min.", "Es Caja?", "Factor", "Editar", "Eliminar"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Name column stretches
        self.table.setWordWrap(True)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
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
        
        # Pagination Controls
        pagination_layout = QHBoxLayout()
        
        self.btn_prev = QPushButton("◀ Anterior")
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_prev.setEnabled(False)
        
        self.lbl_page = QLabel("Página 1 de 1")
        self.lbl_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_next = QPushButton("Siguiente ▶")
        self.btn_next.clicked.connect(self.next_page)
        self.btn_next.setEnabled(False)
        
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.btn_prev)
        pagination_layout.addWidget(self.lbl_page)
        pagination_layout.addWidget(self.btn_next)
        pagination_layout.addStretch()
        
        self.layout.addLayout(pagination_layout)

    def open_new_product_dialog(self):
        """Open dialog to create new product"""
        dialog = ProductFormDialog(self, controller=self.controller)
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
        
        dialog = ProductFormDialog(self, product, controller=self.controller)
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

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_products()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_products()

    def load_products(self):
        self.table.setRowCount(0)
        
        search_text = self.search_input.text().strip()
        products, total_items = self.controller.get_products_paginated(
            page=self.current_page, 
            page_size=self.page_size, 
            search_query=search_text
        )
        
        # Update pagination labels
        import math
        self.total_pages = math.ceil(total_items / self.page_size) if total_items > 0 else 1
        self.lbl_page.setText(f"Página {self.current_page} de {self.total_pages} (Total: {total_items})")
        
        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < self.total_pages)
        
        for row, prod in enumerate(products):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(prod.id)))
            self.table.setItem(row, 1, QTableWidgetItem(prod.name))
            self.table.setItem(row, 2, QTableWidgetItem(prod.sku or ""))
            self.table.setItem(row, 3, QTableWidgetItem(prod.location or "-"))
            self.table.setItem(row, 4, QTableWidgetItem(f"${prod.cost_price:,.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"${prod.price:,.2f}"))
            
            # Calculate margin
            if prod.price > 0:
                margin = ((prod.price - prod.cost_price) / prod.price) * 100
                margin_item = QTableWidgetItem(f"{margin:.1f}%")
                if margin < 0:
                    margin_item.setForeground(QColor("red"))
                else:
                    margin_item.setForeground(QColor("green"))
                self.table.setItem(row, 6, margin_item)
            else:
                self.table.setItem(row, 6, QTableWidgetItem("-"))
            
            stock_item = QTableWidgetItem(str(prod.stock))
            min_stock = prod.min_stock if hasattr(prod, 'min_stock') else 5.0
            
            if prod.stock <= min_stock:
                stock_item.setForeground(QColor("red"))
                stock_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
                stock_item.setBackground(QColor("#FFEBEE")) # Light red background
            
                stock_item.setBackground(QColor("#FFEBEE")) # Light red background
            
            self.table.setItem(row, 7, stock_item)
            self.table.setItem(row, 8, QTableWidgetItem(str(min_stock)))
            self.table.setItem(row, 9, QTableWidgetItem("Sí" if prod.is_box else "No"))
            self.table.setItem(row, 10, QTableWidgetItem(str(prod.conversion_factor)))
            
            # Edit Button
            btn_edit = QPushButton("✏ Editar")
            btn_edit.setStyleSheet("background-color: #2196F3; color: white; padding: 6px; border-radius: 4px;")
            btn_edit.clicked.connect(lambda checked, pid=prod.id: self.open_edit_product_dialog(pid))
            self.table.setCellWidget(row, 11, btn_edit)
            
            # Delete Button
            btn_delete = QPushButton("🗑 Eliminar")
            btn_delete.setStyleSheet("background-color: #F44336; color: white; padding: 6px; border-radius: 4px;")
            btn_delete.clicked.connect(lambda checked, pid=prod.id: self.delete_product(pid))
            self.table.setCellWidget(row, 12, btn_delete)

    def filter_products(self):
        """Filter products based on search text (Debounced)"""
        # Reset to page 1 for new search
        self.current_page = 1
        self.update_timer.start() # This calls load_products after delay

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
        # self.db.close()
        event.accept()
