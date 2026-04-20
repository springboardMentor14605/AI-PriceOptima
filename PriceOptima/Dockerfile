FROM python:3.9-slim

WORKDIR /app

# Copy requirement files (we will write requirements inline for convenience)
COPY ./api /app/api
COPY ./models /app/models

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn pandas scikit-learn xgboost lightgbm joblib pydantic

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
