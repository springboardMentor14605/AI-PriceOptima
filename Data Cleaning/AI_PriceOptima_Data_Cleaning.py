# AI PriceOptima Project

import pandas as pd

# Load Dataset
df = pd.read_csv(r"D:\Infosys Datasets\Shivansh_Updated_dynamic-pricing-dataset.csv")

# Dataset Info
print("Dataset Shape:", df.shape)
print(df.head())

# Standardize Column Names
df.columns = df.columns.str.lower().str.replace(" ", "_")

# Convert Date
df["date"] = pd.to_datetime(df["date"], format="mixed", dayfirst=True)

# Missing Values
print("Missing Values:\n", df.isnull().sum())

df["price"] = df["price"].fillna(df["price"].median())
df["demand_forecast"] = df["demand_forecast"].fillna(df["demand_forecast"].median())
df["weather_condition"] = df["weather_condition"].fillna(df["weather_condition"].mode()[0])

# Remove Duplicates
print("Duplicates:", df.duplicated().sum())
df = df.drop_duplicates()

# Inventory Validation
df = df[df["inventory_level"] >= 0]

# Units Sold Validation
df = df[df["units_sold"] <= df["inventory_level"]]

# Price Validation
df = df[df["price"] > 0]

# Cost Validation
df = df[df["cost"] <= df["price"]]

# Discount Validation
df["discount"] = df["discount"].clip(0,1)

# Visitors Validation
df = df[df["visitors"] >= 0]

# Clean Category
df["category"] = df["category"].str.strip().str.title()

# Clean Weather
df["weather_condition"] = df["weather_condition"].str.title()

# Remove Price Outliers
Q1 = df["price"].quantile(0.25)
Q3 = df["price"].quantile(0.75)

IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

df = df[(df["price"] >= lower) & (df["price"] <= upper)]

# Save Clean Dataset
df.to_csv("clean_dynamic_pricing_dataset.csv", index=False)

print("Data Cleaning Completed")