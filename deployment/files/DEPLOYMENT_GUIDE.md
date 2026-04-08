# 🚀 PriceOptima Deployment Guide
## Milestone 6: Production Deployment & Dashboard

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Local Development Setup](#local-development-setup)
5. [Docker Deployment](#docker-deployment)
6. [Production Deployment](#production-deployment)
7. [API Documentation](#api-documentation)
8. [Dashboard User Guide](#dashboard-user-guide)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Troubleshooting](#troubleshooting)

---

## System Overview

**PriceOptima** is an ML-powered dynamic pricing system that predicts demand and recommends optimal prices in real-time.

### Key Features:
- ✅ **Demand Prediction**: XGBoost model predicts units sold based on market conditions
- ✅ **Price Optimization**: Finds revenue-maximizing prices with margin constraints
- ✅ **Real-time Dashboard**: KPI monitoring with React frontend
- ✅ **A/B Testing**: Simulate price experiments before deployment
- ✅ **Price Elasticity**: Analyze demand sensitivity to price changes
- ✅ **Batch Processing**: Handle multiple predictions efficiently
- ✅ **Containerized**: Docker for consistent deployment across environments

---

## Architecture

```
┌─────────────────┐
│  React Frontend │  (Port 3000)
│   Dashboard     │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI Backend│  (Port 8000)
│   + ML Model    │
└────────┬────────┘
         │
         ├─── XGBoost Model (Demand Prediction)
         ├─── Price Optimizer (Revenue Maximization)
         └─── Redis Cache (Optional)
```

### Tech Stack:
- **Backend**: FastAPI (Python 3.9)
- **ML Model**: XGBoost with Optuna tuning
- **Frontend**: React.js
- **Containerization**: Docker & Docker Compose
- **Monitoring**: Prometheus + Grafana (optional)

---

## Prerequisites

### Required Software:
```bash
# Check installations
python --version        # Python 3.9+
node --version          # Node.js 14+
docker --version        # Docker 20+
docker-compose --version # Docker Compose 1.29+
```

### System Requirements:
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 2GB free space
- **OS**: Linux, macOS, or Windows with WSL2

---

## Local Development Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/your-org/priceoptima.git
cd priceoptima/milestone6_deployment
```

### Step 2: Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**API will be available at**: `http://localhost:8000`
**Interactive docs**: `http://localhost:8000/docs`

### Step 3: Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

**Dashboard will open at**: `http://localhost:3000`

---

## Docker Deployment

### Quick Start (Recommended)
```bash
# From project root
docker-compose up -d

# Check running containers
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Services will be available at**:
- Backend API: `http://localhost:8000`
- Frontend Dashboard: `http://localhost:3000`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001`

### Individual Container Management

#### Backend Only:
```bash
cd backend
docker build -t priceoptima-backend .
docker run -d -p 8000:8000 --name backend priceoptima-backend
```

#### Frontend Only:
```bash
cd frontend
docker build -t priceoptima-frontend .
docker run -d -p 3000:80 --name frontend priceoptima-frontend
```

### Stop & Remove Containers:
```bash
docker-compose down
docker-compose down -v  # Also remove volumes
```

---

## Production Deployment

### AWS EC2 Deployment

#### Step 1: Launch EC2 Instance
```bash
# Recommended: t3.medium (2 vCPU, 4GB RAM)
# OS: Ubuntu 22.04 LTS
# Security Group: Allow ports 22, 80, 443, 8000, 3000
```

#### Step 2: Install Docker
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Step 3: Deploy Application
```bash
# Clone repository
git clone https://github.com/your-org/priceoptima.git
cd priceoptima/milestone6_deployment

# Set environment variables
export ENVIRONMENT=production
export API_URL=http://your-domain.com:8000

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

#### Step 4: Setup Nginx (Reverse Proxy)
```bash
sudo apt install nginx

# Create nginx config
sudo nano /etc/nginx/sites-available/priceoptima
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/priceoptima /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Kubernetes Deployment (Advanced)

See `k8s/` directory for Kubernetes manifests.

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

---

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Health Check
```http
GET /health

Response:
{
    "status": "healthy",
    "timestamp": "2025-04-07T10:30:00",
    "model_loaded": true,
    "model_version": "1.0"
}
```

#### 2. Single Prediction
```http
POST /predict
Content-Type: application/json

Request:
{
    "price": 75.0,
    "cost": 50.0,
    "discount_pct": 10.0,
    "inventory_units": 150,
    "competitor_price": 80.0,
    "category": 1,
    "region": 0,
    "seasonality": 2,
    "weather_condition": 1,
    "month": 4,
    "day_of_week": 2
}

Response:
{
    "predicted_demand": 87.45,
    "recommended_price": 67.50,
    "expected_revenue": 5902.88,
    "profit_margin": 25.93,
    "confidence_interval": {
        "lower": 74.33,
        "upper": 100.57,
        "confidence": 0.95
    },
    "timestamp": "2025-04-07T10:30:00"
}
```

#### 3. Price Optimization
```http
POST /optimize

Request:
{
    "base_price": 75.0,
    "cost": 50.0,
    "min_margin": 0.2,
    "max_discount": 0.3,
    "inventory_units": 100,
    "competitor_price": 80.0,
    "category": 1,
    "region": 0,
    "seasonality": 2,
    "weather_condition": 1,
    "month": 4,
    "day_of_week": 2
}

Response:
{
    "optimal_price": 68.50,
    "expected_demand": 92.3,
    "expected_revenue": 6322.55,
    "profit_margin": 27.01,
    "price_range_tested": {
        "min": 60.0,
        "max": 97.5
    }
}
```

#### 4. A/B Test Simulation
```http
POST /experiment/ab_test

Request:
{
    "price_a": 70.0,
    "price_b": 75.0,
    "sample_size": 1000,
    "features": {}
}

Response:
{
    "variant_a": {
        "price": 70.0,
        "avg_demand": 89.2,
        "avg_revenue": 6244.0,
        "std_revenue": 523.1
    },
    "variant_b": {
        "price": 75.0,
        "avg_demand": 85.3,
        "avg_revenue": 6397.5,
        "std_revenue": 498.7
    },
    "analysis": {
        "revenue_lift_pct": 2.46,
        "winner": "B",
        "confidence": 95,
        "sample_size": 1000
    },
    "recommendation": "Continue Testing"
}
```

#### 5. Dashboard KPIs
```http
GET /kpi/dashboard

Response:
{
    "revenue": {
        "total": 4567890.45,
        "daily_avg": 152263.01,
        "ml_lift": 18.7,
        "trend": "up"
    },
    "demand": {
        "total_units": 45678,
        "daily_avg": 1522,
        "forecast_accuracy": 87.6,
        "trend": "stable"
    },
    ...
}
```

### Interactive API Docs
Visit `http://localhost:8000/docs` for Swagger UI with interactive testing.

---

## Dashboard User Guide

### Overview Tab
- **Real-time KPIs**: Revenue, demand, pricing metrics
- **ML Lift**: Performance vs static pricing
- **Model Performance**: RMSE, accuracy, latency
- **Auto-refresh**: Updates every 30 seconds

### Predict Tab
1. **Enter Product Details**:
   - Price, cost, discount
   - Inventory levels
   - Competitor pricing

2. **Set Market Context**:
   - Category, region
   - Season, weather
   - Day/month

3. **Get Predictions**:
   - Click "Predict Demand"
   - View expected demand, revenue, margin
   - See 95% confidence interval

4. **Analyze Elasticity**:
   - Click "Analyze Elasticity"
   - View optimal price point
   - Understand price sensitivity

### Analytics Tab
- **Price Elasticity Charts**: Demand vs price curves
- **Sensitivity Analysis**: High/low elasticity indicators
- **Optimization Insights**: Revenue maximization recommendations

---

## Monitoring & Maintenance

### Health Checks
```bash
# API health
curl http://localhost:8000/health

# Container health
docker-compose ps
```

### Logs
```bash
# Backend logs
docker-compose logs -f backend

# All services
docker-compose logs -f
```

### Metrics (Prometheus)
```bash
# Access Prometheus
http://localhost:9090

# Key metrics:
- http_requests_total
- prediction_latency_seconds
- model_rmse
```

### Grafana Dashboards
```bash
# Access Grafana
http://localhost:3001

# Default credentials:
Username: admin
Password: admin
```

### Model Updates
```bash
# Replace model file
cp new_model.pkl backend/xgboost_model.pkl

# Restart backend
docker-compose restart backend
```

---

## Troubleshooting

### Backend Not Starting
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Port 8000 already in use: Change port in docker-compose.yml
# - Model file missing: Ensure xgboost_model.pkl exists
# - Dependencies error: Rebuild image: docker-compose build backend
```

### Frontend Not Connecting
```bash
# Check API_URL
echo $REACT_APP_API_URL

# Should be: http://localhost:8000

# Update and rebuild:
export REACT_APP_API_URL=http://localhost:8000
docker-compose build frontend
docker-compose up -d frontend
```

### CORS Errors
```bash
# Ensure CORS middleware is enabled in main.py
# Check browser console for exact error
# Verify API URL matches exactly (no trailing slash)
```

### Slow Predictions
```bash
# Enable Redis caching
docker-compose up -d redis

# Monitor performance
curl http://localhost:8000/metrics
```

---

## Performance Optimization

### Caching Strategy
```python
# In main.py, add Redis caching
import redis
r = redis.Redis(host='redis', port=6379)

@app.post("/predict")
def predict_demand(request: PredictionRequest):
    cache_key = f"pred:{hash(str(request))}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # ... prediction logic ...
    
    r.setex(cache_key, 3600, json.dumps(response))
    return response
```

### Batch Processing
```bash
# Use batch endpoint for multiple predictions
POST /predict/batch
```

### Load Balancing
```yaml
# Add to docker-compose.yml
backend:
    deploy:
        replicas: 3
```

---

## Security Best Practices

1. **API Keys**: Implement authentication for production
2. **HTTPS**: Use SSL certificates (Let's Encrypt)
3. **Input Validation**: Already handled by Pydantic
4. **Rate Limiting**: Add middleware for production
5. **Secrets Management**: Use environment variables, not hardcoded values

---

## Backup & Disaster Recovery

### Backup Strategy
```bash
# Backup model files
tar -czf backup_$(date +%Y%m%d).tar.gz backend/*.pkl backend/*.json

# Backup database (if using)
docker exec priceoptima_db pg_dump -U user dbname > backup.sql
```

### Restore
```bash
# Restore from backup
tar -xzf backup_20250407.tar.gz -C backend/
docker-compose restart backend
```

---

## Support & Resources

- **Documentation**: `/docs` endpoint
- **GitHub Issues**: [Report bugs](https://github.com/your-org/priceoptima/issues)
- **Email**: support@priceoptima.com

---

**Deployment Completed Successfully! 🎉**

For questions or issues, refer to the troubleshooting section or contact the development team.
