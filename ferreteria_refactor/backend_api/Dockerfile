# ============================================
# Backend Dockerfile
# ============================================
# Build Context: Project Root (...)
# Command: docker build -f ferreteria_refactor/backend_api/Dockerfile .
# ============================================

FROM python:3.10-slim

# Labels
LABEL maintainer="ferreteria-saas"
LABEL service="backend-api"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies
# libpq-dev is required for psycopg2 (Postgres)
# gcc is required for compiling some python packages
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from ROOT (context is root)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire backend package structure
# We copy 'ferreteria_refactor' to '/app/ferreteria_refactor'
COPY ferreteria_refactor/ ferreteria_refactor/

# Create a non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/system/health || exit 1

# Command
# We run from /app, calling the module ferreteria_refactor.backend_api.main
CMD ["uvicorn", "ferreteria_refactor.backend_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
