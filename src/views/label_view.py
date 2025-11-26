from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QTextEdit, QMessageBox, QFormLayout
)
from src.database.db import SessionLocal
from src.controllers.label_controller import LabelController
from src.models.models import Product

class LabelWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Impresión de Etiquetas - Módulo 10")
        self.resize(700, 600)
        
        self.db = SessionLocal()
        self.controller = LabelController(self.db)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        # Form
        form_layout = QFormLayout()
        
        self.product_combo = QComboBox()
        self.quantity_input = QLineEdit()
        self.quantity_input.setText("1")
        self.quantity_input.setPlaceholderText("Cantidad de etiquetas")
        
        btn_generate = QPushButton("Generar Etiquetas")
        btn_generate.clicked.connect(self.generate_labels)
        btn_generate.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;")
        
        form_layout.addRow("Producto:", self.product_combo)
        form_layout.addRow("Cantidad:", self.quantity_input)
        form_layout.addRow(btn_generate)
        
        self.layout.addLayout(form_layout)
        
        # Output
        self.layout.addWidget(QLabel("Etiquetas Generadas (Copiar y pegar para imprimir):"))
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFontFamily("Courier New")
        self.layout.addWidget(self.output_text)
        
        # Copy button
        btn_copy = QPushButton("Copiar al Portapapeles")
        btn_copy.clicked.connect(self.copy_to_clipboard)
        self.layout.addWidget(btn_copy)

    def load_products(self):
        self.product_combo.clear()
        products = self.db.query(Product).all()
        for p in products:
            self.product_combo.addItem(f"{p.name} - ${p.price:,.2f}", p.id)

    def generate_labels(self):
        try:
            product_id = self.product_combo.currentData()
            if not product_id:
                QMessageBox.warning(self, "Error", "Seleccione un producto")
                return
            
            quantity = int(self.quantity_input.text())
            if quantity <= 0:
                raise ValueError("La cantidad debe ser mayor a 0")
            
            labels_text = self.controller.generate_label_text(product_id, quantity)
            self.output_text.setPlainText(labels_text)
            
            QMessageBox.information(self, "Éxito", f"{quantity} etiqueta(s) generada(s)")
            
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def copy_to_clipboard(self):
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_text.toPlainText())
        QMessageBox.information(self, "Copiado", "Etiquetas copiadas al portapapeles")

    def closeEvent(self, event):
        self.db.close()
        event.accept()
