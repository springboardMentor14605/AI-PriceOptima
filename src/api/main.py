from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import os
import sys

# Add project root to path for local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.pricing.baseline_engine import get_baseline_price

app = FastAPI(title="AI: PriceOptima Serving API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define paths for models
MODELS_DIR = "models"
XGB_PATH = os.path.join(MODELS_DIR, "xgb_model.joblib")
LGB_PATH = os.path.join(MODELS_DIR, "lgb_model.joblib")
FEATURES_PATH = os.path.join(MODELS_DIR, "feature_names.joblib")

# In-memory storage for models
models = {}

@app.on_event("startup")
def load_models():
    """Loads serialized models and feature metadata on API startup."""
    try:
        models["xgb"] = joblib.load(XGB_PATH)
        models["lgb"] = joblib.load(LGB_PATH)
        models["feature_names"] = joblib.load(FEATURES_PATH)
        print("Models and feature names loaded successfully.")
    except Exception as e:
        print(f"Error loading models: {e}")

class PricingInput(BaseModel):
    category: str
    region: str
    inventory_level: int
    price: float
    # These might be needed if they were features in training
    # store_id and product_id were dropped in training notebook

@app.get("/health")
def health_check():
    """Health check endpoint to verify API status."""
    return {"status": "healthy", "models_loaded": len(models) > 0}

@app.post("/recommend-price")
def recommend_price(input_data: PricingInput):
    """
    Takes product metadata and current state to return pricing recommendations 
    from both a rule-based baseline and advanced ML models.
    """
    if not models:
        raise HTTPException(status_code=503, detail="Models aren't loaded yet.")

    # 1. Baseline Recommendation (Rule-based)
    baseline_rec = get_baseline_price(input_data.price, input_data.inventory_level)

    # 2. ML Recommendation
    # Prepare feature vector for ML models
    # We must match the one-hot encoding used during training
    input_dict = {
        "inventory_level": [input_data.inventory_level],
        "price": [input_data.price],
        "category_" + input_data.category: [1],
        "region_" + input_data.region: [1]
    }
    
    # Create DataFrame and align with training features
    df_input = pd.DataFrame(input_dict)
    
    # Add missing columns (dummies that weren't selected) and set them to 0
    for col in models["feature_names"]:
        if col not in df_input.columns:
            df_input[col] = 0
            
    # Reorder columns to match training exactly
    df_input = df_input[models["feature_names"]]

    # Predict demand (units_sold) using XGBoost
    predicted_demand_xgb = float(models["xgb"].predict(df_input)[0])
    predicted_demand_lgb = float(models["lgb"].predict(df_input)[0])

    # Simple dynamic pricing logic based on ML prediction:
    # (Note: In a real scenario, this would use elasticity or optimization)
    # We follow the notebook logic template (higher predicted demand -> higher price)
    # We use a threshold relative to inventory for the suggestion
    if predicted_demand_xgb > input_data.inventory_level:
        ml_suggestion = input_data.price * 1.10 # Scarcity/High Demand
    elif predicted_demand_xgb < (input_data.inventory_level * 0.1):
        ml_suggestion = input_data.price * 0.90 # Overstock/Low Demand
    else:
        ml_suggestion = input_data.price

    return {
        "baseline_recommendation": baseline_rec,
        "ml_recommendations": {
            "xgb_suggested_price": round(ml_suggestion, 2),
            "predicted_demand_xgb": round(predicted_demand_xgb, 2),
            "predicted_demand_lgb": round(predicted_demand_lgb, 2)
        },
        "current_state": {
            "inventory": input_data.inventory_level,
            "current_price": input_data.price
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
