import pandas as pd
import os

def generate_template():
    """
    Generate a simple Excel template for product import.
    Saves to documentos/PLANTILLA_PRODUCTOS.xlsx
    """
    # Create sample data with instructions
    data = {
        'nombre': [
            'Ejemplo: Tornillo 1/2"',
            'Cemento Portland 50kg',
            'Cable eléctrico 2.5mm'
        ],
        'codigo': [
            'TORN-001',
            'CEM-050',
            'CAB-25'
        ],
        'precio': [
            5.50,
            45.00,
            12.75
        ],
        'costo': [
            3.00,
            30.00,
            8.50
        ],
        'stock': [
            100,
            50,
            200
        ],
        'descripcion': [
            'Tornillo hexagonal galvanizado',
            'Cemento para construcción',
            'Cable de cobre calibre 12'
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Create documentos folder if it doesn't exist
    output_dir = 'documentos'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, 'PLANTILLA_PRODUCTOS.xlsx')
    
    # Save to Excel with formatting
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Productos', index=False)
        
        # Get the worksheet
        worksheet = writer.sheets['Productos']
        
        # Set column widths
        worksheet.column_dimensions['A'].width = 30  # nombre
        worksheet.column_dimensions['B'].width = 15  # codigo
        worksheet.column_dimensions['C'].width = 12  # precio
        worksheet.column_dimensions['D'].width = 12  # costo
        worksheet.column_dimensions['E'].width = 10  # stock
        worksheet.column_dimensions['F'].width = 40  # descripcion
    
    print(f"Plantilla creada exitosamente en: {output_file}")
    print("\nColumnas del archivo:")
    print("  - nombre: Nombre del producto (OBLIGATORIO)")
    print("  - codigo: Código o SKU del producto (opcional)")
    print("  - precio: Precio de venta (opcional, por defecto 0)")
    print("  - costo: Precio de costo (opcional, por defecto 0)")
    print("  - stock: Cantidad en inventario (opcional, por defecto 0)")
    print("  - descripcion: Descripción del producto (opcional)")
    print("\nNOTA: Puedes dejar las columnas precio, costo y stock vacías.")
    print("      El sistema las llenará con 0 y podrás editarlas después.")

if __name__ == "__main__":
    generate_template()
