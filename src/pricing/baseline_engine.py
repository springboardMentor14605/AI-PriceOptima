"""
Baseline Pricing Engine - AI: PriceOptima
This module implements a rule-based pricing strategy to serve as a baseline 
comparison for the advanced ML models.
"""

def get_baseline_price(current_price: float, inventory_level: int) -> float:
    """
    Applies simple business rules to recommend a price based on inventory.
    
    Rules:
    - Low Inventory (< 20): Increase price by 10% to slow down sales and maximize margin.
    - High Inventory (> 100): Decrease price by 10% (discount) to clear stock.
    - Normal Inventory (20-100): Maintain current price.
    
    Args:
        current_price (float): The current selling price of the product.
        inventory_level (int): The current units in stock.
        
    Returns:
        float: The recommended baseline price.
    """
    
    # Rule 1: Scarcity Pricing
    if inventory_level < 20: 
        recommended_price = current_price * 1.10
    
    # Rule 2: Liquidation/Discount Pricing
    elif inventory_level > 100:
        recommended_price = current_price * 0.90
    
    # Rule 3: Static/Standard Pricing
    else:
        recommended_price = current_price
        
    return round(recommended_price, 2)

if __name__ == "__main__":
    # Test cases
    print(f"Low Stock Test: {get_baseline_price(100, 10)}")    # Expect 110.0
    print(f"High Stock Test: {get_baseline_price(100, 150)}")  # Expect 90.0
    print(f"Normal Stock Test: {get_baseline_price(100, 50)}") # Expect 100.0
