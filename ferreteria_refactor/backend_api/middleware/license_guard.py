"""
License Guard Middleware
Valida la licencia JWT en cada petición al backend.
Bloquea todas las peticiones si la licencia es inválida o ha expirado.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from pathlib import Path
import uuid
from datetime import datetime


# Clave pública RSA (debe coincidir con la generada por license_generator.py)
# IMPORTANTE: Esta clave se embebe en el código y se distribuye con la aplicación
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0wnnOdeEW3b181oL2KC9
1lZFKhVOLPiohBL69d6qLSsYJNuv3SIVf6jD+khFZMgAXcIT87Bgov614SKk/IPN
Uip6zEUPWWsATQqIEsK0dchsgaHZYb0/fUOu7NK3Xi2PHvtUE66YgKYEbBbxVlXW
ocGWhyfgUBZWgboG8Ehhe0s/74SKSc+5n7DVKIHm6bwqRhzfANCdaD349sB9HS34
iPS2uot2kBNfNTCuLaxWMhDwvsyEVy75PqRiJj76cbD6PE1N/BRx4U2N8NIy4wyG
rRNtqsPUITYZVaFO/97jS4cLE0pbxxMENM3BzqAJiPL+59IPkyAk9JJDsMHbjXlj
TQIDAQAB
-----END PUBLIC KEY-----"""

# Ruta del archivo de licencia
# Ruta del archivo de licencia
# license_guard.py -> middleware -> backend_api -> ferreteria_refactor -> ferreteria -> license.key
LICENSE_FILE = Path(__file__).parent.parent.parent.parent / "license.key"

# Rutas que NO requieren licencia válida
WHITELIST_PATHS = [
    "/docs",
    "/openapi.json",
    "/redoc",
    "/api/v1/license/activate",
    "/api/v1/license/status",
    "/api/v1/license/machine-id",
]


def get_machine_id():
    """Obtiene el ID de hardware de la máquina actual."""
    return str(uuid.getnode())


def validate_license():
    """
    Valida la licencia JWT.
    
    Returns:
        dict: Payload del token si es válido
        
    Raises:
        HTTPException: Si la licencia es inválida
    """
    # Verificar que existe el archivo de licencia
    if not LICENSE_FILE.exists():
        raise HTTPException(
            status_code=402,
            detail={
                "error": "NO_LICENSE",
                "message": "No se encontró archivo de licencia. Por favor, active una licencia válida.",
                "machine_id": get_machine_id()
            }
        )
    
    # Leer el token
    try:
        with open(LICENSE_FILE, 'r') as f:
            token = f.read().strip()
    except Exception as e:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "LICENSE_READ_ERROR",
                "message": f"Error al leer el archivo de licencia: {str(e)}"
            }
        )
    
    # Validar el token JWT
    try:
        payload = jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=["RS256"]
        )
    except JWTError as e:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "INVALID_LICENSE",
                "message": f"Licencia inválida: {str(e)}"
            }
        )
    
    # Verificar expiración
    exp_timestamp = payload.get("exp")
    if exp_timestamp:
        exp_date = datetime.fromtimestamp(exp_timestamp)
        if datetime.utcnow() > exp_date:
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "LICENSE_EXPIRED",
                    "message": f"La licencia expiró el {exp_date.strftime('%Y-%m-%d %H:%M:%S')}",
                    "expired_date": exp_date.isoformat()
                }
            )
    
    # Verificar hardware ID (solo para licencias FULL)
    license_type = payload.get("type", "FULL")
    if license_type == "FULL":
        license_hw_id = payload.get("hw_id")
        current_hw_id = get_machine_id()
        
        if license_hw_id and license_hw_id != current_hw_id:
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "HARDWARE_MISMATCH",
                    "message": "Esta licencia no es válida para este equipo.",
                    "expected_hw_id": license_hw_id,
                    "current_hw_id": current_hw_id
                }
            )
    
    return payload


class LicenseGuardMiddleware(BaseHTTPMiddleware):
    """
    Middleware que valida la licencia en cada petición.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Verificar si la ruta está en la whitelist
        path = request.url.path
        
        # Permitir rutas whitelisted
        if any(path.startswith(whitelist_path) for whitelist_path in WHITELIST_PATHS):
            return await call_next(request)
        
        # Validar licencia para todas las demás rutas
        try:
            validate_license()
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content=e.detail
            )
        
        # Si la licencia es válida, continuar con la petición
        response = await call_next(request)
        return response
