"""
Quick Test Script for PySide6 + QML Setup
Tests that all components load correctly
"""
import sys
from pathlib import Path

print("=" * 60)
print("PySide6 + QML Setup Test")
print("=" * 60)
print()

# Test 1: PySide6 Import
print("Test 1: Checking PySide6 installation...")
try:
    from PySide6.QtCore import QObject, Signal, Slot
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine
    print("✅ PySide6 imports successful")
except ImportError as e:
    print(f"❌ PySide6 not installed: {e}")
    print("\nRun: install_pyside6.bat")
    sys.exit(1)

# Test 2: Project Structure
print("\nTest 2: Checking QML directory structure...")
qml_dir = Path("src/qml")
required_dirs = [
    qml_dir,
    qml_dir / "components",
    qml_dir / "views",
    qml_dir / "styles"
]
required_files = [
    qml_dir / "main.qml",
    qml_dir / "components" / "Button.qml",
    qml_dir / "components" / "Card.qml",
    qml_dir / "components" / "TextField.qml",
    qml_dir / "components" / "ModuleCard.qml",
    qml_dir / "views" / "LoginView.qml",
    qml_dir / "views" / "MainView.qml",
    qml_dir / "styles" / "Theme.qml",
    qml_dir / "styles" / "qmldir"
]

all_ok = True
for directory in required_dirs:
    if directory.exists():
        print(f"✅ {directory}")
    else:
        print(f"❌ Missing: {directory}")
        all_ok = False

for file in required_files:
    if file.exists():
        print(f"✅ {file}")
    else:
        print(f"❌ Missing: {file}")
        all_ok = False

if not all_ok:
    print("\n❌ Some files are missing!")
    sys.exit(1)

# Test 3: Python Bridges
print("\nTest 3: Checking Python bridges...")
try:
    from src.bridges.auth_bridge import AuthBridge
    print("✅ AuthBridge import successful")
    
    # Try to instantiate
    bridge = AuthBridge()
    print(f"✅ AuthBridge instantiated")
    print(f"   Business Name: {bridge.businessName}")
    print(f"   Logo Path: {bridge.logoPath if bridge.logoPath else '(none)'}")
except Exception as e:
    print(f"❌ Bridge error: {e}")
    sys.exit(1)

# Test 4: Database
print("\nTest 4: Checking database connection...")
try:
    from src.database.db import SessionLocal, engine
    from src.models.models import User
    
    db = SessionLocal()
    user_count = db.query(User).count()
    db.close()
    
    print(f"✅ Database connection successful")
    print(f"   Users in database: {user_count}")
except Exception as e:
    print(f"❌ Database error: {e}")
    sys.exit(1)

# Test 5: QML Engine Test
print("\nTest 5: Testing QML engine initialization...")
try:
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    # Test context property
    test_obj = QObject()
    engine.rootContext().setContextProperty("testObj", test_obj)
    
    print("✅ QML engine created successfully")
    print("✅ Context properties can be set")
    
    # Don't actually load QML, just test setup
    app.quit()
except Exception as e:
    print(f"❌ QML engine error: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print()
print("You can now run the application:")
print("  python src/main_qml.py")
print()
print("Default login credentials:")
print("  Username: admin")
print("  Password: admin123")
print()
