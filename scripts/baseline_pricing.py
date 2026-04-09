# scripts/baseline_pricing.py

import pandas as pd

# Load cleaned dataset
df = pd.read_csv(r"D:\Infosys-Project\AI-PriceOptima\Data\clean_dynamic_pricing_dataset.csv")
# Standardize column names
df.rename(columns={
    'inventory_level': 'inventory'
}, inplace=True)

# Check first 5 rows
print(df.head())

# Convert date column into datetime format
df['date'] = pd.to_datetime(df['date'])

# Extract useful features
df['day_of_week'] = df['date'].dt.dayofweek
df['month'] = df['date'].dt.month

def time_based_price(row):
    if row['day_of_week'] >= 5:  # Saturday=5, Sunday=6
        return row['price'] * 1.10  # 10% increase
    else:
        return row['price']
    
def inventory_based_price(row):
    if row['inventory'] < 50:
        return row['price'] * 1.15  # increase price
    elif row['inventory'] > 200:
        return row['price'] * 0.90  # decrease price
    else:
        return row['price']
    

def dynamic_price(row):
    price = row['price']
    
    # Apply time rule
    if row['day_of_week'] >= 5:
        price *= 1.10
    
    # Apply inventory rule
    if row['inventory'] < 50:
        price *= 1.15
    elif row['inventory'] > 200:
        price *= 0.90
    
    return price

df['dynamic_price'] = df.apply(dynamic_price, axis=1)

df['baseline_revenue'] = df['dynamic_price'] * df['units_sold']

df.to_csv("D:/Infosys-Project/AI-PriceOptima/Outputs/baseline_pricing_output.csv", index=False)