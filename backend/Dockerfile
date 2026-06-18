FROM python:3.11-slim-bookworm
WORKDIR /backend

# Install system dependencies needed for spatial analysis libraries (GDAL)
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Ensure GDAL is correctly referenced by Python
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools==67.4.0 wheel Cython==0.29.35 numpy==1.23.2 && \
    pip install --no-cache-dir --no-build-isolation -r requirements.txt

# Copy backend source code
COPY . .

# Register CLI entry points
RUN python setup.py install

# Configure Python path
ENV PYTHONPATH=/backend
# Expose port 7860 as required by Hugging Face Spaces
EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]