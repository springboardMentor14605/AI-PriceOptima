import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_eda(data_path):
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    # 1. DATA CLEANING
    print("\n--- 1. Data Cleaning ---")
    
    # Handle duplicates
    initial_shape = df.shape
    df = df.drop_duplicates()
    print(f"Removed {initial_shape[0] - df.shape[0]} duplicate rows.")
    
    # Handle missing values
    missing = df.isnull().sum().sum()
    if missing > 0:
        print(f"Found {missing} missing values. Filling numericals with median, categoricals with mode.")
        num_cols = df.select_dtypes(include=np.number).columns
        cat_cols = df.select_dtypes(exclude=np.number).columns
        df[num_cols] = df[num_cols].fillna(df[num_cols].median())
        df[cat_cols] = df[cat_cols].fillna(df[cat_cols].mode().iloc[0])
    else:
        print("No missing values found.")
        
    # Standardize data types
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    
    # Handle outliers in numerical data using IQR (Capping) to prevent visualization skewing
    outlier_cols = ['Units Sold', 'Price']
    for col in outlier_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Cap values logically
        df[col] = np.where(df[col] < lower_bound, lower_bound, df[col])
        df[col] = np.where(df[col] > upper_bound, upper_bound, df[col])
    print("Handled outliers in key continuous variables (capped using IQR).")
    
    # Create folder for saving plots
    os.makedirs('eda_output', exist_ok=True)
    sns.set_theme(style="whitegrid")
    
    # 2. VISUALIZATIONS
    print("\n--- 2. Generating Visualizations ---")
    print("Plots will be saved to the 'eda_output' directory.")
    
    # A) Demand Patterns (Sales vs Price)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Price', y='Units Sold', data=df.sample(min(5000, len(df))), alpha=0.5, color='blue')
    plt.title('Demand Pattern: Units Sold vs Price (Sampled)')
    plt.xlabel('Price ($)')
    plt.ylabel('Units Sold')
    plt.savefig('eda_output/1_demand_vs_price.png', bbox_inches='tight')
    plt.close()
    print("- Saved 1_demand_vs_price.png")
    
    # B) Demand Elasticity (Sales grouped by Price bins)
    # Create price bins to calculate average sales
    df['Price Bin'] = pd.qcut(df['Price'], q=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
    elasticity_df = df.groupby('Price Bin', observed=True)['Units Sold'].mean().reset_index()
    plt.figure(figsize=(8, 5))
    sns.barplot(x='Price Bin', y='Units Sold', data=elasticity_df, hue='Price Bin', palette='coolwarm', legend=False)
    plt.title('Demand Elasticity: Average Units Sold by Price Bin')
    plt.ylabel('Average Units Sold')
    plt.savefig('eda_output/2_demand_elasticity.png', bbox_inches='tight')
    plt.close()
    print("- Saved 2_demand_elasticity.png")
    
    # C) Seasonal Trends (Monthly Sales)
    df['Month'] = df['Date'].dt.month
    monthly_sales = df.groupby('Month')['Units Sold'].sum().reset_index()
    plt.figure(figsize=(10, 5))
    sns.lineplot(x='Month', y='Units Sold', data=monthly_sales, marker='o', color='purple')
    plt.title('Seasonal Trends: Total Units Sold by Month')
    plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    plt.xlabel('Month')
    plt.ylabel('Total Units Sold')
    plt.grid(True)
    plt.savefig('eda_output/3_seasonal_trends.png', bbox_inches='tight')
    plt.close()
    
    # Weekly sales logic - weekday vs weekend
    df['DayOfWeek'] = df['Date'].dt.day_name()
    weekly_sales = df.groupby('DayOfWeek')['Units Sold'].mean().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).reset_index()
    plt.figure(figsize=(10, 5))
    sns.barplot(x='DayOfWeek', y='Units Sold', data=weekly_sales, hue='DayOfWeek', palette='viridis', legend=False)
    plt.title('Weekly Trends: Average Units Sold by Day of Week')
    plt.ylabel('Average Units Sold')
    plt.savefig('eda_output/3b_weekly_trends.png', bbox_inches='tight')
    plt.close()
    print("- Saved 3_seasonal_trends.png and 3b_weekly_trends.png")
    
    # D) Customer/Product segmentation (Sales by Category)
    plt.figure(figsize=(10, 5))
    sns.boxplot(x='Category', y='Units Sold', hue='Category', data=df, palette='Set2', legend=False)
    plt.title('Product Segmentation: Units Sold Distribution by Category')
    plt.savefig('eda_output/4_product_segmentation.png', bbox_inches='tight')
    plt.close()
    
    # High vs Low Demand Products
    product_sales = df.groupby('Product ID')['Units Sold'].sum().sort_values(ascending=False).reset_index()
    plt.figure(figsize=(12, 6))
    sns.barplot(x='Product ID', y='Units Sold', data=product_sales, hue='Product ID', palette='magma', legend=False)
    plt.title('Total Sales by Product ID (High vs Low Demand)')
    plt.xticks(rotation=45)
    plt.savefig('eda_output/4b_product_demand.png', bbox_inches='tight')
    plt.close()
    print("- Saved 4_product_segmentation.png and 4b_product_demand.png")
    
    # E) Inventory Impact on Sales
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x='Inventory Level', y='Units Sold', data=df.sample(min(5000, len(df))), alpha=0.3, color='green')
    plt.title('Inventory Impact: Units Sold vs Inventory Level (Sampled)')
    plt.savefig('eda_output/5_inventory_impact.png', bbox_inches='tight')
    plt.close()
    print("- Saved 5_inventory_impact.png")
    
    # F) Correlation Heatmap
    plt.figure(figsize=(12, 8))
    numeric_cols = df.select_dtypes(include=np.number).columns
    corr_matrix = df[numeric_cols].corr()
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', linewidths=0.5, vmin=-1, vmax=1)
    plt.title('Feature Correlation Heatmap')
    plt.savefig('eda_output/6_correlation_heatmap.png', bbox_inches='tight')
    plt.close()
    print("- Saved 6_correlation_heatmap.png")
    
    print("\nEDA and Visualizations completed successfully!")

if __name__ == "__main__":
    run_eda('data/Updated_dynamic-pricing-dataset (1).csv')
