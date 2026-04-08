FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Ensure we do not generate .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure stdout is unbuffered
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies first to cache docker layers
COPY requirements.txt .
# If you run into issues with xgboost/lightgbm on slim, build-essential helps
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Start the uvicorn server serving the FastAPI app
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
