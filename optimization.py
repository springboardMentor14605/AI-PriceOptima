import numpy as np
import pandas as pd
import joblib
import warnings

def load_ml_assets():
    """Loads the trained ML model and feature list."""
    try:
        model = joblib.load('models/best_pricing_model.pkl')
        expected_features = joblib.load('models/model_features_list.pkl')
        return model, expected_features
    except FileNotFoundError:
        print("Model assets missing. Please train the model (`model.py`) first.")
        return None, None

def encode_row(row_series, expected_features):
    """Encodes a single row of dict/Series into the exact DataFrame feature space expected by the model."""
    row_df = pd.DataFrame([row_series])
    
    # Base columns to drop that aren't features
    identifiers = ['Date', 'Product ID', 'Store ID', 'Units Sold']
    row_features = row_df.drop(columns=[col for col in identifiers if col in row_df.columns])
    
    # One-hot encode using pd.get_dummies to handle any categorical conversion
    row_encoded = pd.get_dummies(row_features)
    
    # Reindex columns to match the model training columns EXACTLY (fill missing dummies with False/0)
    row_aligned = row_encoded.reindex(columns=expected_features, fill_value=0)
    
    with warnings.catch_warnings():
        warnings.simplefilter(action='ignore', category=UserWarning)
        row_numpy = row_aligned.values.astype(np.float64)
        
    return row_numpy, row_aligned

def optimize_price_for_row(row_series, model, expected_features):
    """
    Simulates 5 price points (0.8x to 1.2x) for a row, predicts demand for each,
    calculates expected revenue, and selects the optimal price maximizing revenue.
    """
    current_price = row_series['Price']
    
    # Simulated prices
    simulated_multipliers = [0.8, 0.9, 1.0, 1.1, 1.2]
    simulated_prices = [current_price * m for m in simulated_multipliers]
    
    # We will compute Predicted Revenue for each simulated price
    best_price = current_price
    max_revenue = -1
    best_demand = 0
    
    for sim_price in simulated_prices:
        # Create a copy of the row logic to avoid mutation
        test_row = row_series.copy()
        
        # Override the price field with the simulation
        test_row['Price'] = sim_price
        
        # Determine Demand Adjustments logic dynamically if needed (e.g. Demand_Trend logic)
        # Assuming the model figures out Price vs Demand natively
        
        # Encode to ML structure
        row_matrix, _ = encode_row(test_row, expected_features)
        
        # Predict Demand (Units Sold)
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=UserWarning)
            # XGBoost requires matrix or dataframe matching training columns exactly
            predicted_demand = model.predict(row_matrix)[0]
            
        # Floor negative demand to 0
        predicted_demand = max(0, predicted_demand)
        
        expected_revenue = predicted_demand * sim_price
        
        if expected_revenue > max_revenue:
            max_revenue = expected_revenue
            best_price = sim_price
            best_demand = predicted_demand
            
    # As a secondary check (margin safeguards), ensure we aren't completely breaking minimum profitability rules.
    # The requirement asks for 80% to 120% loop, but also "Margin safeguards" as existing in baseline.
    cost = row_series.get('Cost', -1)
    comp_price = row_series.get('Competitor Pricing', -1)
    
    if cost != -1 and best_price < (cost * 1.20):
        # Prevent losing money/margin
        best_price = max(best_price, cost * 1.20)
        
    if comp_price != -1 and best_price > (comp_price * 1.05):
        # Prevent completely pricing out of market (though ML might have predicted otherwise, safety first)
        best_price = min(best_price, comp_price * 1.05)
        
    return best_price, best_demand, max_revenue

if __name__ == "__main__":
    print("Optimization engine active. Call `optimize_price_for_row()` from backtesting.py")
