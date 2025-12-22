# Excel Export - Installation Instructions

## Required Libraries

To use the Excel export endpoint (`/api/v1/reports/export/excel`), you need to install two Python libraries:

```bash
pip install pandas openpyxl
```

### What these libraries do:

- **pandas**: Data manipulation and analysis library. Used to create DataFrames and export to Excel.
- **openpyxl**: Library for reading and writing Excel 2010 xlsx/xlsm/xltx/xltm files. Used by pandas to write Excel files.

## Installation Steps

1. **Activate your virtual environment** (if using one):
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

2. **Install the required packages**:
   ```bash
   pip install pandas openpyxl
   ```

3. **Verify installation**:
   ```bash
   pip list | findstr pandas
   pip list | findstr openpyxl
   ```

4. **Restart the backend server**:
   ```bash
   # Stop the current server (Ctrl+C)
   # Then restart
   uvicorn ferreteria_refactor.backend_api.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Testing the Endpoint

Once installed, you can test the endpoint:

**Via Browser:**
```
http://localhost:8000/api/v1/reports/export/excel?start_date=2025-01-01&end_date=2025-12-31
```

**Via curl:**
```bash
curl -O -J "http://localhost:8000/api/v1/reports/export/excel?start_date=2025-01-01&end_date=2025-12-31"
```

**Via Python:**
```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/reports/export/excel",
    params={
        "start_date": "2025-01-01",
        "end_date": "2025-12-31"
    }
)

with open("reporte.xlsx", "wb") as f:
    f.write(response.content)
```

## Excel File Structure

The generated Excel file contains 4 sheets:

1. **Dashboard**: Summary KPIs and Top 5 products
2. **Ventas Detalle**: All sales in the period
3. **Auditoría Cajas**: Cash sessions with discrepancies highlighted (red/green)
4. **Inventario**: Current inventory valuation

## Troubleshooting

**Error: "pandas and openpyxl are required"**
- Make sure you installed both libraries
- Restart the backend server after installation

**Error: "ModuleNotFoundError: No module named 'pandas'"**
- The libraries were installed in a different Python environment
- Make sure you're using the same Python environment as your backend

**Excel file is empty or corrupted**
- Check that there's data in the database for the selected date range
- Try with a wider date range
