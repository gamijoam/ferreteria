import sys
import os

# Add current dir to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import src.utils.event_bus...")
    from src.utils.event_bus import event_bus
    print("EventBus imported successfully.")
    
    print("Attempting to import src.controllers.product_controller...")
    from src.controllers.product_controller import ProductController
    print("ProductController imported successfully.")

    print("Attempting to import src.views.product_view...")
    from src.views.product_view import ProductWindow
    print("ProductWindow imported successfully.")

    print("Attempting to import src.main...")
    from src.main import MainWindow
    print("MainWindow imported successfully.")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
