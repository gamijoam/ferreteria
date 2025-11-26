import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QDialog
from src.database.db import engine, Base
from src.views.product_view import ProductWindow
from src.views.inventory_view import InventoryWindow
from src.views.pos_view import POSWindow
from src.views.cash_view import CashWindow
from src.views.login_view import LoginDialog
from src.views.advanced_report_view import AdvancedReportWindow
from src.views.return_view import ReturnDialog
from src.views.price_rule_view import PriceRuleWindow
from src.views.quote_view import QuoteWindow
from src.views.label_view import LabelWindow
from src.views.user_management_view import UserManagementWindow
from src.views.dashboard_view import DashboardWindow
from src.views.customer_view import CustomerWindow
from src.models.models import UserRole

class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Sistema Ferretería - Usuario: {user.username} ({user.role.value})")
        self.resize(400, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Dashboard (All roles)
        btn_dashboard = QPushButton("📊 DASHBOARD")
        btn_dashboard.setStyleSheet("background-color: #2196F3; color: white; padding: 15px; font-size: 16px; font-weight: bold;")
        btn_dashboard.clicked.connect(self.open_dashboard)
        layout.addWidget(btn_dashboard)
        
        layout.addWidget(QLabel("---"))
        
        # Products: Admin & Warehouse
        if user.role in [UserRole.ADMIN, UserRole.WAREHOUSE]:
            btn_products = QPushButton("Módulo 1: Productos")
            btn_products.clicked.connect(self.open_products)
            layout.addWidget(btn_products)
        
        # Inventory: Admin & Warehouse
        if user.role in [UserRole.ADMIN, UserRole.WAREHOUSE]:
            btn_inventory = QPushButton("Módulo 2: Inventario (Bodega)")
            btn_inventory.clicked.connect(self.open_inventory)
            layout.addWidget(btn_inventory)
        
        # POS: Admin & Cashier
        if user.role in [UserRole.ADMIN, UserRole.CASHIER]:
            btn_pos = QPushButton("Módulo 3: Punto de Venta (POS)")
            btn_pos.clicked.connect(self.open_pos)
            layout.addWidget(btn_pos)
        
        # Cash: Admin & Cashier
        if user.role in [UserRole.ADMIN, UserRole.CASHIER]:
            btn_cash = QPushButton("Módulo 4: Caja y Finanzas")
            btn_cash.clicked.connect(self.open_cash)
            layout.addWidget(btn_cash)

        # Returns: Admin & Cashier (Usually requires auth, but for now open to both)
        if user.role in [UserRole.ADMIN, UserRole.CASHIER]:
            btn_returns = QPushButton("Módulo 6: Devoluciones")
            btn_returns.clicked.connect(self.open_returns)
            layout.addWidget(btn_returns)

        # Customers: Admin & Cashier
        if user.role in [UserRole.ADMIN, UserRole.CASHIER]:
            btn_customers = QPushButton("Módulo 7: Clientes y Crédito")
            btn_customers.clicked.connect(self.open_customers)
            layout.addWidget(btn_customers)

        # Price Rules: Admin Only
        if user.role == UserRole.ADMIN:
            btn_prices = QPushButton("Módulo 8: Precios Mayoristas")
            btn_prices.clicked.connect(self.open_price_rules)
            layout.addWidget(btn_prices)

        # Quotes: Admin & Cashier
        if user.role in [UserRole.ADMIN, UserRole.CASHIER]:
            btn_quotes = QPushButton("Módulo 9: Cotizaciones")
            btn_quotes.clicked.connect(self.open_quotes)
            layout.addWidget(btn_quotes)

        # Labels: Admin & Warehouse
        if user.role in [UserRole.ADMIN, UserRole.WAREHOUSE]:
            btn_labels = QPushButton("Módulo 10: Etiquetas")
            btn_labels.clicked.connect(self.open_labels)
            layout.addWidget(btn_labels)

        # User Management: Admin Only
        if user.role == UserRole.ADMIN:
            btn_users = QPushButton("Módulo 11: Gestión de Usuarios")
            btn_users.clicked.connect(self.open_user_management)
            layout.addWidget(btn_users)

        # Reports: Admin Only
        if user.role == UserRole.ADMIN:
            btn_reports = QPushButton("Módulo 12: Reportes Avanzados")
            btn_reports.clicked.connect(self.open_reports)
            layout.addWidget(btn_reports)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_products(self):
        self.product_window = ProductWindow()
        self.product_window.show()

    def open_inventory(self):
        self.inventory_window = InventoryWindow()
        self.inventory_window.show()

    def open_pos(self):
        self.pos_window = POSWindow()
        self.pos_window.show()

    def open_cash(self):
        self.cash_window = CashWindow()
        self.cash_window.show()

    def open_reports(self):
        self.report_window = AdvancedReportWindow()
        self.report_window.show()

    def open_returns(self):
        dialog = ReturnDialog()
        dialog.exec()

    def open_customers(self):
        self.customer_window = CustomerWindow()
        self.customer_window.show()

    def open_price_rules(self):
        self.price_rule_window = PriceRuleWindow()
        self.price_rule_window.show()

    def open_quotes(self):
        # Pass POS reference if open
        pos_ref = getattr(self, 'pos_window', None)
        self.quote_window = QuoteWindow(pos_window=pos_ref)
        self.quote_window.show()

    def open_labels(self):
        self.label_window = LabelWindow()
        self.label_window.show()

    def open_user_management(self):
        self.user_mgmt_window = UserManagementWindow()
        self.user_mgmt_window.show()

    def open_dashboard(self):
        self.dashboard_window = DashboardWindow(main_window=self)
        self.dashboard_window.show()

def main():
    # Create tables
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas exitosamente.")

    app = QApplication(sys.argv)
    
    # Show Login First
    login = LoginDialog()
    if login.exec() == QDialog.DialogCode.Accepted:
        window = MainWindow(login.user)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
