# Set up Python environment
FROM python:3.11-slim AS python_setup
WORKDIR /backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Ensure GDAL is correctly referenced by Python
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Install Python dependencies
COPY . .
RUN pip install -r requirements.txt \
    && python3 setup.py install