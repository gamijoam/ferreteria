# --- ETAPA 1: Construcción del Frontend (React) ---
FROM node:20-alpine as frontend-build

WORKDIR /app/frontend

# Copiamos archivos de dependencias
COPY ferreteria_refactor/frontend_web/package.json ferreteria_refactor/frontend_web/package-lock.json ./

# Instalamos dependencias
RUN npm ci

# Copiamos el código fuente del frontend
COPY ferreteria_refactor/frontend_web/ ./

# Compilamos para producción (Esto crea la carpeta dist)
RUN npm run build

# --- ETAPA 2: Construcción del Backend (FastAPI) ---
FROM python:3.11-slim

WORKDIR /app

# Instalamos dependencias de sistema necesarias para PostgreSQL y compilación
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiamos requirements e instalamos dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install uvicorn psycopg2-binary aiofiles

# Copiamos todo el código del proyecto
COPY . .

# Copiamos el build del frontend desde la Etapa 1 a una carpeta 'static'
# OJO: Ajustamos la ruta para que FastAPI la encuentre fácil
COPY --from=frontend-build /app/frontend/dist /app/static

# Variable de entorno para indicar que estamos en Docker
ENV DOCKER_CONTAINER=true
ENV DATABASE_URL=sqlite:///./ferreteria.db

# Exponemos el puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "ferreteria_refactor.backend_api.main:app", "--host", "0.0.0.0", "--port", "8000"]