import os
import pandas as pd
from src.database.db import SessionLocal
from src.models.models import Product, Supplier, Category, Customer
from sqlalchemy.exc import IntegrityError

class ExcelImportController:
    """Controller to import Excel files from a folder into the database.
    
    Expected file naming conventions (case‑insensitive):
    - *products*.xlsx  → imports rows into the Product table
    - *suppliers*.xlsx → imports rows into the Supplier table
    - *categories*.xlsx → imports rows into the Category table
    - *customers*.xlsx → imports rows into the Customer table
    
    The Excel columns should match the model fields (or a subset). Missing
    optional columns are ignored. The function is tolerant to extra columns.
    """
    def __init__(self):
        self.db = SessionLocal()

    def import_folder(self, folder_path: str) -> dict:
        """Import all supported Excel files from *folder_path*.
        Returns a dict with summary of imported rows and any errors.
        """
        summary = {
            "products": 0,
            "suppliers": 0,
            "categories": 0,
            "customers": 0,
            "errors": []
        }
        if not os.path.isdir(folder_path):
            summary["errors"].append(f"Folder not found: {folder_path}")
            return summary
        
        for filename in os.listdir(folder_path):
            if not filename.lower().endswith('.xlsx'):
                continue
            file_path = os.path.join(folder_path, filename)
            try:
                # Read all sheets from the Excel file
                xls = pd.read_excel(file_path, sheet_name=None)
            except Exception as e:
                summary["errors"].append(f"Failed to read {filename}: {e}")
                continue
            
            # Iterate through each sheet in the Excel file
            for sheet_name, df in xls.items():
                lowered_sheet_name = sheet_name.lower()
                # Use a more descriptive name for error reporting
                source_name = f"{filename} (sheet: {sheet_name})"

                if 'product' in lowered_sheet_name:
                    summary["products"] += self._import_products(df, source_name, summary)
                elif 'supplier' in lowered_sheet_name:
                    summary["suppliers"] += self._import_suppliers(df, source_name, summary)
                elif 'category' in lowered_sheet_name:
                    summary["categories"] += self._import_categories(df, source_name, summary)
                elif 'customer' in lowered_sheet_name:
                    summary["customers"] += self._import_customers(df, source_name, summary)
                else:
                    summary["errors"].append(f"Unrecognized sheet type in {source_name}")
        
        self.db.commit()
        self.db.close()
        return summary

    # ---------------------------------------------------------------------
    # Individual import helpers
    # ---------------------------------------------------------------------
    def _import_products(self, df, filename, summary):
        count = 0
        for _, row in df.iterrows():
            try:
                prod = Product(
                    name=row.get('name') or row.get('nombre'),
                    sku=row.get('sku') or row.get('codigo'),
                    price=float(row.get('price') or row.get('precio') or 0),
                    cost_price=float(row.get('cost_price') or row.get('costo') or 0),
                    stock=int(row.get('stock') or 0),
                    is_box=bool(row.get('is_box') or False),
                    conversion_factor=int(row.get('conversion_factor') or 1),
                    unit_type=row.get('unit_type') or 'Unidad',
                    category_id=self._lookup_category_id(row.get('category')),
                    supplier_id=self._lookup_supplier_id(row.get('supplier')),
                )
                self.db.add(prod)
                count += 1
            except Exception as e:
                summary["errors"].append(f"Product row error in {filename}: {e}")
        return count

    def _import_suppliers(self, df, filename, summary):
        count = 0
        for _, row in df.iterrows():
            try:
                sup = Supplier(
                    name=row.get('name') or row.get('nombre'),
                    contact_person=row.get('contact_person') or row.get('contacto'),
                    phone=row.get('phone') or row.get('telefono'),
                    email=row.get('email'),
                    address=row.get('address') or row.get('direccion'),
                    notes=row.get('notes') or row.get('notas'),
                    is_active=bool(row.get('is_active', True)),
                )
                self.db.add(sup)
                count += 1
            except Exception as e:
                summary["errors"].append(f"Supplier row error in {filename}: {e}")
        return count

    def _import_categories(self, df, filename, summary):
        count = 0
        for _, row in df.iterrows():
            try:
                cat = Category(
                    name=row.get('name') or row.get('nombre'),
                    description=row.get('description') or row.get('descripcion')
                )
                self.db.add(cat)
                count += 1
            except Exception as e:
                summary["errors"].append(f"Category row error in {filename}: {e}")
        return count

    def _import_customers(self, df, filename, summary):
        count = 0
        for _, row in df.iterrows():
            try:
                cust = Customer(
                    name=row.get('name') or row.get('nombre'),
                    phone=row.get('phone') or row.get('telefono'),
                    address=row.get('address') or row.get('direccion')
                )
                self.db.add(cust)
                count += 1
            except Exception as e:
                summary["errors"].append(f"Customer row error in {filename}: {e}")
        return count

    # ---------------------------------------------------------------------
    # Helper look‑ups (simple name → id queries)
    # ---------------------------------------------------------------------
    def _lookup_category_id(self, name):
        if not name:
            return None
        cat = self.db.query(Category).filter(Category.name == name).first()
        return cat.id if cat else None

    def _lookup_supplier_id(self, name):
        if not name:
            return None
        sup = self.db.query(Supplier).filter(Supplier.name == name).first()
        return sup.id if sup else None
