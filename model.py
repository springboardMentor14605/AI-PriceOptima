import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import joblib
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import RandomizedSearchCV
import shap

from data_loader import load_and_preprocess_data

def prepare_data(df):
    """Sorts data chronologically for time-based split and encodes categoricals."""
    print("Preparing data for modeling...")
    df = df.sort_values('Date').reset_index(drop=True)
    
    # Store identifiers aside for backtesting later
    identifiers = ['Date', 'Product ID', 'Store ID']
    target = 'Units Sold'
    
    # Drop identifiers to form base feature matrix
    X_base = df.drop(columns=identifiers + [target])
    y = df[target]
    
    # One-hot encode categoricals if any (e.g. Category, DayOfWeek if they were created)
    # We will use pd.get_dummies to be safe for XGBoost
    X_encoded = pd.get_dummies(X_base, drop_first=True)
    
    return X_encoded, y, df

def train_and_evaluate_models(data_path):
    print("=================== STARTING ML PIPELINE ===================")
    # 1. Load using the project's data loader
    df_raw = load_and_preprocess_data(data_path)
    
    # Ensure no NaNs remain (data_loader or EDA should have handled most)
    df_raw = df_raw.dropna().reset_index(drop=True) 
    
    X, y, df_sorted = prepare_data(df_raw)
    
    # 2. TIME-BASED SPLIT (Critical Requirement: 80% Train, 20% Test)
    split_idx = int(len(X) * 0.8)
    
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    # Save the test set raw data for backtesting step
    test_df_raw = df_sorted.iloc[split_idx:].copy()
    test_df_raw.to_csv('data/test_data_for_backtest.csv', index=False)
    
    print(f"Time-Based Split completed:")
    print(f"- Train instances: {len(X_train)} (Up to {df_sorted['Date'].iloc[split_idx-1].date()})")
    print(f"- Test instances:  {len(X_test)} (From {df_sorted['Date'].iloc[split_idx].date()})")
    
    # We will save the exact column structure of X_train so optimization.py knows what features to expect
    joblib.dump(list(X_train.columns), 'models/model_features_list.pkl')
    
    # 3. XGBoost Model Setup
    print("\n--- Training XGBoost Model ---")
    xgb = XGBRegressor(random_state=42)
    xgb_params = {
        'n_estimators': [100, 200, 300],
        'learning_rate': [0.01, 0.05, 0.1],
        'max_depth': [3, 5, 7],
        'subsample': [0.8, 0.9, 1.0],
        'colsample_bytree': [0.8, 0.9, 1.0]
    }
    
    xgb_search = RandomizedSearchCV(xgb, param_distributions=xgb_params, n_iter=10, 
                                    scoring='neg_mean_squared_error', cv=3, random_state=42, n_jobs=-1)
    xgb_search.fit(X_train, y_train)
    best_xgb = xgb_search.best_estimator_
    
    # 4. LightGBM Model Setup
    print("--- Training LightGBM Model ---")
    lgbm = LGBMRegressor(random_state=42)
    lgbm_params = {
        'n_estimators': [100, 200, 300],
        'learning_rate': [0.01, 0.05, 0.1],
        'num_leaves': [31, 50, 70],
        'min_child_samples': [10, 20, 30],
        'subsample': [0.8, 0.9, 1.0]
    }
    
    lgbm_search = RandomizedSearchCV(lgbm, param_distributions=lgbm_params, n_iter=10, 
                                     scoring='neg_mean_squared_error', cv=3, random_state=42, n_jobs=-1)
    lgbm_search.fit(X_train, y_train)
    best_lgbm = lgbm_search.best_estimator_
    
    # 5. Evaluate and Compare
    print("\n=================== MODEL EVALUATION ===================")
    models = {'XGBoost': best_xgb, 'LightGBM': best_lgbm}
    best_model = None
    best_name = ""
    lowest_rmse = float('inf')
    
    for name, model in models.items():
        train_preds = model.predict(X_train)
        test_preds = model.predict(X_test)
        
        train_rmse = np.sqrt(mean_squared_error(y_train, train_preds))
        test_rmse = np.sqrt(mean_squared_error(y_test, test_preds))
        
        print(f"[{name}]")
        print(f"{name} Train RMSE: {train_rmse:.4f}")
        print(f"{name} RMSE: {test_rmse:.4f}")
        
        # Overfitting Warning Check
        if test_rmse > train_rmse * 1.5:
            print("Model may be overfitting")
            
        if test_rmse < lowest_rmse:
            lowest_rmse = test_rmse
            best_model = model
            best_name = name
            
    print(f"\n=> Best Model Selected: {best_name} with Test RMSE: {lowest_rmse:.4f}")
    
    # Save best model
    joblib.dump(best_model, 'models/best_pricing_model.pkl')
    print(f"Saved best model to 'models/best_pricing_model.pkl'")
    joblib.dump({'name': best_name, 'rmse': lowest_rmse}, 'models/model_metrics.pkl')
    
    # 6. SHAP Explainability on Best Model
    print("\n--- Generating SHAP Explanations ---")
    os.makedirs('output_plots', exist_ok=True)
    
    # Because tree models handle missing/dummy logic differently, use the subset to save memory
    X_shap_sample = X_test.sample(n=min(1000, len(X_test)), random_state=42)
    joblib.dump(X_shap_sample, 'models/X_test_sample.pkl')
    print("Test sample saved for explainability plots. Run `explainability.py`.")


    print("=================== PIPELINE COMPLETE ===================")

if __name__ == "__main__":
    dataset_path = 'data/Updated_dynamic-pricing-dataset (1).csv'
    train_and_evaluate_models(dataset_path)
