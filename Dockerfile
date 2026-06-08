# Face Recognition & PPE Compliance System
# Production-ready Docker image

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    libopencv-dev \
    python3-opencv \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt requirements_ppe.txt requirements_web.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements_ppe.txt && \
    pip install --no-cache-dir -r requirements_web.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p faces ppe_compliance logs exports static templates

# Download PPE model
RUN python download_ppe_model.py || echo "PPE model will be downloaded on first run"

# Expose ports
EXPOSE 5000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=web_dashboard.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/dashboard/stats')" || exit 1

# Default command - run web dashboard
CMD ["python", "web_dashboard.py"]
