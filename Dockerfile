FROM python:3.10-slim

WORKDIR /app

# Prevent pip ReadTimeoutError on slow networking
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_RETRIES=10

# Copy requirement list
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn pydantic scikit-learn
RUN pip install --no-cache-dir xgboost lightgbm optuna shap

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8000

# Run the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
