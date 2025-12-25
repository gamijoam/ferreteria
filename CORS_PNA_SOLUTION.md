# Solución al Error de CORS: HTTPS → localhost

## Problema
Chrome bloquea peticiones de sitios HTTPS (como `https://demo.invensoft.lat`) hacia `http://localhost:5001` por política de Private Network Access (PNA).

## Soluciones Disponibles

### Opción 1: Flag de Chrome (Temporal - Solo Desarrollo)
Abrir Chrome con el flag que desactiva la verificación PNA:

**Windows:**
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --disable-features=PrivateNetworkAccessRespectPreflightResults
```

**Crear acceso directo:**
1. Click derecho en Chrome → Crear acceso directo
2. Click derecho en el acceso directo → Propiedades
3. En "Destino", agregar al final: ` --disable-features=PrivateNetworkAccessRespectPreflightResults`
4. Aplicar y usar ese acceso directo

### Opción 2: Usar Edge en lugar de Chrome
Microsoft Edge tiene una política PNA menos estricta. Prueba con Edge.

### Opción 3: Extensión de Chrome (Recomendada para Usuarios)
Instalar extensión "CORS Unblock" o similar que permita CORS a localhost.

### Opción 4: Arquitectura Alternativa (Mejor a largo plazo)
En lugar de que el frontend llame directamente a localhost, implementar:

1. **Frontend** → llama a **Backend VPS** (`/api/v1/print-local`)
2. **Backend VPS** → retorna payload
3. **Frontend** → usa **WebSocket** para notificar al Hardware Bridge local
4. **Hardware Bridge** → escucha WebSocket y imprime

Esto requiere refactorizar pero es la solución más robusta para producción.

## Solución Temporal Actual
Por ahora, el usuario debe:
1. Usar el flag de Chrome mencionado arriba, O
2. Usar Microsoft Edge, O  
3. Instalar extensión CORS

## Notas
- `targetAddressSpace: 'private'` está implementado pero Chrome lo ignora en algunos casos
- El Hardware Bridge tiene los headers CORS correctos
- El problema es una restricción del navegador, no del código
