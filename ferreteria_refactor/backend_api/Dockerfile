# ============================================
# Backend Dockerfile
# ============================================
FROM python:3.9-slim

# Metadata
LABEL maintainer="ferreteria@example.com"
LABEL description="Backend API para Sistema de Ferretería"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from root
COPY ../../requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . /app/backend_api

# Set PYTHONPATH to include the parent directory
ENV PYTHONPATH=/app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/system/health')" || exit 1

# Run uvicorn
CMD ["uvicorn", "backend_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
