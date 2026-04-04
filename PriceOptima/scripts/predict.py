"""
===========================================================
AI PriceOptima – Advanced Prediction Script
===========================================================

This script:
  1. Loads the saved advanced pricing model
  2. Takes sample input data (without price)
  3. Simulates multiple candidate prices
  4. Predicts demand (units_sold) for each price
  5. Selects the price that maximizes expected revenue
  6. Prints the result
===========================================================
"""

import os
import pandas as pd
import numpy as np
import joblib
import warnings

warnings.filterwarnings('ignore')

# ============================================================
# STEP 1: LOAD SAVED MODEL
# ============================================================
print("=" * 60)
print("   AI PriceOptima – Real Price Optimization Prediction")
print("=" * 60)

model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'advanced_pricing_model.pkl')

if not os.path.exists(model_path):
    print("ERROR: Model file not found!")
    print(f"   Expected at: {os.path.abspath(model_path)}")
    print("   Please run 'python scripts/pricing_model.py' first to train and save the model.")
    exit(1)

model_package = joblib.load(model_path)
model = model_package['model']
feature_names = model_package['feature_names']
model_name = model_package['model_name']
target = model_package['target']

print(f"\n[OK] Model loaded: {model_name}")
print(f"   -> Expected features: {len(feature_names)}")
print(f"   -> Predicting:        {target} (Demand)")

# ============================================================
# STEP 2: PREPARE SAMPLE INPUT
# ============================================================
print("\n" + "-" * 60)
print("SAMPLE INPUT DATA (Scenario)")
print("-" * 60)

# Sample base features (excluding 'price')
sample_data = {
    'inventory_level': 120,
    'units_ordered': 50,
    'demand_forecast': 48,
    'discount': 10.0,
    'holiday_promotion': 1,
    'competitor_pricing': 85.0,
    'visitors': 500,
    'cost': 60.0,
    'demand_ratio': 0.9375,
    'inventory_pressure': 0.375,
    'stock_remaining': 75,
    'conversion_rate': 0.09,
    'traffic_intensity': 4.167,
    'day_of_week': 3,
    'month': 6,
    'is_weekend': 0,
}

print("Base attributes:")
for key, val in sample_data.items():
    print(f"   {key:<25} = {val}")

# ============================================================
# STEP 3: PRICE OPTIMIZATION SIMULATION
# ============================================================
print("\n" + "-" * 60)
print("RUNNING OPTIMIZATION SIMULATION")
print("-" * 60)

# Build a DataFrame with all required features initialized to 0
input_df = pd.DataFrame(0, index=[0], columns=feature_names)

# Fill in the numeric features
for key, val in sample_data.items():
    if key in input_df.columns:
        input_df[key] = val

# Set category dummy variables manually for this sample
for col in feature_names:
    if col == 'category_Electronics':
        input_df[col] = 1
    elif col == 'region_North':
        input_df[col] = 1
    elif col == 'seasonality_Summer':
        input_df[col] = 1
    elif col == 'weather_condition_Clear':
        input_df[col] = 1

# We simulate prices around the competitor pricing (e.g. from 80% to 120%)
base_sim_price = sample_data['competitor_pricing']
multipliers = np.linspace(0.8, 1.2, 11)  # 11 distinct price points

best_price = base_sim_price
best_revenue = 0
best_demand = 0

print("\nSimulating candidate prices...")
print(f"{'Price':<10} | {'Expected Demand':<20} | {'Expected Revenue'}")
print("-" * 55)

for m in multipliers:
    candidate_price = base_sim_price * m
    input_df['price'] = candidate_price
    
    # Predict expected demand (units sold)
    predicted_demand = model.predict(input_df)[0]
    
    # We cannot have negative demand
    predicted_demand = max(0, predicted_demand)
    
    expected_revenue = candidate_price * predicted_demand
    
    print(f"${candidate_price:<9.2f} | {predicted_demand:<20.2f} | ${expected_revenue:.2f}")
    
    if expected_revenue > best_revenue:
        best_revenue = expected_revenue
        best_price = candidate_price
        best_demand = predicted_demand

# ============================================================
# STEP 4: PREDICTION RESULT
# ============================================================
print("\n" + "=" * 60)
print("🏆 OPTIMAL PRICE RECOMMENDATION")
print("=" * 60)

print(f"   Recommended Price        : ${best_price:.2f}")
print(f"   Expected Demand          : {best_demand:.1f} units")
print(f"   Maximum Expected Revenue : ${best_revenue:.2f}")
print(f"   Competitor Price         : ${sample_data['competitor_pricing']:.2f}")
print(f"   Cost                     : ${sample_data['cost']:.2f}")

predicted_margin = best_price - sample_data['cost']
margin_pct = (predicted_margin / best_price) * 100 if best_price > 0 else 0

print(f"\n   Estimated Profit Margin per unit: ${predicted_margin:.2f} ({margin_pct:.1f}%)")

if best_price > sample_data['competitor_pricing']:
    diff = best_price - sample_data['competitor_pricing']
    print(f"   Positioning: Premium (+${diff:.2f} compared to competitor)")
elif best_price < sample_data['competitor_pricing']:
    diff = sample_data['competitor_pricing'] - best_price
    print(f"   Positioning: Competitive (-${diff:.2f} compared to competitor)")
else:
    print(f"   Positioning: Price matched with competitor")

print("\n===========================================================")
