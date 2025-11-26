import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QDialog
from src.database.db import engine, Base
from src.views.product_view import ProductWindow
from src.views.inventory_view import InventoryWindow
from src.views.pos_view import POSWindow
from src.views.cash_view import CashWindow
from src.views.login_view import LoginDialog
from src.views.report_view import ReportWindow
from src.views.return_view import ReturnDialog
from src.views.customer_view import CustomerWindow
from src.models.models import UserRole

class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Sistema Ferretería - Usuario: {user.username} ({user.role.value})")
        self.resize(400, 400)
        
        layout = QVBoxLayout()
        
        # Role Based Access Control
        
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

        # Reports: Admin Only
        if user.role == UserRole.ADMIN:
            btn_reports = QPushButton("Módulo 5: Reportes y Seguridad")
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
        self.report_window = ReportWindow()
        self.report_window.show()

    def open_returns(self):
        dialog = ReturnDialog()
        dialog.exec()

    def open_customers(self):
        self.customer_window = CustomerWindow()
        self.customer_window.show()

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
