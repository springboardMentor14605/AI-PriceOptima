# feature_engineering.py

import pandas as pd

print("Loading dataset...")

# Load cleaned dataset
df = pd.read_csv("../data/clean_dynamic_pricing_dataset.csv")
print("Dataset loaded successfully!")
print("Rows:", df.shape[0], " Columns:", df.shape[1])

# -------------------------------
# PROFIT FEATURES
# -------------------------------

# Profit margin
df["profit_margin"] = df["price"] - df["cost"]

# Margin percentage
df["margin_percent"] = df["profit_margin"] / df["price"]


# -------------------------------
# DEMAND FEATURES
# -------------------------------

# Demand ratio
df["demand_ratio"] = df["units_sold"] / df["visitors"]

# Inventory pressure
df["inventory_pressure"] = df["units_sold"] / df["inventory_level"]


# -------------------------------
# COMPETITOR FEATURES
# -------------------------------

# Price difference with competitor
df["competitor_gap"] = df["price"] - df["competitor_pricing"]


# -------------------------------
# PRICE FEATURES
# -------------------------------

# Correct discounted price (fix percentage issue)
df["discounted_price"] = df["price"] * (1 - df["discount"] / 100)


# -------------------------------
# BUSINESS FEATURES
# -------------------------------

# Revenue
df["revenue"] = df["units_sold"] * df["discounted_price"]

# Conversion rate
df["conversion_rate"] = df["units_sold"] / df["visitors"]

# Price to demand ratio
df["price_demand_ratio"] = df["price"] / (df["units_sold"] + 1)


# -------------------------------
# INVENTORY FEATURES
# -------------------------------

# Remaining stock
df["stock_remaining"] = df["inventory_level"] - df["units_sold"]


# -------------------------------
# TRAFFIC FEATURES
# -------------------------------

# Traffic intensity
df["traffic_intensity"] = df["visitors"] / df["visitors"].mean()


# -------------------------------
# TIME FEATURES
# -------------------------------

# Convert date column properly
df["date"] = pd.to_datetime(df["date"], dayfirst=True)

# Extract day of week
df["day_of_week"] = df["date"].dt.dayofweek

# Extract month
df["month"] = df["date"].dt.month

# Weekend indicator
df["is_weekend"] = df["day_of_week"].apply(lambda x: 1 if x >= 5 else 0)


# -------------------------------
# SAVE DATASET
# -------------------------------

df.to_csv("../data/feature_engineered_dataset.csv", index=False)

print("Feature Engineering Completed Successfully!")
print("New dataset saved as: feature_engineered_dataset.csv")