from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog
)
from src.database.db import SessionLocal
from src.controllers.return_controller import ReturnController

class ReturnDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Procesar Devolución - Módulo 6")
        self.resize(1200, 750)
        
        self.db = SessionLocal()
        self.controller = ReturnController(self.db)
        self.current_sale = None
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.setup_ui()

    def setup_ui(self):
        # Search
        search_layout = QHBoxLayout()
        self.input_sale_id = QLineEdit()
        self.input_sale_id.setPlaceholderText("Número de Ticket / Venta ID")
        
        btn_search = QPushButton("Buscar Venta")
        btn_search.clicked.connect(self.search_sale)
        
        search_layout.addWidget(QLabel("Ticket #:"))
        search_layout.addWidget(self.input_sale_id)
        search_layout.addWidget(btn_search)
        self.layout.addLayout(search_layout)
        
        # Info
        self.lbl_info = QLabel("")
        self.layout.addWidget(self.lbl_info)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID Prod", "Producto", "Cant. Comprada", "Precio Unit.", "Devolver (Cant)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)
        
        # Action
        btn_process = QPushButton("PROCESAR DEVOLUCIÓN")
        btn_process.setStyleSheet("background-color: red; color: white; font-weight: bold; padding: 10px;")
        btn_process.clicked.connect(self.process_return)
        self.layout.addWidget(btn_process)

    def search_sale(self):
        sale_id_text = self.input_sale_id.text()
        if not sale_id_text.isdigit():
            QMessageBox.warning(self, "Error", "ID inválido")
            return
            
        sale_id = int(sale_id_text)
        sale = self.controller.find_sale(sale_id)
        
        if not sale:
            QMessageBox.warning(self, "Error", "Venta no encontrada")
            self.current_sale = None
            self.table.setRowCount(0)
            self.lbl_info.setText("")
            return
            
        self.current_sale = sale
        self.lbl_info.setText(f"Venta del {sale.date} - Total: ${sale.total_amount:,.0f}")
        
        self.table.setRowCount(0)
        for i, detail in enumerate(sale.details):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(detail.product_id)))
            self.table.setItem(i, 1, QTableWidgetItem(detail.product.name))
            self.table.setItem(i, 2, QTableWidgetItem(str(detail.quantity)))
            self.table.setItem(i, 3, QTableWidgetItem(f"${detail.unit_price:,.0f}"))
            
            # Editable Return Qty (Default 0)
            qty_item = QTableWidgetItem("0")
            self.table.setItem(i, 4, qty_item)

    def process_return(self):
        if not self.current_sale:
            return

        items_to_return = []
        
        for i in range(self.table.rowCount()):
            try:
                qty_return = int(self.table.item(i, 4).text())
                if qty_return > 0:
                    product_id = int(self.table.item(i, 0).text())
                    items_to_return.append({
                        "product_id": product_id,
                        "quantity": qty_return
                    })
            except ValueError:
                continue
                
        if not items_to_return:
            QMessageBox.warning(self, "Alerta", "No has seleccionado ningún item para devolver (Cant > 0)")
            return

        reason, ok = QInputDialog.getText(self, "Motivo", "Razón de la devolución:")
        if not ok or not reason:
            return

        try:
            ret = self.controller.process_return(self.current_sale.id, items_to_return, reason)
            QMessageBox.information(self, "Éxito", f"Devolución procesada. Reembolso total: ${ret.total_refunded:,.0f}")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def closeEvent(self, event):
        self.db.close()
        event.accept()
