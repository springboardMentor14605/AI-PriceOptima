# -------------------------------
# STEP 1: IMPORT LIBRARIES
# -------------------------------
import pandas as pd
import numpy as np

from sklearn.metrics import mean_squared_error
from sklearn.model_selection import RandomizedSearchCV

import xgboost as xgb
import matplotlib.pyplot as plt


# -------------------------------
# STEP 2: LOAD DATASET
# -------------------------------
df = pd.read_csv("feature_engineered_dynamic_pricing_dataset.csv")
print("✅ Dataset Loaded Successfully")

df.columns = df.columns.str.lower().str.replace(" ", "_")

required_cols = ["date", "units_sold", "price"]
for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"❌ '{col}' column not found!")

df["date"] = pd.to_datetime(df["date"], errors="coerce")


# -------------------------------
# STEP 3: TIME-BASED SPLIT
# -------------------------------
df = df.sort_values("date")

train = df[df["date"] < "2022-10-01"].copy()
test = df[df["date"] >= "2022-10-01"].copy()

# 🔥 IMPORTANT FIX: reset index
test = test.reset_index(drop=True)

print("✅ Time-based split done")


# -------------------------------
# STEP 4: FEATURES & TARGET
# -------------------------------
X_train = train.drop(["units_sold", "date"], axis=1, errors='ignore')
y_train = train["units_sold"]

X_test = test.drop(["units_sold", "date"], axis=1, errors='ignore')
y_test = test["units_sold"]

X_train = X_train.apply(pd.to_numeric, errors='coerce').fillna(0)
X_test = X_test.apply(pd.to_numeric, errors='coerce').fillna(0)


# -------------------------------
# STEP 5: MODEL
# -------------------------------
xgb_model = xgb.XGBRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=8,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1
)


# -------------------------------
# STEP 6: TUNING
# -------------------------------
params = {
    "max_depth": [4, 6, 8],
    "learning_rate": [0.01, 0.05, 0.1]
}

search = RandomizedSearchCV(
    xgb_model,
    param_distributions=params,
    n_iter=5,
    cv=3,
    verbose=1,
    n_jobs=-1
)

search.fit(X_train, y_train)
xgb_model = search.best_estimator_

print("✅ Best Model Selected")


# -------------------------------
# STEP 7: TRAIN
# -------------------------------
xgb_model.fit(X_train, y_train)


# -------------------------------
# STEP 8: EVALUATE
# -------------------------------
y_pred = xgb_model.predict(X_test)

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print("📊 RMSE:", rmse)


# -------------------------------
# STEP 9: FEATURE IMPORTANCE
# -------------------------------
xgb.plot_importance(xgb_model)
plt.title("Feature Importance")
plt.show()


# -------------------------------
# STEP 10: PRICE OPTIMIZATION (FINAL FIX)
# -------------------------------
print("🚀 Running Optimization...")

price_multipliers = [0.8, 0.9, 1.0, 1.1, 1.2]

scenario_list = []

for m in price_multipliers:
    temp = test.copy()
    temp["price"] = temp["price"] * m
    temp["scenario_id"] = np.arange(len(test))   # 🔥 KEY FIX
    scenario_list.append(temp)

scenarios = pd.concat(scenario_list, ignore_index=True)

# Prepare features
X_scenarios = scenarios[X_train.columns]
X_scenarios = X_scenarios.apply(pd.to_numeric, errors='coerce').fillna(0)

# Predict
scenarios["demand"] = xgb_model.predict(X_scenarios)
scenarios["revenue"] = scenarios["demand"] * scenarios["price"]

# 🔥 KEY FIX: group using scenario_id
best = scenarios.loc[scenarios.groupby("scenario_id")["revenue"].idxmax()]

# Assign safely
test["optimal_price"] = best["price"].values
test["ml_revenue"] = best["revenue"].values


# -------------------------------
# STEP 11: BASELINE
# -------------------------------
test["baseline_revenue"] = test["price"] * test["units_sold"]

ml_revenue = test["ml_revenue"].sum()
baseline_revenue = test["baseline_revenue"].sum()

lift = (ml_revenue - baseline_revenue) / baseline_revenue * 100

print("\n🚀 Revenue Lift (%):", lift)


# -------------------------------
# STEP 12: OVERFITTING CHECK
# -------------------------------
train_pred = xgb_model.predict(X_train)
test_pred = xgb_model.predict(X_test)

print("\n📊 Overfitting Check:")
print("Train RMSE:", np.sqrt(mean_squared_error(y_train, train_pred)))
print("Test RMSE:", np.sqrt(mean_squared_error(y_test, test_pred)))


# -------------------------------
# DONE
# -------------------------------
print("\n🎯 Project Completed Successfully!")
import joblib

joblib.dump(xgb_model, "pricing_model.pkl")
print("✅ Model saved successfully")