"""
Test script to verify template generation works
"""
import sys
sys.path.insert(0, 'c:\\Users\\Equipo\\Documents\\ferreteria')

from ferreteria_refactor.backend_api.services.product_export_service import ProductExportService

try:
    print("Generating template...")
    buffer = ProductExportService.generate_template()
    size = len(buffer.getvalue())
    print(f"✅ Success! Template size: {size} bytes")
    
    # Save to file for testing
    with open('test_template.xlsx', 'wb') as f:
        f.write(buffer.getvalue())
    print("✅ Saved to test_template.xlsx")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
