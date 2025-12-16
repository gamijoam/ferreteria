from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QWidget, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QIcon

class UnitSelectionDialog(QDialog):
    def __init__(self, parent=None, product=None, units=None, exchange_rate=1.0):
        super().__init__(parent)
        self.product = product
        self.units = units or []
        self.exchange_rate = exchange_rate
        self.selected_unit = None
        
        self.setWindowTitle("Seleccione Presentación")
        self.resize(800, 600)
        self.setStyleSheet("background-color: #f5f5f5;")
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #1976D2; color: white; border-radius: 5px;")
        header_layout = QVBoxLayout()
        header_frame.setLayout(header_layout)
        
        lbl_title = QLabel(f"Producto: {self.product.get('name', 'Unknown')}")
        lbl_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(lbl_title)
        
        lbl_subtitle = QLabel("Seleccione la unidad a vender:")
        lbl_subtitle.setFont(QFont("Arial", 12))
        lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(lbl_subtitle)
        
        layout.addWidget(header_frame)
        
        # Scroll Area for Grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        grid = QGridLayout()
        grid.setSpacing(15)
        container.setLayout(grid)
        
        # Base Unit Button (First option)
        # Calculate Base Price
        base_price_usd = self.product.get('price', 0.0)
        base_price_bs = base_price_usd * self.exchange_rate
        base_unit_name = self.product.get('base_unit', 'UNIDAD')
        
        btn_base = self.create_unit_button(
            name=f"{base_unit_name} (Base)",
            factor=1.0,
            price_usd=base_price_usd,
            price_bs=base_price_bs,
            is_default=True
        )
        # Store unit info in button data or use lambda
        # We'll use a standardized dict structure for the return value
        base_unit_data = {
            'unit_name': base_unit_name,
            'unit_id': None, # None implies base unit
            'conversion_factor': 1.0,
            'price': base_price_usd,
            'barcode': self.product.get('sku')
        }
        btn_base.clicked.connect(lambda checked, data=base_unit_data: self.select_unit(data))
        grid.addWidget(btn_base, 0, 0)
        
        # Dynamic Units
        row, col = 0, 1
        max_cols = 3
        
        for unit in self.units:
            # Calculate price for this unit
            # Logic: If unit has specific price, use it. Else Base * Factor.
            unit_price = unit.get('price')
            factor = unit.get('conversion_factor', 1.0)
            
            if unit_price and unit_price > 0:
                final_usd = unit_price
            else:
                final_usd = base_price_usd * factor
            
            final_bs = final_usd * self.exchange_rate
            
            btn = self.create_unit_button(
                name=unit.get('name', 'Unknown'),
                factor=factor,
                price_usd=final_usd,
                price_bs=final_bs,
                is_default=unit.get('is_default_sale', False)
            )
            
            unit_data = {
                'unit_name': unit.get('name'),
                'unit_id': unit.get('id'),
                'conversion_factor': factor,
                'price': final_usd,
                'barcode': unit.get('barcode')
            }
            btn.clicked.connect(lambda checked, data=unit_data: self.select_unit(data))
            
            grid.addWidget(btn, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # Cancel Button
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #BDBDBD; 
                color: black; 
                font-size: 14pt; 
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #9E9E9E; }
        """)
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)

    def create_unit_button(self, name, factor, price_usd, price_bs, is_default):
        btn = QPushButton()
        btn.setMinimumSize(200, 150)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Style
        bg_color = "#E8F5E9" if is_default else "white"
        border_color = "#4CAF50" if is_default else "#ccc"
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 10px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: #C8E6C9;
                border-color: #2E7D32;
            }}
        """)
        
        # Layout inside button (using QVBoxLayout on a widget set as layout? No, QPushButton can't have layout directly easily)
        # We will use HTML text for rich formatting
        
        text = f"""
        <div style='color: #333;'>
            <h2 style='margin:0;'>{name}</h2>
            <p style='color: #666; font-size: 12px;'>Factor: {factor}</p>
            <hr>
            <h1 style='color: #1976D2; margin:5px;'>${price_usd:,.2f}</h1>
            <h3 style='color: #388E3C; margin:0;'>Bs {price_bs:,.2f}</h3>
        </div>
        """
        btn.setText(name) # Fallback
        
        # Better approach: Create a custom widget or just use setText with HTML if supported well (it isn't fully centered usually)
        # Let's use QLabels inside a layout on top of the button? 
        # Actually standard HTML in setText works okay for QButtons in PyQt6 usually, 
        # but let's just make the text the HTML.
        
        btn.setText("") # Clear standard text
        
        # Create a layout for the button
        btn_layout = QVBoxLayout(btn)
        
        lbl_name = QLabel(name)
        lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_name.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        lbl_name.setStyleSheet("color: #333; border: none; background: transparent;")
        
        lbl_price_usd = QLabel(f"${price_usd:,.2f}")
        lbl_price_usd.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_price_usd.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_price_usd.setStyleSheet("color: #1976D2; border: none; background: transparent;")
        
        lbl_price_bs = QLabel(f"Bs {price_bs:,.2f}")
        lbl_price_bs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_price_bs.setFont(QFont("Arial", 12))
        lbl_price_bs.setStyleSheet("color: #388E3C; border: none; background: transparent;")
        
        btn_layout.addWidget(lbl_name)
        btn_layout.addWidget(lbl_price_usd)
        btn_layout.addWidget(lbl_price_bs)
        
        return btn

    def select_unit(self, unit_data):
        self.selected_unit = unit_data
        self.accept()
