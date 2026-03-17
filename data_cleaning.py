import pandas as pd

# Step 1: Load the dataset
df = pd.read_csv("dynamic-pricing-dataset.csv")

# Step 2: Display first 5 rows
print("First 5 rows of the dataset:")
print(df.head())

# Step 3: Display dataset information
print("\nDataset Information:")
print(df.info())

# Step 4: Check missing values
print("\nMissing values in each column:")
print(df.isnull().sum())

# Step 5: Remove duplicate rows
df = df.drop_duplicates()
print("\nDuplicates removed")

# Step 6: Clean column names (remove extra spaces)
df.columns = df.columns.str.strip()

# Step 7: Convert Date column to datetime (FIXED)
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)

# Step 8: Fill missing numeric values with mean
numeric_columns = df.select_dtypes(include=['int64','float64']).columns
df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())

# Step 9: Fill missing categorical values
categorical_columns = df.select_dtypes(include=['object']).columns
df[categorical_columns] = df[categorical_columns].fillna("Unknown")

# Step 10: Display dataset statistics
print("\nDataset Statistics:")
print(df.describe())

# Step 11: Save cleaned dataset
df.to_csv("cleaned_dynamic_pricing_dataset.csv", index=False)

print("\nDataset cleaned successfully and saved as 'cleaned_dynamic_pricing_dataset.csv'")