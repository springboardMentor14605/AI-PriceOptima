import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
import os

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

warnings.filterwarnings("ignore")

class RuleBasedPricingEngine:
    """
    Advanced, Object-Oriented Rule-Based Engine for Dynamic Pricing.
    Utilizes highly performant vectorized pandas and numpy operations 
    to process datasets scaling to millions of rows seamlessly.
    """

    def __init__(self, data_path, config=None):
        self.data_path = data_path
        self.df = None
        self.results = None
        
        # Configuration for dynamic rule multipliers.
        # This makes the logic tunable without code changes.
        self.config = config or {
            "inv_very_high": 0.12,
            "inv_high": 0.07,
            "inv_overstock": -0.10,
            "inv_slow": -0.04,
            
            "dem_very_high": 0.10,
            "dem_high": 0.05,
            "dem_weak": -0.08,
            "dem_very_weak": -0.03,
            
            "comp_much_costlier": 0.08,
            "comp_costlier": 0.04,
            "comp_much_cheaper": -0.09,
            "comp_cheaper": -0.04,
            
            "holiday_boost": 0.06,
            "peak_season_boost": 0.05,
            "off_season_discount": -0.03,
            
            "poor_weather_discount": -0.04,
            "good_weather_boost": 0.02,
            
            "weekend_boost": 0.03,
            "high_traffic_boost": 0.04,
            
            "margin_floor": 1.10,   # Minimum 10% margin
            "price_band_lower": 0.70, # Max 30% discount from listed
            "price_band_upper": 1.30  # Max 30% markup from listed
        }

    def load_data(self):
        print("=" * 65)
        print("        MILESTONE 4: RULE-BASED DYNAMIC PRICING ENGINE")
        print("                 (Advanced Vectorized Mode)            ")
        print("=" * 65)

        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"File not found: {self.data_path}. Please adjust path.")

        self.df = pd.read_csv(self.data_path)
        self.df["date"] = pd.to_datetime(self.df["date"], format='mixed', dayfirst=True)
        
        # Normalise column names to lowercase so rules can reference them consistently
        self.df.columns = [c.lower() for c in self.df.columns]

        print(f"\n Dataset loaded: {self.df.shape[0]:,} rows × {self.df.shape[1]} columns")
        print(f"   Date range: {self.df['date'].min().date()} → {self.df['date'].max().date()}")
        print(f"   Stores: {self.df['store_id'].nunique()}  |  Products: {self.df['product_id'].nunique()}")
        return self

    def calculate_baseline(self):
        """Computes the static (baseline) revenue."""
        # Using discounted price as actual static basis
        self.df["static_price"] = self.df["discounted_price"] if "discounted_price" in self.df.columns else self.df["price"]
        self.df["static_revenue"] = self.df["static_price"] * self.df["units_sold"]
        print(f"\n Baseline (Static) Revenue Total : \u20b9{self.df['static_revenue'].sum():,.2f}")
        return self

    def apply_vectorized_rules(self):
        """
        Replaces the slow df.apply() iterative loop with true vectorization.
        Calculates all conditional rule multipliers simultaneously for maximum performance.
        """
        print("\n\u23f3 Applying advanced rule-based pricing engine (vectorized)...")
        c = self.config
        df = self.df

        # Start with a 1.0 base multiplier array matching the number of rows
        multiplier = np.ones(len(df))

        # RULE 1: INVENTORY PRESSURE
        inv_p = df["inventory_pressure"].values
        multiplier += np.select(
            [inv_p > 0.8, inv_p > 0.6, inv_p < 0.2, inv_p < 0.4],
            [c["inv_very_high"], c["inv_high"], c["inv_overstock"], c["inv_slow"]],
            default=0.0
        )

        # RULE 2: DEMAND RATIO
        dem_r = df["demand_ratio"].values
        multiplier += np.select(
            [dem_r > 1.3, dem_r > 1.1, dem_r < 0.7, dem_r < 0.9],
            [c["dem_very_high"], c["dem_high"], c["dem_weak"], c["dem_very_weak"]],
            default=0.0
        )

        # RULE 3: COMPETITOR GAP
        comp_g = df["competitor_gap"].values
        multiplier += np.select(
            [comp_g > 10, comp_g > 3, comp_g < -10, comp_g < -3],
            [c["comp_much_costlier"], c["comp_costlier"], c["comp_much_cheaper"], c["comp_cheaper"]],
            default=0.0
        )

        # RULE 4: HOLIDAY
        multiplier += np.where(df["holiday/promotion"] == 1, c["holiday_boost"], 0.0)

        # RULE 5: SEASONALITY
        season = df["seasonality"].values
        # Using np.isin for fast array set containment checks
        multiplier += np.where(np.isin(season, ["Summer", "Winter"]), c["peak_season_boost"], 0.0)
        multiplier += np.where(np.isin(season, ["Spring", "Autumn"]), c["off_season_discount"], 0.0)

        # RULE 6: WEATHER
        weather = df["weather_condition"].values
        multiplier += np.where(np.isin(weather, ["Snowy", "Rainy"]), c["poor_weather_discount"], 0.0)
        multiplier += np.where(weather == "Sunny", c["good_weather_boost"], 0.0)

        # RULE 7: WEEKEND
        multiplier += np.where(df["is_weekend"] == 1, c["weekend_boost"], 0.0)

        # RULE 8: HIGH TRAFFIC
        if "traffic_intensity" in df.columns:
            multiplier += np.where(df["traffic_intensity"] > 0.75, c["high_traffic_boost"], 0.0)

        # Base Dynamic Calculation
        dynamic_price = df["price"].values * multiplier

        # RULE 9: PROFIT FLOOR GUARD (Minimum Margin)
        min_allowed = df["cost"].values * c["margin_floor"]
        dynamic_price = np.maximum(dynamic_price, min_allowed)

        # RULE 10: PRICE BAND GUARD (Bounded Swings)
        lower_band = df["price"].values * c["price_band_lower"]
        upper_band = df["price"].values * c["price_band_upper"]
        dynamic_price = np.clip(dynamic_price, lower_band, upper_band)

        # Assign back and finalize KPIs
        df["dynamic_price"] = np.round(dynamic_price, 2)
        df["dynamic_revenue"] = df["dynamic_price"] * df["units_sold"]
        df["price_change_pct"] = (df["dynamic_price"] - df["static_price"]) / df["static_price"] * 100

        print("\u2705 Dynamic prices computed via localized native C arrays (vectorized).")
        return self

    def generate_metrics(self):
        """Compiles KPIs based on the static vs dynamic output."""
        total_static = self.df["static_revenue"].sum()
        total_dynamic = self.df["dynamic_revenue"].sum()
        revenue_lift = ((total_dynamic - total_static) / total_static) * 100

        self.results = {
            "total_static": total_static,
            "total_dynamic": total_dynamic,
            "revenue_lift": revenue_lift
        }

        print("\n" + "=" * 65)
        print("                  REVENUE COMPARISON RESULTS")
        print("=" * 65)
        print(f"  Static  (Baseline) Revenue : \u20b9{total_static:>15,.2f}")
        print(f"  Dynamic (Rule-Based) Revenue : \u20b9{total_dynamic:>15,.2f}")
        print(f"  Revenue Lift               :  {revenue_lift:>+.2f}%")
        print("=" * 65)

        print(f"\n\U0001f4ca Price Change Statistics:")
        safe_pct = self.df["price_change_pct"].replace([np.inf, -np.inf], np.nan)
        print(f"   Mean adjustment    : {safe_pct.mean():+.2f}%")
        print(f"   Median adjustment  : {safe_pct.median():+.2f}%")
        print(f"   Max increase       : {safe_pct.max():+.2f}%")
        print(f"   Max decrease       : {safe_pct.min():+.2f}%")
        print(f"   Rows with price UP : {(safe_pct > 0).sum():,}")
        print(f"   Rows with price DN : {(safe_pct < 0).sum():,}")

        # Category Output
        self.df["year_month"] = self.df["date"].dt.to_period("M")
        return self

    def plot_visualizations(self, filename="milestone4_advanced_results.png"):
        """Encapsulates Matplotlib procedures for cleanliness and modular execution."""
        print("\n\U0001f4c8 Generating advanced visualisation plots...")
        df = self.df
        total_static = self.results["total_static"]
        total_dynamic = self.results["total_dynamic"]

        fig = plt.figure(figsize=(18, 14))
        fig.suptitle("Milestone 4 \u2014 Advanced Vectorized Dynamic Pricing Engine\nPriceOptima Project",
                     fontsize=16, fontweight="bold", y=0.98)

        gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.38)

        # Plot 1: Total Revenue Comparison
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.bar(["Static\nBaseline", "Rule-Based\nDynamic"], 
                [total_static / 1e6, total_dynamic / 1e6], 
                color=["#E74C3C", "#2ECC71"], width=0.5, edgecolor="black")
        ax1.set_title("Total Revenue Comparison", fontweight="bold")
        ax1.set_ylabel("Revenue (Millions \u20b9)")
        ax1.set_ylim(0, max([total_static, total_dynamic]) / 1e6 * 1.15)

        # Groupby Helpers
        cat_summary = self._calculate_lift_by("category")
        season_summary = self._calculate_lift_by("seasonality")
        monthly = self._calculate_lift_by("year_month")

        # Plot 2: Revenue Lift by Category
        ax2 = fig.add_subplot(gs[0, 1])
        c_colors = ["#3498DB" if x >= 0 else "#E74C3C" for x in cat_summary["lift_%"]]
        ax2.barh(cat_summary["category"], cat_summary["lift_%"], color=c_colors, edgecolor="black")
        ax2.axvline(0, color="black", linewidth=1)
        ax2.set_title("Revenue Lift % by Category", fontweight="bold")

        # Plot 3: Lift by Season
        ax3 = fig.add_subplot(gs[0, 2])
        s_colors = ["#F39C12" if x >= 0 else "#E74C3C" for x in season_summary["lift_%"]]
        ax3.bar(season_summary["seasonality"], season_summary["lift_%"], color=s_colors, edgecolor="black")
        ax3.axhline(0, color="black", linewidth=1)
        ax3.set_title("Revenue Lift % by Season", fontweight="bold")

        # Plot 4: Monthly Trend Line
        ax4 = fig.add_subplot(gs[1, :])
        x = range(len(monthly))
        ax4.plot(x, monthly["static_revenue"] / 1e6, label="Static Baseline", color="#E74C3C", marker="o")
        ax4.plot(x, monthly["dynamic_revenue"] / 1e6, label="Dynamic Expected", color="#2ECC71", marker="s")
        ax4.fill_between(x, monthly["static_revenue"] / 1e6, monthly["dynamic_revenue"] / 1e6, alpha=0.15, color="#2ECC71")
        ax4.set_xticks(x)
        ax4.set_xticklabels([str(p) for p in monthly["year_month"]], rotation=45)
        ax4.set_title("Monthly Revenue Trend", fontweight="bold")
        ax4.legend()
        ax4.grid(alpha=0.3)

        # Plot 5: Histogram — filter inf values before plotting
        ax5 = fig.add_subplot(gs[2, 0])
        safe_pct = df["price_change_pct"].replace([np.inf, -np.inf], np.nan).dropna()
        ax5.hist(safe_pct, bins=60, color="#9B59B6", edgecolor="white")
        ax5.axvline(0, color="red")
        ax5.axvline(safe_pct.mean(), color="orange")
        ax5.set_title("Distribution of Price Adjustments", fontweight="bold")

        plt.savefig(filename, dpi=150, bbox_inches="tight")
        print(f"\u2705 Visualisation saved: {filename}")
        plt.close("all")
        return self
        
    def _calculate_lift_by(self, column):
        summary = self.df.groupby(column).agg(
            static_revenue=("static_revenue", "sum"),
            dynamic_revenue=("dynamic_revenue", "sum")
        ).reset_index()
        summary["lift_%"] = ((summary["dynamic_revenue"] - summary["static_revenue"]) / summary["static_revenue"]) * 100
        return summary

    def save_output(self, filename=None):
        """Saves the fully processed dataset."""
        if filename is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            os.makedirs(os.path.join(base_dir, "Outputs"), exist_ok=True)
            filename = os.path.join(base_dir, "Outputs", "milestone4_output.csv")
        base_cols = [
            "date", "store_id", "product_id", "category", "region",
            "price", "cost", "static_price", "dynamic_price",
            "units_sold", "static_revenue", "dynamic_revenue", "price_change_pct",
            "inventory_pressure", "demand_ratio", "competitor_gap",
            "seasonality", "weather_condition", "holiday/promotion", "is_weekend"
        ]
        cols = [c for c in base_cols if c in self.df.columns]
        self.df[cols].to_csv(filename, index=False)
        print(f"\u2705 Results saved: {filename}\n")

if __name__ == "__main__":
    # The default execution logic acts as a quick runner for the advanced engine.
    
    # Resolving typical locations based on the workspace format
    DATA_PATH = r"d:\Infosys-Project\AI-PriceOptima\Feature Engineering\feature_engineered_dataset.csv"
    if not os.path.exists(DATA_PATH):
        # Fallback to current directory sibling paths if running inside 'scripts' etc.
        DATA_PATH = r"../Feature Engineering/feature_engineered_dataset.csv"

    # Instantiate, Compute, and Plot
    engine = RuleBasedPricingEngine(data_path=DATA_PATH)
    engine.load_data() \
          .calculate_baseline() \
          .apply_vectorized_rules() \
          .generate_metrics() \
          .plot_visualizations() \
          .save_output()
