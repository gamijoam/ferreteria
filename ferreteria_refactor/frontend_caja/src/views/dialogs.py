from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QAbstractItemView, QCompleter, QMessageBox,
    QComboBox, QDialog, QDoubleSpinBox, QFrame, QFormLayout
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QColor, QStandardItemModel, QStandardItem, QIcon, QAction

class CartItemEditDialog(QDialog):
    """
    Dialog for editing a cart item (Quantity & potentially Price).
    Pop-up approach prevents table editing bugs.
    """
    def __init__(self, item_dict, parent=None):
        super().__init__(parent)
        self.item = item_dict
        self.new_quantity = item_dict['quantity']
        self.setWindowTitle("Editar Item")
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Header: Product Name
        lbl_name = QLabel(item_dict['name'])
        lbl_name.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        lbl_name.setWordWrap(True)
        lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_name)
        
        # Sub-header: Unit / Presentation
        lbl_unit = QLabel(f"Presentación: {item_dict.get('unit_name', 'Unidad')}")
        lbl_unit.setStyleSheet("color: #555; font-size: 11pt;")
        lbl_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_unit)
        
        layout.addSpacing(20)
        
        # Quantity Input
        q_layout = QHBoxLayout()
        q_layout.addWidget(QLabel("Cantidad:"))
        
        self.spin_qty = QDoubleSpinBox()
        self.spin_qty.setRange(0.01, 99999.99)
        self.spin_qty.setDecimals(2)
        self.spin_qty.setValue(self.new_quantity)
        self.spin_qty.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.spin_qty.setFixedHeight(50)
        self.spin_qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        q_layout.addWidget(self.spin_qty)
        
        layout.addLayout(q_layout)
        
        # Price Info (ReadOnly for now, or editable if permitted)
        price_layout = QHBoxLayout()
        lbl_p = QLabel(f"Precio Unit: ${item_dict['unit_price']:,.2f}")
        lbl_p.setStyleSheet("color: #1976D2; font-weight: bold;")
        price_layout.addStretch()
        price_layout.addWidget(lbl_p)
        price_layout.addStretch()
        layout.addLayout(price_layout)
        
        layout.addSpacing(20)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setStyleSheet("padding: 10px;")
        
        btn_save = QPushButton("Guardar Cambios")
        btn_save.clicked.connect(self.validate_and_accept)
        btn_save.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;")
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)
        
        # Auto-focus quantity
        self.spin_qty.setFocus()
        self.spin_qty.selectAll()

    def validate_and_accept(self):
        val = self.spin_qty.value()
        if val <= 0:
            QMessageBox.warning(self, "Error", "La cantidad debe ser mayor a 0")
            return
        self.new_quantity = val
        self.accept()

class UnitSelectionDialog(QDialog):
    """
    Dialog to select a specific unit/presentation when adding a product with multiple active units.
    """
    def __init__(self, parent=None, product=None, units=None, exchange_rate=1.0):
        super().__init__(parent)
        self.product = product
        self.units = units or []
        self.exchange_rate = exchange_rate
        self.selected_unit = None
        
        self.setWindowTitle(f"Seleccionar Presentación: {product.get('name')}")
        self.setFixedWidth(500)
        self.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(self)
        
        lbl_inst = QLabel("Este producto tiene múltiples presentaciones.\nSeleccione cuál desea agregar:")
        lbl_inst.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_inst.setStyleSheet("color: #555; font-size: 11pt; margin-bottom: 10px;")
        layout.addWidget(lbl_inst)
        
        # Grid/List of Options
        # Use a Vertical layout of styled buttons for simplicity and readability
        options_layout = QVBoxLayout()
        options_layout.setSpacing(10)
        
        for unit in self.units:
            btn = QPushButton()
            
            # Prepare Text
            u_name = unit.get('name', 'Unidad')
            u_factor = unit.get('conversion_factor', 1.0)
            u_price = unit.get('price')
            
            # If price is None, it uses math (Base * Factor)
            if u_price is None:
                base_price = product.get('price', 0)
                u_price = base_price * u_factor
            
            price_bs = u_price * self.exchange_rate
            
            text = f"{u_name}\n${u_price:,.2f}  /  Bs {price_bs:,.2f}"
            btn.setText(text)
            
            # Styling
            btn.setFixedHeight(60)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #E3F2FD;
                    border: 1px solid #2196F3;
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 20px;
                    font-size: 12pt;
                    font-weight: bold;
                    color: #0D47A1;
                }
                QPushButton:hover {
                    background-color: #BBDEFB;
                }
            """)
            
            # Connect
            # Use default arg to capture 'unit' in lambda scope correctly
            btn.clicked.connect(lambda checked, u=unit: self.select_unit(u))
            
            options_layout.addWidget(btn)
            
        layout.addLayout(options_layout)
        layout.addStretch()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)

    def select_unit(self, unit):
        self.selected_unit = unit
        self.accept()
