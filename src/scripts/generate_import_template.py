import pandas as pd
import os

# Define the folder where the template will be saved (project root / documentos)
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'documentos'))
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'template_import.xlsx')

# --- Sheet: Products ---
products_columns = [
    'name',          # Nombre del producto (string, obligatorio)
    'sku',           # Código SKU (string, opcional)
    'price',         # Precio de venta (float, obligatorio)
    'cost_price',    # Precio de costo (float, opcional, default 0)
    'stock',         # Stock inicial (int, opcional, default 0)
    'is_box',        # Es caja/pack? (bool, opcional, default False)
    'conversion_factor', # Unidades por caja (int, opcional, default 1)
    'unit_type',     # Tipo de unidad (string, ej. "Unidad", "Metro", "Kilo", "Litro")
    'category',      # Nombre de la categoría (string, opcional)
    'supplier'       # Nombre del proveedor (string, opcional)
]
products_df = pd.DataFrame(columns=products_columns)

# --- Sheet: Suppliers ---
suppliers_columns = [
    'name',            # Nombre del proveedor (string, obligatorio)
    'contact_person',  # Persona de contacto (string, opcional)
    'phone',           # Teléfono (string, opcional)
    'email',           # Email (string, opcional)
    'address',         # Dirección (string, opcional)
    'notes',           # Notas (string, opcional)
    'is_active'        # Activo? (bool, opcional, default True)
]
suppliers_df = pd.DataFrame(columns=suppliers_columns)

# --- Sheet: Categories ---
categories_columns = [
    'name',        # Nombre de la categoría (string, obligatorio)
    'description'  # Descripción (string, opcional)
]
categories_df = pd.DataFrame(columns=categories_columns)

# --- Sheet: Customers ---
customers_columns = [
    'name',    # Nombre del cliente (string, obligatorio)
    'phone',   # Teléfono (string, opcional)
    'address'  # Dirección (string, opcional)
]
customers_df = pd.DataFrame(columns=customers_columns)

# Write all sheets to a single Excel file
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    products_df.to_excel(writer, sheet_name='Products', index=False)
    suppliers_df.to_excel(writer, sheet_name='Suppliers', index=False)
    categories_df.to_excel(writer, sheet_name='Categories', index=False)
    customers_df.to_excel(writer, sheet_name='Customers', index=False)

print(f"Plantilla de importación creada en: {output_path}")
