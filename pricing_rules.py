import pandas as pd
import numpy as np

def apply_pricing_rules(df):
    print("Applying pricing rules...")
    
    # Extract base price
    base_price = df['Price']
    
    # 1. Time-Based Adjustment
    # +10% on holidays/promotions, +5% on standard weekends
    time_adj = np.where(df['Holiday/Promotion'] == 1, 0.10,
               np.where(df['Is_Weekend'], 0.05, 0.0))
               
    # 2. Inventory-Based Adjustment
    # +5% if Low_Inventory (scarcity), -5% if High_Inventory (clear stock)
    inv_adj = np.where(df['Inventory Level'] < df['Low_Threshold'], 0.05,
              np.where(df['Inventory Level'] > df['High_Threshold'], -0.05, 0.0))
              
    # 3. Demand-Based Adjustment
    # +5% if Demand Forecast > Demand_Trend (increasing)
    # -5% if Demand Forecast < Demand_Trend (falling)
    demand_adj = np.where(df['Demand Forecast'] > df['Demand_Trend'], 0.05,
                 np.where(df['Demand Forecast'] < df['Demand_Trend'], -0.05, 0.0))
                 
    # Total Adjustment Multiplier
    # Sum of adjustments (e.g. +5% -5% +5% = +5%)
    total_adj = time_adj + inv_adj + demand_adj
    calculated_price = base_price * (1 + total_adj)
    
    # 4. Apply Business Constraints
    # Min price bounds: Cost + 20% margin to prevent losses
    # Max price bounds: Competitor Pricing + 5% max to remain competitive
    min_price = df['Cost'] * 1.20
    max_price = df['Competitor Pricing'] * 1.05
    
    # Enforce constraints using vectorized maximums and minimums
    # In rare edges where min_price > max_price, we must still respect min_price (margin).
    capped_price = np.minimum(calculated_price, max_price)
    recommended_price = np.maximum(capped_price, min_price)
    
    print("Pricing rules applied and constraints enforced successfully.")
    return recommended_price
