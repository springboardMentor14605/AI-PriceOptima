from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .schemas import InputData
from .model import predict_demand, elasticity_analysis
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "PriceOptima API Running"}

@app.post("/predict")
def predict(data: InputData):
    demand = predict_demand(data)
    revenue = demand * data.price
    profit = ((data.price - data.cost) / data.price) * 100

    return {
        "predicted_demand": demand,
        "expected_revenue": revenue,
        "profit_margin": profit,
        "recommended_price": data.price * 1.1,
        "confidence_interval": {
            "lower": demand * 0.9,
            "upper": demand * 1.1
        }
    }

@app.get("/kpi/dashboard")
def kpi():
    return {
        "revenue": {
            "total": 5000000,
            "daily_avg": 120000,
            "trend": "up",
            "ml_lift": 12
        },
        "demand": {
            "total_units": 20000,
            "daily_avg": 500,
            "trend": "up",
            "forecast_accuracy": 92
        },
        "performance": {
            "model_rmse": 12.5,
            "prediction_latency_ms": 45
        },
        "pricing": {
            "optimal_prices_applied": 78
        },
        "timestamp": time.time()
    }

@app.get("/experiment/elasticity")
def elasticity(base_price: float, price_range: float, steps: int):
    return elasticity_analysis(base_price, price_range, steps)
