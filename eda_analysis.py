import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------
# Settings
# -------------------------------
sns.set(style="whitegrid")
plt.rcParams.update({'font.size': 10})

# -------------------------------
# Load Dataset
# -------------------------------
df = pd.read_csv("feature_engineered_dynamic_pricing_dataset.csv")

# Fix column names
df.columns = df.columns.str.lower().str.replace(" ", "_")

print("Dataset Loaded Successfully\n")

# -------------------------------
# Basic Info
# -------------------------------
print(df.head())
print(df.shape)
print(df.info())
print(df.describe())

# -------------------------------
# Histograms (Clean)
# -------------------------------
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns

for i in range(0, len(numeric_cols), 6):
    df[numeric_cols[i:i+6]].hist(figsize=(15,8))
    plt.suptitle("Feature Distribution", fontsize=16)
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.show()

# -------------------------------
# Scatter Plots (PDF Steps)
# -------------------------------

# Price vs Units Sold
sns.scatterplot(x="price", y="units_sold", data=df)
plt.title("Price vs Units Sold")
plt.show()

# Visitors vs Sales
sns.scatterplot(x="visitors", y="units_sold", data=df)
plt.title("Visitors vs Units Sold")
plt.show()

# Inventory vs Sales
sns.scatterplot(x="inventory_level", y="units_sold", data=df)
plt.title("Inventory vs Units Sold")
plt.show()

# Competitor Pricing Impact
sns.scatterplot(x="competitor_pricing", y="price", data=df)
plt.title("Competitor Pricing vs Price")
plt.show()

# Discount Impact
sns.scatterplot(x="discount", y="units_sold", data=df)
plt.title("Discount vs Units Sold")
plt.show()

# -------------------------------
# Correlation Heatmap (Clean)
# -------------------------------
corr = df.corr(numeric_only=True)

plt.figure(figsize=(18,12))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
plt.xticks(rotation=45, ha='right')
plt.title("Correlation Heatmap")
plt.tight_layout()
plt.show()

# -------------------------------
# Category-wise Sales (Fixed)
# -------------------------------
category_cols = [col for col in df.columns if "category_" in col]

if category_cols:
    df_cat = df[category_cols + ["units_sold"]]
    df_cat = df_cat.melt(id_vars="units_sold", var_name="category", value_name="value")
    df_cat = df_cat[df_cat["value"] == 1]

    plt.figure(figsize=(10,5))
    sns.barplot(x="category", y="units_sold", data=df_cat)
    plt.xticks(rotation=45)
    plt.title("Category-wise Sales")
    plt.show()

# -------------------------------
# Region-wise Analysis
# -------------------------------
region_cols = [col for col in df.columns if "region_" in col]

if region_cols:
    df_reg = df[region_cols + ["units_sold"]]
    df_reg = df_reg.melt(id_vars="units_sold", var_name="region", value_name="value")
    df_reg = df_reg[df_reg["value"] == 1]

    plt.figure(figsize=(10,5))
    sns.barplot(x="region", y="units_sold", data=df_reg)
    plt.xticks(rotation=45)
    plt.title("Region-wise Sales")
    plt.show()

# -------------------------------
# Seasonality Impact
# -------------------------------
if "seasonality" in df.columns:
    sns.boxplot(x="seasonality", y="units_sold", data=df)
    plt.title("Seasonality Impact")
    plt.show()

# -------------------------------
# Weather Impact
# -------------------------------
weather_cols = [col for col in df.columns if "weather_condition_" in col]

if weather_cols:
    df_weather = df[weather_cols + ["units_sold"]]
    df_weather = df_weather.melt(id_vars="units_sold", var_name="weather", value_name="value")
    df_weather = df_weather[df_weather["value"] == 1]

    sns.boxplot(x="weather", y="units_sold", data=df_weather)
    plt.xticks(rotation=45)
    plt.title("Weather Impact")
    plt.show()

# -------------------------------
# Holiday Effect
# -------------------------------
if "holiday_promotion" in df.columns:
    sns.barplot(x="holiday_promotion", y="units_sold", data=df)
    plt.title("Holiday Promotion Effect")
    plt.show()

# -------------------------------
# Revenue & Profit
# -------------------------------
if "revenue" in df.columns:
    sns.histplot(df["revenue"], kde=True)
    plt.title("Revenue Distribution")
    plt.show()

if "profit_margin" in df.columns:
    sns.histplot(df["profit_margin"], kde=True)
    plt.title("Profit Margin")
    plt.show()

# -------------------------------
# PDF Missing Steps (ADDED)
# -------------------------------

# Competitor Gap
if "competitor_gap" in df.columns:
    sns.histplot(df["competitor_gap"], kde=True)
    plt.title("Competitor Gap")
    plt.show()

# Inventory Pressure
if "inventory_pressure" in df.columns:
    sns.histplot(df["inventory_pressure"], kde=True)
    plt.title("Inventory Pressure")
    plt.show()

# Demand Ratio
if "price_demand_ratio" in df.columns:
    sns.histplot(df["price_demand_ratio"], kde=True)
    plt.title("Demand Ratio")
    plt.show()

# Conversion Rate
if "conversion_rate" in df.columns:
    sns.histplot(df["conversion_rate"], kde=True)
    plt.title("Conversion Rate")
    plt.show()

# -------------------------------
# Time-based Analysis
# -------------------------------
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"])
    df.groupby("date")["units_sold"].sum().plot(figsize=(12,5))
    plt.title("Sales Over Time")
    plt.show()

if "month" in df.columns:
    df.groupby("month")["units_sold"].mean().plot(kind="bar")
    plt.title("Monthly Trend")
    plt.show()

if "is_weekend" in df.columns:
    sns.barplot(x="is_weekend", y="units_sold", data=df)
    plt.title("Weekend vs Weekday")
    plt.show()

# -------------------------------
# End
# -------------------------------
print("\nEDA Completed Successfully ✅")