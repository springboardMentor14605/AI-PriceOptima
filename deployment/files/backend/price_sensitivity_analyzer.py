"""
=============================================================================
EXPERIMENT: ADVANCED PRICE SENSITIVITY ANALYZER
=============================================================================
PURPOSE: Analyze how demand responds to price changes across different
         product categories, seasons, and regions
         
METHODOLOGY:
  1. Test multiple price points for each scenario
  2. Calculate price elasticity coefficients
  3. Identify optimal pricing zones
  4. Generate actionable insights

NEW FEATURES BEYOND BASIC ELASTICITY:
  ✅ Category-specific elasticity analysis
  ✅ Seasonal pricing recommendations
  ✅ Regional price sensitivity mapping
  ✅ Competitive response modeling
  ✅ Revenue vs margin trade-off analysis
=============================================================================
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import json

# Mock model for demonstration (replace with actual trained model)
class DemandPredictor:
    """Simplified demand prediction model"""
    def predict_demand(self, price: float, cost: float, category: int, 
                      season: int, region: int, competitor_price: float) -> float:
        """
        Simplified demand model:
        - Base demand decreases with price
        - Increases with competitor price gap
        - Varies by category, season, region
        """
        base_demand = 100
        
        # Price effect (elastic)
        price_effect = -0.8 * price
        
        # Competitor effect
        comp_effect = 0.3 * (competitor_price - price)
        
        # Category multiplier (electronics more elastic)
        category_multipliers = [1.2, 0.9, 1.0, 0.8, 0.95]
        cat_effect = category_multipliers[category] * 10
        
        # Seasonal multiplier
        season_multipliers = [0.9, 1.1, 0.95, 1.2]  # Winter highest
        season_effect = season_multipliers[season] * 5
        
        # Regional multiplier
        region_multipliers = [1.0, 0.85, 0.9, 1.1]
        region_effect = region_multipliers[region] * 5
        
        # Random noise
        noise = np.random.normal(0, 3)
        
        demand = (base_demand + price_effect + comp_effect + 
                 cat_effect + season_effect + region_effect + noise)
        
        return max(0, demand)  # Demand can't be negative


class PriceSensitivityAnalyzer:
    def __init__(self, model: DemandPredictor):
        self.model = model
        self.results = {}
    
    def analyze_category_elasticity(self, 
                                    base_price: float = 70.0,
                                    cost: float = 50.0,
                                    price_range: float = 0.4,
                                    steps: int = 20) -> Dict:
        """
        Analyze price sensitivity across different product categories
        """
        print("\n" + "="*70)
        print("EXPERIMENT 1: CATEGORY-SPECIFIC PRICE ELASTICITY")
        print("="*70)
        
        categories = {
            0: "Electronics",
            1: "Fashion", 
            2: "Home & Kitchen",
            3: "Sports",
            4: "Books"
        }
        
        results = {}
        
        for cat_id, cat_name in categories.items():
            print(f"\nAnalyzing {cat_name}...")
            
            prices = np.linspace(
                base_price * (1 - price_range),
                base_price * (1 + price_range),
                steps
            )
            
            demands = []
            revenues = []
            elasticities = []
            
            for i, price in enumerate(prices):
                # Predict demand
                demand = self.model.predict_demand(
                    price=price,
                    cost=cost,
                    category=cat_id,
                    season=2,  # Autumn
                    region=0,  # North
                    competitor_price=75.0
                )
                
                revenue = price * demand
                demands.append(demand)
                revenues.append(revenue)
                
                # Calculate elasticity
                if i > 0:
                    price_change = (price - prices[i-1]) / prices[i-1]
                    demand_change = (demand - demands[i-1]) / demands[i-1]
                    elasticity = demand_change / price_change if price_change != 0 else 0
                    elasticities.append(elasticity)
            
            # Find optimal price (max revenue)
            optimal_idx = np.argmax(revenues)
            optimal_price = prices[optimal_idx]
            max_revenue = revenues[optimal_idx]
            
            # Calculate average elasticity
            avg_elasticity = np.mean(elasticities) if elasticities else 0
            
            results[cat_name] = {
                "optimal_price": float(optimal_price),
                "max_revenue": float(max_revenue),
                "avg_elasticity": float(avg_elasticity),
                "elasticity_type": "Elastic" if abs(avg_elasticity) > 1 else "Inelastic",
                "price_sensitivity": "High" if abs(avg_elasticity) > 1.5 else "Medium" if abs(avg_elasticity) > 0.8 else "Low"
            }
            
            print(f"  ✓ Optimal Price: ₹{optimal_price:.2f}")
            print(f"  ✓ Max Revenue: ₹{max_revenue:.2f}")
            print(f"  ✓ Avg Elasticity: {avg_elasticity:.3f} ({results[cat_name]['elasticity_type']})")
            print(f"  ✓ Price Sensitivity: {results[cat_name]['price_sensitivity']}")
        
        self.results['category_elasticity'] = results
        return results
    
    def analyze_seasonal_pricing(self,
                                 base_price: float = 70.0,
                                 cost: float = 50.0,
                                 category: int = 0) -> Dict:
        """
        Analyze optimal pricing for different seasons
        """
        print("\n" + "="*70)
        print("EXPERIMENT 2: SEASONAL PRICING OPTIMIZATION")
        print("="*70)
        
        seasons = {
            0: "Spring",
            1: "Summer",
            2: "Autumn",
            3: "Winter"
        }
        
        results = {}
        
        for season_id, season_name in seasons.items():
            print(f"\nOptimizing for {season_name}...")
            
            # Test price range
            prices = np.linspace(base_price * 0.7, base_price * 1.3, 15)
            best_revenue = 0
            best_price = base_price
            
            for price in prices:
                demand = self.model.predict_demand(
                    price=price,
                    cost=cost,
                    category=category,
                    season=season_id,
                    region=0,
                    competitor_price=75.0
                )
                revenue = price * demand
                
                if revenue > best_revenue:
                    best_revenue = revenue
                    best_price = price
            
            profit_margin = ((best_price - cost) / best_price) * 100
            
            results[season_name] = {
                "recommended_price": float(best_price),
                "expected_revenue": float(best_revenue),
                "profit_margin": float(profit_margin),
                "vs_base": float(((best_price - base_price) / base_price) * 100)
            }
            
            print(f"  ✓ Recommended Price: ₹{best_price:.2f} ({results[season_name]['vs_base']:+.1f}% vs base)")
            print(f"  ✓ Expected Revenue: ₹{best_revenue:.2f}")
            print(f"  ✓ Profit Margin: {profit_margin:.1f}%")
        
        self.results['seasonal_pricing'] = results
        return results
    
    def analyze_regional_sensitivity(self,
                                     base_price: float = 70.0,
                                     cost: float = 50.0,
                                     category: int = 0) -> Dict:
        """
        Analyze price sensitivity across different regions
        """
        print("\n" + "="*70)
        print("EXPERIMENT 3: REGIONAL PRICE SENSITIVITY")
        print("="*70)
        
        regions = {
            0: "North",
            1: "South",
            2: "East",
            3: "West"
        }
        
        results = {}
        
        for region_id, region_name in regions.items():
            print(f"\nAnalyzing {region_name} region...")
            
            # Test multiple price points
            prices = np.linspace(base_price * 0.8, base_price * 1.2, 12)
            demands = []
            
            for price in prices:
                demand = self.model.predict_demand(
                    price=price,
                    cost=cost,
                    category=category,
                    season=2,
                    region=region_id,
                    competitor_price=75.0
                )
                demands.append(demand)
            
            # Calculate price sensitivity (slope of demand curve)
            price_sensitivity = np.polyfit(prices, demands, 1)[0]
            
            # Find optimal price
            revenues = [p * d for p, d in zip(prices, demands)]
            optimal_idx = np.argmax(revenues)
            optimal_price = prices[optimal_idx]
            max_revenue = revenues[optimal_idx]
            
            results[region_name] = {
                "optimal_price": float(optimal_price),
                "max_revenue": float(max_revenue),
                "price_sensitivity": float(price_sensitivity),
                "sensitivity_level": "High" if abs(price_sensitivity) > 1.0 else "Medium" if abs(price_sensitivity) > 0.5 else "Low",
                "recommended_strategy": "Competitive pricing" if abs(price_sensitivity) > 1.0 else "Premium pricing"
            }
            
            print(f"  ✓ Optimal Price: ₹{optimal_price:.2f}")
            print(f"  ✓ Max Revenue: ₹{max_revenue:.2f}")
            print(f"  ✓ Sensitivity: {results[region_name]['sensitivity_level']}")
            print(f"  ✓ Strategy: {results[region_name]['recommended_strategy']}")
        
        self.results['regional_sensitivity'] = results
        return results
    
    def competitive_response_analysis(self,
                                      base_price: float = 70.0,
                                      cost: float = 50.0,
                                      category: int = 0) -> Dict:
        """
        Analyze optimal pricing relative to competitor prices
        """
        print("\n" + "="*70)
        print("EXPERIMENT 4: COMPETITIVE RESPONSE MODELING")
        print("="*70)
        
        competitor_prices = [60, 65, 70, 75, 80, 85, 90]
        results = {}
        
        for comp_price in competitor_prices:
            print(f"\nCompetitor Price: ₹{comp_price}")
            
            # Test our price points
            our_prices = np.linspace(comp_price * 0.85, comp_price * 1.15, 10)
            best_revenue = 0
            best_price = base_price
            
            for our_price in our_prices:
                demand = self.model.predict_demand(
                    price=our_price,
                    cost=cost,
                    category=category,
                    season=2,
                    region=0,
                    competitor_price=comp_price
                )
                revenue = our_price * demand
                
                if revenue > best_revenue:
                    best_revenue = revenue
                    best_price = our_price
            
            price_gap = ((best_price - comp_price) / comp_price) * 100
            
            results[f"Competitor_₹{comp_price}"] = {
                "competitor_price": float(comp_price),
                "our_optimal_price": float(best_price),
                "price_gap_pct": float(price_gap),
                "expected_revenue": float(best_revenue),
                "strategy": "Premium" if price_gap > 5 else "Match" if abs(price_gap) < 5 else "Undercut"
            }
            
            print(f"  ✓ Our Optimal: ₹{best_price:.2f} ({price_gap:+.1f}% vs competitor)")
            print(f"  ✓ Strategy: {results[f'Competitor_₹{comp_price}']['strategy']}")
            print(f"  ✓ Expected Revenue: ₹{best_revenue:.2f}")
        
        self.results['competitive_response'] = results
        return results
    
    def revenue_margin_tradeoff(self,
                               base_price: float = 70.0,
                               cost: float = 50.0,
                               category: int = 0) -> Dict:
        """
        Analyze trade-off between revenue maximization and margin protection
        """
        print("\n" + "="*70)
        print("EXPERIMENT 5: REVENUE vs MARGIN TRADE-OFF ANALYSIS")
        print("="*70)
        
        prices = np.linspace(cost * 1.1, base_price * 1.5, 30)
        revenues = []
        margins = []
        demands = []
        
        for price in prices:
            demand = self.model.predict_demand(
                price=price,
                cost=cost,
                category=category,
                season=2,
                region=0,
                competitor_price=75.0
            )
            revenue = price * demand
            margin = ((price - cost) / price) * 100
            
            revenues.append(revenue)
            margins.append(margin)
            demands.append(demand)
        
        # Find different optimization points
        max_revenue_idx = np.argmax(revenues)
        max_margin_idx = np.argmax(margins)
        
        # Find balanced point (Pareto optimal)
        # Normalized revenue + normalized margin
        norm_revenues = (revenues - np.min(revenues)) / (np.max(revenues) - np.min(revenues))
        norm_margins = (margins - np.min(margins)) / (np.max(margins) - np.min(margins))
        combined_score = norm_revenues + norm_margins
        balanced_idx = np.argmax(combined_score)
        
        results = {
            "max_revenue_strategy": {
                "price": float(prices[max_revenue_idx]),
                "revenue": float(revenues[max_revenue_idx]),
                "margin": float(margins[max_revenue_idx]),
                "demand": float(demands[max_revenue_idx])
            },
            "max_margin_strategy": {
                "price": float(prices[max_margin_idx]),
                "revenue": float(revenues[max_margin_idx]),
                "margin": float(margins[max_margin_idx]),
                "demand": float(demands[max_margin_idx])
            },
            "balanced_strategy": {
                "price": float(prices[balanced_idx]),
                "revenue": float(revenues[balanced_idx]),
                "margin": float(margins[balanced_idx]),
                "demand": float(demands[balanced_idx])
            }
        }
        
        print("\nStrategy Comparison:")
        print(f"\n1. MAX REVENUE Strategy:")
        print(f"   Price: ₹{results['max_revenue_strategy']['price']:.2f}")
        print(f"   Revenue: ₹{results['max_revenue_strategy']['revenue']:.2f}")
        print(f"   Margin: {results['max_revenue_strategy']['margin']:.1f}%")
        
        print(f"\n2. MAX MARGIN Strategy:")
        print(f"   Price: ₹{results['max_margin_strategy']['price']:.2f}")
        print(f"   Revenue: ₹{results['max_margin_strategy']['revenue']:.2f}")
        print(f"   Margin: {results['max_margin_strategy']['margin']:.1f}%")
        
        print(f"\n3. BALANCED Strategy (Recommended):")
        print(f"   Price: ₹{results['balanced_strategy']['price']:.2f}")
        print(f"   Revenue: ₹{results['balanced_strategy']['revenue']:.2f}")
        print(f"   Margin: {results['balanced_strategy']['margin']:.1f}%")
        
        self.results['revenue_margin_tradeoff'] = results
        return results
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("\n" + "="*70)
        print("PRICE SENSITIVITY ANALYSIS - SUMMARY REPORT")
        print("="*70)
        
        print("\n📊 KEY INSIGHTS:")
        
        # Category insights
        if 'category_elasticity' in self.results:
            print("\n1. CATEGORY ELASTICITY:")
            for cat, data in self.results['category_elasticity'].items():
                print(f"   • {cat}: {data['elasticity_type']} "
                      f"(Elasticity: {data['avg_elasticity']:.3f}, "
                      f"Optimal: ₹{data['optimal_price']:.2f})")
        
        # Seasonal insights
        if 'seasonal_pricing' in self.results:
            print("\n2. SEASONAL RECOMMENDATIONS:")
            for season, data in self.results['seasonal_pricing'].items():
                print(f"   • {season}: ₹{data['recommended_price']:.2f} "
                      f"({data['vs_base']:+.1f}% vs base)")
        
        # Regional insights
        if 'regional_sensitivity' in self.results:
            print("\n3. REGIONAL STRATEGIES:")
            for region, data in self.results['regional_sensitivity'].items():
                print(f"   • {region}: {data['recommended_strategy']} "
                      f"(Sensitivity: {data['sensitivity_level']})")
        
        print("\n" + "="*70)
        
        # Save results to JSON
        with open('price_sensitivity_analysis.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print("\n✅ Full analysis saved to: price_sensitivity_analysis.json")


def main():
    """Run all price sensitivity experiments"""
    print("\n" + "="*70)
    print("ADVANCED PRICE SENSITIVITY ANALYZER")
    print("Milestone 6 - New Experimentation")
    print("="*70)
    
    # Initialize model and analyzer
    model = DemandPredictor()
    analyzer = PriceSensitivityAnalyzer(model)
    
    # Run all experiments
    analyzer.analyze_category_elasticity()
    analyzer.analyze_seasonal_pricing()
    analyzer.analyze_regional_sensitivity()
    analyzer.competitive_response_analysis()
    analyzer.revenue_margin_tradeoff()
    
    # Generate summary
    analyzer.generate_summary_report()
    
    print("\n🎉 All experiments completed successfully!\n")


if __name__ == "__main__":
    main()
