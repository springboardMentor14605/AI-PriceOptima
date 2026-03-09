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

def load_data(file_path):
    """Loads CSV dataset and reports shape."""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    df = pd.read_csv(file_path)
    logger.info(f"Dataset loaded successfully. Shape: {df.shape}")
    return df

def clean_data(df):
    """Performs professional dataset cleaning."""
    # 1. Standardize column names to snake_case
    df.columns = [col.lower().replace(' ', '_').replace('/', '_') for col in df.columns]
    logger.info(f"Standardized column names: {list(df.columns)}")

    # 2. Convert date column to datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        logger.info("Converted 'date' column to datetime.")

    # 3. Check for missing values
    missing_count = df.isnull().sum()
    logger.info(f"Missing values before cleaning:\n{missing_count[missing_count > 0]}")

    # 4. Fill numeric missing values using median
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            logger.info(f"Filled missing values in '{col}' with median: {median_val}")

    # 5. Fill categorical missing values using mode
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if df[col].isnull().any():
            mode_val = df[col].mode()[0]
            df[col] = df[col].fillna(mode_val)
            logger.info(f"Filled missing values in '{col}' with mode: {mode_val}")

    # 6. Remove duplicate rows
    initial_len = len(df)
    df = df.drop_duplicates()
    logger.info(f"Removed {initial_len - len(df)} duplicate rows.")

    # 7. Validate values & Remove invalid rows
    # Logic: 
    # - Inventory level should be >= 0
    # - Price should be > 0
    # - Cost should be < price
    # - Discount should be between 0 and 1
    # - Units sold should not exceed inventory (assuming inventory_level is what's left or available)
    
    valid_mask = (
        (df['inventory_level'] >= 0) &
        (df['price'] > 0) &
        (df['cost'] < df['price']) &
        (df['discount'] >= 0) & (df['discount'] <= 1) &
        (df['units_sold'] >= 0)
    )
    
    invalid_rows = len(df) - valid_mask.sum()
    df = df[valid_mask]
    logger.info(f"Removed {invalid_rows} rows due to validation failures (negatives, cost > price, etc.).")

    # 8. Remove extreme outliers using IQR method
    # We'll apply this to key numeric columns like price and units_sold
    cols_to_check = ['price', 'units_sold', 'cost']
    for col in cols_to_check:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        initial_count = len(df)
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
        logger.info(f"Removed {initial_count - len(df)} outliers from '{col}' using IQR.")

    logger.info(f"Final dataset shape after cleaning: {df.shape}")
    return df

def save_data(df, output_path):
    """Saves cleaned dataset to CSV."""
    df.to_csv(output_path, index=False)
    logger.info(f"Cleaned dataset saved to: {output_path}")

if __name__ == "__main__":
    input_file = "PriceOptima/data/dynamic_pricing_dataset.csv"
    output_file = "PriceOptima/data/clean_dynamic_pricing_dataset.csv"

    # Execution Flow
    data = load_data(input_file)
    if data is not None:
        cleaned_data = clean_data(data)
        save_data(cleaned_data, output_file)
