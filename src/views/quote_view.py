from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from src.database.db import SessionLocal
from src.controllers.quote_controller import QuoteController

class QuoteWindow(QWidget):
    def __init__(self, pos_window=None):
        super().__init__()
        self.setWindowTitle("Cotizaciones - Módulo 9")
        self.resize(900, 600)
        
        self.db = SessionLocal()
        self.controller = QuoteController(self.db)
        self.pos_window = pos_window  # Reference to POS for loading quotes
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.setup_ui()
        self.load_quotes()

    def setup_ui(self):
        # Header
        self.layout.addWidget(QLabel("Listado de Cotizaciones"))
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Fecha", "Cliente", "Total", "Estado", "Acciones"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)
        
        # Refresh button
        btn_refresh = QPushButton("Actualizar")
        btn_refresh.clicked.connect(self.load_quotes)
        self.layout.addWidget(btn_refresh)

    def load_quotes(self):
        quotes = self.controller.get_all_quotes()
        self.table.setRowCount(0)
        
        for i, quote in enumerate(quotes):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(quote.id)))
            self.table.setItem(i, 1, QTableWidgetItem(quote.date.strftime('%Y-%m-%d %H:%M')))
            self.table.setItem(i, 2, QTableWidgetItem(quote.customer.name if quote.customer else "N/A"))
            self.table.setItem(i, 3, QTableWidgetItem(f"${quote.total_amount:,.2f}"))
            self.table.setItem(i, 4, QTableWidgetItem(quote.status))
            
            # Action buttons
            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(0, 0, 0, 0)
            
            btn_print = QPushButton("Imprimir")
            btn_print.clicked.connect(lambda checked, q=quote: self.print_quote(q))
            
            btn_convert = QPushButton("Convertir a Venta")
            btn_convert.clicked.connect(lambda checked, q=quote: self.convert_to_sale(q))
            if quote.status == "CONVERTED":
                btn_convert.setEnabled(False)
            
            btn_layout.addWidget(btn_print)
            btn_layout.addWidget(btn_convert)
            btn_widget.setLayout(btn_layout)
            
            self.table.setCellWidget(i, 5, btn_widget)

    def print_quote(self, quote):
        text = self.controller.generate_quote_text(quote.id)
        QMessageBox.information(self, f"Cotización #{quote.id}", text)

    def convert_to_sale(self, quote):
        if not self.pos_window:
            QMessageBox.warning(self, "Error", "No se puede cargar al POS. Abra el POS primero.")
            return
        
        reply = QMessageBox.question(
            self, "Confirmar", 
            f"¿Cargar cotización #{quote.id} al POS?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                cart = self.controller.convert_to_cart(quote.id)
                self.pos_window.controller.cart = cart
                self.pos_window.refresh_table()
                
                # Mark as converted
                self.controller.mark_as_converted(quote.id)
                
                QMessageBox.information(self, "Éxito", "Cotización cargada al POS. Puede finalizar la venta.")
                self.load_quotes()  # Refresh
                self.close()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def closeEvent(self, event):
        self.db.close()
        event.accept()
