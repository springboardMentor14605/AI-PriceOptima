"""
===========================================================
AI PriceOptima – Pricing Model (Training & Evaluation)
===========================================================

This script performs:
  1. Data loading & preparation (encoding, splitting)
  2. Model training (Linear Regression + Random Forest)
  3. Model evaluation (MSE, R2 comparison)
  4. Saving the best model to disk

Usage:
  python pricing_model.py

Output:
  - Model comparison printed to console
  - Best model saved to ../models/best_pricing_model.pkl
===========================================================
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import warnings

warnings.filterwarnings('ignore')

# ============================================================
# STEP 1: DATA LOADING
# ============================================================
print("=" * 60)
print("   AI PriceOptima – Model Training Pipeline")
print("=" * 60)

# Load the feature-engineered dataset
data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'feature_engineered_dataset.csv')
df = pd.read_csv(data_path)
print(f"\n✅ Dataset loaded: {df.shape[0]} rows × {df.shape[1]} columns")

# ============================================================
# STEP 2: DATA PREPARATION
# ============================================================
print("\n" + "-" * 60)
print("📋 STEP 2: Data Preparation")
print("-" * 60)

# 2.1 Drop unnecessary columns
# 'date' is dropped because temporal info is captured via day_of_week, month, is_weekend
# 'store_id' and 'product_id' are identifiers, not useful for general pricing prediction
# IMPORTANT: Drop features derived from price (target) to prevent data leakage
# - discounted_price = price * (1 - discount/100) → directly uses price
# - profit_margin = price - cost → directly uses price
# - margin_percent = (profit_margin / price) * 100 → directly uses price
# - revenue = price * units_sold → directly uses price
# - price_demand_ratio = price / demand_forecast → directly uses price
# - competitor_gap = price - competitor_pricing → directly uses price
drop_cols = ['date', 'store_id', 'product_id',
             'discounted_price', 'profit_margin', 'margin_percent',
             'revenue', 'price_demand_ratio', 'competitor_gap']
df_model = df.drop(columns=drop_cols, errors='ignore')
print(f"   → Dropped columns: {drop_cols}")

# 2.1b Handle missing values (NaN) and infinite values
# Some rows may have NaN in day_of_week, month, is_weekend due to missing dates
nan_before = df_model.isnull().sum().sum()
# Replace infinite values with NaN first
df_model = df_model.replace([np.inf, -np.inf], np.nan)
# Fill NaN in numeric columns with median
numeric_cols_fill = df_model.select_dtypes(include=np.number).columns
df_model[numeric_cols_fill] = df_model[numeric_cols_fill].fillna(df_model[numeric_cols_fill].median())
# Fill NaN in categorical columns with mode
cat_cols_fill = df_model.select_dtypes(include='object').columns
for col in cat_cols_fill:
    df_model[col] = df_model[col].fillna(df_model[col].mode()[0])
nan_after = df_model.isnull().sum().sum()
print(f"   → NaN values handled: {nan_before} → {nan_after}")

# 2.2 Separate target and features
target = 'price'
X = df_model.drop(columns=[target])
y = df_model[target]
print(f"   → Target variable: '{target}'")
print(f"   → Feature columns: {X.shape[1]}")

# 2.3 Handle categorical variables using One-Hot Encoding
# Identify categorical columns
cat_cols = X.select_dtypes(include='object').columns.tolist()
print(f"   → Categorical columns to encode: {cat_cols}")

X = pd.get_dummies(X, columns=cat_cols, drop_first=True)
print(f"   → Shape after encoding: {X.shape}")

# 2.4 Save feature names for later use
feature_names = X.columns.tolist()

# 2.5 Train-Test Split (80/20)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"\n   → Training set: {X_train.shape[0]} samples")
print(f"   → Testing set:  {X_test.shape[0]} samples")

# ============================================================
# STEP 3: MODEL TRAINING
# ============================================================
print("\n" + "-" * 60)
print("🤖 STEP 3: Model Training")
print("-" * 60)

# --- Model 1: Linear Regression (Baseline) ---
print("\n   Training Model 1: Linear Regression (Baseline)...")
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)
lr_pred = lr_model.predict(X_test)
print("   ✅ Linear Regression trained successfully!")

# --- Model 2: Random Forest Regressor ---
print("\n   Training Model 2: Random Forest Regressor...")
rf_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1  # Use all CPU cores for faster training
)
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)
print("   ✅ Random Forest Regressor trained successfully!")

# ============================================================
# STEP 4: MODEL EVALUATION
# ============================================================
print("\n" + "-" * 60)
print("📊 STEP 4: Model Evaluation")
print("-" * 60)

# Calculate metrics for both models
lr_mse = mean_squared_error(y_test, lr_pred)
lr_r2 = r2_score(y_test, lr_pred)

rf_mse = mean_squared_error(y_test, rf_pred)
rf_r2 = r2_score(y_test, rf_pred)

# Print comparison table
print("\n" + "=" * 60)
print("        📊 MODEL COMPARISON RESULTS")
print("=" * 60)
print(f"{'Model':<25} {'MSE':>12} {'R² Score':>12}")
print("-" * 60)
print(f"{'Linear Regression':<25} {lr_mse:>12.4f} {lr_r2:>12.4f}")
print(f"{'Random Forest':<25} {rf_mse:>12.4f} {rf_r2:>12.4f}")
print("=" * 60)

# Determine best model
if rf_r2 > lr_r2:
    best_model = rf_model
    best_name = "Random Forest Regressor"
    best_r2 = rf_r2
    best_mse = rf_mse
else:
    best_model = lr_model
    best_name = "Linear Regression"
    best_r2 = lr_r2
    best_mse = lr_mse

print(f"\n🏆 Best Model: {best_name}")
print(f"   → R² Score: {best_r2:.4f}")
print(f"   → MSE:      {best_mse:.4f}")

# ============================================================
# STEP 5: FEATURE IMPORTANCE (Random Forest)
# ============================================================
print("\n" + "-" * 60)
print("🔍 STEP 5: Top 10 Most Important Features (Random Forest)")
print("-" * 60)

importance = pd.Series(rf_model.feature_importances_, index=feature_names)
top_features = importance.sort_values(ascending=False).head(10)

for rank, (feat, imp) in enumerate(top_features.items(), 1):
    bar = "█" * int(imp * 100)
    print(f"   {rank:>2}. {feat:<30} {imp:.4f}  {bar}")

# ============================================================
# STEP 6: SAVE BEST MODEL
# ============================================================
print("\n" + "-" * 60)
print("💾 STEP 6: Saving Best Model")
print("-" * 60)

model_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(model_dir, exist_ok=True)

model_path = os.path.join(model_dir, 'best_pricing_model.pkl')

# Save model along with feature names and scaler info for prediction
model_package = {
    'model': best_model,
    'model_name': best_name,
    'feature_names': feature_names,
    'r2_score': best_r2,
    'mse': best_mse,
    'categorical_columns': cat_cols,
    'drop_columns': drop_cols,
    'target': target
}

joblib.dump(model_package, model_path)
print(f"   ✅ Model saved to: {os.path.abspath(model_path)}")
print(f"   → Model: {best_name}")
print(f"   → R² Score: {best_r2:.4f}")

print("\n" + "=" * 60)
print("   ✅ Pipeline Complete! Model is ready for predictions.")
print("=" * 60)
