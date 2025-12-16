import sys
import os

# Set up path to include project root AND refactor dir AND frontend_caja
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'ferreteria_refactor'))
sys.path.append(os.path.join(os.getcwd(), 'ferreteria_refactor', 'frontend_caja'))

from ferreteria_refactor.frontend_caja.services.api_client import APIClient
from ferreteria_refactor.frontend_caja.config import API_BASE_URL

print(f"--- DIAGNÓSTICO DE API FRONTEND ---")
print(f"API_BASE_URL: {API_BASE_URL}")

client = APIClient()
endpoint = "/api/v1/config/currencies"

print(f"\nIntentando GET {endpoint}...")
try:
    # Use internal make_url to see real URL
    real_url = client._make_url(endpoint)
    print(f"URL Real: {real_url}")
    
    response = client.get(endpoint)
    
    print(f"\nRespuesta ({type(response)}):")
    print(response)
    
    if isinstance(response, list):
        print(f"[EXITO] Recibida lista con {len(response)} elementos.")
    elif response is None:
        print("[ERROR] La respuesta fue None (Fallo en APIClient).")
    else:
        print(f"[ADVERTENCIA] Tipo inesperado.")

except Exception as e:
    print(f"[EXCEPCION] {e}")
    import traceback
    traceback.print_exc()
