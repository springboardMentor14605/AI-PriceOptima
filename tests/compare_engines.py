import sys
import os
import pandas as pd

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.pricing.baseline_engine import get_baseline_price
import joblib

def compare():
    print("AI: PriceOptima - Engine Comparison Report")
    print("="*50)
    
    # Load ML models for comparison
    models_dir = "models"
    xgb_model = joblib.load(os.path.join(models_dir, "xgb_model.joblib"))
    feature_names = joblib.load(os.path.join(models_dir, "feature_names.joblib"))
    
    # Test Scenarios
    scenarios = [
        {"desc": "Low Stock / Normal Price", "cat": "Electronics", "reg": "South", "inv": 10, "price": 500},
        {"desc": "High Stock / Normal Price", "cat": "Clothing", "reg": "North", "inv": 200, "price": 50},
        {"desc": "Optimal Stock", "cat": "Home & Kitchen", "reg": "West", "inv": 50, "price": 120},
    ]
    
    results = []
    
    for s in scenarios:
        # 1. Baseline
        base_price = get_baseline_price(s["price"], s["inv"])
        
        # 2. ML Prediction (Demand)
        input_dict = {
            "inventory_level": [s["inv"]],
            "price": [s["price"]],
            "category_" + s["cat"]: [1],
            "region_" + s["reg"]: [1]
        }
        df_input = pd.DataFrame(input_dict)
        for col in feature_names:
            if col not in df_input.columns:
                df_input[col] = 0
        df_input = df_input[feature_names]
        
        pred_demand = xgb_model.predict(df_input)[0]
        
        results.append({
            "Scenario": s["desc"],
            "Current Price": s["price"],
            "Inventory": s["inv"],
            "Baseline Rec": base_price,
            "ML Pred Demand": round(pred_demand, 2)
        })
        
    df_results = pd.DataFrame(results)
    print(df_results)
    print("\nObservation: Baseline reacts strictly to inventory (10% up/down).")
    print("ML provides demand elasticity used for more granular adjustments.")

if __name__ == "__main__":
    compare()
