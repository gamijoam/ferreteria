from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog,
    QComboBox, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.database.db import SessionLocal
from src.controllers.return_controller import ReturnController
from frontend_caja.services.cash_service import CashService

class ReturnDialog(QDialog):
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.setWindowTitle("Procesar Devolución - Módulo 6")
        self.resize(1300, 800)
        
        self.db = SessionLocal()
        self.controller = ReturnController(self.db)
        self.cash_service = CashService()
        self.current_sale = None
        
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        
        self.setup_ui()
        self.load_initial_sales()

    # ... (setup_ui, load_methods unchanged) ...

    def validate_session(self):
        """Check if user has an open cash session"""
        if not self.user: 
            return True
        try:
            session = self.cash_service.get_current_session(self.user.id)
            if not session or session.get("status") != "OPEN":
                QMessageBox.warning(self, "Caja Cerrada", "Debe abrir una sesión de caja antes de realizar devoluciones.")
                return False
            return True
        except Exception as e:
            print(f"Error checking session: {e}")
            return False

    def setup_ui(self):
        # --- LEFT PANEL: Sales List ---
        left_panel = QVBoxLayout()
        
        left_panel.addWidget(QLabel("<b>Buscar Venta:</b>"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por ID o Cliente...")
        self.search_input.textChanged.connect(self.filter_sales)
        left_panel.addWidget(self.search_input)
        
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(4)
        self.sales_table.setHorizontalHeaderLabels(["ID", "Fecha", "Cliente", "Total"])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.sales_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.sales_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sales_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.sales_table.itemSelectionChanged.connect(self.on_sale_selected)
        left_panel.addWidget(self.sales_table)
        
        # Wrap left panel in a widget/frame if needed, or just add layout
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        self.layout.addWidget(left_widget, 35) # 35% width
        
        # --- RIGHT PANEL: Sale Details ---
        right_panel = QVBoxLayout()
        
        self.lbl_info = QLabel("Seleccione una venta para ver detalles")
        self.lbl_info.setStyleSheet("font-size: 14pt; font-weight: bold; color: #1976D2;")
        right_panel.addWidget(self.lbl_info)
        
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(5)
        self.details_table.setHorizontalHeaderLabels([
            "ID Prod", "Producto", "Cant. Comprada", "Precio Unit.", "Devolver (Cant)"
        ])
        self.details_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        right_panel.addWidget(self.details_table)
        
        # Action Layout
        action_layout = QHBoxLayout()
        
        # Currency Selector
        action_layout.addWidget(QLabel("Moneda de Reembolso:"))
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["USD", "Bs"])
        self.currency_combo.setCurrentIndex(1)  # Default to Bs
        self.currency_combo.setFont(QFont("Arial", 12))
        action_layout.addWidget(self.currency_combo)
        
        action_layout.addStretch()
        
        # Void Button
        btn_void = QPushButton("ANULAR VENTA COMPLETA")
        btn_void.setStyleSheet("background-color: #ff9800; color: white; font-weight: bold; padding: 10px;")
        btn_void.clicked.connect(self.void_sale)
        action_layout.addWidget(btn_void)
        
        # Process Button
        btn_process = QPushButton("PROCESAR DEVOLUCIÓN")
        btn_process.setStyleSheet("background-color: red; color: white; font-weight: bold; padding: 10px;")
        btn_process.clicked.connect(self.process_return)
        action_layout.addWidget(btn_process)
        
        right_panel.addLayout(action_layout)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        self.layout.addWidget(right_widget, 65) # 65% width

    def load_initial_sales(self):
        sales = self.controller.get_recent_sales()
        self.populate_sales_table(sales)

    def filter_sales(self):
        query = self.search_input.text().strip()
        if not query:
            self.load_initial_sales()
            return
            
        sales = self.controller.search_sales(query)
        self.populate_sales_table(sales)

    def populate_sales_table(self, sales):
        self.sales_table.blockSignals(True)
        self.sales_table.setRowCount(0)
        for i, sale in enumerate(sales):
            self.sales_table.insertRow(i)
            self.sales_table.setItem(i, 0, QTableWidgetItem(str(sale.id)))
            self.sales_table.setItem(i, 1, QTableWidgetItem(sale.date.strftime("%Y-%m-%d %H:%M")))
            customer_name = sale.customer.name if sale.customer else "Cliente General"
            self.sales_table.setItem(i, 2, QTableWidgetItem(customer_name))
            self.sales_table.setItem(i, 3, QTableWidgetItem(f"${sale.total_amount:,.2f}"))
            
            # Store sale object in first item
            self.sales_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, sale.id)
        self.sales_table.blockSignals(False)

    def on_sale_selected(self):
        selected_items = self.sales_table.selectedItems()
        if not selected_items:
            return
            
        row = selected_items[0].row()
        sale_id = self.sales_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        self.load_sale_details(sale_id)

    def load_sale_details(self, sale_id):
        sale = self.controller.find_sale(sale_id)
        if not sale:
            return
            
        self.current_sale = sale
        self.lbl_info.setText(f"Venta #{sale.id} - {sale.date.strftime('%d/%m/%Y')} - Total: ${sale.total_amount:,.2f}")
        
        self.details_table.setRowCount(0)
        for i, detail in enumerate(sale.details):
            self.details_table.insertRow(i)
            self.details_table.setItem(i, 0, QTableWidgetItem(str(detail.product_id)))
            self.details_table.setItem(i, 1, QTableWidgetItem(detail.product.name))
            self.details_table.setItem(i, 2, QTableWidgetItem(str(detail.quantity)))
            self.details_table.setItem(i, 3, QTableWidgetItem(f"${detail.unit_price:,.2f}"))
            
            # Editable Return Qty (Default 0)
            qty_item = QTableWidgetItem("0")
            self.details_table.setItem(i, 4, qty_item)

    def void_sale(self):
        """Set all return quantities to max and auto-process"""
        if not self.validate_session(): return

        if not self.current_sale:
            QMessageBox.warning(self, "Alerta", "Seleccione una venta primero")
            return
        
        # Detect original payment method to determine refund currency
        original_payment = self.current_sale.payment_method
        
        # Determine refund currency based on original payment
        if "USD" in original_payment:
            refund_currency = "USD"
        elif "Bs" in original_payment or "Pago Móvil" in original_payment:
            refund_currency = "Bs"
        else:
            # For other methods (Tarjeta, Crédito), ask user
            refund_currency = self.currency_combo.currentText()
            
        for i in range(self.details_table.rowCount()):
            # Get max qty from column 2 (Cant. Comprada)
            max_qty = self.details_table.item(i, 2).text()
            self.details_table.item(i, 4).setText(max_qty)
        
        # Auto-trigger process with void message
        reason, ok = QInputDialog.getText(self, "Anular Venta", f"Razón de la anulación:\\n(Reembolso en {refund_currency})")
        if not ok or not reason:
            # Reset quantities if cancelled
            for i in range(self.details_table.rowCount()):
                self.details_table.item(i, 4).setText("0")
            return
        
        # Process immediately with detected currency
        try:
            items_to_return = []
            
            for i in range(self.details_table.rowCount()):
                try:
                    qty_return = float(self.details_table.item(i, 4).text())
                    if qty_return > 0:
                        product_id = int(self.details_table.item(i, 0).text())
                        items_to_return.append({
                            "product_id": product_id,
                            "quantity": qty_return
                        })
                except ValueError:
                    continue
            
            # Get current rate
            from src.controllers.config_controller import ConfigController
            config_ctrl = ConfigController(self.db)
            rate = config_ctrl.get_exchange_rate()
            
            ret = self.controller.process_return(self.current_sale.id, items_to_return, reason, refund_currency, rate)
            
            msg = f"Venta ANULADA correctamente.\\n\\nReembolso Total: ${ret.total_refunded:,.2f} (USD Base)"
            if refund_currency == "Bs":
                refund_bs = ret.total_refunded * rate
                msg += f"\\n\\nSe registró una salida de caja de: Bs {refund_bs:,.2f}"
            else:
                msg += f"\\n\\nSe registró una salida de caja de: ${ret.total_refunded:,.2f}"
                
            QMessageBox.information(self, "Venta Anulada", msg)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def process_return(self):
        if not self.validate_session(): return

        if not self.current_sale:
            QMessageBox.warning(self, "Alerta", "Seleccione una venta primero")
            return

        items_to_return = []
        
        for i in range(self.details_table.rowCount()):
            try:
                qty_return = float(self.details_table.item(i, 4).text())
                if qty_return > 0:
                    product_id = int(self.details_table.item(i, 0).text())
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
            # Get currency and rate
            currency = self.currency_combo.currentText()
            
            # Get current rate
            from src.controllers.config_controller import ConfigController
            config_ctrl = ConfigController(self.db)
            rate = config_ctrl.get_exchange_rate()
            
            ret = self.controller.process_return(self.current_sale.id, items_to_return, reason, currency, rate)
            
            msg = f"Devolución procesada correctamente.\\n\\nReembolso Total: ${ret.total_refunded:,.2f} (USD Base)"
            if currency == "Bs":
                refund_bs = ret.total_refunded * rate
                msg += f"\\n\\nSe registró una salida de caja de: Bs {refund_bs:,.2f}"
            else:
                msg += f"\\n\\nSe registró una salida de caja de: ${ret.total_refunded:,.2f}"
                
            QMessageBox.information(self, "Éxito", msg)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def closeEvent(self, event):
        self.db.close()
        event.accept()
