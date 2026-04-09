import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import xgboost as xgb
import lightgbm as lgb
import joblib
import os

# Define paths
DATA_PATH = "data/feature_engineered_dataset.csv"
MODEL_DIR = "models"

def train_and_save():
    """
    Loads the cleaned dataset, trains XGBoost and LightGBM models,
    and serializes them for use in the Serving API.
    """
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)

    # Define target variable: units_sold (demand prediction)
    y = df["units_sold"]

    # Define features: dropping identifiers and date
    X = df.drop(["units_sold", "date", "store_id", "product_id"], axis=1)

    # Convert categorical variables to dummy/indicator variables
    X = pd.get_dummies(X)
    
    # Save feature names for consistent input shape in API
    feature_names = X.columns.tolist()
    joblib.dump(feature_names, os.path.join(MODEL_DIR, "feature_names.joblib"))
    print("Feature names saved.")

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 1. Train XGBoost Model
    print("Training XGBoost Regressor...")
    xgb_model = xgb.XGBRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=6
    )
    xgb_model.fit(X_train, y_train)
    
    # Evaluate
    y_pred_xgb = xgb_model.predict(X_test)
    rmse_xgb = np.sqrt(mean_squared_error(y_test, y_pred_xgb))
    print(f"XGBoost RMSE: {rmse_xgb:.4f}")
    
    # Save XGBoost
    joblib.dump(xgb_model, os.path.join(MODEL_DIR, "xgb_model.joblib"))
    print("XGBoost model saved.")

    # 2. Train LightGBM Model
    print("Training LightGBM Regressor...")
    lgb_model = lgb.LGBMRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=6
    )
    lgb_model.fit(X_train, y_train)

    # Evaluate
    y_pred_lgb = lgb_model.predict(X_test)
    rmse_lgb = np.sqrt(mean_squared_error(y_test, y_pred_lgb))
    print(f"LightGBM RMSE: {rmse_lgb:.4f}")
    
    # Save LightGBM
    joblib.dump(lgb_model, os.path.join(MODEL_DIR, "lgb_model.joblib"))
    print("LightGBM model saved.")

if __name__ == "__main__":
    train_and_save()
