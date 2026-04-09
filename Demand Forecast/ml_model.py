import pandas as pd
import numpy as np

from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder

import xgboost as xgb
import lightgbm as lgb

# ==============================
# 1. LOAD DATA
# ==============================
df = pd.read_csv(r"D:\Infosys-Project\AI-PriceOptima\Feature Engineering\feature_engineered_dataset.csv")

# Sort by date (IMPORTANT for time series)
df = df.sort_values("date")

# ==============================
# 2. TRAIN-TEST SPLIT (TIME BASED)
# ==============================
train = df[df["date"] < "2022-10-01"]
test = df[df["date"] >= "2022-10-01"]

# ==============================
# 3. DEFINE FEATURES & TARGET
# ==============================
X_train = train.drop(["units_sold", "date"], axis=1)
y_train = train["units_sold"]

X_test = test.drop(["units_sold", "date"], axis=1)
y_test = test["units_sold"]

# Save feature columns (VERY IMPORTANT)
feature_columns = X_train.columns

# ==============================
# 4. ENCODE CATEGORICAL FEATURES
# ==============================
categorical_cols = [
    'store_id',
    'product_id',
    'category',
    'region',
    'weather_condition',
    'seasonality'
]

# Store encoders for reuse
encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    X_train[col] = le.fit_transform(X_train[col].astype(str))
    X_test[col] = le.transform(X_test[col].astype(str))
    encoders[col] = le

# ==============================
# 5. TRAIN XGBOOST
# ==============================
xgb_model = xgb.XGBRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=8,
    subsample=0.8,
    colsample_bytree=0.8
)

xgb_model.fit(X_train, y_train)

# Evaluate
y_pred = xgb_model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print("XGBoost RMSE:", rmse)

# ==============================
# 6. TRAIN LIGHTGBM
# ==============================
lgb_model = lgb.LGBMRegressor(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=6
)

lgb_model.fit(X_train, y_train)

# Evaluate
y_pred_lgb = lgb_model.predict(X_test)
rmse_lgb = np.sqrt(mean_squared_error(y_test, y_pred_lgb))
print("LightGBM RMSE:", rmse_lgb)

# ==============================
# 7. PRICE OPTIMIZATION FUNCTION (FIXED)
# ==============================

counter = 0 

def find_best_price(row):
    global counter
    counter += 1

    if counter % 1000 == 0:
        print(f"Processed {counter} rows... Remaining: {len(df) - counter}")

    prices = [row["price"] * i for i in [0.8, 0.9, 1.0, 1.1, 1.2]]
    
    best_price = row["price"]
    best_revenue = 0
    
    for p in prices:
        temp = row.copy()
        temp["price"] = p
        
        # Convert to DataFrame
        temp_df = pd.DataFrame([temp])
        
        # Keep ONLY training columns
        temp_df = temp_df[feature_columns]
        
        # Apply SAME encoding (CRITICAL FIX)
        for col in categorical_cols:
            temp_df[col] = encoders[col].transform(temp_df[col].astype(str))
        
        # Predict demand
        demand = xgb_model.predict(temp_df)[0]
        
        revenue = demand * p
        
        if revenue > best_revenue:
            best_revenue = revenue
            best_price = p
    
    return best_price

# ==============================
# 8. APPLY OPTIMAL PRICING
# ==============================
df["optimal_price"] = df.apply(find_best_price, axis=1)

# ==============================
# 9. BACKTESTING
# ==============================
revenues = []

for i in range(len(test)):
    row = test.iloc[i]
    
    price = find_best_price(row)
    
    revenue = price * row["units_sold"]
    revenues.append(revenue)

ml_revenue = sum(revenues)

# ==============================
# 10. BASELINE COMPARISON
# ==============================
if "dynamic_price" not in test.columns:
    print("⚠️ WARNING: dynamic_price not found. Run baseline model first.")
    test["dynamic_price"] = test["price"]  # fallback

baseline = test["dynamic_price"] * test["units_sold"]

lift = (ml_revenue - baseline.sum()) / baseline.sum() * 100

print("Revenue Lift (%):", lift)

# ==============================
# 11. SAVE OUTPUT
# ==============================
df.to_csv("D:/Infosys-Project/AI-PriceOptima/Outputs/ml_pricing_output.csv", index=False)

print("ML Pricing completed successfully!")