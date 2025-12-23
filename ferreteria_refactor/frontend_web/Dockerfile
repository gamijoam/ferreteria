# ============================================
# Frontend Dockerfile (Multi-stage)
# ============================================
# Build Context: ./ferreteria_refactor/frontend_web
# ============================================

# --------------------------------------------
# Stage 1: Builder
# --------------------------------------------
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package.json and lock file
# Context is frontend folder, so they are at root of context
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build args
ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=$VITE_API_URL

# Build
RUN npm run build

# --------------------------------------------
# Stage 2: Production Runner (Nginx)
# --------------------------------------------
FROM nginx:alpine

# Install curl for healthcheck
RUN apk add --no-cache curl

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Create Nginx Config Inline (Single file solution)
RUN echo 'server { \
    listen 80; \
    server_name _; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    # Compression \
    gzip on; \
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript; \
    \
    # Security \
    add_header X-Frame-Options "SAMEORIGIN"; \
    add_header X-Content-Type-Options "nosniff"; \
    \
    # SPA Routing \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    \
    # Cache Static Assets \
    location ~* \.(?:css|js|jpg|jpeg|gif|png|ico|svg|woff|woff2|ttf|eot)$ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Copy build artifacts from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
