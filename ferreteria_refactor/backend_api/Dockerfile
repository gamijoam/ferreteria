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
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install uvicorn explicitly first (critical dependency)
RUN pip install --no-cache-dir uvicorn[standard]

# Copy requirements from root (build context is project root)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Verify uvicorn installation (debug step)
RUN which uvicorn && uvicorn --version

# Copy entire project structure
COPY ferreteria_refactor/ /app/ferreteria_refactor/

# Set PYTHONPATH to include the app directory
ENV PYTHONPATH=/app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/system/health', timeout=5)" || exit 1

# Run uvicorn using python -m for maximum compatibility
CMD ["python", "-m", "uvicorn", "ferreteria_refactor.backend_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
