from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QFrame, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Services
from frontend_caja.services.product_service import ProductService
from src.utils.label_generator import LabelGenerator
import os

class LabelWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Impresión de Etiquetas (PDF) - Módulo 10")
        self.resize(1200, 750)
        
        self.product_service = ProductService()
        self.label_generator = LabelGenerator()
        self.products = []
        self.queue = [] # List of dicts
        
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        
        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        # LEFT PANEL: Controls
        left_panel = QVBoxLayout()
        
        item_group = QGroupBox("Agregar a Cola")
        form_layout = QVBoxLayout()
        
        # Search / Combo
        form_layout.addWidget(QLabel("Producto:"))
        self.product_combo = QComboBox()
        self.product_combo.setEditable(True) # Searchable
        self.product_combo.completer().setCompletionMode(self.product_combo.completer().CompletionMode.PopupCompletion)
        form_layout.addWidget(self.product_combo)
        
        # Qty
        form_layout.addWidget(QLabel("Cantidad de Etiquetas:"))
        self.qty_input = QLineEdit("1")
        self.qty_input.setPlaceholderText("Ej. 10")
        form_layout.addWidget(self.qty_input)
        
        # Add Button
        btn_add = QPushButton("Agregar a Cola ⬇")
        btn_add.setStyleSheet("background-color: #2196F3; color: white; padding: 10px; font-weight: bold;")
        btn_add.clicked.connect(self.add_to_queue)
        form_layout.addWidget(btn_add)
        
        item_group.setLayout(form_layout)
        left_panel.addWidget(item_group)
        
        # PDF Options (Simple for now)
        opt_group = QGroupBox("Configuración de Página")
        opt_layout = QVBoxLayout()
        opt_layout.addWidget(QLabel("Formato: Hoja Carta (3 col x 10 filas)"))
        # Here we could add dropdown for Thermal / A4
        opt_group.setLayout(opt_layout)
        left_panel.addWidget(opt_group)
        
        left_panel.addStretch()
        
        # RIGHT PANEL: Queue Table
        right_panel = QVBoxLayout()
        
        right_panel.addWidget(QLabel("<b>Cola de Impresión:</b>"))
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Producto", "SKU", "Cant.", "Acción"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        right_panel.addWidget(self.table)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        
        btn_clear = QPushButton("Limpiar Cola")
        btn_clear.clicked.connect(self.clear_queue)
        btn_layout.addWidget(btn_clear)
        
        btn_generate = QPushButton("🖨️ Generar PDF")
        btn_generate.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        btn_generate.setStyleSheet("background-color: #4CAF50; color: white; padding: 15px;")
        btn_generate.clicked.connect(self.generate_pdf)
        btn_layout.addWidget(btn_generate)
        
        right_panel.addLayout(btn_layout)
        
        # Add to main
        self.layout.addLayout(left_panel, 35)
        self.layout.addLayout(right_panel, 65)

    def load_products(self):
        try:
            self.products = self.product_service.get_all_products()
            self.product_combo.clear()
            for p in self.products:
                display = f"{p['name']} - ${p['price']} (SKU: {p.get('sku', 'N/A')})"
                self.product_combo.addItem(display, p['id'])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando productos: {e}")

    def add_to_queue(self):
        try:
            prod_id = self.product_combo.currentData()
            if not prod_id:
                return
            
            # Find product data
            product = next((p for p in self.products if p['id'] == prod_id), None)
            if not product:
                return

            qty = int(self.qty_input.text())
            if qty <= 0:
                raise ValueError
            
            # Add to queue
            self.queue.append({
                "product_id": product['id'],
                "name": product['name'],
                "sku": product.get('sku'),
                "price": product['price'],
                "quantity": qty
            })
            
            self.refresh_table()
            self.qty_input.setText("1")
            self.qty_input.setFocus()
            
        except ValueError:
            QMessageBox.warning(self, "Error", "Cantidad inválida")

    def refresh_table(self):
        self.table.setRowCount(0)
        for i, item in enumerate(self.queue):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(item['name']))
            self.table.setItem(i, 1, QTableWidgetItem(item['sku'] or "N/A"))
            self.table.setItem(i, 2, QTableWidgetItem(str(item['quantity'])))
            
            btn_del = QPushButton("X")
            btn_del.setStyleSheet("color: red;")
            btn_del.clicked.connect(lambda checked, idx=i: self.remove_item(idx))
            self.table.setCellWidget(i, 3, btn_del)

    def remove_item(self, index):
        if 0 <= index < len(self.queue):
            self.queue.pop(index)
            self.refresh_table()

    def clear_queue(self):
        self.queue = []
        self.refresh_table()

    def generate_pdf(self):
        if not self.queue:
            QMessageBox.warning(self, "Cola vacía", "Agregue productos a la cola")
            return
        
        try:
            pdf_path = self.label_generator.generate_pdf(self.queue)
            
            # Ask to open
            reply = QMessageBox.question(
                self, "PDF Generado", 
                f"Etiquetas generadas exitosamente.\n\n¿Desea abrir el archivo ahora?\n{pdf_path}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                os.startfile(pdf_path)
                
            # Clear queue? Maybe user wants to reprint.
            # self.clear_queue()
            
        except Exception as e:
            QMessageBox.critical(self, "Error Generando PDF", str(e))
