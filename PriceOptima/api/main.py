"""
===========================================================
AI PriceOptima – FastAPI Prediction Service
===========================================================

REST API for dynamic price prediction using the trained ML model.

Endpoints:
  GET  /           -> Health check & API info
  GET  /health     -> Health status
  POST /predict    -> Predict optimal price

Usage:
  uvicorn main:app --reload --port 8000

  Then open http://localhost:8000/docs for interactive Swagger UI.
===========================================================
"""

import os
import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

# ============================================================
# LOAD MODEL ON STARTUP
# ============================================================
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'best_pricing_model.pkl')

if os.path.exists(MODEL_PATH):
    model_package = joblib.load(MODEL_PATH)
    model = model_package['model']
    feature_names = model_package['feature_names']
    model_name = model_package['model_name']
    print(f"Model loaded: {model_name}")
else:
    model = None
    feature_names = []
    model_name = "Not Loaded"
    print("Warning: Model file not found. Run pricing_model.py first.")

# ============================================================
# FASTAPI APP
# ============================================================
app = FastAPI(
    title="AI PriceOptima API",
    description="Dynamic Pricing Prediction API powered by Machine Learning",
    version="1.0.0",
)


# ============================================================
# REQUEST / RESPONSE MODELS
# ============================================================
class PricingInput(BaseModel):
    """Input features for price prediction.
    NOTE: Does not include leaky features (discounted_price, profit_margin,
    margin_percent, revenue, price_demand_ratio, competitor_gap) as they
    are derived from the target variable (price)."""
    inventory_level: float = Field(..., description="Current inventory level", example=120)
    units_sold: float = Field(..., description="Number of units sold", example=45)
    units_ordered: float = Field(..., description="Number of units ordered", example=50)
    demand_forecast: float = Field(..., description="Forecasted demand", example=48)
    discount: float = Field(..., description="Discount percentage", example=10.0)
    holiday_promotion: int = Field(..., description="Holiday promotion flag (0 or 1)", example=1)
    competitor_pricing: float = Field(..., description="Competitor's price ($)", example=85.0)
    visitors: float = Field(..., description="Number of store/page visitors", example=500)
    cost: float = Field(..., description="Product cost ($)", example=60.0)
    demand_ratio: float = Field(..., description="Actual/forecasted demand ratio", example=0.94)
    inventory_pressure: float = Field(..., description="Inventory pressure metric", example=0.375)
    stock_remaining: float = Field(..., description="Remaining stock", example=75)
    conversion_rate: float = Field(..., description="Visitor to buyer ratio", example=0.09)
    traffic_intensity: float = Field(..., description="Traffic intensity metric", example=4.17)
    day_of_week: int = Field(..., description="Day of week (0=Mon, 6=Sun)", example=3)
    month: int = Field(..., description="Month (1-12)", example=6)
    is_weekend: int = Field(..., description="Weekend flag (0 or 1)", example=0)
    category: Optional[str] = Field("Electronics", description="Product category")
    region: Optional[str] = Field("North", description="Store region")
    seasonality: Optional[str] = Field("Summer", description="Current season")
    weather_condition: Optional[str] = Field("Clear", description="Weather condition")


class PricingOutput(BaseModel):
    """Prediction response."""
    predicted_price: float
    model_used: str
    confidence_r2: float
    competitor_price: float
    estimated_margin: float
    margin_percent: float
    pricing_position: str


# ============================================================
# ENDPOINTS
# ============================================================
@app.get("/")
def root():
    """API Home - Returns basic info and status."""
    return {
        "service": "AI PriceOptima - Dynamic Pricing API",
        "version": "1.0.0",
        "model": model_name,
        "status": "ready" if model is not None else "model not loaded",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy" if model is not None else "degraded",
        "model_loaded": model is not None,
        "model_name": model_name
    }


@app.post("/predict", response_model=PricingOutput)
def predict_price(data: PricingInput):
    """
    Predict the optimal price for a product based on input features.

    Takes market conditions, inventory data, competitor pricing, and other
    features to predict the optimal selling price using the trained ML model.
    """
    # Check if model is loaded
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please run pricing_model.py to train and save the model first."
        )

    # Build feature vector (initialize all features to 0)
    input_df = pd.DataFrame(0, index=[0], columns=feature_names)

    # Map numeric features from request
    numeric_fields = {
        'inventory_level': data.inventory_level,
        'units_sold': data.units_sold,
        'units_ordered': data.units_ordered,
        'demand_forecast': data.demand_forecast,
        'discount': data.discount,
        'holiday_promotion': data.holiday_promotion,
        'competitor_pricing': data.competitor_pricing,
        'visitors': data.visitors,
        'cost': data.cost,
        'demand_ratio': data.demand_ratio,
        'inventory_pressure': data.inventory_pressure,
        'stock_remaining': data.stock_remaining,
        'conversion_rate': data.conversion_rate,
        'traffic_intensity': data.traffic_intensity,
        'day_of_week': data.day_of_week,
        'month': data.month,
        'is_weekend': data.is_weekend,
    }

    for key, val in numeric_fields.items():
        if key in input_df.columns:
            input_df[key] = val

    # Handle one-hot encoded categorical features
    categorical_values = {
        'category': data.category,
        'region': data.region,
        'seasonality': data.seasonality,
        'weather_condition': data.weather_condition
    }

    for prefix, value in categorical_values.items():
        if value:
            col_name = f"{prefix}_{value}"
            if col_name in input_df.columns:
                input_df[col_name] = 1

    # Make prediction
    predicted_price = float(model.predict(input_df)[0])

    # Calculate margin analysis
    estimated_margin = predicted_price - data.cost
    margin_pct = (estimated_margin / predicted_price * 100) if predicted_price > 0 else 0

    # Determine pricing position
    if predicted_price > data.competitor_pricing:
        position = f"Premium (${predicted_price - data.competitor_pricing:.2f} above competitor)"
    elif predicted_price < data.competitor_pricing:
        position = f"Competitive (${data.competitor_pricing - predicted_price:.2f} below competitor)"
    else:
        position = "At parity with competitor"

    return PricingOutput(
        predicted_price=round(predicted_price, 2),
        model_used=model_name,
        confidence_r2=round(model_package['r2_score'], 4),
        competitor_price=data.competitor_pricing,
        estimated_margin=round(estimated_margin, 2),
        margin_percent=round(margin_pct, 1),
        pricing_position=position
    )
