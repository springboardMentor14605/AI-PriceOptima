import pandas as pd
import numpy as np
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_cleaned_data(file_path):
    """Loads the cleaned dataset."""
    if not os.path.exists(file_path):
        logger.error(f"Cleaned file not found: {file_path}. Please run data_cleaning.py first.")
        return None
    df = pd.read_csv(file_path)
    logger.info(f"Cleaned dataset loaded. Shape: {df.shape}")
    return df

def engineer_features(df):
    """Generates useful ML features from the cleaned dataset."""
    logger.info("Starting feature engineering...")

    # 1. Financial Features
    # Note: price is assumed base price, but we should use discounted price for revenue calculations
    df['discounted_price'] = df['price'] * (1 - df['discount'])
    df['profit_margin'] = df['discounted_price'] - df['cost']
    df['margin_percent'] = (df['profit_margin'] / df['discounted_price']).replace([np.inf, -np.inf], 0).fillna(0)
    df['revenue'] = df['discounted_price'] * df['units_sold']

    # 2. Demand & Inventory Features
    # Avoid division by zero by adding a small epsilon or filling NaNs
    df['demand_ratio'] = (df['units_sold'] / df['demand_forecast']).replace([np.inf, -np.inf], 0).fillna(0)
    df['inventory_pressure'] = (df['inventory_level'] / (df['units_sold'] + 1)).fillna(0)
    df['stock_remaining'] = df['inventory_level'] - df['units_sold']
    
    # 3. Market & Traffic Features
    df['competitor_gap'] = df['price'] - df['competitor_pricing']
    df['conversion_rate'] = (df['units_sold'] / (df['visitors'] + 1)).fillna(0)
    df['price_demand_ratio'] = (df['price'] / (df['demand_forecast'] + 1)).fillna(0)
    df['traffic_intensity'] = df['visitors'] / (df['visitors'].mean() if df['visitors'].mean() != 0 else 1)

    # 4. Time-based Features
    # Ensure date is datetime
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

    logger.info("Feature engineering completed.")
    return df

def save_features(df, output_path):
    """Saves the featured dataset to CSV."""
    df.to_csv(output_path, index=False)
    logger.info(f"Feature-engineered dataset saved to: {output_path}")

if __name__ == "__main__":
    input_file = "PriceOptima/data/clean_dynamic_pricing_dataset.csv"
    output_file = "PriceOptima/data/feature_engineered_dataset.csv"

    # Execution Flow
    data = load_cleaned_data(input_file)
    if data is not None:
        featured_data = engineer_features(data)
        save_features(featured_data, output_file)
