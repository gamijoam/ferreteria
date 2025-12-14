import pandas as pd
from frontend_caja.services.product_service import ProductService

class ExcelImportController:
    """
    Client-Server Excel import controller.
    Parses Excel using Pandas and sends data to Backend API via ProductService.
    """
    
    def __init__(self):
        self.service = ProductService()
    
    def import_products_from_file(self, file_path: str) -> dict:
        """
        Import products from an Excel file.
        Returns dict with keys: success, errors, skipped.
        """
        result = {
            "success": 0,
            "errors": [],
            "skipped": 0
        }
        
        try:
            # Read Excel file
            excel_file = pd.ExcelFile(file_path)
            
            # Find the products sheet
            sheet_name = None
            for name in excel_file.sheet_names:
                if 'product' in name.lower() or 'producto' in name.lower():
                    sheet_name = name
                    break
            
            if not sheet_name:
                result["errors"].append("No se encontró una hoja llamada 'Productos' o 'Products' en el archivo Excel.")
                return result
            
            # Read the sheet
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Normalize column names
            df.columns = df.columns.str.strip().str.lower()
            
            products_to_send = []
            
            # Process each row
            for index, row in df.iterrows():
                row_number = index + 2
                
                try:
                    # Extract fields
                    nombre = self._get_value(row, ['nombre', 'name', 'producto', 'product'])
                    codigo = self._get_value(row, ['codigo', 'sku', 'code'])
                    
                    # Skip empty rows
                    if pd.isna(nombre) and pd.isna(codigo):
                        result["skipped"] += 1
                        continue
                    
                    # Validate required
                    if pd.isna(nombre) or str(nombre).strip() == '':
                        result["errors"].append(f"Fila {row_number}: El nombre es obligatorio")
                        continue
                    
                    # Get optionals
                    precio = self._get_float_value(row, ['precio', 'price', 'precio_venta'], default=0.0)
                    costo = self._get_float_value(row, ['costo', 'cost', 'precio_costo', 'cost_price'], default=0.0)
                    stock = self._get_int_value(row, ['stock', 'cantidad', 'quantity'], default=0)
                    descripcion = self._get_value(row, ['descripcion', 'description', 'desc'])
                    
                    # Prepare dict matching ProductCreate schema
                    product_data = {
                        "name": str(nombre).strip(),
                        "sku": str(codigo).strip() if not pd.isna(codigo) else None,
                        "price": precio,
                        "cost_price": costo,
                        "stock": stock,
                        "description": str(descripcion).strip() if not pd.isna(descripcion) else None,
                        "min_stock": 5.0, # Default defaults
                        "is_box": False,
                        "conversion_factor": 1,
                        "is_active": True
                    }
                    
                    products_to_send.append(product_data)
                    
                except Exception as e:
                    result["errors"].append(f"Fila {row_number}: Error procesando datos locales - {str(e)}")
            
            # Send to API if we have valid products
            if products_to_send:
                try:
                    # chunking (optional, but good for huge files) - sending all now for simplicity
                    api_response = self.service.bulk_create_products(products_to_send)
                    
                    if api_response:
                        result["success"] = api_response.get("success_count", 0)
                        # Add API errors
                        if api_response.get("errors"):
                            result["errors"].extend(api_response["errors"])
                            # Adjust failure count if needed, but errors list acts as count
                    else:
                        result["errors"].append("Error: Sin respuesta del servidor")
                        
                except Exception as e:
                     result["errors"].append(f"Error enviando datos al servidor: {str(e)}")
            
        except FileNotFoundError:
            result["errors"].append(f"No se encontró el archivo: {file_path}")
        except Exception as e:
            result["errors"].append(f"Error al leer el archivo Excel: {str(e)}")
        
        return result

    def _get_value(self, row, possible_names):
        """Get value from row trying multiple column names"""
        for name in possible_names:
            if name in row.index:
                value = row[name]
                if not pd.isna(value):
                    return value
        return None
    
    def _get_float_value(self, row, possible_names, default=0.0):
        value = self._get_value(row, possible_names)
        if value is None or pd.isna(value):
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _get_int_value(self, row, possible_names, default=0):
        value = self._get_value(row, possible_names)
        if value is None or pd.isna(value):
            return default
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return default
