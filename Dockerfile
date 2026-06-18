# Stage 1: Build Frontend
FROM node:18 AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install --legacy-peer-deps
COPY frontend/ ./
RUN npm run build

# Stage 2: Build Backend & Combine
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies needed for spatial analysis libraries (GDAL) & Nginx
RUN apt-get update && apt-get install -y \
    nginx \
    gdal-bin \
    libgdal-dev \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Ensure GDAL is correctly referenced by Python
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir --upgrade pip setuptools==67.4.0 wheel Cython==0.29.35 numpy==1.23.2 && \
    pip install --no-cache-dir --no-build-isolation -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Register CLI entry points and setup packages
WORKDIR /app/backend
RUN python setup.py install
ENV PYTHONPATH=/app/backend

# Reset WORKDIR to root
WORKDIR /app

# Copy built frontend files to Nginx web root directory
COPY --from=frontend-builder /app/frontend/build/ /var/www/html/
COPY --from=frontend-builder /app/frontend/index.html /var/www/html/
COPY --from=frontend-builder /app/frontend/logo.png /var/www/html/

# Configure Nginx and startup scripts
COPY hf_nginx.conf /etc/nginx/sites-available/default
RUN ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default
COPY start_hf.sh .
RUN chmod +x start_hf.sh

EXPOSE 7860
CMD ["./start_hf.sh"]
