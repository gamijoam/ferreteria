from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QGridLayout, QFrame
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from src.database.db import SessionLocal
from src.controllers.report_controller import ReportController
from src.controllers.profit_controller import ProfitController
from src.models.models import Quote, Sale
import datetime

class DashboardWindow(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.setWindowTitle("Dashboard Ejecutivo - Módulo 13")
        self.resize(1200, 750)
        
        self.db = SessionLocal()
        self.controller = ReportController(self.db)
        self.profit_controller = ProfitController(self.db)
        self.main_window = main_window  # Reference to open other modules
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Title
        title = QLabel("📊 DASHBOARD EJECUTIVO")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)
        
        # Metrics Grid
        metrics_layout = QGridLayout()
        self.layout.addLayout(metrics_layout)
        
        # Today's Sales
        self.sales_widget = self.create_metric_widget(
            "💰 Ventas del Día",
            "$0",
            "0 transacciones"
        )
        metrics_layout.addWidget(self.sales_widget, 0, 0)
        
        # Stock Alerts
        self.stock_widget = self.create_metric_widget(
            "⚠️ Alertas de Stock",
            "0",
            "productos bajo stock"
        )
        metrics_layout.addWidget(self.stock_widget, 0, 1)
        
        # Pending Quotes
        self.quotes_widget = self.create_metric_widget(
            "📋 Cotizaciones Pendientes",
            "0",
            "sin convertir"
        )
        metrics_layout.addWidget(self.quotes_widget, 1, 0)
        
        # Customer Debt
        self.debt_widget = self.create_metric_widget(
            "💳 Deuda Total Clientes",
            "$0",
            "por cobrar"
        )
        metrics_layout.addWidget(self.debt_widget, 1, 1)
        
        # Inventory Value
        self.inventory_widget = self.create_metric_widget(
            "📦 Valor Inventario",
            "$0",
            "en stock"
        )
        metrics_layout.addWidget(self.inventory_widget, 2, 0)
        
        # Average Ticket
        self.ticket_widget = self.create_metric_widget(
            "🎫 Ticket Promedio",
            "$0",
            "últimos 7 días"
        )
        metrics_layout.addWidget(self.ticket_widget, 2, 1)
        
        # Month Profit (NEW)
        self.profit_widget = self.create_metric_widget(
            "💰 Ganancia del Mes",
            "$0",
            "margen: 0%"
        )
        metrics_layout.addWidget(self.profit_widget, 3, 0, 1, 2)  # Span 2 columns
        
        # Refresh Button
        btn_refresh = QPushButton("🔄 Actualizar Dashboard")
        btn_refresh.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        btn_refresh.setStyleSheet("background-color: #4CAF50; color: white; padding: 15px;")
        btn_refresh.clicked.connect(self.refresh_dashboard)
        self.layout.addWidget(btn_refresh)
        
        # Quick Actions
        self.layout.addWidget(QLabel("Accesos Rápidos:"))
        quick_actions = QHBoxLayout()
        
        if main_window:
            btn_pos = QPushButton("🛒 Abrir POS")
            btn_pos.clicked.connect(lambda: main_window.open_pos())
            quick_actions.addWidget(btn_pos)
            
            btn_cash = QPushButton("💵 Abrir Caja")
            btn_cash.clicked.connect(lambda: main_window.open_cash())
            quick_actions.addWidget(btn_cash)
            
            btn_reports = QPushButton("📊 Ver Reportes")
            btn_reports.clicked.connect(lambda: main_window.open_reports())
            quick_actions.addWidget(btn_reports)
        
        self.layout.addLayout(quick_actions)
        
        # Initial load
        self.refresh_dashboard()

    def create_metric_widget(self, title, value, subtitle):
        """Create a metric display widget"""
        widget = QGroupBox(title)
        widget.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("color: #2196F3;")
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #666;")
        
        layout.addWidget(value_label)
        layout.addWidget(subtitle_label)
        widget.setLayout(layout)
        
        # Store labels for updating
        widget.value_label = value_label
        widget.subtitle_label = subtitle_label
        
        return widget

    def refresh_dashboard(self):
        """Refresh all dashboard metrics"""
        today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_end = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
        
        # Get current exchange rate
        from src.controllers.config_controller import ConfigController
        config_ctrl = ConfigController(self.db)
        rate = config_ctrl.get_exchange_rate()
        
        # 1. Today's Sales
        summary = self.controller.get_sales_summary(today_start, today_end)
        self.sales_widget.value_label.setText(f"${summary['total_revenue']:,.2f}\nBs {summary['total_revenue_bs']:,.2f}")
        self.sales_widget.subtitle_label.setText(f"{summary['total_transactions']} transacciones")
        
        # 2. Stock Alerts
        low_stock = self.controller.get_low_stock_products(threshold=5)
        self.stock_widget.value_label.setText(str(len(low_stock)))
        self.stock_widget.subtitle_label.setText("productos bajo stock")
        if len(low_stock) > 0:
            self.stock_widget.value_label.setStyleSheet("color: red;")
        else:
            self.stock_widget.value_label.setStyleSheet("color: green;")
        
        # 3. Pending Quotes
        pending_quotes = self.db.query(Quote).filter(Quote.status == "PENDING").count()
        self.quotes_widget.value_label.setText(str(pending_quotes))
        self.quotes_widget.subtitle_label.setText("sin convertir")
        
        # 4. Customer Debt
        debt_report = self.controller.get_customer_debt_report()
        total_debt = sum(item['debt'] for item in debt_report)
        total_debt_bs = total_debt * rate
        self.debt_widget.value_label.setText(f"${total_debt:,.2f}\nBs {total_debt_bs:,.2f}")
        self.debt_widget.subtitle_label.setText(f"{len(debt_report)} clientes")
        
        # 5. Inventory Value
        valuation = self.controller.get_inventory_valuation(exchange_rate=rate)
        self.inventory_widget.value_label.setText(f"${valuation['total_value']:,.2f}\nBs {valuation['total_value_bs']:,.2f}")
        self.inventory_widget.subtitle_label.setText(f"{valuation['total_products']} productos")
        
        # 6. Average Ticket (last 7 days)
        week_start = datetime.datetime.now() - datetime.timedelta(days=7)
        week_summary = self.controller.get_sales_summary(week_start, today_end)
        self.ticket_widget.value_label.setText(f"${week_summary['average_ticket']:,.2f}")
        self.ticket_widget.subtitle_label.setText("últimos 7 días")
        
        # 7. Month Profitability (NEW)
        try:
            month_profit = self.profit_controller.get_month_profitability()
            profit_bs = month_profit['total_profit'] * rate
            self.profit_widget.value_label.setText(f"${month_profit['total_profit']:,.2f}\nBs {profit_bs:,.2f}")
            self.profit_widget.subtitle_label.setText(f"Margen: {month_profit['avg_margin']:.1f}%")
            if month_profit['total_profit'] < 0:
                self.profit_widget.value_label.setStyleSheet("color: red;")
            else:
                self.profit_widget.value_label.setStyleSheet("color: green;")
        except:
            self.profit_widget.value_label.setText("$0.00")
            self.profit_widget.subtitle_label.setText("sin datos")

    def closeEvent(self, event):
        self.db.close()
        event.accept()
