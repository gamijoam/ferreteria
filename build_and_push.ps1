# Script para Construir y Subir Imágenes Docker
# Autor: AntiGravity
# Uso: .\build_and_push.ps1 [version]
# Ejemplo: .\build_and_push.ps1 v1.0.1

param (
    [string]$Version = "latest"
)

# Configuración
$REGISTRY = "ghcr.io"
$NAMESPACE = "gamijoam" # Tu usuario de GitHub
$IMAGE_BACKEND = "$REGISTRY/$NAMESPACE/ferreteria-backend"
$IMAGE_FRONTEND = "$REGISTRY/$NAMESPACE/ferreteria-frontend"

Write-Host "🚧 Iniciando proceso de construcción para la versión: $Version" -ForegroundColor Yellow

# 1. Login (Si falla, el usuario debe hacerlo manual)
Write-Host "🔑 Verificando sesión en Docker..." -ForegroundColor Cyan
docker login $REGISTRY
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: No se pudo iniciar sesión en $REGISTRY. Ejecuta 'docker login ghcr.io' manualmente con un TOKEN personal (PAT)." -ForegroundColor Red
    exit 1
}

# 2. Construir Backend
Write-Host "📦 Construyendo Backend..." -ForegroundColor Cyan
docker build -t "$IMAGE_BACKEND:$Version" -f ferreteria_refactor/backend_api/Dockerfile .
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Falló build de Backend"; exit 1 }

# 3. Construir Frontend
Write-Host "📦 Construyendo Frontend..." -ForegroundColor Cyan
docker build -t "$IMAGE_FRONTEND:$Version" -f ferreteria_refactor/frontend_web/Dockerfile ./ferreteria_refactor/frontend_web
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Falló build de Frontend"; exit 1 }

# 4. Push Backend
Write-Host "🚀 Subiendo Backend..." -ForegroundColor Cyan
docker push "$IMAGE_BACKEND:$Version"

# 5. Push Frontend
Write-Host "🚀 Subiendo Frontend..." -ForegroundColor Cyan
docker push "$IMAGE_FRONTEND:$Version"

Write-Host "✅ ¡Proceso completado con éxito! Las imágenes están en $REGISTRY" -ForegroundColor Green
Write-Host "   - $IMAGE_BACKEND:$Version"
Write-Host "   - $IMAGE_FRONTEND:$Version"
