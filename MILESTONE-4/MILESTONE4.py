# =============================================================================
# MILESTONE 4: RULE-BASED DYNAMIC PRICING ENGINE
# Project: PriceOptima
# =============================================================================
# OBJECTIVE: Build a rule-based pricing engine that adjusts prices based on
# business logic using inventory levels, demand forecasts, competitor pricing,
# seasonality, and more — then compare revenue lift against static pricing.
#
# WHY RULE-BASED FIRST?
# Before we use ML (Milestone 5), we create a simple interpretable engine that
# business managers can understand, audit, and trust. It also serves as our
# BASELINE BENCHMARK to measure how much ML actually improves things.
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# =============================================================================
# STEP 1: LOAD THE FEATURE-ENGINEERED DATASET
# =============================================================================
# WHY: We load the already feature-engineered dataset (not raw data) because
# it contains derived columns like inventory_pressure, competitor_gap,
# demand_ratio etc. — which are exactly what rule-based engines use.
#
# ALTERNATIVE: Load raw data and compute features here.
# OUR APPROACH IS BETTER: Avoids code duplication; keeps pipeline clean.
# =============================================================================

print("=" * 65)
print("        MILESTONE 4: RULE-BASED DYNAMIC PRICING ENGINE")
print("=" * 65)

df = pd.read_csv(r"../datasets/feature_engineered_dataset.csv")

# Parse date column so we can sort by time later
df["date"] = pd.to_datetime(df["date"], format='mixed', dayfirst=True)

print(f"\n Dataset loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"   Date range: {df['date'].min().date()} → {df['date'].max().date()}")
print(f"   Stores: {df['store_id'].nunique()}  |  Products: {df['product_id'].nunique()}")

# =============================================================================
# STEP 2: DEFINE THE STATIC / BASELINE PRICE
# =============================================================================
# WHY: The "static price" is the original listed price with a flat discount
# applied. Real businesses often use this simple approach: one price for
# everyone, with occasional discounts. We use this as our baseline revenue.
#
# ALTERNATIVE: Use `price` directly as the baseline (no discount).
# OUR APPROACH: Use `discounted_price` = price × (1 − discount).
# This reflects what the customer actually pays, which is fairer as a baseline.
# =============================================================================

df["static_price"] = df["discounted_price"]         # original discounted price
df["static_revenue"] = df["static_price"] * df["units_sold"]

print(f"\n Baseline (Static) Revenue Total : ₹{df['static_revenue'].sum():,.2f}")

# =============================================================================
# STEP 3: THE RULE-BASED PRICING FUNCTION
# =============================================================================
# WHY: We define a function that looks at multiple signals for EACH row and
# decides a final adjusted price. Each rule is a business constraint.
#
# RULES APPLIED (in layered order):
#   Rule 1 — Inventory Pressure  : If stock is tight (high pressure) → raise price
#                                  If overstock (low pressure) → lower to clear stock
#   Rule 2 — Demand Ratio        : If demand_forecast >> units_sold → raise price
#                                  If demand_forecast << units_sold → lower price
#   Rule 3 — Competitor Gap      : If our price >> competitor → lower to match
#                                  If our price << competitor → can raise slightly
#   Rule 4 — Holiday / Promotion : On holidays, demand is high → raise slightly
#   Rule 5 — Seasonality         : Summer/Winter = peak → raise
#                                  Spring/Autumn = low → lower
#   Rule 6 — Weather             : Snowy/Rainy → people stay indoors → discount
#   Rule 7 — Weekend Boost       : Weekend traffic is high → small markup
#   Rule 8 — Profit Floor Guard  : Never sell below cost (cost + 10% minimum)
#   Rule 9 — Price Band Guard    : Price must stay within ±30% of original price
# =============================================================================

def apply_rules(row):
    """
    Takes one row of the dataset and returns an adjusted price based on
    layered business rules.
    """

    price = row["price"]        # the original listed price
    cost  = row["cost_price"]         # the cost to procure/produce

    # We'll accumulate a multiplier that nudges price up or down
    multiplier = 1.0

    # ------------------------------------------------------------------
    # RULE 1: INVENTORY PRESSURE
    # inventory_pressure is pre-computed as: units_sold / inventory_level
    # High value → selling fast → stock running low → raise price (scarcity)
    # Low value  → selling slow → lots of stock     → lower price (clear stock)
    # ------------------------------------------------------------------
    inv_pressure = row["inventory_pressure"]
    if inv_pressure > 0.8:
        multiplier += 0.12      # +12% for very high pressure (near stock-out)
    elif inv_pressure > 0.6:
        multiplier += 0.07      # +7% for moderate-high pressure
    elif inv_pressure < 0.2:
        multiplier -= 0.10      # -10% for overstock (push clearance)
    elif inv_pressure < 0.4:
        multiplier -= 0.04      # -4% for slow-moving stock

    # ------------------------------------------------------------------
    # RULE 2: DEMAND RATIO
    # demand_ratio = demand_forecast / units_sold
    # Ratio > 1 → forecast is higher than actual → demand is rising → raise
    # Ratio < 1 → forecast is lower than actual → demand is falling → lower
    # ------------------------------------------------------------------
    demand_ratio = row["demand_ratio"]
    if demand_ratio > 1.3:
        multiplier += 0.10      # strong predicted demand → markup
    elif demand_ratio > 1.1:
        multiplier += 0.05      # mild predicted demand
    elif demand_ratio < 0.7:
        multiplier -= 0.08      # weak predicted demand → discount
    elif demand_ratio < 0.9:
        multiplier -= 0.03

    # ------------------------------------------------------------------
    # RULE 3: COMPETITOR GAP
    # competitor_gap = competitor_pricing - price
    # Positive → our price < competitor → we can afford to raise a little
    # Negative → our price > competitor → we risk losing customers → lower
    # ------------------------------------------------------------------
    comp_gap = row["competitor_gap"]
    if comp_gap > 10:
        multiplier += 0.08      # competitors much costlier → raise confidently
    elif comp_gap > 3:
        multiplier += 0.04      # small advantage → mild raise
    elif comp_gap < -10:
        multiplier -= 0.09      # we are too expensive vs competitor → cut
    elif comp_gap < -3:
        multiplier -= 0.04      # slightly above competitor → small trim

    # ------------------------------------------------------------------
    # RULE 4: HOLIDAY / PROMOTION
    # holiday/promotion == 1 → people are shopping → demand is high → raise
    # ------------------------------------------------------------------
    if row["holiday"] == 1:
        multiplier += 0.06

    # ------------------------------------------------------------------
    # RULE 5: SEASONALITY
    # Summer and Winter tend to be peak seasons for most categories
    # ------------------------------------------------------------------
    season = row["seasonality"]
    if season in ["Summer", "Winter"]:
        multiplier += 0.05      # peak season → markup
    elif season in ["Spring", "Autumn"]:
        multiplier -= 0.03      # off-peak → slight discount to attract buyers

    # ------------------------------------------------------------------
    # RULE 6: WEATHER CONDITION
    # Snowy / Rainy → fewer people go to physical stores → incentivise online
    # Sunny → foot traffic is high → normal or slight markup
    # ------------------------------------------------------------------
    weather = row["weather_condition"]
    if weather in ["Snowy", "Rainy"]:
        multiplier -= 0.04      # lower price to encourage purchase
    elif weather == "Sunny":
        multiplier += 0.02      # high foot traffic → slight boost

    # ------------------------------------------------------------------
    # RULE 7: WEEKEND BOOST
    # is_weekend == 1 → more leisure shoppers → higher willingness to pay
    # ------------------------------------------------------------------
    if row["is_weekend"] == 1:
        multiplier += 0.03

    # ------------------------------------------------------------------
    # RULE 8: HIGH TRAFFIC INTENSITY BOOST
    # traffic_intensity is a pre-computed feature reflecting visitor volume
    # More visitors on a day → more competition for products → higher price
    # ------------------------------------------------------------------
    if row["traffic_intensity"] > 0.75:
        multiplier += 0.04

    # ------------------------------------------------------------------
    # Apply the total multiplier to the original price
    # ------------------------------------------------------------------
    dynamic_price = price * multiplier

    # ------------------------------------------------------------------
    # RULE 9 (SAFETY): PROFIT FLOOR GUARD
    # We must NEVER price below cost. Minimum = cost × 1.10 (10% min margin)
    # WHY: Selling below cost destroys the business.
    # ------------------------------------------------------------------
    min_allowed = cost * 1.10
    dynamic_price = max(dynamic_price, min_allowed)

    # ------------------------------------------------------------------
    # RULE 10 (SAFETY): PRICE BAND GUARD
    # Dynamic price must stay within ±30% of original listed price.
    # WHY: Extreme price swings damage customer trust.
    # ALTERNATIVE: ±20% is more conservative; ±50% more aggressive.
    # ±30% is the industry-standard band for dynamic pricing systems.
    # ------------------------------------------------------------------
    lower_band = price * 0.70
    upper_band = price * 1.30
    dynamic_price = np.clip(dynamic_price, lower_band, upper_band)

    return round(dynamic_price, 2)


# =============================================================================
# STEP 4: APPLY RULES TO ENTIRE DATASET
# =============================================================================
# WHY: We apply the function row-by-row. pandas .apply() calls the function
# for each row and stores the returned price in a new column.
#
# ALTERNATIVE: Vectorised numpy operations (faster but less readable).
# OUR APPROACH: .apply() is slower but easier to understand and debug,
# which is perfect for a rule-based system where clarity matters.
# =============================================================================

print("\n⏳ Applying rule-based pricing engine to all rows...")
df["dynamic_price"] = df.apply(apply_rules, axis=1)

# Calculate revenue with our dynamic price
df["dynamic_revenue"] = df["dynamic_price"] * df["units_sold"]

print("✅ Dynamic prices computed.")

# =============================================================================
# STEP 5: REVENUE LIFT CALCULATION
# =============================================================================
# WHY: Revenue Lift measures how much MORE revenue our engine generates
# compared to the baseline static pricing.
# FORMULA: Lift = (ML Revenue - Baseline Revenue) / Baseline Revenue × 100
# A positive lift means our pricing strategy is profitable.
# =============================================================================

total_static   = df["static_revenue"].sum()
total_dynamic  = df["dynamic_revenue"].sum()
revenue_lift   = (total_dynamic - total_static) / total_static * 100

print("\n" + "=" * 65)
print("                  REVENUE COMPARISON RESULTS")
print("=" * 65)
print(f"  Static  (Baseline) Revenue : ₹{total_static:>15,.2f}")
print(f"  Dynamic (Rule-Based) Revenue : ₹{total_dynamic:>15,.2f}")
print(f"  Revenue Lift               :  {revenue_lift:>+.2f}%")
print("=" * 65)

# =============================================================================
# STEP 6: AVERAGE PRICE CHANGE ANALYSIS
# =============================================================================
# WHY: We want to see HOW MUCH our engine is changing prices on average.
# This validates the rules are actually doing something meaningful.
# =============================================================================

df["price_change_pct"] = np.where(
    df["static_price"] == 0,
    0,
    (df["dynamic_price"] - df["static_price"]) / df["static_price"] * 100
)
# FIX: Remove infinite and NaN values
df["price_change_pct"].replace([np.inf, -np.inf], np.nan, inplace=True)
df["price_change_pct"].fillna(0, inplace=True)

print(f"\n📊 Price Change Statistics:")
print(f"   Mean adjustment    : {df['price_change_pct'].mean():+.2f}%")
print(f"   Median adjustment  : {df['price_change_pct'].median():+.2f}%")
print(f"   Max increase       : {df['price_change_pct'].max():+.2f}%")
print(f"   Max decrease       : {df['price_change_pct'].min():+.2f}%")
print(f"   Rows with price UP : {(df['price_change_pct'] > 0).sum():,}")
print(f"   Rows with price DN : {(df['price_change_pct'] < 0).sum():,}")

# =============================================================================
# STEP 7: REVENUE LIFT BY CATEGORY
# =============================================================================
# WHY: Different product categories behave differently. Breaking down by
# category tells us where our engine performs best and worst.
# =============================================================================

print("\n📦 Revenue Lift by Category:")
cat_summary = df.groupby("category").agg(
    static_rev   = ("static_revenue",  "sum"),
    dynamic_rev  = ("dynamic_revenue", "sum")
).reset_index()
cat_summary["lift_%"] = (
    (cat_summary["dynamic_rev"] - cat_summary["static_rev"])
    / cat_summary["static_rev"] * 100
)
print(cat_summary.to_string(index=False))

# =============================================================================
# STEP 8: REVENUE LIFT BY SEASON
# =============================================================================

print("\n🌤  Revenue Lift by Seasonality:")
season_summary = df.groupby("seasonality").agg(
    static_rev  = ("static_revenue",  "sum"),
    dynamic_rev = ("dynamic_revenue", "sum")
).reset_index()
season_summary["lift_%"] = (
    (season_summary["dynamic_rev"] - season_summary["static_rev"])
    / season_summary["static_rev"] * 100
)
print(season_summary.to_string(index=False))

# =============================================================================
# STEP 9: MONTHLY REVENUE TREND
# =============================================================================
# WHY: Shows how our engine performs over time. If lift is consistent across
# months, the rules are robust. Inconsistency may reveal seasonal bias.
# =============================================================================

df["year_month"] = df["date"].dt.to_period("M")
monthly = df.groupby("year_month").agg(
    static_rev  = ("static_revenue",  "sum"),
    dynamic_rev = ("dynamic_revenue", "sum")
).reset_index()
monthly["lift_%"] = (monthly["dynamic_rev"] - monthly["static_rev"]) / monthly["static_rev"] * 100

# =============================================================================
# STEP 10: VISUALISATIONS
# =============================================================================

print("\n📈 Generating visualisation plots...")

fig = plt.figure(figsize=(18, 14))
fig.suptitle("Milestone 4 — Rule-Based Dynamic Pricing Engine\nPriceOptima Project",
             fontsize=16, fontweight="bold", y=0.98)

gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.38)

# --- Plot 1: Total Revenue Comparison (Bar) ---
ax1 = fig.add_subplot(gs[0, 0])
labels = ["Static\nBaseline", "Rule-Based\nDynamic"]
values = [total_static / 1e6, total_dynamic / 1e6]
colors = ["#E74C3C", "#2ECC71"]
bars = ax1.bar(labels, values, color=colors, width=0.5, edgecolor="black", linewidth=0.8)
ax1.set_title("Total Revenue Comparison", fontweight="bold")
ax1.set_ylabel("Revenue (Millions ₹)")
for bar, val in zip(bars, values):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
             f"₹{val:.2f}M", ha="center", va="bottom", fontsize=10, fontweight="bold")
ax1.set_ylim(0, max(values) * 1.15)

# --- Plot 2: Revenue Lift by Category ---
ax2 = fig.add_subplot(gs[0, 1])
color_list = ["#3498DB" if x >= 0 else "#E74C3C" for x in cat_summary["lift_%"]]
ax2.barh(cat_summary["category"], cat_summary["lift_%"], color=color_list, edgecolor="black", linewidth=0.6)
ax2.axvline(0, color="black", linewidth=1)
ax2.set_title("Revenue Lift % by Category", fontweight="bold")
ax2.set_xlabel("Lift (%)")
for i, v in enumerate(cat_summary["lift_%"]):
    ax2.text(v + 0.1, i, f"{v:+.1f}%", va="center", fontsize=8)

# --- Plot 3: Revenue Lift by Seasonality ---
ax3 = fig.add_subplot(gs[0, 2])
s_colors = ["#F39C12" if x >= 0 else "#E74C3C" for x in season_summary["lift_%"]]
ax3.bar(season_summary["seasonality"], season_summary["lift_%"], color=s_colors, edgecolor="black", linewidth=0.6)
ax3.axhline(0, color="black", linewidth=1)
ax3.set_title("Revenue Lift % by Season", fontweight="bold")
ax3.set_ylabel("Lift (%)")
for i, v in enumerate(season_summary["lift_%"]):
    ax3.text(i, v + 0.05, f"{v:+.1f}%", ha="center", va="bottom", fontsize=9)

# --- Plot 4: Monthly Revenue Trend ---
ax4 = fig.add_subplot(gs[1, :])
x = range(len(monthly))
ax4.plot(x, monthly["static_rev"] / 1e6, label="Static Baseline",
         color="#E74C3C", linewidth=2, marker="o", markersize=4)
ax4.plot(x, monthly["dynamic_rev"] / 1e6, label="Dynamic Rule-Based",
         color="#2ECC71", linewidth=2, marker="s", markersize=4)
ax4.fill_between(x, monthly["static_rev"] / 1e6, monthly["dynamic_rev"] / 1e6,
                 alpha=0.15, color="#2ECC71")
ax4.set_xticks(x)
ax4.set_xticklabels([str(p) for p in monthly["year_month"]], rotation=45, ha="right", fontsize=7)
ax4.set_title("Monthly Revenue: Static vs Rule-Based Dynamic Pricing", fontweight="bold")
ax4.set_ylabel("Revenue (Millions ₹)")
ax4.legend()
ax4.grid(axis="y", alpha=0.3)

# --- Plot 5: Price Change % Distribution ---
ax5 = fig.add_subplot(gs[2, 0])
clean_data = df["price_change_pct"].replace([np.inf, -np.inf], np.nan).dropna()

ax5.hist(clean_data, bins=60, color="#9B59B6", edgecolor="white", linewidth=0.4)
ax5.axvline(0, color="red", linestyle="--", linewidth=1.5, label="No Change")
ax5.axvline(df["price_change_pct"].mean(), color="orange", linestyle="-",
            linewidth=1.5, label=f"Mean={df['price_change_pct'].mean():+.1f}%")
ax5.set_title("Distribution of Price Adjustments", fontweight="bold")
ax5.set_xlabel("Price Change %")
ax5.set_ylabel("Frequency")
ax5.legend(fontsize=8)

# --- Plot 6: Price Change by Inventory Pressure Bucket ---
ax6 = fig.add_subplot(gs[2, 1])
df["inv_bucket"] = pd.cut(df["inventory_pressure"],
                           bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                           labels=["Very Low", "Low", "Med", "High", "Very High"])
inv_change = df.groupby("inv_bucket", observed=True)["price_change_pct"].mean()
inv_colors = ["#E74C3C", "#E67E22", "#F1C40F", "#2ECC71", "#27AE60"]
ax6.bar(inv_change.index, inv_change.values, color=inv_colors, edgecolor="black", linewidth=0.6)
ax6.axhline(0, color="black", linewidth=1)
ax6.set_title("Avg Price Change\nby Inventory Pressure", fontweight="bold")
ax6.set_xlabel("Inventory Pressure")
ax6.set_ylabel("Avg Price Change %")

# --- Plot 7: Monthly Lift % Line ---
ax7 = fig.add_subplot(gs[2, 2])
lift_colors = ["#2ECC71" if x >= 0 else "#E74C3C" for x in monthly["lift_%"]]
ax7.bar(range(len(monthly)), monthly["lift_%"], color=lift_colors, edgecolor="black", linewidth=0.4)
ax7.axhline(0, color="black", linewidth=1)
ax7.set_title("Monthly Revenue Lift %", fontweight="bold")
ax7.set_ylabel("Lift (%)")
ax7.set_xticks(range(len(monthly)))
ax7.set_xticklabels([str(p)[-5:] for p in monthly["year_month"]], rotation=45, ha="right", fontsize=6)

plt.savefig("milestone4_results.png", dpi=150, bbox_inches="tight")
print("✅ Visualisation saved: milestone4_results.png")
plt.show()

# =============================================================================
# STEP 11: SAVE RESULTS TO CSV
# =============================================================================
# WHY: We save the dataset with new pricing columns so Milestone 5 can also
# compare against this rule-based engine (not just static baseline).
# =============================================================================

output_cols = [
    "date", "store_id", "product_id", "category", "region",
    "price", "cost_price", "static_price", "dynamic_price",
    "units_sold", "static_revenue", "dynamic_revenue", "price_change_pct",
    "inventory_pressure", "demand_ratio", "competitor_gap",
    "seasonality", "weather_condition", "holiday", "is_weekend"
]
df[output_cols].to_csv("milestone4_output.csv", index=False)
print("✅ Results saved: milestone4_output.csv")

# =============================================================================
# FINAL SUMMARY
# =============================================================================

print("\n" + "=" * 65)
print("                     FINAL SUMMARY")
print("=" * 65)
print(f"  Total Rows Processed     : {len(df):,}")
print(f"  Static Baseline Revenue  : ₹{total_static:,.2f}")
print(f"  Rule-Based Revenue       : ₹{total_dynamic:,.2f}")
print(f"  Revenue Lift             : {revenue_lift:+.2f}%")
print()
print("  ✅ Rules Applied:")
print("     1. Inventory Pressure  (scarcity / overstock adjustment)")
print("     2. Demand Ratio        (forecast vs actual signal)")
print("     3. Competitor Gap      (competitive positioning)")
print("     4. Holiday/Promotion   (peak demand boost)")
print("     5. Seasonality         (peak / off-peak adjustment)")
print("     6. Weather Condition   (foot traffic proxy)")
print("     7. Weekend Boost       (leisure shopping signal)")
print("     8. Traffic Intensity   (visitor volume signal)")
print("     9. Profit Floor Guard  (never sell below cost)")
print("    10. Price Band Guard    (±30% band from listed price)")
print("=" * 65)
print("\nMilestone 4 complete. Use milestone4_output.csv in Milestone 5.")