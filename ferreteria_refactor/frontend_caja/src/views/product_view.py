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
    """Dialog for creating/editing products"""
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle("Editar Producto" if product else "Nuevo Producto")
        self.resize(600, 500)  # Reasonable initial size
        self.setMinimumHeight(400)  # Prevent window from being too small
        
        self.setup_ui()
        
        if product:
            self.populate_form(product)
    
    def setup_ui(self):
        # Main layout (only 2 elements: scroll area + buttons)
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Get base currency configuration
        self.base_currency, self.currency_symbol = self.get_base_currency()
        
        # ===== ELEMENT 1: SCROLL AREA (Scrollable Content) =====
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Container widget for all form fields
        scroll_content = QWidget()
        content_layout = QVBoxLayout()
        scroll_content.setLayout(content_layout)
        
        # Grid Layout for form fields (2 columns)
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(10)
        
        # --- FIELDS ---
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre del Producto")
        
        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText("Código único")
        
        self.cost_input = QLineEdit()
        self.cost_input.setPlaceholderText("0.00")
        self.cost_input.textChanged.connect(self.calculate_margin)
        
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("0.00")
        self.price_input.textChanged.connect(self.calculate_margin)
        self.price_input.textChanged.connect(self.update_converted_price)
        
        self.margin_label = QLabel("Margen: -")
        self.margin_label.setStyleSheet("font-weight: bold; color: green;")
        
        self.stock_input = QDoubleSpinBox()
        self.stock_input.setRange(0, 1000000)
        self.stock_input.setDecimals(2)
        self.stock_input.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        
        self.min_stock_input = QDoubleSpinBox()
        self.min_stock_input.setRange(0, 1000000)
        self.min_stock_input.setDecimals(2)
        self.min_stock_input.setValue(5.0)
        self.min_stock_input.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        
        self.unit_type_combo = QComboBox()
        self.unit_type_combo.addItems(["Unidad", "Metro", "Kilo", "Litro", "Servicio"])
        
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Ubicación en almacén")
        
        # Box / Pack Logic
        self.is_box_check = QCheckBox("Es Caja / Pack")
        self.is_box_check.toggled.connect(self.toggle_box_fields)
        
        self.conversion_factor_input = QLineEdit()
        self.conversion_factor_input.setPlaceholderText("Unidades por caja")
        self.conversion_factor_input.setEnabled(False)
        self.conversion_factor_input.setText("1")

        # --- Adding to Grid (Label, Widget, Row, Col) ---
        # First Column
        grid_layout.addWidget(QLabel("Nombre del Producto:*"), 0, 0)
        grid_layout.addWidget(self.name_input, 1, 0)
        
        grid_layout.addWidget(QLabel("SKU / Código:"), 2, 0)
        grid_layout.addWidget(self.sku_input, 3, 0)
        
        # Dynamic currency labels
        cost_label = QLabel(f"Costo de Compra ({self.currency_symbol}):")
        cost_label.setToolTip(f"Precio en {self.base_currency}")
        grid_layout.addWidget(cost_label, 4, 0)
        grid_layout.addWidget(self.cost_input, 5, 0)
        
        grid_layout.addWidget(QLabel("Stock Actual:"), 6, 0)
        grid_layout.addWidget(self.stock_input, 7, 0)
        
        grid_layout.addWidget(QLabel("Ubicación:"), 8, 0)
        grid_layout.addWidget(self.location_input, 9, 0)

        # Second Column
        grid_layout.addWidget(QLabel("Tipo de Unidad:"), 0, 1)
        grid_layout.addWidget(self.unit_type_combo, 1, 1)

        price_label = QLabel(f"Precio Venta ({self.currency_symbol}):")
        price_label.setToolTip(f"Precio en {self.base_currency}")
        grid_layout.addWidget(price_label, 4, 1)
        grid_layout.addWidget(self.price_input, 5, 1)
        
        grid_layout.addWidget(self.margin_label, 6, 1)
        
        grid_layout.addWidget(QLabel("Stock Mínimo (Alerta):"), 7, 1)
        grid_layout.addWidget(self.min_stock_input, 8, 1)

        # Add grid to content layout
        content_layout.addLayout(grid_layout)
        
        # Currency Reference Section
        currency_group = QGroupBox("Conversión de Moneda (Referencia)")
        currency_layout = QFormLayout()
        
        # Reference rate selector
        self.reference_rate_combo = QComboBox()
        self.reference_rate_combo.setToolTip("Seleccione una tasa para ver el precio convertido")
        self.load_exchange_rates()
        self.reference_rate_combo.currentIndexChanged.connect(self.update_converted_price)
        currency_layout.addRow("Tasa Referencial:", self.reference_rate_combo)
        
        # Converted price display
        self.converted_price_label = QLabel("")
        self.converted_price_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2196F3;
                padding: 8px;
                background-color: #E3F2FD;
                border-radius: 4px;
                border: 2px solid #2196F3;
            }
        """)
        self.converted_price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        currency_layout.addRow("", self.converted_price_label)
        
        currency_group.setLayout(currency_layout)
        content_layout.addWidget(currency_group)
        
        # Section for Packs
        pack_group = QGroupBox("Configuración de Empaque")
        pack_layout = QHBoxLayout()
        pack_layout.addWidget(self.is_box_check)
        pack_layout.addWidget(QLabel("Factor:"))
        pack_layout.addWidget(self.conversion_factor_input)
        pack_group.setLayout(pack_layout)
        content_layout.addWidget(pack_group)
        
        # Add stretch to push content to top
        content_layout.addStretch()
        
        # Set scroll content
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # ===== ELEMENT 2: FIXED FOOTER (Buttons) =====
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("Guardar Producto")
        save_btn.setStyleSheet("""
            background-color: #2ecc71; 
            color: white; 
            padding: 10px 20px; 
            font-size: 11pt; 
            font-weight: bold; 
            border-radius: 4px;
        """)
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet("""
            background-color: #e74c3c; 
            color: white; 
            padding: 10px 20px; 
            font-size: 11pt; 
            border-radius: 4px;
        """)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        main_layout.addLayout(btn_layout)
    
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
            "unit_type": self.unit_type_combo.currentText(),
            "location": self.location_input.text().strip() or None
        }


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
