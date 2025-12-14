from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, 
    QTabWidget, QDateEdit, QComboBox, QFormLayout, QGroupBox, QTextEdit
)
from PyQt6.QtCore import QDate
from src.controllers.report_controller import ReportController
from src.controllers.customer_controller import CustomerController
import datetime

class AdvancedReportWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reportes Avanzados - Módulo 12")
        self.resize(1200, 750)
        
        self.controller = ReportController()
        self.customer_controller = CustomerController()
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.setup_sales_report_tab()
        self.setup_cash_flow_tab()
        self.setup_top_products_tab()
        self.setup_customer_debt_tab()
        self.setup_stock_tab()

    # ===== TAB 1: SALES REPORT =====
    
    def setup_sales_report_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Filters
        filter_group = QGroupBox("Filtros")
        filter_layout = QFormLayout()
        
        self.sales_start_date = QDateEdit()
        self.sales_start_date.setDate(QDate.currentDate().addDays(-7))
        self.sales_start_date.setCalendarPopup(True)
        
        self.sales_end_date = QDateEdit()
        self.sales_end_date.setDate(QDate.currentDate())
        self.sales_end_date.setCalendarPopup(True)
        
        self.sales_customer_combo = QComboBox()
        self.sales_customer_combo.addItem("Todos los clientes", None)
        
        self.sales_payment_combo = QComboBox()
        self.sales_payment_combo.addItem("Todos", None)
        self.sales_payment_combo.addItem("Efectivo", "Efectivo")
        self.sales_payment_combo.addItem("Crédito", "Credito")
        
        btn_generate = QPushButton("Generar Reporte")
        btn_generate.clicked.connect(self.generate_sales_report)
        btn_generate.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        
        filter_layout.addRow("Fecha Inicio:", self.sales_start_date)
        filter_layout.addRow("Fecha Fin:", self.sales_end_date)
        filter_layout.addRow("Cliente:", self.sales_customer_combo)
        filter_layout.addRow("Método Pago:", self.sales_payment_combo)
        filter_layout.addRow(btn_generate)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Summary
        self.sales_summary_label = QLabel("Resumen: -")
        self.sales_summary_label.setStyleSheet("font-size: 14px; font-weight: bold; color: blue;")
        layout.addWidget(self.sales_summary_label)
        
        # Table
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(6)
        self.sales_table.setHorizontalHeaderLabels([
            "ID", "Fecha", "Cliente", "Total", "Método Pago", "Estado"
        ])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.sales_table)
        
        # Export button
        btn_export = QPushButton("Exportar a CSV")
        btn_export.clicked.connect(self.export_sales_report)
        layout.addWidget(btn_export)
        
        self.tabs.addTab(tab, "Ventas Detalladas")
        self.load_customers_for_filter()

    def load_customers_for_filter(self):
        customers = self.customer_controller.get_all_customers()
        for c in customers:
            # c is a CustomerObj with attributes
            self.sales_customer_combo.addItem(c.name, c.id)

    def generate_sales_report(self):
        start = self.sales_start_date.date().toPyDate()
        end = self.sales_end_date.date().toPyDate()
        customer_id = self.sales_customer_combo.currentData()
        payment_method = self.sales_payment_combo.currentData()
        
        start_dt = datetime.datetime.combine(start, datetime.time.min)
        end_dt = datetime.datetime.combine(end, datetime.time.max)
        
        sales = self.controller.get_detailed_sales_report(
            start_dt, end_dt, customer_id=customer_id, payment_method=payment_method
        )
        
        summary = self.controller.get_sales_summary(start_dt, end_dt)
        
        # Update summary
        if summary:
            self.sales_summary_label.setText(
                f"Total Ventas: ${summary['total_revenue']:,.2f} | "
                f"Transacciones: {summary['total_transactions']} | "
                f"Ticket Promedio: ${summary['average_ticket']:,.2f}"
            )
        
        # Fill table
        self.sales_table.setRowCount(0)
        for i, sale in enumerate(sales):
            self.sales_table.insertRow(i)
            # sale is a dict from API
            self.sales_table.setItem(i, 0, QTableWidgetItem(str(sale['id'])))
            
            # Parse date
            date_str = sale['date']
            if isinstance(date_str, str):
                try:
                    date_obj = datetime.datetime.fromisoformat(date_str)
                    date_display = date_obj.strftime('%Y-%m-%d %H:%M')
                except:
                    date_display = date_str
            else:
                date_display = date_str
            self.sales_table.setItem(i, 1, QTableWidgetItem(date_display))
            
            # Customer name
            customer = sale.get('customer')
            customer_name = customer['name'] if customer else "N/A"
            self.sales_table.setItem(i, 2, QTableWidgetItem(customer_name))
            
            # Display total with correct currency
            payment_method = sale.get('payment_method', '')
            total_amount = sale.get('total_amount', 0)
            
            if "Bs" in payment_method:
                total_amount_bs = sale.get('total_amount_bs')
                if total_amount_bs and total_amount_bs > 0:
                    amount = total_amount_bs
                else:
                    rate = sale.get('exchange_rate_used', 1.0)
                    amount = total_amount * rate
                self.sales_table.setItem(i, 3, QTableWidgetItem(f"Bs{amount:,.2f}"))
            else:
                self.sales_table.setItem(i, 3, QTableWidgetItem(f"${total_amount:,.2f}"))
            
            self.sales_table.setItem(i, 4, QTableWidgetItem(payment_method))
            self.sales_table.setItem(i, 5, QTableWidgetItem("Pagado" if sale.get('paid') else "Pendiente"))


    def export_sales_report(self):
        if self.sales_table.rowCount() == 0:
            QMessageBox.warning(self, "Alerta", "No hay datos para exportar")
            return
        
        filename = f"reporte_ventas_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        data = []
        for row in range(self.sales_table.rowCount()):
            data.append([
                self.sales_table.item(row, col).text() if self.sales_table.item(row, col) else ""
                for col in range(self.sales_table.columnCount())
            ])
        
        headers = [self.sales_table.horizontalHeaderItem(i).text() for i in range(self.sales_table.columnCount())]
        
        self.controller.export_to_csv(data, headers, filename)
        QMessageBox.information(self, "Éxito", f"Reporte exportado a: {filename}")

    # ===== TAB 2: CASH FLOW =====
    
    def setup_cash_flow_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Date filters
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Desde:"))
        
        self.cash_start_date = QDateEdit()
        self.cash_start_date.setDate(QDate.currentDate().addDays(-30))
        self.cash_start_date.setCalendarPopup(True)
        filter_layout.addWidget(self.cash_start_date)
        
        filter_layout.addWidget(QLabel("Hasta:"))
        
        self.cash_end_date = QDateEdit()
        self.cash_end_date.setDate(QDate.currentDate())
        self.cash_end_date.setCalendarPopup(True)
        filter_layout.addWidget(self.cash_end_date)
        
        btn_generate = QPushButton("Generar")
        btn_generate.clicked.connect(self.generate_cash_flow_report)
        filter_layout.addWidget(btn_generate)
        
        layout.addLayout(filter_layout)
        
        # Table
        self.cash_table = QTableWidget()
        self.cash_table.setColumnCount(5)
        self.cash_table.setHorizontalHeaderLabels([
            "Fecha", "Tipo", "Monto", "Descripción", "Sesión"
        ])
        self.cash_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.cash_table)
        
        self.tabs.addTab(tab, "Flujo de Caja")

    def generate_cash_flow_report(self):
        start = self.cash_start_date.date().toPyDate()
        end = self.cash_end_date.date().toPyDate()
        
        start_dt = datetime.datetime.combine(start, datetime.time.min)
        end_dt = datetime.datetime.combine(end, datetime.time.max)
        
        movements = self.controller.get_cash_flow_report(start_dt, end_dt)
        
        self.cash_table.setRowCount(0)
        for i, mov in enumerate(movements):
            self.cash_table.insertRow(i)
            # Parse date string from API
            date_str = mov['date']
            if isinstance(date_str, str):
                try:
                    date_obj = datetime.datetime.fromisoformat(date_str)
                    date_display = date_obj.strftime('%Y-%m-%d %H:%M')
                except:
                    date_display = date_str
            else:
                date_display = date_str.strftime('%Y-%m-%d %H:%M')
            
            self.cash_table.setItem(i, 0, QTableWidgetItem(date_display))
            self.cash_table.setItem(i, 1, QTableWidgetItem(mov['type']))
            # Display amount with correct currency symbol
            currency = mov.get('currency', 'USD')
            symbol = '$' if currency == 'USD' else 'Bs'
            self.cash_table.setItem(i, 2, QTableWidgetItem(f"{symbol}{mov['amount']:,.2f}"))
            self.cash_table.setItem(i, 3, QTableWidgetItem(mov['description']))
            self.cash_table.setItem(i, 4, QTableWidgetItem(str(mov['session_id']) if mov['session_id'] else "N/A"))

    # ===== TAB 3: TOP PRODUCTS =====
    
    def setup_top_products_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        self.top_start_date = QDateEdit()
        self.top_start_date.setDate(QDate.currentDate().addDays(-30))
        self.top_start_date.setCalendarPopup(True)
        filter_layout.addWidget(QLabel("Desde:"))
        filter_layout.addWidget(self.top_start_date)
        
        self.top_end_date = QDateEdit()
        self.top_end_date.setDate(QDate.currentDate())
        self.top_end_date.setCalendarPopup(True)
        filter_layout.addWidget(QLabel("Hasta:"))
        filter_layout.addWidget(self.top_end_date)
        
        self.top_by_combo = QComboBox()
        self.top_by_combo.addItem("Por Cantidad", "quantity")
        self.top_by_combo.addItem("Por Ingresos", "revenue")
        filter_layout.addWidget(self.top_by_combo)
        
        btn_generate = QPushButton("Generar")
        btn_generate.clicked.connect(self.generate_top_products)
        filter_layout.addWidget(btn_generate)
        
        layout.addLayout(filter_layout)
        
        # Table
        self.top_table = QTableWidget()
        self.top_table.setColumnCount(3)
        self.top_table.setHorizontalHeaderLabels([
            "Producto", "Cantidad Vendida", "Ingresos"
        ])
        self.top_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.top_table)
        
        self.tabs.addTab(tab, "Top Productos")

    def generate_top_products(self):
        start = self.top_start_date.date().toPyDate()
        end = self.top_end_date.date().toPyDate()
        by = self.top_by_combo.currentData()
        
        start_dt = datetime.datetime.combine(start, datetime.time.min)
        end_dt = datetime.datetime.combine(end, datetime.time.max)
        
        top_products = self.controller.get_top_products(start_dt, end_dt, limit=20, by=by)
        
        self.top_table.setRowCount(0)
        for i, prod in enumerate(top_products):
            self.top_table.insertRow(i)
            self.top_table.setItem(i, 0, QTableWidgetItem(prod['product_name']))
            
            if by == "quantity":
                self.top_table.setItem(i, 1, QTableWidgetItem(str(int(prod['quantity_sold']))))
                self.top_table.setItem(i, 2, QTableWidgetItem("-"))
            else:
                self.top_table.setItem(i, 1, QTableWidgetItem("-"))
                self.top_table.setItem(i, 2, QTableWidgetItem(f"${prod['revenue']:,.2f}"))

    # ===== TAB 4: CUSTOMER DEBT =====
    
    def setup_customer_debt_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        btn_generate = QPushButton("Actualizar Reporte de Deudas")
        btn_generate.clicked.connect(self.generate_debt_report)
        layout.addWidget(btn_generate)
        
        self.debt_table = QTableWidget()
        self.debt_table.setColumnCount(4)
        self.debt_table.setHorizontalHeaderLabels([
            "Cliente", "Teléfono", "Deuda", "Acción"
        ])
        self.debt_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.debt_table)
        
        self.tabs.addTab(tab, "Deuda de Clientes")

    def generate_debt_report(self):
        report = self.controller.get_customer_debt_report()
        
        self.debt_table.setRowCount(0)
        total_debt = 0
        
        for i, item in enumerate(report):
            self.debt_table.insertRow(i)
            self.debt_table.setItem(i, 0, QTableWidgetItem(item['customer_name']))
            self.debt_table.setItem(i, 1, QTableWidgetItem(item['phone'] or "N/A"))
            self.debt_table.setItem(i, 2, QTableWidgetItem(f"${item['debt']:,.2f}"))
            
            total_debt += item['debt']
        
        # Add total row
        if report:
            row = self.debt_table.rowCount()
            self.debt_table.insertRow(row)
            
            from PyQt6.QtGui import QFont, QColor
            from PyQt6.QtCore import Qt
            
            total_item = QTableWidgetItem("TOTAL")
            font = QFont()
            font.setBold(True)
            total_item.setFont(font)
            self.debt_table.setItem(row, 0, total_item)
            
            debt_item = QTableWidgetItem(f"${total_debt:,.2f}")
            debt_item.setFont(font)
            debt_item.setForeground(QColor("red"))
            self.debt_table.setItem(row, 2, debt_item)

    # ===== TAB 5: STOCK =====
    
    def setup_stock_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        btn_low_stock = QPushButton("Ver Stock Bajo")
        btn_low_stock.clicked.connect(self.show_low_stock)
        layout.addWidget(btn_low_stock)
        
        btn_valuation = QPushButton("Valorización de Inventario")
        btn_valuation.clicked.connect(self.show_inventory_valuation)
        layout.addWidget(btn_valuation)
        
        self.stock_output = QTextEdit()
        self.stock_output.setReadOnly(True)
        layout.addWidget(self.stock_output)
        
        self.tabs.addTab(tab, "Inventario")

    def show_low_stock(self):
        products = self.controller.get_low_stock_products(threshold=5)
        
        output = "=== PRODUCTOS CON STOCK BAJO ===\n\n"
        for p in products:
            output += f"{p.name}: {p.stock} unidades\n"
        
        if not products:
            output += "No hay productos con stock bajo."
        
        self.stock_output.setPlainText(output)

    def show_inventory_valuation(self):
        valuation = self.controller.get_inventory_valuation()
        
        output = "=== VALORIZACIÓN DE INVENTARIO ===\n\n"
        output += f"Total Productos: {valuation['total_products']}\n"
        output += f"Total Unidades en Stock: {valuation['total_stock_units']}\n"
        output += f"Valor Total del Inventario: ${valuation['total_value']:,.2f}\n"
        
        self.stock_output.setPlainText(output)

    def closeEvent(self, event):
        event.accept()
