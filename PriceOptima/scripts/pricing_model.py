"""
===========================================================
AI PriceOptima – Advanced ML Pricing Model
===========================================================

This script performs:
  1. Data loading & chronological sorting (Time-based split)
  2. Feature Engineering (Predicting `units_sold` using `price`)
  3. Model training (XGBoost + LightGBM) with Hyperparameter Tuning
  4. Real Price Optimization (Simulating prices to maximize Revenue)
  5. Backtesting against rule-based baseline
  6. SHAP Explainability & Saving best model
===========================================================
"""

import os
import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import RandomizedSearchCV
import joblib
import warnings
import shap
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')

# ============================================================
# STEP 1: DATA LOADING
# ============================================================
print("=" * 60)
print("   AI PriceOptima – Advanced Model Training Pipeline")
print("=" * 60)

data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'feature_engineered_dataset.csv')
df = pd.read_csv(data_path)
print(f"\n✅ Dataset loaded: {df.shape[0]} rows × {df.shape[1]} columns")

# ============================================================
# STEP 2: DATA PREPARATION & TIME-BASED SPLIT
# ============================================================
print("\n" + "-" * 60)
print("📋 STEP 2: Data Preparation & Time-Based Split")
print("-" * 60)

# Sort by date to avoid future data leakage
df = df.sort_values("date").reset_index(drop=True)

# Handle NaNs
df = df.replace([np.inf, -np.inf], np.nan)
numeric_cols = df.select_dtypes(include=np.number).columns
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
cat_cols = df.select_dtypes(include='object').columns
for col in cat_cols:
    df[col] = df[col].fillna(df[col].mode()[0])

# Time-based Split (Last 20% for testing)
split_idx = int(len(df) * 0.8)
train_df = df.iloc[:split_idx].copy()
test_df = df.iloc[split_idx:].copy()

print(f"   → Training set (Past data):   {len(train_df)} samples")
print(f"   → Testing set  (Future data): {len(test_df)} samples")

# ============================================================
# STEP 3: FEATURE DEFINITION
# ============================================================
print("\n" + "-" * 60)
print("🎯 STEP 3: Defining Features and Target")
print("-" * 60)

# Target is 'units_sold' (Demand). Price is a FEATURE to predict demand.
target = 'units_sold'

# Drop target, identifiers, and price-derived metrics that cause leakage
drop_cols = ['units_sold', 'date', 'store_id', 'product_id', 
             'discounted_price', 'profit_margin', 'margin_percent', 
             'revenue', 'price_demand_ratio', 'competitor_gap']

# Encode categorical columns globally first to keep feature alignment
X_all = df.drop(columns=drop_cols, errors='ignore')
cat_cols_to_encode = X_all.select_dtypes(include='object').columns.tolist()

df_encoded = pd.get_dummies(df, columns=cat_cols_to_encode, drop_first=True)

# Re-split after encoding
train_df_encoded = df_encoded.iloc[:split_idx].copy()
test_df_encoded = df_encoded.iloc[split_idx:].copy()

X_train = train_df_encoded.drop(columns=drop_cols, errors='ignore')
y_train = train_df_encoded[target]

X_test = test_df_encoded.drop(columns=drop_cols, errors='ignore')
y_test = test_df_encoded[target]

feature_names = X_train.columns.tolist()
print(f"   → Features: {len(feature_names)}")
print("   → Target: units_sold")
print("   → Note: Tree-based models do not require normalization.")

# ============================================================
# STEP 4: MODEL TRAINING (XGBoost & LightGBM)
# ============================================================
print("\n" + "-" * 60)
print("🤖 STEP 4: Model Training & Tuning")
print("-" * 60)

print("\n   Training Model 1: XGBoost (with RandomizedSearchCV)...")
xgb_base = xgb.XGBRegressor(random_state=42)
param_dist = {
    "n_estimators": [100, 200],
    "max_depth": [4, 6, 8],
    "learning_rate": [0.01, 0.05, 0.1],
    "subsample": [0.8, 1.0]
}
search = RandomizedSearchCV(xgb_base, param_distributions=param_dist, n_iter=5, scoring='neg_root_mean_squared_error', cv=3, random_state=42, n_jobs=-1)
search.fit(X_train, y_train)
xgb_model = search.best_estimator_

print("\n   Training Model 2: LightGBM...")
lgb_model = lgb.LGBMRegressor(n_estimators=200, learning_rate=0.05, max_depth=6, random_state=42, n_jobs=-1)
lgb_model.fit(X_train, y_train)

# ============================================================
# STEP 5: EVALUATION
# ============================================================
print("\n" + "-" * 60)
print("📊 STEP 5: Model Evaluation (RMSE on Demand)")
print("-" * 60)

xgb_pred = xgb_model.predict(X_test)
lgb_pred = lgb_model.predict(X_test)

rmse_xgb = np.sqrt(mean_squared_error(y_test, xgb_pred))
rmse_lgb = np.sqrt(mean_squared_error(y_test, lgb_pred))

print(f"   → XGBoost RMSE:  {rmse_xgb:.4f}")
print(f"   → LightGBM RMSE: {rmse_lgb:.4f}")

if rmse_xgb <= rmse_lgb:
    best_model = xgb_model
    best_name = "XGBoost Regressor"
else:
    best_model = lgb_model
    best_name = "LightGBM Regressor"
    
print(f"\n🏆 Best Model for Demand Prediction: {best_name}")

# ============================================================
# STEP 6: REAL PRICE OPTIMIZATION SIMULATION
# ============================================================
print("\n" + "-" * 60)
print("💰 STEP 6: Real Price Optimization & Backtesting")
print("-" * 60)

# We optimize the price for the first 100 rows in test_df for speed in this demonstration
subset_test_df = test_df_encoded.head(500).copy()
subset_X_test = X_test.head(500).copy()
subset_y_test = y_test.head(500).copy()

def find_best_price(row, index):
    base_price = row['price']
    # Simulate prices from 80% to 120%
    price_multipliers = [0.8, 0.9, 1.0, 1.1, 1.2]
    
    best_price = base_price
    best_revenue = 0
    
    # Prepare feature vector (needs to match exact X_test columns)
    feats = subset_X_test.loc[index].copy()
    
    for mult in price_multipliers:
        simulated_price = base_price * mult
        feats['price'] = simulated_price
        
        # Predict demand for this simulated price
        # Convert to DF to keep feature names
        pred_demand = best_model.predict(pd.DataFrame([feats]))[0]
        
        revenue = pred_demand * simulated_price
        if revenue > best_revenue:
            best_revenue = revenue
            best_price = simulated_price
            
    return best_price

print("   → Simulating 5 price points per product to find optimal revenue...")
subset_test_df['optimal_price'] = [find_best_price(row, idx) for idx, row in subset_test_df.iterrows()]

# Compare against Baseline (Rule-based dynamic price * actual units sold)
# Since dynamic_price might not exist, we use actual price as baseline
subset_test_df['baseline_revenue'] = subset_test_df['price'] * subset_test_df['units_sold']

# ML Revenue: We assume the ML recommended price yields the model's predicted demand for that price 
# However, to be conservative, we calculate ML Revenue. Let's calculate expected ML demand at optimal ML price.
ml_revenues = []
for idx, row in subset_test_df.iterrows():
    feats = subset_X_test.loc[idx].copy()
    opt_p = row['optimal_price']
    feats['price'] = opt_p
    opt_demand = best_model.predict(pd.DataFrame([feats]))[0]
    ml_revenues.append(opt_p * opt_demand)

subset_test_df['ml_revenue'] = ml_revenues

baseline_total = subset_test_df['baseline_revenue'].sum()
ml_total = sum(ml_revenues)

if baseline_total > 0:
    lift = ((ml_total - baseline_total) / baseline_total) * 100
else:
    lift = 0

print(f"   → Baseline Revenue (Subset): ${baseline_total:,.2f}")
print(f"   → ML Optimized Revenue:      ${ml_total:,.2f}")
print(f"   → ML Revenue Lift:           {lift:+.2f}%\n")

# ============================================================
# STEP 7: SAVE BEST MODEL & SHAP EXPLAINER
# ============================================================
print("-" * 60)
print("💾 STEP 7: Saving Best Model & Generating Explainability")
print("-" * 60)

model_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, 'advanced_pricing_model.pkl')

model_package = {
    'model': best_model,
    'model_name': best_name,
    'feature_names': feature_names,
    'cat_cols': cat_cols_to_encode,
    'drop_cols': drop_cols,
    'target': target
}

joblib.dump(model_package, model_path)
print(f"   ✅ Advanced Model saved to: {os.path.abspath(model_path)}")

# Explainability: Save a feature importance plot
try:
    print("   → Generating SHAP summary plot...")
    # Use a small sample for SHAP to avoid long computation
    shap_sample = X_test.sample(n=min(200, len(X_test)), random_state=42)
    explainer = shap.Explainer(best_model)
    shap_values = explainer(shap_sample)
    
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, shap_sample, show=False)
    shap_plot_path = os.path.join(model_dir, 'shap_summary.png')
    plt.savefig(shap_plot_path, bbox_inches='tight')
    plt.close()
    print(f"   ✅ SHAP explanation saved to: {os.path.abspath(shap_plot_path)}")
except Exception as e:
    print(f"   ⚠️ Could not generate SHAP plot: {e}")

print("\n" + "=" * 60)
print("   ✅ Advanced ML Pipeline Complete! Pipeline is ready for deployment.")
print("=" * 60)
