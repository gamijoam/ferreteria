import pandas as pd
from src.database.db import SessionLocal
from src.models.models import Product
from sqlalchemy.exc import IntegrityError

class ExcelImportController:
    """
    Simple and robust Excel import controller for products.
    
    Expected Excel format:
    - Single file with a sheet named "Productos" or "Products"
    - Columns: nombre, codigo, precio, costo, stock, descripcion
    - Optional columns can be empty
    """
    
    def __init__(self):
        self.db = SessionLocal()
    
    def import_products_from_file(self, file_path: str) -> dict:
        """
        Import products from an Excel file.
        
        Returns:
            dict with keys:
                - success: int (number of products imported)
                - errors: list of error messages
                - skipped: int (number of rows skipped)
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
            
            # Normalize column names (remove spaces, lowercase)
            df.columns = df.columns.str.strip().str.lower()
            
            # Process each row
            for index, row in df.iterrows():
                row_number = index + 2  # +2 because Excel is 1-indexed and has header
                
                try:
                    # Extract and validate required fields
                    nombre = self._get_value(row, ['nombre', 'name', 'producto', 'product'])
                    codigo = self._get_value(row, ['codigo', 'sku', 'code'])
                    
                    # Skip empty rows
                    if pd.isna(nombre) and pd.isna(codigo):
                        result["skipped"] += 1
                        continue
                    
                    # Validate required fields
                    if pd.isna(nombre) or str(nombre).strip() == '':
                        result["errors"].append(f"Fila {row_number}: El nombre es obligatorio")
                        continue
                    
                    # Extract optional fields with defaults
                    precio = self._get_float_value(row, ['precio', 'price', 'precio_venta'], default=0.0)
                    costo = self._get_float_value(row, ['costo', 'cost', 'precio_costo', 'cost_price'], default=0.0)
                    stock = self._get_int_value(row, ['stock', 'cantidad', 'quantity'], default=0)
                    descripcion = self._get_value(row, ['descripcion', 'description', 'desc'])
                    
                    # Create product
                    product = Product(
                        name=str(nombre).strip(),
                        sku=str(codigo).strip() if not pd.isna(codigo) else None,
                        price=precio,
                        cost_price=costo,
                        stock=stock,
                        description=str(descripcion).strip() if not pd.isna(descripcion) else None,
                        is_active=True
                    )
                    
                    self.db.add(product)
                    result["success"] += 1
                    
                except IntegrityError as e:
                    self.db.rollback()
                    if 'sku' in str(e).lower():
                        result["errors"].append(f"Fila {row_number}: El código '{codigo}' ya existe en la base de datos")
                    else:
                        result["errors"].append(f"Fila {row_number}: Error de integridad - {str(e)}")
                except Exception as e:
                    self.db.rollback()
                    result["errors"].append(f"Fila {row_number}: {str(e)}")
            
            # Commit all successful imports
            if result["success"] > 0:
                try:
                    self.db.commit()
                except Exception as e:
                    self.db.rollback()
                    result["errors"].append(f"Error al guardar en la base de datos: {str(e)}")
                    result["success"] = 0
            
        except FileNotFoundError:
            result["errors"].append(f"No se encontró el archivo: {file_path}")
        except Exception as e:
            result["errors"].append(f"Error al leer el archivo Excel: {str(e)}")
        finally:
            self.db.close()
        
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
        """Get float value from row, return default if not found or invalid"""
        value = self._get_value(row, possible_names)
        if value is None or pd.isna(value):
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _get_int_value(self, row, possible_names, default=0):
        """Get integer value from row, return default if not found or invalid"""
        value = self._get_value(row, possible_names)
        if value is None or pd.isna(value):
            return default
        try:
            return int(float(value))  # Convert through float to handle "10.0"
        except (ValueError, TypeError):
            return default
