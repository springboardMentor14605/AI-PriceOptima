from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager
import pandas as pd
import joblib
import os
import sys

# Pre-add root project folder to pythonpath to import optimization
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from optimization import load_ml_assets, optimize_price_for_row

# Global variables for model cache
model = None
expected_features = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, expected_features
    print("Loading ML models for FastAPI...")
    # Change CWD temporarily if necessary or rely on load_ml_assets doing it right
    original_cwd = os.getcwd()
    os.chdir(BASE_DIR)
    
    try:
        model, expected_features = load_ml_assets()
        if model is None:
            print("WARNING: Model assets missing. Ensure models directory is populated.")
    finally:
        os.chdir(original_cwd)
    yield
    print("Shutting down model inference layer.")

app = FastAPI(title="AI Price Optima API", lifespan=lifespan)

class PriceRequest(BaseModel):
    product_id: str
    price: float
    cost: float
    inventory_level: float
    demand_forecast: float
    competitor_pricing: float
    visitors: float
    date: str

class BatchPriceRequest(BaseModel):
    requests: List[PriceRequest]

@app.get("/")
def health_check():
    return {"status": "API running"}

@app.post("/predict-price")
def predict_price(request: PriceRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model assets not loaded")

    try:
        row_dict = {
            'Product ID': request.product_id,
            'Price': request.price,
            'Cost': request.cost,
            'Inventory Level': request.inventory_level,
            'Competitor Pricing': request.competitor_pricing,
            'Visitors': request.visitors,
            'Date': pd.to_datetime(request.date),
        }

        # Emulate feature-engineering layer features implicitly expected by original model
        row_dict['Is_Weekend'] = row_dict['Date'].dayofweek >= 5
        row_dict['Demand_Trend'] = request.demand_forecast
        
        row_series = pd.Series(row_dict)
        
        best_price, best_demand, max_revenue = optimize_price_for_row(row_series, model, expected_features)
        
        return {
            "optimal_price": round(best_price, 2),
            "predicted_demand": int(best_demand),
            "expected_revenue": round(max_revenue, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

@app.post("/batch-predict")
def batch_predict(batch: BatchPriceRequest):
    results = []
    for req in batch.requests:
        try:
            # We can directly invoke the logic here to emulate batching
            res = predict_price(req)
            results.append({"product_id": req.product_id, "result": res})
        except Exception as e:
            results.append({"product_id": req.product_id, "error": str(e)})
    return {"batch_results": results}

@app.get("/model-info")
def model_info():
    metrics_path = os.path.join(BASE_DIR, 'models', 'model_metrics.pkl')
    try:
        metrics = joblib.load(metrics_path)
    except FileNotFoundError:
        metrics = {"name": "Unknown", "rmse": "Unknown"}

    return {
        "model_type": metrics.get("name", "Unknown"),
        "rmse": metrics.get("rmse", "Unknown"),
        "features_used": expected_features if expected_features else []
    }
