import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtCore import QUrl
from database.db import engine as db_engine, Base, SessionLocal
from bridges.auth_bridge import AuthBridge
from controllers.license_controller import LicenseController


def main():
    # Create database tables
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=db_engine)
    print("Tablas creadas exitosamente.")

    # Initialize Admin User if needed
    from controllers.auth_controller import AuthController
    
    db = SessionLocal()
    try:
        auth = AuthController(db)
        if auth.init_admin():
            print("Usuario admin creado por defecto (admin/admin123)")
    except Exception as e:
        print(f"Error inicializando admin: {e}")
    finally:
        db.close()

    # Create Qt Application
    app = QGuiApplication(sys.argv)
    app.setApplicationName("POS Ultra")
    app.setOrganizationName("POS Ultra")
    
    # Set Material Style
    QQuickStyle.setStyle("Material")
    
    # Create QML Engine
    qml_engine = QQmlApplicationEngine()
    
    # --- LICENSE CHECK ---
    license_ctrl = LicenseController()
    status, msg = license_ctrl.check_status()
    
    if status in ['EXPIRED', 'INVALID']:
        print(f"[!] Licencia {status}: {msg}")
        print("Por favor active el sistema para continuar.")
        # TODO: Implement QML license dialog
        # For now, we'll allow demo mode
    elif status == 'DEMO':
        print(f"[i] Modo Demo Activo: {msg}")
    # ---------------------
    
    # Create Python-QML bridges
    auth_bridge = AuthBridge()
    from bridges.pos_bridge import POSBridge
    pos_bridge = POSBridge()
    from bridges.product_bridge import ProductBridge
    product_bridge = ProductBridge()
    from bridges.pin_auth_bridge import PINAuthBridge
    pin_auth_bridge = PINAuthBridge()
    from bridges.inventory_bridge import InventoryBridge
    inventory_bridge = InventoryBridge()
    from bridges.cash_bridge import CashBridge
    
    # Expose bridges to QML
    qml_engine.rootContext().setContextProperty("authBridge", auth_bridge)
    qml_engine.rootContext().setContextProperty("posBridge", pos_bridge)
    qml_engine.rootContext().setContextProperty("productBridge", product_bridge)
    qml_engine.rootContext().setContextProperty("pinAuthBridge", pin_auth_bridge)
    qml_engine.rootContext().setContextProperty("inventoryBridge", inventory_bridge)

    cash_bridge = CashBridge()
    qml_engine.rootContext().setContextProperty("cashBridge", cash_bridge)

    from bridges.customer_bridge import CustomerBridge
    customer_bridge = CustomerBridge()
    qml_engine.rootContext().setContextProperty("customerBridge", customer_bridge)
    
    # Set QML import paths
    qml_dir = Path(__file__).parent / "qml"
    qml_engine.addImportPath(str(qml_dir))
    
    # Load main QML file
    qml_file = qml_dir / "main.qml"
    qml_engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    if not qml_engine.rootObjects():
        print("[X] Error: No se pudo cargar el archivo QML")
        return -1
    
    print("[OK] Aplicacion QML cargada exitosamente")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
