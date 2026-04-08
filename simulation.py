import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from data_loader import load_and_preprocess_data
from pricing_rules import apply_pricing_rules

def run_simulation(data_path):
    # 1. Load Data
    df = load_and_preprocess_data(data_path)
    
    # 2. Apply Custom Baseline Pricing Rules
    df['Recommended_Price'] = apply_pricing_rules(df)
    
    # 3. Predict Demand/Revenue Adjustments (Price Elasticity Model)
    # Average expected price elasticity of demand
    E = 1.5
    
    # Percentage Change in Price
    df['Price_Change_Pct'] = (df['Recommended_Price'] - df['Price']) / df['Price']
    
    # Simulated Unit Demand 
    # Simulated Demand = Original Demand * (1 - Elasticity * Price Change %)
    df['Simulated_Units_Sold'] = df['Units Sold'] * (1 - (E * df['Price_Change_Pct']))
    
    # Floor to zero in case of astronomical price hikes (prevent negative demand)
    df['Simulated_Units_Sold'] = np.maximum(0, df['Simulated_Units_Sold'])
    
    # 4. Calculate Final Revenues
    df['Original_Revenue'] = df['Units Sold'] * df['Price']
    df['Simulated_Revenue'] = df['Simulated_Units_Sold'] * df['Recommended_Price']
    
    # Evaluate Revenue Lift
    total_original_revenue = df['Original_Revenue'].sum()
    total_simulated_revenue = df['Simulated_Revenue'].sum()
    revenue_lift = total_simulated_revenue - total_original_revenue
    lift_pct = (revenue_lift / total_original_revenue) * 100
    
    print("\n" + "="*40)
    print("         SIMULATION RESULTS         ")
    print("="*40)
    print(f"Total Original Revenue:  ${total_original_revenue:,.2f}")
    print(f"Total Simulated Revenue: ${total_simulated_revenue:,.2f}")
    print(f"Revenue Lift:            ${revenue_lift:,.2f} ({lift_pct:.2f}%)")
    print("="*40)
    
    # Output Directory
    output_dir = 'output_plots'
    os.makedirs(output_dir, exist_ok=True)
    
    # Sample Outputs for 3 Specific Products
    sample_products = df['Product ID'].unique()[:3]
    print("\n--- Sample Pricing Recommendations ---")
    
    for pid in sample_products:
        sample_df = df[df['Product ID'] == pid].head(5)
        print(f"\nProduct ID: {pid}")
        cols_to_show = ['Date', 'Cost', 'Competitor Pricing', 'Price', 'Recommended_Price', 'Price_Change_Pct', 'Units Sold', 'Simulated_Units_Sold']
        print(sample_df[cols_to_show].to_string(index=False))
        
    print("\n--- Generating Visualizations ---")
    
    # Visualization 1: Revenue Comparison Bar Chart
    plt.figure(figsize=(8, 6))
    revenues = [total_original_revenue, total_simulated_revenue]
    labels = ['Original (Static)', 'Simulated (Dynamic)']
    ax = sns.barplot(x=labels, y=revenues, hue=labels, palette=['#FF9999', '#99FF99'], dodge=False, legend=False)
    plt.title('Total Revenue Comparison: Static vs. Dynamic Pricing', fontsize=14)
    plt.ylabel('Total Revenue ($)', fontsize=12)
    
    # Annotate bars
    for i, v in enumerate(revenues):
        ax.text(i, v + (v * 0.02), f"${v:,.0f}", ha='center', va='bottom', fontsize=11)
        
    plt.savefig(f'{output_dir}/revenue_comparison.png', bbox_inches='tight')
    plt.close()
    
    # Visualization 2: Price Trend for a Sample Product
    sample_prod_df = df[df['Product ID'] == sample_products[0]].sort_values('Date').head(30)
    
    plt.figure(figsize=(14, 7))
    sns.lineplot(data=sample_prod_df, x='Date', y='Price', label='Original Price', color='red', marker='o')
    sns.lineplot(data=sample_prod_df, x='Date', y='Recommended_Price', label='Recommended Price', color='green', marker='s')
    
    # Add bounds 
    sns.lineplot(data=sample_prod_df, x='Date', y=sample_prod_df['Cost'] * 1.20, label='Min Bound (Cost + 20%)', color='grey', linestyle='--')
    sns.lineplot(data=sample_prod_df, x='Date', y=sample_prod_df['Competitor Pricing'] * 1.05, label='Max Bound (Competitor + 5%)', color='blue', linestyle=':')
    
    plt.title(f'Price Optimization over Time for Product "{sample_products[0]}" (First 30 Days)', fontsize=14)
    plt.ylabel('Price ($)', fontsize=12)
    plt.xlabel('Date', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/price_trends_sample.png', bbox_inches='tight')
    plt.close()
    
    print(f"\nVisualizations successfully saved to '{output_dir}/'.")

if __name__ == "__main__":
    # Ensure correct dataset is mapped
    dataset_path = 'data/Updated_dynamic-pricing-dataset (1).csv'
    run_simulation(dataset_path)
