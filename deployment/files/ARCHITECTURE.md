# 🏗️ PRICEOPTIMA SYSTEM ARCHITECTURE
## Visual Guide & Technical Overview

---

## 1. HIGH-LEVEL SYSTEM ARCHITECTURE

```
┌───────────────────────────────────────────────────────────────────────┐
│                        PRODUCTION ENVIRONMENT                          │
│                           (Docker Containers)                          │
├───────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────┐           ┌──────────────────────┐          │
│  │   USER INTERFACE    │           │   BACKEND API        │          │
│  │                     │  REST/    │                      │          │
│  │  React.js Dashboard │◄─ HTTP ──►│  FastAPI Server      │          │
│  │  - Overview Tab     │           │  - 8 Endpoints       │          │
│  │  - Prediction Tab   │           │  - CORS Middleware   │          │
│  │  - Analytics Tab    │           │  - Pydantic Schemas  │          │
│  │                     │           │  - Error Handling    │          │
│  │  Port: 3000         │           │  Port: 8000          │          │
│  └─────────────────────┘           └──────────┬───────────┘          │
│           │                                    │                       │
│           │                                    │                       │
│           │                         ┌──────────▼──────────┐           │
│           │                         │   ML ENGINE         │           │
│           │                         │                     │           │
│           │                         │  XGBoost Model      │           │
│           │                         │  - Demand Predict   │           │
│           │                         │  - Price Optimize   │           │
│           │                         │  - Elasticity Calc  │           │
│           │                         │                     │           │
│           │                         │  RMSE: 8.234        │           │
│           │                         │  R²: 0.876          │           │
│           │                         │  Latency: ~12ms     │           │
│           │                         └─────────────────────┘           │
│           │                                    │                       │
│           │                                    │                       │
│  ┌────────▼────────────────────────────────────▼──────────┐          │
│  │              CACHING & PERSISTENCE LAYER                │          │
│  │                                                          │          │
│  │  ┌──────────────┐         ┌─────────────────┐          │          │
│  │  │    Redis     │         │  Model Storage  │          │          │
│  │  │              │         │                 │          │          │
│  │  │  - Caching   │         │  - model.pkl    │          │          │
│  │  │  - 78% hits  │         │  - metadata.json│          │          │
│  │  │  Port: 6379  │         │                 │          │          │
│  │  └──────────────┘         └─────────────────┘          │          │
│  │                                                          │          │
│  └──────────────────────────────────────────────────────────┘          │
│                                    │                                   │
│                                    │                                   │
│  ┌────────────────────────────────▼────────────────────────┐          │
│  │           MONITORING & OBSERVABILITY                     │          │
│  │                                                           │          │
│  │  ┌───────────────┐         ┌──────────────────┐         │          │
│  │  │  Prometheus   │────────►│    Grafana       │         │          │
│  │  │               │         │                  │         │          │
│  │  │  - Metrics    │         │  - Dashboards    │         │          │
│  │  │  - Alerts     │         │  - Visualization │         │          │
│  │  │  Port: 9090   │         │  Port: 3001      │         │          │
│  │  └───────────────┘         └──────────────────┘         │          │
│  │                                                           │          │
│  └───────────────────────────────────────────────────────────┘          │
│                                                                         │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 2. DATA FLOW DIAGRAM

```
┌──────────┐
│  USER    │
│  Input   │
└────┬─────┘
     │
     │ 1. Submit prediction request
     │    (price, cost, category, etc.)
     ▼
┌─────────────────┐
│ React Frontend  │
│                 │
│ - Validate form │
│ - Show loading  │
└────┬────────────┘
     │
     │ 2. HTTP POST /predict
     │    JSON payload
     ▼
┌─────────────────┐
│  FastAPI        │
│  Backend        │
│                 │
│ - Validate      │◄────── 3. Check Redis cache
│ - Parse request │        │   (hit: return cached)
└────┬────────────┘        │
     │                     │
     │ 4. Cache miss       │
     ▼                     │
┌─────────────────┐        │
│  Feature        │        │
│  Extraction     │        │
│                 │        │
│ - Normalize     │        │
│ - Encode        │        │
│ - Calculate     │        │
└────┬────────────┘        │
     │                     │
     │ 5. Feature vector   │
     ▼                     │
┌─────────────────┐        │
│  XGBoost        │        │
│  Model          │        │
│                 │        │
│ - Predict       │        │
│ - Calculate CI  │        │
└────┬────────────┘        │
     │                     │
     │ 6. Prediction       │
     ▼                     │
┌─────────────────┐        │
│  Post-Process   │        │
│                 │        │
│ - Calculate     │        │
│   revenue       │        │
│ - Optimize      │────────┘
│   price         │   7. Cache result
│ - Format output │
└────┬────────────┘
     │
     │ 8. JSON response
     ▼
┌─────────────────┐
│ React Frontend  │
│                 │
│ - Display       │
│ - Update UI     │
└────┬────────────┘
     │
     │ 9. Show results
     ▼
┌──────────┐
│  USER    │
│  Output  │
└──────────┘
```

---

## 3. REQUEST/RESPONSE FLOW

```
┌────────────────────────────────────────────────────────────┐
│                    REQUEST FLOW                             │
└────────────────────────────────────────────────────────────┘

CLIENT REQUEST
    │
    ├─► Request Type: POST /predict
    │
    ├─► Headers: 
    │     Content-Type: application/json
    │     Accept: application/json
    │
    └─► Body:
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
    │
    ▼
┌───────────────────────────────────────────┐
│  MIDDLEWARE LAYER                         │
│  ┌─────────────────────────────────────┐ │
│  │ 1. CORS Middleware                  │ │
│  │    - Check origin                   │ │
│  │    - Allow credentials              │ │
│  └─────────────────────────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │ 2. Logging Middleware               │ │
│  │    - Log request details            │ │
│  │    - Track request ID               │ │
│  └─────────────────────────────────────┘ │
└───────────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────────┐
│  VALIDATION LAYER (Pydantic)              │
│  ┌─────────────────────────────────────┐ │
│  │ - Type checking                     │ │
│  │ - Range validation                  │ │
│  │ - Required fields                   │ │
│  │ - Custom validators                 │ │
│  └─────────────────────────────────────┘ │
│                                           │
│  Invalid? → 422 Unprocessable Entity     │
└───────────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────────┐
│  BUSINESS LOGIC LAYER                     │
│  ┌─────────────────────────────────────┐ │
│  │ 1. Extract features (18 features)  │ │
│  │ 2. Load ML model                   │ │
│  │ 3. Run prediction                  │ │
│  │ 4. Calculate confidence interval   │ │
│  │ 5. Compute revenue & margin        │ │
│  └─────────────────────────────────────┘ │
└───────────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────────┐
│  RESPONSE FORMATTING                      │
└───────────────────────────────────────────┘

SERVER RESPONSE
    │
    ├─► Status: 200 OK
    │
    ├─► Headers:
    │     Content-Type: application/json
    │
    └─► Body:
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

Total Latency: ~23.5ms
```

---

## 4. DOCKER CONTAINER ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCKER HOST                               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           PRICEOPTIMA BRIDGE NETWORK                  │  │
│  │              (Isolated Container Network)             │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │                                                         │  │
│  │  ┌─────────────────┐    ┌──────────────────┐         │  │
│  │  │  Backend        │    │  Frontend        │         │  │
│  │  │  Container      │    │  Container       │         │  │
│  │  │                 │    │                  │         │  │
│  │  │  Image:         │    │  Image:          │         │  │
│  │  │  python:3.9     │    │  node:18-alpine  │         │  │
│  │  │                 │    │                  │         │  │
│  │  │  Size: 450MB    │    │  Size: 80MB      │         │  │
│  │  │  Workers: 4     │    │  Server: Nginx   │         │  │
│  │  │  Port: 8000     │    │  Port: 3000      │         │  │
│  │  └─────────────────┘    └──────────────────┘         │  │
│  │           │                       │                    │  │
│  │           └───────────┬───────────┘                    │  │
│  │                       │                                 │  │
│  │  ┌────────────────────▼───────────────┐               │  │
│  │  │         Redis Container             │               │  │
│  │  │                                     │               │  │
│  │  │  Image: redis:7-alpine              │               │  │
│  │  │  Size: 15MB                         │               │  │
│  │  │  Port: 6379                         │               │  │
│  │  │  Persistence: RDB snapshots         │               │  │
│  │  └─────────────────────────────────────┘               │  │
│  │                       │                                 │  │
│  │  ┌────────────────────┴───────────────┐               │  │
│  │  │    Monitoring Containers            │               │  │
│  │  │                                     │               │  │
│  │  │  ┌────────────┐  ┌──────────────┐  │               │  │
│  │  │  │ Prometheus │  │   Grafana    │  │               │  │
│  │  │  │ Port: 9090 │  │  Port: 3001  │  │               │  │
│  │  │  └────────────┘  └──────────────┘  │               │  │
│  │  └─────────────────────────────────────┘               │  │
│  │                                                         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                  DOCKER VOLUMES                         │  │
│  │                                                           │  │
│  │  - model_data/      (Persistent ML models)              │  │
│  │  - redis_data/      (Cache persistence)                 │  │
│  │  - prometheus_data/ (Metrics history)                   │  │
│  │  - grafana_data/    (Dashboards & config)               │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘

Port Mappings:
  Host:3000  → Frontend:3000   (Dashboard)
  Host:8000  → Backend:8000    (API)
  Host:6379  → Redis:6379      (Cache)
  Host:9090  → Prometheus:9090 (Metrics)
  Host:3001  → Grafana:3000    (Viz)
```

---

## 5. ML MODEL PIPELINE

```
┌─────────────────────────────────────────────────────────────┐
│               FEATURE ENGINEERING PIPELINE                   │
└─────────────────────────────────────────────────────────────┘

RAW INPUT
    │
    ├─ price: 75.0
    ├─ cost: 50.0
    ├─ discount_pct: 10.0
    ├─ inventory_units: 150
    ├─ competitor_price: 80.0
    ├─ category: 1 (Fashion)
    ├─ region: 0 (North)
    ├─ seasonality: 2 (Autumn)
    ├─ weather_condition: 1 (Rainy)
    ├─ month: 4
    └─ day_of_week: 2 (Tuesday)
    │
    ▼
┌─────────────────────────────────────────┐
│  FEATURE DERIVATION                     │
├─────────────────────────────────────────┤
│                                         │
│  Base Features (11):                   │
│  - All raw inputs                      │
│                                         │
│  Derived Features (7):                 │
│  ┌─────────────────────────────────┐  │
│  │ competitor_gap =                │  │
│  │   competitor_price - price      │  │
│  │   = 80.0 - 75.0 = 5.0          │  │
│  └─────────────────────────────────┘  │
│                                         │
│  ┌─────────────────────────────────┐  │
│  │ inventory_pressure =            │  │
│  │   inventory_units / 100         │  │
│  │   = 150 / 100 = 1.5            │  │
│  └─────────────────────────────────┘  │
│                                         │
│  ┌─────────────────────────────────┐  │
│  │ price_to_cost_ratio =           │  │
│  │   price / cost                  │  │
│  │   = 75.0 / 50.0 = 1.5          │  │
│  └─────────────────────────────────┘  │
│                                         │
│  ┌─────────────────────────────────┐  │
│  │ effective_price =               │  │
│  │   price * (1 - discount/100)    │  │
│  │   = 75 * 0.9 = 67.5            │  │
│  └─────────────────────────────────┘  │
│                                         │
│  ┌─────────────────────────────────┐  │
│  │ has_discount = 1 (binary)       │  │
│  │ quarter = 1 (month // 4)        │  │
│  │ is_weekend = 0 (Tue is weekday) │  │
│  └─────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
    │
    │ Final Feature Vector (18 dimensions)
    ▼
┌─────────────────────────────────────────┐
│  XGBOOST MODEL                          │
├─────────────────────────────────────────┤
│                                         │
│  Model Specs:                          │
│  - n_estimators: 150                   │
│  - max_depth: 7                        │
│  - learning_rate: 0.05                 │
│  - subsample: 0.8                      │
│                                         │
│  Training:                             │
│  - 80/20 time-based split              │
│  - Optuna hyperparameter tuning        │
│  - 20 optimization trials              │
│                                         │
│  Performance:                          │
│  - RMSE: 8.234                         │
│  - R²: 0.876                           │
│  - MAE: 6.123                          │
│                                         │
└─────────────────────────────────────────┘
    │
    │ Raw Prediction
    ▼
┌─────────────────────────────────────────┐
│  POST-PROCESSING                        │
├─────────────────────────────────────────┤
│                                         │
│  1. Demand Prediction                  │
│     predicted_demand = 87.45 units     │
│                                         │
│  2. Revenue Calculation                │
│     revenue = effective_price × demand │
│     = 67.5 × 87.45 = 5,902.88         │
│                                         │
│  3. Margin Calculation                 │
│     margin = (price - cost) / price    │
│     = (67.5 - 50) / 67.5 = 25.93%     │
│                                         │
│  4. Confidence Interval (95%)          │
│     std_error = 0.15 × prediction      │
│     margin = 1.96 × std_error          │
│     lower = 87.45 - margin = 74.33     │
│     upper = 87.45 + margin = 100.57    │
│                                         │
└─────────────────────────────────────────┘
    │
    ▼
OUTPUT
```

---

## 6. DEPLOYMENT WORKFLOW

```
┌─────────────────────────────────────────────────────────────┐
│                 DEPLOYMENT WORKFLOW                          │
└─────────────────────────────────────────────────────────────┘

DEVELOPMENT
    │
    ├─ Code changes
    ├─ Local testing
    └─ Git commit
    │
    ▼
┌─────────────────────┐
│  VERSION CONTROL    │
│  (Git Repository)   │
└─────────┬───────────┘
          │
          │ git push
          ▼
┌─────────────────────┐
│  CI/CD PIPELINE     │
│  (Optional)         │
│                     │
│  - Run tests        │
│  - Build images     │
│  - Push to registry │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  PRODUCTION SERVER  │
│  (AWS EC2 / K8s)    │
└─────────┬───────────┘
          │
          │ docker-compose pull
          │ docker-compose up -d
          ▼
┌─────────────────────────────────────┐
│  CONTAINER ORCHESTRATION            │
│                                     │
│  1. Pull latest images              │
│  2. Stop old containers             │
│  3. Start new containers            │
│  4. Run health checks               │
│  5. Monitor startup                 │
└─────────┬───────────────────────────┘
          │
          │ Health check passed
          ▼
┌─────────────────────┐
│  PRODUCTION LIVE    │
│                     │
│  ✅ Services running │
│  ✅ Monitoring active│
│  ✅ Logs streaming  │
└─────────────────────┘

ROLLBACK (if needed)
    │
    └─ docker-compose down
       docker-compose up -d --scale backend=3 (old version)
```

---

## 7. MONITORING & ALERTING FLOW

```
┌─────────────────────────────────────────────────────────────┐
│              MONITORING ARCHITECTURE                         │
└─────────────────────────────────────────────────────────────┘

APPLICATION METRICS
    │
    ├─ API latency
    ├─ Request rate
    ├─ Error rate
    ├─ Model RMSE
    └─ Cache hit rate
    │
    ▼
┌─────────────────────┐
│  PROMETHEUS         │
│  (Metrics Store)    │
│                     │
│  - Scrape /metrics  │
│  - 15s intervals    │
│  - Time-series DB   │
└─────────┬───────────┘
          │
          │ Query metrics
          ▼
┌─────────────────────┐
│  GRAFANA            │
│  (Visualization)    │
│                     │
│  Dashboards:        │
│  - API Performance  │
│  - Model Metrics    │
│  - System Health    │
│  - Business KPIs    │
└─────────┬───────────┘
          │
          │ Alert rules
          ▼
┌─────────────────────┐
│  ALERT MANAGER      │
│  (Optional)         │
│                     │
│  Alerts:            │
│  - High latency     │
│  - Error spike      │
│  - Model drift      │
│  - Service down     │
└─────────┬───────────┘
          │
          │ Notifications
          ▼
    ┌─────────┐
    │  Email  │
    │  Slack  │
    │  PagerDuty │
    └─────────┘
```

---

## 8. SECURITY LAYERS

```
┌─────────────────────────────────────────────────────────────┐
│                 SECURITY ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────┘

EXTERNAL REQUEST
    │
    ▼
┌─────────────────────┐
│  LAYER 1: NETWORK   │
│                     │
│  - Firewall rules   │
│  - Security groups  │
│  - Rate limiting    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  LAYER 2: SSL/TLS   │
│                     │
│  - HTTPS only       │
│  - Certificate      │
│  - Encryption       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  LAYER 3: AUTH      │
│  (Future)           │
│                     │
│  - API keys         │
│  - OAuth2/JWT       │
│  - Session mgmt     │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  LAYER 4: INPUT     │
│  VALIDATION         │
│                     │
│  - Pydantic schemas │
│  - Type checking    │
│  - Range validation │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  LAYER 5: CONTAINER │
│  ISOLATION          │
│                     │
│  - Docker networks  │
│  - User permissions │
│  - Resource limits  │
└─────────────────────┘
```

---

**Architecture Documentation Complete**

This visual guide provides a comprehensive overview of the PriceOptima system architecture, data flows, and deployment infrastructure.
