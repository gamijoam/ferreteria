# Estrategias de Despliegue: Dashboard Gerencial

Para que el dueño vea el negocio "desde cualquier lugar", **no** recomendamos ejecutar Streamlit en la computadora local de la tienda. Si la computadora se apaga o se va la luz, el dashboard se cae.

## Opción Recomendada: Arquitectura Híbrida (VPS)

En este modelo, el "Cerebro" (Base de Datos + API + Dashboard) vive en la Nube (VPS). La tienda física (Caja) se conecta a la nube.

### 1. ¿Dónde se instala el Dashboard?
Se instala en el **servidor VPS** (Ubuntu/Linux), no en la PC del cliente.
*   **Ventaja**: Accesible 24/7 desde el celular, tablet o casa.
*   **IP/Dominio**: El cliente entra a `www.miferreteria-dashboard.com` o una IP pública `142.x.x.x`. No necesita saber la IP local de la tienda.

### 2. ¿Y si la Base de Datos es Local? (Peor escenario para remoto)
Si la BD está en la tienda física y quieres verla desde fuera:
*   Necesitas una **IP Pública Fija** (costoso) o usar túneles como **Ngrok** / **Cloudflare Tunnel**.
*   **Desventaja**: Si se va internet en la tienda, no puedes ver el reporte.

### 3. ¿Cómo se actualiza?
*   **En VPS**: Tú subes los cambios al servidor (git pull) y reinicias el servicio. El cliente no hace nada, solo refresca la página web.
*   **En Local**: El `Launcher` debería descargar el nuevo código y reiniciar el proceso de Streamlit en segundo plano.

## Solución Técnica: URL Dinámica

Para que el código funcione tanto en Local (`localhost`) como en Nube (`midominio.com`), debemos sacar la URL de la API del código y ponerla en un archivo de configuración (`.env`).

### Cambios Requeridos
1. Crear archivo `.env` o `secrets.toml`.
2. Modificar `api_client.py` para leer esa variable.
