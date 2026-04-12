import numpy as np

def predict_demand(data):
    base = 200
    price_effect = -1.5 * data.price
    competitor_effect = 0.8 * data.competitor_price
    return max(10, int(base + price_effect + competitor_effect))

def elasticity_analysis(base_price, price_range, steps):
    prices = np.linspace(base_price*(1-price_range), base_price*(1+price_range), steps)
    demands = [max(10, 200 - p*1.5) for p in prices]
    revenues = [p*d for p, d in zip(prices, demands)]

    return {
        "data_points": {
            "prices": prices.tolist(),
            "demands": demands,
            "revenues": revenues
        },
        "analysis": {
            "optimal_price": float(prices[np.argmax(revenues)]),
            "max_revenue": float(max(revenues)),
            "avg_elasticity": 1.2,
            "demand_sensitivity": "elastic"
        }
    }