import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="AI Dynamic Pricing", layout="wide")

# -------------------------------
# LOAD MODEL
# -------------------------------
@st.cache_resource
def load_model():
    return joblib.load("pricing_model.pkl")

model = load_model()

# -------------------------------
# FEATURE COLUMNS (MUST MATCH TRAINING)
# -------------------------------
columns = [
'store_id','product_id','inventory_level','units_ordered','demand_forecast','price','discount',
'holiday/promotion','competitor_pricing','seasonality','visitors','cost','profit_margin',
'margin_percent','inventory_pressure','competitor_gap','discounted_price','revenue',
'conversion_rate','price_demand_ratio','stock_remaining','traffic_intensity','day_of_week',
'month','is_weekend','category_clothing','category_electronics','category_furniture',
'category_groceries','category_toys','region_east','region_north','region_south','region_west',
'weather_condition_cloudy','weather_condition_rainy','weather_condition_snowy','weather_condition_sunny'
]

# -------------------------------
# CUSTOM CSS
# -------------------------------
st.markdown("""
<style>
body {background-color: #0f172a;}
.block-container {padding-top: 2rem;}
.stTextInput input, .stNumberInput input {
    background-color: #1e293b;
    color: white;
    border-radius: 8px;
}
.stButton button {
    background: linear-gradient(90deg, #22c55e, #16a34a);
    color: white;
    border-radius: 10px;
    height: 50px;
    width: 100%;
}
.stMetric {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# TITLE
# -------------------------------
st.title("🚀 AI Dynamic Pricing Engine")
st.caption("Smart pricing powered by Machine Learning")

# -------------------------------
# LAYOUT
# -------------------------------
col1, col2 = st.columns([1, 2])

# -------------------------------
# INPUTS
# -------------------------------
with col1:
    st.subheader("📋 Product Inputs")

    product_name = st.text_input("Product Name", "Toy Car")
    price = st.number_input("Current Price", value=100.0)
    inventory = st.number_input("Available Quantity (Inventory)", value=50)
    competitor_price = st.number_input("Competitor Price", value=95.0)
    demand_forecast = st.number_input("Demand Forecast", value=60)

    predict_btn = st.button("✨ Generate AI Recommendation")

# -------------------------------
# OUTPUT
# -------------------------------
with col2:
    st.subheader("📊 AI Insights Dashboard")

    if predict_btn:
        try:
            # -------------------------------
            # CREATE INPUT DATA
            # -------------------------------
            input_data = pd.DataFrame([[0]*len(columns)], columns=columns)

            input_data["price"] = price
            input_data["inventory_level"] = inventory
            input_data["competitor_pricing"] = competitor_price
            input_data["demand_forecast"] = demand_forecast

            # -------------------------------
            # DERIVED FEATURES
            # -------------------------------
            input_data["cost"] = price * 0.7
            input_data["profit_margin"] = input_data["price"] - input_data["cost"]
            input_data["margin_percent"] = input_data["profit_margin"] / (input_data["price"] + 1e-5)
            input_data["competitor_gap"] = input_data["price"] - input_data["competitor_pricing"]
            input_data["inventory_pressure"] = input_data["demand_forecast"] / (input_data["inventory_level"] + 1)
            input_data["discounted_price"] = input_data["price"] * 0.95
            input_data["stock_remaining"] = input_data["inventory_level"] - input_data["demand_forecast"]

            input_data = input_data.apply(pd.to_numeric, errors='coerce').fillna(0)
            input_data = input_data[columns]

            # -------------------------------
            # MODEL PREDICTION
            # -------------------------------
            prediction = model.predict(input_data)[0]

            # -------------------------------
            # SMART PRICE LOGIC (KEY UPGRADE)
            # -------------------------------
            if inventory < prediction:
                new_price = price * 1.10
                suggestion = "Increase Price 📈 (Low Stock)"
            elif inventory > prediction * 1.5:
                new_price = price * 0.90
                suggestion = "Decrease Price 📉 (Overstock)"
            else:
                new_price = price * 1.02
                suggestion = "Balanced Pricing ⚖️"

            # -------------------------------
            # REVENUE
            # -------------------------------
            current_revenue = price * prediction
            optimized_revenue = new_price * prediction

            # -------------------------------
            # METRICS
            # -------------------------------
            c1, c2, c3 = st.columns(3)

            c1.metric("💰 Optimal Price", f"₹{round(new_price,2)}")
            c2.metric("📦 Predicted Demand", f"{round(prediction,2)}")
            c3.metric("📈 Expected Revenue", f"₹{round(optimized_revenue,2)}")

            # -------------------------------
            # GRAPH
            # -------------------------------
            labels = ["Current Revenue", "Optimized Revenue", "Inventory"]
            values = [current_revenue, optimized_revenue, inventory]

            fig, ax = plt.subplots()
            ax.bar(labels, values, color=["blue", "green", "orange"])

            ax.set_title("📊 Pricing vs Inventory Impact")
            ax.set_ylabel("Value")

            st.pyplot(fig)

            # -------------------------------
            # AI INSIGHTS
            # -------------------------------
            st.markdown("### 🧠 AI Recommendation")

            st.success(f"🛒 Product: {product_name}")
            st.info(f"📌 Strategy: {suggestion}")

            if inventory < prediction:
                st.error("🚨 Demand exceeds inventory → Risk of stockout")
            elif inventory > prediction:
                st.warning("📦 High inventory → Risk of unsold stock")
            else:
                st.success("✅ Inventory is well balanced")

        except Exception as e:
            st.error(f"Error: {str(e)}")