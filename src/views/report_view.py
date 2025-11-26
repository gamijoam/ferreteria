from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView, QTabWidget, QDateEdit, QPushButton, QFrame
)
from PyQt6.QtCore import QDate
from src.database.db import SessionLocal
from src.controllers.report_controller import ReportController

class ReportWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reportes y Estadísticas - Módulo 5")
        self.resize(800, 600)
        
        self.db = SessionLocal()
        self.controller = ReportController(self.db)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.setup_stock_tab()
        self.setup_sales_tab()

    def setup_stock_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        layout.addWidget(QLabel("Productos con Stock Crítico (<= 5 Unidades)"))
        
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(3)
        self.stock_table.setHorizontalHeaderLabels(["Producto", "SKU", "Stock Actual"])
        self.stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.stock_table)
        
        btn_refresh = QPushButton("Actualizar")
        btn_refresh.clicked.connect(self.load_critical_stock)
        layout.addWidget(btn_refresh)
        
        self.tabs.addTab(tab, "Stock Crítico")
        self.load_critical_stock()

    def setup_sales_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Filters
        filter_layout = QHBoxLayout()
        self.date_start = QDateEdit()
        self.date_start.setDate(QDate.currentDate())
        self.date_start.setCalendarPopup(True)
        
        self.date_end = QDateEdit()
        self.date_end.setDate(QDate.currentDate())
        self.date_end.setCalendarPopup(True)
        
        btn_gen = QPushButton("Generar Reporte")
        btn_gen.clicked.connect(self.load_sales_report)
        
        filter_layout.addWidget(QLabel("Desde:"))
        filter_layout.addWidget(self.date_start)
        filter_layout.addWidget(QLabel("Hasta:"))
        filter_layout.addWidget(self.date_end)
        filter_layout.addWidget(btn_gen)
        layout.addLayout(filter_layout)
        
        # Results
        self.result_frame = QFrame()
        self.result_layout = QVBoxLayout()
        self.result_frame.setLayout(self.result_layout)
        
        self.lbl_revenue = QLabel("Ingresos Totales: $0")
        self.lbl_revenue.setStyleSheet("font-size: 18px; font-weight: bold; color: green;")
        
        self.lbl_tx = QLabel("Transacciones: 0")
        self.lbl_items = QLabel("Items Vendidos: 0")
        
        self.result_layout.addWidget(self.lbl_revenue)
        self.result_layout.addWidget(self.lbl_tx)
        self.result_layout.addWidget(self.lbl_items)
        self.result_layout.addStretch()
        
        layout.addWidget(self.result_frame)
        
        self.tabs.addTab(tab, "Reporte de Ventas")

    def load_critical_stock(self):
        products = self.controller.get_low_stock_products()
        self.stock_table.setRowCount(0)
        for i, p in enumerate(products):
            self.stock_table.insertRow(i)
            self.stock_table.setItem(i, 0, QTableWidgetItem(p.name))
            self.stock_table.setItem(i, 1, QTableWidgetItem(p.sku or ""))
            self.stock_table.setItem(i, 2, QTableWidgetItem(str(p.stock)))

    def load_sales_report(self):
        start = self.date_start.date().toPyDate()
        end = self.date_end.date().toPyDate()
        
        # Convert QDate to datetime for controller
        import datetime
        start_dt = datetime.datetime.combine(start, datetime.time.min)
        end_dt = datetime.datetime.combine(end, datetime.time.max)
        
        data = self.controller.get_sales_report(start_dt, end_dt)
        
        self.lbl_revenue.setText(f"Ingresos Totales: ${data['total_revenue']:,.0f}")
        self.lbl_tx.setText(f"Transacciones: {data['transaction_count']}")
        self.lbl_items.setText(f"Items Vendidos: {data['items_sold']}")

    def closeEvent(self, event):
        self.db.close()
        event.accept()
