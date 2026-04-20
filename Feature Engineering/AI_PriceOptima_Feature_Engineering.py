#Import Libraries
import pandas as pd

#Load the Cleaned Dataset
df = pd.read_csv(r"D:\Infosys Datasets\clean_dynamic_pricing_dataset.csv")

#Profit Margin
df["profit_margin"] = df["price"] - df["cost"]

#Margin Percentage
df["margin_percentage"] = (df["price"] - df["cost"]) / df["price"]

#Demand Ratio
df["demand_ratio"] = df["units_sold"] / (df["demand_forecast"] + 1)

#Inventory Pressure
df["Inventory_pressure"] = df["units_sold"] / (df["inventory_level"] + 1)

#Competitor Price Gap
df["competitor_gap"] = df["price"] - df["competitor_pricing"]

#Discounted Price
df["discounted_price"] = df["price"] * (1 - df["discount"])

#Revenue Calculation 
df["revenue"] = df["units_sold"] * df["discounted_price"]

#Conversion Rate
df["conversion_rate"] = df["units_sold"] / (df["visitors"] + 1)

#Price Demand Ratio
df["price_demand_ratio"] = df["price"] / (df["units_sold"] + 1)

#Remaning Stock
df["stock_remaning"] = df["inventory_level"] - df["units_sold"]

#Traffic Intensity
df["traffic_intensity"] = df["visitors"] / (df["inventory_level"] + 1)

#Time Based Features
df["date"] = pd.to_datetime(df["date"])
df["day_of_week"] = df["date"].dt.dayofweek
df["month"] = df["date"].dt.month
df["is_weekend"] = df["day_of_week"].isin([5,6]).astype(int)

#Save the Dataset
df.to_csv("feature_engineered_dataset.csv", index=False)
print("Dataset Saved")