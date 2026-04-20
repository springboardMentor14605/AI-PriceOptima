# 🎯 AI-PriceOptima: Dynamic Pricing System

![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.2-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-Dashboard-61DAFB?logo=react)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python)
![Status](https://img.shields.io/badge/Status-UAT_Passed-success)

## 📖 Project Overview
AI-PriceOptima is a robust, machine learning–driven dynamic pricing system designed to adjust prices in real-time or periodically to maximize revenue and maintain competitiveness. 

By analyzing historical sales data, demand elasticity, and inventory levels, the system simulates and deploys an optimal pricing strategy that significantly outperforms static baseline pricing. It ensures adaptability and transparency, helping businesses increase profitability while preserving customer trust.

---

## ✨ Key Features
- **Dynamic Demand Forecasting:** Utilizes Gradient Boosting architectures (`XGBoost`, `LightGBM`) to accurately predict market demand based on temporal and competitive features.
- **Rule-Based & ML Pricing Engine:** Seamlessly combines safety guardrails (min/max price limits) with advanced Machine Learning predictions.
- **Real-Time FastAPI Backend:** Low-latency endpoints (`/pricing/predict`, `/kpi`) containerized via Docker for instant model inference and simulator data fetching.
- **Interactive React Dashboard:** A premium, fully responsive Glassmorphism UI built with Vanilla CSS and Recharts to visualize revenue impacts and KPI trends in real-time.
- **Decoupled Docker Architecture:** Separation of heavy ML-training workloads and lightweight API serving, sharing data via persistent volumes.

---

## 🛠️ Technology Stack
| Layer | Technologies |
|:---|:---|
| **Frontend** | React.js, Recharts, Vanilla CSS (Glassmorphism UI) |
| **Backend API** | FastAPI, Uvicorn, Pydantic |
| **Machine Learning** | Scikit-Learn, XGBoost, LightGBM, SHAP, Optuna |
| **Data Processing** | Pandas, Numpy, Matplotlib |
| **Infrastructure** | Docker, Docker Compose |

---

## 🏗️ System Architecture
The application runs on a dual-container architecture managed by `docker-compose`:

1. **`api` (FastAPI Server):** 
   - Runs continuously on port `8000`.
   - Responsible for serving pricing predictions and KPI data to the React Dashboard.
2. **`ml-runner` (Model Training Container):** 
   - Runs strictly on-demand.
   - Executes the heavy ML data pipelines (Data Cleaning -> Feature Engineering -> Training).
   - Once training is complete, it outputs the `model.pkl` to the shared `app/models/` volume which the `api` container automatically hot-loads.

---

## 📂 Directory Structure
```text
AI-PriceOptima/
├── app/                      # FastAPI Application
│   ├── main.py               # API Endpoints
│   └── models/               # Shared volume for trained ML models
├── dashboard/                # React UI Frontend
│   ├── src/                  
│   │   ├── App.jsx           # Dashboard Logic
│   │   └── index.css         # Glassmorphism Styling
├── Data/                     # Raw datasets
├── Data Cleaning/            # Pre-processing scripts
├── Feature Engineering/      # Feature creation & encoding
├── Demand Forecast/          # Advanced ML Pipeline (XGBoost/LightGBM)
├── scripts/                  # Run and Pipeline automation
├── Outputs/                  # Generated CSVs and Evaluation outputs
├── docker-compose.yml        # Multi-container orchestration
├── Dockerfile                # API Container Blueprint
├── Dockerfile.ml             # ML Runner Container Blueprint
├── requirements.txt          # API dependencies
└── requirements.ml.txt       # ML & Training dependencies
```

---

## 🚀 Installation & Setup

### 1. Prerequisites
- **Python 3.10+** (if running locally)
- **Docker & Docker Compose** (highly recommended)
- **Node.js & npm** (for the React Dashboard)

### 2. Docker Deployment (Recommended)
This system is pre-configured to handle Out-Of-Memory (OOM) issues via chunked dependency installation in the Dockerfiles.

**Build the Containers:**
```bash
# Build the API server first
docker compose build api

# Build the ML runner second (Downloads C++ dependencies, takes ~15 mins)
docker compose build ml-runner
```

**Run the System:**
```bash
# 1. Train the ML Model (generates models into app/models/)
docker compose run ml-runner

# 2. Start the API Server in detached mode
docker compose up api -d
```
The FastAPI backend will now be available at `http://localhost:8000/docs`.

---

## 📊 Live Dashboard Setup
To start the React frontend and view your pricing KPIs:

```bash
cd dashboard
npm install
npm run dev
```
The application will launch automatically at `http://localhost:3000`.

---

## 🔗 API Endpoints (FastAPI)

- `GET /`: Health check endpoint.
- `GET /kpi`: Returns real-time KPI evaluations, revenue comparisons (Baseline vs Dynamic), and uplift metrics based on the simulation outputs.
- `POST /pricing/predict`: Accepts JSON payload of competitive pricing and inventory features to return an optimal dynamic price.

---

## 📈 Evaluation & UAT
The system has passed comprehensive User Acceptance Testing (UAT):
- **Simulation Validation:** Baseline tracking vs Dynamic tracking demonstrates measurable percent uplift in top-line revenue.
- **Latency Testing:** API yields inferences at `< 50ms`.
- **UI:** Responsive error handling and visually cohesive dashboard analytics.

### Rollout Strategy
1. **Shadow Deployment:** Generating theoretical prices dynamically in the background without exposing them to customers.
2. **A/B Testing:** Pushing dynamic prices to 10% of traffic, monitoring conversion rates. 
3. **Full Production:** 100% traffic allocation utilizing automated weekly model-retraining loops.

---
*Created for the dynamic pricing optimization milestone.*
