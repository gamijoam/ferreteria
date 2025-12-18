import sys
import os

# Add local path to sys.path to ensure 'src' module can be resolved relative to this script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to 'frontend_caja' so we can import 'src' as a package?
# Actually the code uses 'from src...' which implies `frontend_caja` (the parent of src) should be in PYTHONPATH
sys.path.append(os.path.dirname(current_dir))
# Go up two levels to 'ferreteria_refactor' so we can import 'frontend_caja' as a package
sys.path.append(os.path.dirname(os.path.dirname(current_dir)))

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
    QDialog,
    QFileDialog,
    QMessageBox,
    QGridLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

# DEBUG IMPORT SOURCE
import src
print(f"DEBUG: 'src' module loaded from: {src.__file__}")
# print(f"DEBUG: sys.path: {sys.path}")

from src.database.db import engine, Base, SessionLocal
from src.controllers.excel_import_controller import ExcelImportController
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
from src.views.supplier_view import SupplierWindow
from src.views.purchase_view import PurchaseOrderWindow
from src.views.config_view import ConfigDialog
# Ensure all models are imported so Base metadata is populated
import src.models.models 
from src.models.models import UserRole

# Config Controller (Missing previously)
from src.controllers.config_controller import ConfigController

# Database and other imports
from src.database.db import SessionLocal
from src.views.cash_history_view import CashHistoryWindow
import os

class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        
        # Load business config
        self.db = SessionLocal()
        self.config_controller = ConfigController(self.db)
        self.business_info = self.config_controller.get_business_info()
        
        self.setWindowTitle(f"🏪 {self.business_info['name']} - ERP (v1.0.2)")
        # self.resize(900, 700)
        self.showMaximized()

# ... (skipped lines)



        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #E3F2FD, stop:1 #BBDEFB);
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Header
        header = QWidget()
        header.setStyleSheet("background-color: #1976D2; border-radius: 10px; padding: 20px;")
        header_layout = QVBoxLayout()
        header.setLayout(header_layout)

        # Logo in header
        logo_path = self.config_controller.get_config("business_logo_path", "")
        if logo_path and os.path.exists(logo_path):
            lbl_logo = QLabel()
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(150, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl_logo.setPixmap(scaled_pixmap)
            lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_layout.addWidget(lbl_logo)

        title = QLabel(f"🏪 {self.business_info['name'].upper()}")
        title.setStyleSheet("color: #FFFF00; font-size: 28pt; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)

        role_val = getattr(user.role, 'value', str(user.role))
        user_label = QLabel(f"👤 Usuario: {user.username} | Rol: {role_val}")
        user_label.setStyleSheet("color: white; font-size: 12pt;")
        user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(user_label)

        main_layout.addWidget(header)

        # Dashboard Button (Prominent)
        btn_dashboard = self.create_module_button(
            "📊", "DASHBOARD",
            "Vista general del negocio",
            "#2196F3"
        )
        btn_dashboard.clicked.connect(self.open_dashboard)
        main_layout.addWidget(btn_dashboard)

        # Modules Grid
        grid = QGridLayout()
        grid.setSpacing(15)
        main_layout.addLayout(grid)

        row, col = 0, 0

        # Products & Inventory
        if user.role in [UserRole.ADMIN, UserRole.WAREHOUSE]:
            btn = self.create_module_button("📦", "Productos", "Gestión de productos", "#4CAF50")
            btn.clicked.connect(self.open_products)
            grid.addWidget(btn, row, col)
            col += 1

            btn = self.create_module_button("📥", "Inventario", "Control de stock", "#4CAF50")
            btn.clicked.connect(self.open_inventory)
            grid.addWidget(btn, row, col)
            col += 1
            
            btn = self.create_module_button("🚚", "Proveedores", "Gestión de proveedores", "#4CAF50")
            btn.clicked.connect(self.open_suppliers)
            grid.addWidget(btn, row, col)
            col += 1

            if col >= 4:
                row += 1
                col = 0

        # POS & Cash & Purchases
        if user.role in [UserRole.ADMIN, UserRole.WAREHOUSE]:
            btn = self.create_module_button("🛍️", "Compras", "Órdenes de compra", "#FF9800")
            btn.clicked.connect(self.open_purchases)
            grid.addWidget(btn, row, col)
            col += 1

        if col >= 4:
            row += 1
            col = 0

        if user.role in [UserRole.ADMIN, UserRole.CASHIER]:
            btn = self.create_module_button("🛒", "Punto de Venta", "Ventas rápidas", "#FF9800")
            btn.clicked.connect(self.open_pos)
            grid.addWidget(btn, row, col)
            col += 1

            btn = self.create_module_button("💵", "Caja", "Control de efectivo", "#FF9800")
            btn.clicked.connect(self.open_cash)
            grid.addWidget(btn, row, col)
            col += 1
            
            btn = self.create_module_button("↩️", "Devoluciones", "Gestión de returns", "#F44336")
            btn.clicked.connect(self.open_returns)
            grid.addWidget(btn, row, col)
            col += 1

            btn = self.create_module_button("👥", "Clientes", "Crédito y pagos", "#9C27B0")
            btn.clicked.connect(self.open_customers)
            grid.addWidget(btn, row, col)
            col += 1

            if col >= 4:
                row += 1
                col = 0
            
            btn = self.create_module_button("📝", "Cotizaciones", "Presupuestos", "#9C27B0")
            btn.clicked.connect(self.open_quotes)
            grid.addWidget(btn, row, col)
            col += 1

        # Admin & Management Tools
        if user.role == UserRole.ADMIN:
            btn = self.create_module_button("💰", "Precios", "Mayoristas", "#00BCD4")
            btn.clicked.connect(self.open_price_rules)
            grid.addWidget(btn, row, col)
            col += 1

        if user.role in [UserRole.ADMIN, UserRole.WAREHOUSE]:
            btn = self.create_module_button("🏷️", "Etiquetas", "Impresión", "#607D8B")
            btn.clicked.connect(self.open_labels)
            grid.addWidget(btn, row, col)
            col += 1

        if user.role == UserRole.ADMIN:
            # Add Historial Caja for admin only
            btn = self.create_module_button("📋", "Historial Caja", "Cierres anteriores", "#607D8B")
            btn.clicked.connect(self.open_cash_history)
            grid.addWidget(btn, row, col)
            col += 1

            if col >= 4:
                row += 1
                col = 0

            btn = self.create_module_button("⚙️", "Configuración", "Datos del negocio", "#607D8B")
            btn.clicked.connect(self.open_config)
            grid.addWidget(btn, row, col)
            col += 1

            btn = self.create_module_button("📊", "Reportes", "Análisis avanzado", "#3F51B5")
            btn.clicked.connect(self.open_reports)
            grid.addWidget(btn, row, col)
            col += 1

            btn = self.create_module_button("📄", "Importar Excel", "Cargar productos", "#009688")
            btn.clicked.connect(self.open_excel_import)
            grid.addWidget(btn, row, col)
            col += 1
            
            btn = self.create_module_button("👥", "Usuarios", "Gestión de accesos", "#607D8B")
            btn.clicked.connect(self.open_user_management)
            grid.addWidget(btn, row, col)
            col += 1

        main_layout.addStretch()

        # Footer
        footer = QLabel("Sistema ERP v2.0")
        footer.setStyleSheet("color: #666; font-size: 9pt; padding: 10px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(footer)

    # -----------------------------------------------------------------
    # UI helper methods
    # -----------------------------------------------------------------
    def create_module_button(self, icon, title, subtitle, color):
        """Create a modern card‑style button"""
        btn = QPushButton()
        btn.setMinimumHeight(100)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px;
                text-align: left;
                font-size: 14pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.3)};
            }}
        """)
        btn.setText(f"{icon}  {title}\n{subtitle}")
        return btn

    def darken_color(self, hex_color, factor=0.15):
        """Darken a hex colour by *factor*"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        return f'#{r:02x}{g:02x}{b:02x}'

    # -----------------------------------------------------------------
    # Open window helpers
    # -----------------------------------------------------------------
    def open_config(self):
        dialog = ConfigDialog(self)
        if dialog.exec():
            # Refresh title if changed
            info = self.config_controller.get_business_info()
            self.setWindowTitle(f"🏪 {info['name']} - ERP")
            
            # Find and update title label if possible
            # This is a bit hacky but works for immediate feedback
            for widget in self.findChildren(QLabel):
                if "🏪" in widget.text():
                    widget.setText(f"🏪 {info['name'].upper()}")
                    break

    def open_products(self):
        self.product_window = ProductWindow()
        self.product_window.show()

    def open_inventory(self):
        self.inventory_window = InventoryWindow()
        self.inventory_window.show()

    def open_pos(self):
        if not hasattr(self, 'pos_window') or not self.pos_window.isVisible():
            self.pos_window = POSWindow(user=self.user)
            self.pos_window.show()
        else:
            self.pos_window.raise_()
            self.pos_window.activateWindow()
        return self.pos_window

    def open_cash(self):
        self.cash_window = CashWindow()
        self.cash_window.show()
    def open_cash_history(self):
        self.cash_history_window = CashHistoryWindow()
        self.cash_history_window.show()
    def open_reports(self):
        self.report_window = AdvancedReportWindow()
        self.report_window.show()

    def open_returns(self):
        dialog = ReturnDialog(user=self.user)
        dialog.exec()

    def open_customers(self):
        self.customer_window = CustomerWindow()
        self.customer_window.show()

    def open_price_rules(self):
        self.price_rule_window = PriceRuleWindow()
        self.price_rule_window.show()

    def open_quotes(self):
        self.quote_window = QuoteWindow(main_window=self)
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

    def open_suppliers(self):
        self.supplier_window = SupplierWindow()
        self.supplier_window.show()

    def open_purchases(self):
        self.purchase_window = PurchaseOrderWindow(self.user)
        self.purchase_window.show()

    def open_excel_import(self):
        """Open a dialog to select an Excel file and import products"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Seleccionar archivo Excel de productos", 
            "./documentos",
            "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return
        
        controller = ExcelImportController()
        result = controller.import_products_from_file(file_path)
        
        # Build summary message
        msg = "=== RESUMEN DE IMPORTACION ===\n\n"
        msg += f"Productos importados: {result['success']}\n"
        msg += f"Filas omitidas (vacias): {result['skipped']}\n"
        
        if result['errors']:
            msg += f"\nErrores encontrados: {len(result['errors'])}\n\n"
            # Show first 10 errors
            for error in result['errors'][:10]:
                msg += f"  - {error}\n"
            if len(result['errors']) > 10:
                msg += f"\n  ... y {len(result['errors']) - 10} errores mas\n"
        
        if result['success'] > 0:
            QMessageBox.information(self, "Importacion completada", msg)
        else:
            QMessageBox.warning(self, "Importacion fallida", msg)

    def closeEvent(self, event):
        # Ensure DB session is closed if needed (handled elsewhere)
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # --- DIAGNOSTIC START ---
    from src.database.db import DATABASE_URL, BASE_DIR, env_files
    
    debug_msg = f"Diagnostic Info:\n\n"
    debug_msg += f"BASE_DIR: {BASE_DIR}\n"
    debug_msg += f"DB_URL: {DATABASE_URL}\n"
    
    # Check what env file existed
    found_envs = [p for p in env_files if os.path.exists(p)]
    debug_msg += f"Found .env files: {found_envs}\n"
    
    QMessageBox.information(None, "Startup Diagnostic", debug_msg)
    # --- DIAGNOSTIC END ---

    # Create tables
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas exitosamente.")

    # Initialize Admin User if needed
    # (Admin/Auth logic is handled by Backend API)
    pass
    
    # Remove the second app creation below since we moved it up
    # app = QApplication(sys.argv) <- This needs to be handled carefully as main() had it later.


    # Apply modern theme
    from src.theme import MODERN_THEME
    app.setStyleSheet(MODERN_THEME)

    # --- LICENSE CHECK ---
    from src.controllers.license_controller import LicenseController
    from src.views.license_view import LicenseDialog
    
    license_ctrl = LicenseController()
    status, msg = license_ctrl.check_status()
    
    if status in ['EXPIRED', 'INVALID']:
        # Show activation dialog
        dialog = LicenseDialog(license_ctrl, status, msg)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            sys.exit(0)
    elif status == 'DEMO':
        # Optional: Show demo reminder toast or just log it
        print(f"Modo Demo Activo: {msg}")
    # ---------------------

    # Show Login First
    login = LoginDialog()
    
    if login.exec() == QDialog.DialogCode.Accepted:
        try:
            window = MainWindow(login.user)
            window.show()
            sys.exit(app.exec())
        except Exception as e:
            import traceback
            traceback.print_exc()
            try:
                QMessageBox.critical(None, "Error Fatal", f"Error al iniciar ventana principal:\n{str(e)}")
            except:
                pass
            sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
