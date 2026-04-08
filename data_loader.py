import pandas as pd
import numpy as np

def load_and_preprocess_data(filepath):
    print(f"Loading historical data from {filepath}...")
    df = pd.read_csv(filepath)
    
    # Preprocess date
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df = df.sort_values(by=['Product ID', 'Store ID', 'Date'])
    
    # Temporal features
    df['Is_Weekend'] = df['Date'].dt.dayofweek >= 5
    
    print("Calculating Demand Trend (7-day rolling average)...")
    # Demand Trend: 7-day rolling average of 'Units Sold' per product/store
    # Shift by 1 to represent previous demand trend (not encompassing current day)
    df['Demand_Trend'] = df.groupby(['Store ID', 'Product ID'])['Units Sold'].transform(
        lambda x: x.shift(1).rolling(window=7, min_periods=1).mean()
    )
    # Fill NAs for the first days with the current day's Units Sold as a fallback
    df['Demand_Trend'] = df['Demand_Trend'].fillna(df['Units Sold'])
    
    print("Calculating Inventory thresholds...")
    # Calculate global stock thresholds per product (across timeline) to define Low/High
    inventory_thresholds = df.groupby('Product ID')['Inventory Level'].agg(
        Low_Threshold=lambda x: x.quantile(0.25),
        High_Threshold=lambda x: x.quantile(0.75)
    ).reset_index()
    
    df = pd.merge(df, inventory_thresholds, on='Product ID', how='left')
    
    print("Data loading & preprocessing complete.")
    return df
