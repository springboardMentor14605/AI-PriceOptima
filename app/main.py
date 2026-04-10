from fastapi import FastAPI
from pydantic import BaseModel
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Dynamic Pricing API")

# Allow CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PricingRequest(BaseModel):
    price: float
    inventory: int
    day_of_week: int

@app.post("/pricing/predict")
def predict_price(req: PricingRequest):
    price = req.price
    cost = price * 0.50 # Baseline assumption
    
    # ---------------------------------------------------------
    # ADVANCED ML MODEL PIPELINE WIRING (MILESTONE 5)
    # ---------------------------------------------------------
    try:
        import xgboost as xgb
        import pandas as pd
        import numpy as np
        import pickle
        import os
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_dir, "app", "models", "xgboost_model.pkl")
        
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            
            # Construct standard feature vector payload
            features = {
                "price": price,
                "cost": cost,
                "inventory_pressure": max(0.1, min(2.0, req.inventory / 100)),
                "demand_ratio": 1.0,
                "competitor_gap": 0.0,
                "is_weekend": 1 if req.day_of_week >= 5 else 0,
                "traffic_intensity": 0.5,
                "category": 1,
                "region": 1,
                "seasonality": 1,
                "weather_condition": 1,
                "holiday/promotion": 0
            }
            
            df_cand = pd.DataFrame([features])
            
            # Dynamically resolve missing columns based on training signature
            if hasattr(model, "feature_names_in_"):
                expected_cols = model.feature_names_in_
                for c in expected_cols:
                    if c not in df_cand.columns:
                        df_cand[c] = 0.0
                df_cand = df_cand[expected_cols]
                
            # Perform matrix price simulation
            multipliers = np.linspace(0.8, 1.25, 9)
            best_revenue = -1
            best_price = price
            
            for mult in multipliers:
                cand_price = price * mult
                df_cand["price"] = cand_price
                
                # Rule Guard: Profit Floor
                if cand_price >= cost * 1.15:
                    pred_demand = max(model.predict(df_cand)[0], 0)
                    sim_revenue = pred_demand * cand_price
                    if sim_revenue > best_revenue:
                        best_revenue = sim_revenue
                        best_price = cand_price
                        
            return {
                "original_price": req.price, 
                "dynamic_price": round(best_price, 2),
                "inventory": req.inventory,
                "day_of_week": req.day_of_week,
                "engine": "Machine Learning (XGBoost)"
            }
    except Exception as e:
        print(f"ML Engine Fallback | Reason: {e}")
        pass
        
    # ---------------------------------------------------------
    # RULE-BASED ENGINE FALLBACK (MILESTONE 4)
    # ---------------------------------------------------------
    
    # Apply time rule (>=5 represents weekend - Saturday=5, Sunday=6)
    if req.day_of_week >= 5:
        price *= 1.10
    
    # Apply inventory rule
    if req.inventory < 50:
        price *= 1.15
    elif req.inventory > 200:
        price *= 0.90
        
    # Price floor guard
    min_allowed = cost * 1.10
    price = max(price, min_allowed)
        
    return {
        "original_price": req.price, 
        "dynamic_price": round(price, 2),
        "inventory": req.inventory,
        "day_of_week": req.day_of_week,
        "engine": "Rule-Based Engine"
    }

import csv
from collections import defaultdict
from datetime import datetime

@app.get("/kpi")
def get_kpi():
    """
    Returns aggregated KPIs based on the baseline pricing output.
    This simulates accessing a real database or processed metrics.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "Outputs", "baseline_pricing_output.csv")
    
    if not os.path.exists(file_path):
        return {"error": "KPI data not available yet."}
    
    base_revenue = 0.0
    dynamic_revenue = 0.0
    sum_base_price = 0.0
    sum_dynamic_price = 0.0
    total_units_sold = 0
    row_count = 0
    
    daily_stats = defaultdict(lambda: {"sum_base_price": 0.0, "sum_dynamic_price": 0.0, "daily_revenue": 0.0, "count": 0})
    
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                price = float(row.get('price', 0))
                units = float(row.get('units_sold', 0))
                dyn_price = float(row.get('dynamic_price', 0))
                dyn_rev = float(row.get('baseline_revenue', 0))
                date_str = row.get('date', '')
                
                base_revenue += price * units
                dynamic_revenue += dyn_rev
                sum_base_price += price
                sum_dynamic_price += dyn_price
                total_units_sold += int(units)
                row_count += 1
                
                if date_str:
                    try:
                        # Extract YYYY-MM-DD
                        dt_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        date_key = dt_obj.strftime("%Y-%m-%d")
                        daily_stats[date_key]["sum_base_price"] += price
                        daily_stats[date_key]["sum_dynamic_price"] += dyn_price
                        daily_stats[date_key]["daily_revenue"] += dyn_rev
                        daily_stats[date_key]["count"] += 1
                    except ValueError:
                        pass
            except Exception:
                pass
                
    if row_count == 0:
        return {"error": "No valid data found."}
        
    avg_base = sum_base_price / row_count
    avg_dyn = sum_dynamic_price / row_count
    
    kpis = {
        "total_revenue_baseline": round(base_revenue, 2),
        "total_revenue_dynamic": round(dynamic_revenue, 2),
        "revenue_uplift_percent": round(((dynamic_revenue - base_revenue) / base_revenue) * 100, 2) if base_revenue > 0 else 0,
        "avg_base_price": round(avg_base, 2),
        "avg_dynamic_price": round(avg_dyn, 2),
        "total_units_sold": total_units_sold
    }
    
    # Process chart data
    chart_data = []
    for date_key in sorted(daily_stats.keys()):
        stats = daily_stats[date_key]
        count = stats["count"]
        if count > 0:
            chart_data.append({
                "date": date_key,
                "avg_base_price": stats["sum_base_price"] / count,
                "avg_dynamic_price": stats["sum_dynamic_price"] / count,
                "daily_revenue": stats["daily_revenue"]
            })
            
    # Tail 30
    kpis["chart_data"] = chart_data[-30:]
    
    return kpis

@app.get("/health")
def health_check():
    return {"status": "healthy"}
