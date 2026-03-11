import pandas as pd

print("Starting data cleaning process...")

# Step 1: Load dataset from data folder
df = pd.read_csv("../data/updated_dynamic_pricing_dataset.csv")

print("Dataset Loaded Successfully")
print("Dataset Shape:", df.shape)

# Step 2: View first rows
print(df.head())


# Step 3: Check missing values
print("\nMissing Values:")
print(df.isnull().sum())


# Step 4: Fill missing numeric values
df["Price"] = df["Price"].fillna(df["Price"].median())


# Step 5: Fill missing categorical values
df["Weather Condition"] = df["Weather Condition"].fillna(df["Weather Condition"].mode()[0])


# Step 6: Remove duplicate rows
print("\nDuplicate Rows:", df.duplicated().sum())
df = df.drop_duplicates()


# Step 7: Standardize column names
df.columns = df.columns.str.lower().str.replace(" ", "_")

print("\nUpdated Column Names:")
print(df.columns)


# Step 8: Remove negative inventory
df = df[df["inventory_level"] >= 0]


# Step 9: Remove negative visitors
df = df[df["visitors"] >= 0]


# Step 10: Clean category values
df["category"] = df["category"].str.strip().str.title()


# Step 11: Clean weather condition values
df["weather_condition"] = df["weather_condition"].str.title()


# Step 12: Detect and remove outliers using IQR (Price column)

Q1 = df["price"].quantile(0.25)
Q3 = df["price"].quantile(0.75)

IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

df = df[(df["price"] >= lower) & (df["price"] <= upper)]

print("\nOutliers removed")


# Step 13: Save cleaned dataset into data folder
df.to_csv("../data/clean_dynamic_pricing_dataset.csv", index=False)

print("\nCleaning Completed Successfully!")
print("Clean dataset saved in data folder as clean_dynamic_pricing_dataset.csv")