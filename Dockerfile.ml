# ============================================================
# Dockerfile.ml — ML Training Environment for PriceOptima
# Uses Python 3.10 to support xgboost, lightgbm, shap, optuna
# ============================================================
FROM python:3.10-slim

WORKDIR /app

# Prevent pip ReadTimeoutError on slow networking
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_RETRIES=10

# Install system-level build tools required by some ML packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install ML requirements first (for Docker layer caching)
COPY requirements.ml.txt .
RUN pip install --no-cache-dir pandas==2.0.3 numpy==1.24.4 matplotlib==3.7.5
RUN pip install --no-cache-dir scikit-learn==1.3.2 fastapi==0.109.2 uvicorn==0.27.1 pydantic==2.6.1
RUN pip install --no-cache-dir xgboost==2.0.3 lightgbm==4.3.0
RUN pip install --no-cache-dir optuna==3.6.1 shap==0.44.1

# Copy the full project into the container
COPY . .

# Create the output directories that the scripts write to
RUN mkdir -p /app/Outputs /app/app/models

# Default command: run the Milestone 5 ML pipeline
CMD ["python", "Demand Forecast/milestone5_advanced_ml.py"]
