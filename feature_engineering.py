import pandas as pd

# Load cleaned dataset
df = pd.read_csv("cleaned_dynamic_pricing_dataset.csv")

print("Dataset loaded successfully")

# -------------------------------
# Feature Engineering
# -------------------------------

# Profit Margin
df["Profit_Margin"] = df["Price"] - df["Cost"]

# Margin Percentage
df["Margin_Percent"] = (df["Price"] - df["Cost"]) / df["Price"]

# Inventory Pressure
df["Inventory_Pressure"] = df["Units Sold"] / (df["Inventory Level"] + 1)

# Competitor Price Gap
df["Competitor_Gap"] = df["Price"] - df["Competitor Pricing"]

# Discounted Price
df["Discounted_Price"] = df["Price"] * (1 - df["Discount"])

# Revenue Calculation
df["Revenue"] = df["Units Sold"] * df["Discounted_Price"]

# Conversion Rate
df["Conversion_Rate"] = df["Units Sold"] / (df["Visitors"] + 1)

# Price Demand Ratio
df["Price_Demand_Ratio"] = df["Price"] / (df["Units Sold"] + 1)

# Stock Remaining
df["Stock_Remaining"] = df["Inventory Level"] - df["Units Sold"]

# Traffic Intensity
df["Traffic_Intensity"] = df["Visitors"] / (df["Inventory Level"] + 1)

# -------------------------------
# Time-Based Features
# -------------------------------

df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

df["Day_of_Week"] = df["Date"].dt.dayofweek
df["Month"] = df["Date"].dt.month
df["Is_Weekend"] = df["Day_of_Week"].isin([5,6]).astype(int)

# -------------------------------
# Encode categorical variables
# -------------------------------

df = pd.get_dummies(df, columns=["Category", "Region", "Weather Condition"])

# -------------------------------
# Save new dataset
# -------------------------------

df.to_csv("feature_engineered_dynamic_pricing_dataset.csv", index=False)

print("Feature engineering completed")
print("New dataset saved as feature_engineered_dynamic_pricing_dataset.csv")

print(df.head())