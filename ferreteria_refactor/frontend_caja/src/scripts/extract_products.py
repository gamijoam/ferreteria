import pandas as pd
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def extract_and_merge_products():
    print("="*60)
    print("EXTRACTOR DE PRODUCTOS DESDE EXCEL")
    print("="*60)
    
    docu_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "docu")
    output_file = os.path.join(docu_dir, "PLANTILLA_PRODUCTOS_IMPORTAR.xlsx")
    
    all_products = []
    
    # Files to process
    files = [
        "0a6bc3f9-32f7-4569-877f-9548daa8e002.xls",
        "LISTA DE PRECIOS LA OFERTA 19-11-2025 DISPONIBLES.xlsx"
    ]
    
    for filename in files:
        file_path = os.path.join(docu_dir, filename)
        if not os.path.exists(file_path):
            print(f"⚠️ Archivo no encontrado: {filename}")
            continue
            
        print(f"\nProcesando: {filename}...")
        
        try:
            # 1. Detect Header Row dynamically
            # Read first 20 rows to find where the headers are
            df_preview = pd.read_excel(file_path, header=None, nrows=20)
            
            header_row_idx = None
            for idx, row in df_preview.iterrows():
                row_str = str(row.values).lower()
                # Look for keywords in the row
                if ('descrip' in row_str or 'nombre' in row_str) and ('costo' in row_str or 'precio' in row_str):
                    header_row_idx = idx
                    break
            
            if header_row_idx is None:
                print(f"  ⚠️ No se encontró fila de encabezados en las primeras 20 filas. Intentando lectura estándar...")
                header_row_idx = 0

            print(f"  ℹ️ Encabezados detectados en la fila: {header_row_idx + 1}")

            # 2. Read full file with correct header
            df = pd.read_excel(file_path, header=header_row_idx)
            
            # Normalize column names (lowercase, strip)
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            print(f"  Columnas encontradas: {list(df.columns)}")
            
            # Identify columns
            name_col = next((c for c in df.columns if 'descrip' in c or 'nombre' in c or 'producto' in c), None)
            sku_col = next((c for c in df.columns if 'sku' in c or 'codigo' in c or 'código' in c), None)
            cost_col = next((c for c in df.columns if 'costo' in c or 'precio' in c or 'valor' in c), None)
            
            if not name_col or not cost_col:
                print(f"  ❌ No se pudieron identificar columnas clave (Nombre/Costo) en {filename}")
                continue
                
            print(f"  Mapeo: Nombre='{name_col}', SKU='{sku_col}', Costo='{cost_col}'")
            
            # Extract data
            count = 0
            current_category = "General" # Default category
            
            for _, row in df.iterrows():
                name = str(row[name_col]).strip()
                if not name or name.lower() == 'nan':
                    continue
                
                # Check if it's a category header row
                # Logic: Has name but NO price and NO SKU (or very short/invalid)
                try:
                    cost_val = row[cost_col]
                    has_cost = pd.notna(cost_val) and float(cost_val) > 0
                except:
                    has_cost = False
                    
                sku_val = str(row[sku_col]).strip() if sku_col and pd.notna(row[sku_col]) else ""
                has_sku = len(sku_val) > 2
                
                # If it looks like a header (Name exists, but no cost/sku)
                if not has_cost and not has_sku:
                    # It's likely a category header
                    current_category = name.upper().replace("---", "").strip()
                    # print(f"    📂 Nueva Categoría detectada: {current_category}")
                    continue

                # It's a product
                sku = sku_val
                if sku.lower() == 'nan': sku = ""
                
                # Auto-generate SKU if missing to avoid unique constraint errors
                if not sku:
                    sku = f"GEN-{count+1:04d}"
                
                try:
                    cost = float(row[cost_col])
                except:
                    cost = 0.0
                    
                all_products.append({
                    "Nombre": name,
                    "Código (SKU)": sku,
                    "Categoría": current_category, # Use detected category
                    "Precio Costo ($)": cost,
                    "Precio Venta ($)": cost * 1.3, # Default 30% margin
                    "Stock Actual": 0,
                    "Stock Mínimo": 5
                })
                count += 1
                
            print(f"  ✅ {count} productos extraídos.")
            
        except Exception as e:
            print(f"  ❌ Error procesando archivo: {e}")

    if not all_products:
        print("\n❌ No se extrajeron productos.")
        return
        
    # Create DataFrame for template
    print(f"\nGenerando plantilla con {len(all_products)} productos...")
    template_df = pd.DataFrame(all_products)
    
    # Reorder columns to match expected template format
    expected_columns = [
        "Nombre", "Código (SKU)", "Categoría", "Precio Costo ($)", 
        "Precio Venta ($)", "Stock Actual", "Stock Mínimo"
    ]
    
    # Ensure all columns exist
    for col in expected_columns:
        if col not in template_df.columns:
            template_df[col] = ""
            
    template_df = template_df[expected_columns]
    
    # Save to Excel
    try:
        template_df.to_excel(output_file, index=False)
        print(f"\n✅ Archivo generado exitosamente:\n{output_file}")
    except Exception as e:
        print(f"\n❌ Error guardando archivo: {e}")

if __name__ == "__main__":
    extract_and_merge_products()
