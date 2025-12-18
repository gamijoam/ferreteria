import requests
import datetime
import random

class APIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def login(self, username, password):
        """
        Intenta loguearse contra la API.
        Retorna el token si es exitoso, o None si falla.
        """
        try:
            # Endpoint correcto segun backend: POST /api/v1/token
            url = f"{self.base_url}/api/v1/token"
            
            # OAuth2PasswordRequestForm espera form-data, no JSON
            data = {
                "username": username,
                "password": password
            }
            
            # headers no son necesarios para form-data simple en requests, lo maneja auto
            response = requests.post(url, data=data, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("access_token")
            else:
                print(f"Login failed: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")
            return None

    def get_sales_summary(self, token):
        """
        Obtiene resumen de ventas.
        """
        headers = {"Authorization": f"Bearer {token}"}
        try:
            # Necesitamos pasar fechas para el endpoint de reporte
            today = datetime.date.today()
            params = {
                "start_date": today.isoformat(),
                "end_date": today.isoformat()
            }
            # Endpoint correcto: /api/v1/reports/sales/summary
            response = requests.get(f"{self.base_url}/api/v1/reports/sales/summary", headers=headers, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # El dashboard espera claves especificas, mapeamos la respuesta de la API
                return {
                    "daily_sales": data.get("total_revenue", 0),
                    "transactions": data.get("total_transactions", 0),
                    "avg_margin": 30.0 # Este dato no viene en sales/summary, se podria sacar de profit/sales
                }
        except Exception as e:
            print(f"Error fetching summary: {e}")
            pass
        
        # Datos Simulados (Fallback)
        return {
            "daily_sales": 15430.50,
            "transactions": 45,
            "avg_margin": 32.5
        }

    def get_low_stock_products(self, token):
        """
        Obtiene productos con bajo stock.
        """
        headers = {"Authorization": f"Bearer {token}"}
        try:
            # Endpoint correcto: /api/v1/reports/low-stock (threshold default=5)
            response = requests.get(f"{self.base_url}/api/v1/reports/low-stock", headers=headers, timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
            
        # Datos Simulados
        return [
            {"id": 101, "name": "Martillo", "stock": 2, "min_stock": 5},
            {"id": 204, "name": "Clavos 2in", "stock": 0, "min_stock": 100},
            {"id": 305, "name": "Cinta Aislante", "stock": 4, "min_stock": 10}
        ]

    def get_hourly_sales(self, token):
        """
        Genera datos para el gráfico de barras.
        """
        # Simulamos datos horarios ya que la API actual no devuelve desglose por hora facil
        hours = [f"{h:02d}:00" for h in range(8, 19)] # 8am a 6pm
        sales = [random.randint(500, 3000) for _ in range(len(hours))]
        return {"hours": hours, "sales": sales}

    def get_detailed_sales(self, token, start_date, end_date):
        """
        Obtiene reporte detallado de ventas.
        """
        headers = {"Authorization": f"Bearer {token}"}
        try:
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            # Endpoint correcto: /api/v1/reports/sales/detailed
            response = requests.get(f"{self.base_url}/api/v1/reports/sales/detailed", headers=headers, params=params, timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return []

    def get_products(self, token):
        """
        Obtiene lista completa de productos.
        """
        headers = {"Authorization": f"Bearer {token}"}
        try:
            # Endpoint correcto: /api/v1/products/
            response = requests.get(f"{self.base_url}/api/v1/products/", headers=headers, params={"limit": 1000}, timeout=10)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return []
