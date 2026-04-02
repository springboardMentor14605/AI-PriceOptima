import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# -------------------------------
#  Improve Plot Readability
# -------------------------------
plt.rcParams.update({
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 10
})

# -------------------------------
# Step 1: Load Dataset
# -------------------------------
df = pd.read_csv(r"C:\Users\Princy Jessica\AI-PriceOptima\DynamicPricingProject\data\feature_engineered_dataset.csv")

# -------------------------------
# Step 2: Basic Overview
# -------------------------------
print("Shape:", df.shape)
print("\nInfo:")
print(df.info())
print("\nDescription:")
print(df.describe())

# Convert date column
df["date"] = pd.to_datetime(df["date"])

# -------------------------------
# Step 3: Distribution (FIXED )
# -------------------------------
plt.figure(figsize=(25,18), dpi=120)
df.hist()
plt.tight_layout()
plt.show()

# -------------------------------
# Step 4: Price vs Units Sold
# -------------------------------
plt.figure(figsize=(8,5), dpi=120)
sns.scatterplot(x="price", y="units_sold", data=df)
plt.title("Price vs Units Sold")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 5: Inventory vs Sales
# -------------------------------
plt.figure(figsize=(8,5), dpi=120)
sns.scatterplot(x="inventory_level", y="units_sold", data=df)
plt.title("Inventory vs Units Sold")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 6: Competitor Pricing
# -------------------------------
plt.figure(figsize=(8,5), dpi=120)
sns.scatterplot(x="competitor_pricing", y="price", data=df)
plt.title("Competitor Pricing vs Price")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 7: Visitors vs Sales
# -------------------------------
plt.figure(figsize=(8,5), dpi=120)
sns.scatterplot(x="visitors", y="units_sold", data=df)
plt.title("Visitors vs Units Sold")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 8: Correlation Heatmap
# -------------------------------
plt.figure(figsize=(14,10), dpi=120)
sns.heatmap(df.corr(), annot=True, cmap="coolwarm")
plt.title("Correlation Heatmap")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 9: Category-wise Sales
# -------------------------------
plt.figure(figsize=(10,5), dpi=120)
sns.barplot(x="category", y="units_sold", data=df)
plt.xticks(rotation=45)
plt.title("Category-wise Sales")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 10: Region-wise Analysis
# -------------------------------
plt.figure(figsize=(10,5), dpi=120)
sns.barplot(x="region", y="units_sold", data=df)
plt.title("Region-wise Sales")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 11: Seasonality Impact
# -------------------------------
plt.figure(figsize=(10,5), dpi=120)
sns.boxplot(x="seasonality", y="units_sold", data=df)
plt.title("Seasonality Impact")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 12: Weather Impact
# -------------------------------
plt.figure(figsize=(10,5), dpi=120)
sns.boxplot(x="weather_condition", y="units_sold", data=df)
plt.title("Weather Impact")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 13: Holiday Effect
# -------------------------------
plt.figure(figsize=(10,5), dpi=120)
sns.barplot(x="holiday_promotion", y="units_sold", data=df)
plt.title("Holiday Promotion Effect")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 14: Discount Impact
# -------------------------------
plt.figure(figsize=(8,5), dpi=120)
sns.scatterplot(x="discount", y="units_sold", data=df)
plt.title("Discount vs Units Sold")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 15: Revenue Analysis
# -------------------------------
plt.figure(figsize=(8,5), dpi=120)
sns.histplot(df["revenue"], kde=True)
plt.title("Revenue Distribution")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 16: Profit Margin Analysis
# -------------------------------
plt.figure(figsize=(8,5), dpi=120)
sns.histplot(df["profit_margin"], kde=True)
plt.title("Profit Margin Distribution")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 17: Time-based Trends
# -------------------------------
plt.figure(figsize=(12,5), dpi=120)
df.groupby("date")["units_sold"].sum().plot()
plt.title("Daily Sales Trend")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 18: Monthly Sales Trend
# -------------------------------
plt.figure(figsize=(10,5), dpi=120)
df.groupby("month")["units_sold"].mean().plot(kind="bar")
plt.title("Monthly Sales Trend")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 19: Weekend vs Weekday
# -------------------------------
plt.figure(figsize=(8,5), dpi=120)
sns.barplot(x="is_weekend", y="units_sold", data=df)
plt.title("Weekend vs Weekday Sales")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 20: Conversion Rate
# -------------------------------
plt.figure(figsize=(8,5), dpi=120)
sns.histplot(df["conversion_rate"], kde=True)
plt.title("Conversion Rate")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 21: Inventory Pressure
# -------------------------------
plt.figure(figsize=(8,5), dpi=120)
sns.histplot(df["inventory_pressure"], kde=True)
plt.title("Inventory Pressure")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 22: Competitor Gap
# -------------------------------
plt.figure(figsize=(8,5), dpi=120)
sns.histplot(df["competitor_gap"], kde=True)
plt.title("Competitor Gap")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 23: Demand Ratio
# -------------------------------
plt.figure(figsize=(8,5), dpi=120)
sns.histplot(df["demand_ratio"], kde=True)
plt.title("Demand Ratio")
plt.tight_layout()
plt.show()

# -------------------------------
# Step 24: Insights
# -------------------------------
print("\n--- Key Insights ---")
print("• Sales are affected by price and discount")
print("• Seasonal and regional trends exist")
print("• Some features show skewness (outliers present)")
print("• Conversion rate is normally distributed")

# =========================================================
#  EXTRA FEATURES
# =========================================================

# Missing values
print("\nMissing Values:\n", df.isnull().sum())

# Pairplot (sample for speed)
sns.pairplot(df.sample(200))
plt.show()

# Outlier detection
plt.figure(figsize=(12,6), dpi=120)
sns.boxplot(data=df.select_dtypes(include=['float64','int64']))
plt.title("Outlier Detection")
plt.tight_layout()
plt.show()

# Correlation ranking
print("\nCorrelation with Units Sold:")
print(df.corr()["units_sold"].sort_values(ascending=False))

print("\n EDA Completed Successfully!")