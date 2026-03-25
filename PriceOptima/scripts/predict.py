"""
===========================================================
AI PriceOptima – Prediction Script
===========================================================

This script:
  1. Loads the saved best pricing model
  2. Takes sample input data
  3. Predicts the optimal price
  4. Prints the predicted price

Usage:
  python predict.py
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
print("   AI PriceOptima – Price Prediction")
print("=" * 60)

model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'best_pricing_model.pkl')

if not os.path.exists(model_path):
    print("ERROR: Model file not found!")
    print(f"   Expected at: {os.path.abspath(model_path)}")
    print("   Please run 'python pricing_model.py' first to train and save the model.")
    exit(1)

# Load the model package (contains model + metadata)
model_package = joblib.load(model_path)
model = model_package['model']
feature_names = model_package['feature_names']
model_name = model_package['model_name']

print(f"\n[OK] Model loaded: {model_name}")
print(f"   -> R2 Score: {model_package['r2_score']:.4f}")
print(f"   -> Expected features: {len(feature_names)}")

# ============================================================
# STEP 2: PREPARE SAMPLE INPUT
# ============================================================
print("\n" + "-" * 60)
print("SAMPLE INPUT DATA")
print("-" * 60)

# Create a sample input that matches the feature-engineered dataset structure
# These values represent a realistic product scenario
# NOTE: We do NOT include leaky features (discounted_price, profit_margin,
#       margin_percent, revenue, price_demand_ratio, competitor_gap)
#       as they were removed during training to prevent data leakage.
sample_data = {
    'inventory_level': 120,
    'units_sold': 45,
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

# Print sample values
for key, val in sample_data.items():
    print(f"   {key:<25} = {val}")

# ============================================================
# STEP 3: CREATE FEATURE VECTOR
# ============================================================
# Build a DataFrame with all required features (initialized to 0)
input_df = pd.DataFrame(0, index=[0], columns=feature_names)

# Fill in the numeric features from our sample
for key, val in sample_data.items():
    if key in input_df.columns:
        input_df[key] = val

# Set the relevant one-hot encoded category
# (set one of the encoded columns to 1 based on scenario)
for col in feature_names:
    if col.startswith('category_') and 'Electronics' in col:
        input_df[col] = 1
    if col.startswith('region_') and 'North' in col:
        input_df[col] = 1
    if col.startswith('seasonality_') and 'Summer' in col:
        input_df[col] = 1
    if col.startswith('weather_condition_') and 'Clear' in col:
        input_df[col] = 1

# ============================================================
# STEP 4: PREDICT PRICE
# ============================================================
print("\n" + "-" * 60)
print("PREDICTION RESULT")
print("-" * 60)

predicted_price = model.predict(input_df)[0]

print(f"\n   Predicted Optimal Price  : ${predicted_price:.2f}")
print(f"   Product Category         : Electronics")
print(f"   Region                   : North")
print(f"   Weather                  : Clear")
print(f"   Season                   : Summer")
print(f"   Competitor Price         : ${sample_data['competitor_pricing']:.2f}")
print(f"   Cost                     : ${sample_data['cost']:.2f}")

# Margin analysis
predicted_margin = predicted_price - sample_data['cost']
margin_pct = (predicted_margin / predicted_price) * 100 if predicted_price > 0 else 0

print(f"\n   Estimated Profit Margin: ${predicted_margin:.2f} ({margin_pct:.1f}%)")

if predicted_price > sample_data['competitor_pricing']:
    diff = predicted_price - sample_data['competitor_pricing']
    print(f"   Price is ${diff:.2f} ABOVE competitor -> Premium positioning")
elif predicted_price < sample_data['competitor_pricing']:
    diff = sample_data['competitor_pricing'] - predicted_price
    print(f"   Price is ${diff:.2f} BELOW competitor -> Competitive advantage")
else:
    print(f"   Price matches competitor exactly")

print("\n" + "=" * 60)
print("   Prediction Complete!")
print("=" * 60)
