import os
import traceback
import joblib
import numpy as np
import pandas as pd
import streamlit as st

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_OK = True
except Exception:
    PLOTLY_OK = False


# ══════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="PriceIQ · Dynamic Pricing",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

MODEL_PATH = "pricing_model.pkl"

FEATURE_COLS = [
    "store_id", "product_id", "inventory_level", "units_ordered", "demand_forecast", "price", "discount",
    "holiday/promotion", "competitor_pricing", "seasonality", "visitors", "cost", "profit_margin",
    "margin_percent", "inventory_pressure", "competitor_gap", "discounted_price", "revenue",
    "conversion_rate", "price_demand_ratio", "stock_remaining", "traffic_intensity", "day_of_week",
    "month", "is_weekend", "category_clothing", "category_electronics", "category_furniture",
    "category_groceries", "category_toys", "region_east", "region_north", "region_south", "region_west",
    "weather_condition_cloudy", "weather_condition_rainy", "weather_condition_snowy", "weather_condition_sunny"
]


# ══════════════════════════════════════════════════════════
# MODEL LOADER
# ══════════════════════════════════════════════════════════
@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        return None, f"`{MODEL_PATH}` not found. Using fallback demand estimate."
    try:
        model = joblib.load(MODEL_PATH)
        return model, None
    except Exception as e:
        return None, f"Could not load model. Using fallback demand estimate. Details: {e}"


model, model_note = load_model()


# ══════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════
def build_input_df(price, competitor_price, inventory, demand_forecast):
    row = {col: 0 for col in FEATURE_COLS}

    row["price"] = float(price)
    row["inventory_level"] = int(inventory)
    row["competitor_pricing"] = float(competitor_price)
    row["demand_forecast"] = float(demand_forecast)

    row["cost"] = float(price) * 0.70
    row["profit_margin"] = row["price"] - row["cost"]
    row["margin_percent"] = row["profit_margin"] / (row["price"] + 1e-5)
    row["competitor_gap"] = row["price"] - row["competitor_pricing"]
    row["inventory_pressure"] = row["demand_forecast"] / (row["inventory_level"] + 1)
    row["discounted_price"] = row["price"] * 0.95
    row["stock_remaining"] = row["inventory_level"] - row["demand_forecast"]
    row["revenue"] = row["price"] * row["demand_forecast"]
    row["price_demand_ratio"] = row["price"] / (row["demand_forecast"] + 1e-5)

    df = pd.DataFrame([row])
    df = df.reindex(columns=FEATURE_COLS, fill_value=0)
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)
    return df


def fallback_demand(price, competitor_price, inventory, demand_forecast):
    base = float(demand_forecast)

    price_gap_ratio = (competitor_price - price) / (price + 1e-5)
    price_gap_ratio = max(-0.30, min(0.30, price_gap_ratio))

    inventory_ratio = inventory / max(demand_forecast, 1)
    inventory_ratio = max(0.20, min(2.00, inventory_ratio))

    pred = base * (1 + 0.55 * price_gap_ratio) * (0.92 + 0.08 * inventory_ratio)
    return max(1.0, round(pred, 2))


def predict_demand(model_obj, input_df, price, competitor_price, inventory, demand_forecast):
    if model_obj is not None:
        try:
            pred = float(np.squeeze(model_obj.predict(input_df)))
            if np.isnan(pred) or np.isinf(pred):
                raise ValueError("Prediction returned NaN/Inf")
            return max(pred, 0.0), None
        except Exception as e:
            return fallback_demand(price, competitor_price, inventory, demand_forecast), f"Model prediction failed, so fallback logic was used. Details: {e}"

    return fallback_demand(price, competitor_price, inventory, demand_forecast), model_note


def get_strategy(price, inventory, pred_demand):
    if inventory < pred_demand:
        return (
            round(price * 1.10, 2),
            "Increase Price",
            "📈",
            "Demand exceeds supply — pricing power is yours.",
            "#ff8c42"
        )
    elif inventory > pred_demand * 1.5:
        return (
            round(price * 0.90, 2),
            "Decrease Price",
            "📉",
            "Overstock — discount to accelerate sell-through.",
            "#386aff"
        )
    else:
        return (
            round(price * 1.02, 2),
            "Balanced Pricing",
            "⚖️",
            "Healthy equilibrium — apply a gentle margin nudge.",
            "#34e0a1"
        )


def build_revenue_chart(curr_rev, opt_rev):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Baseline", "Optimised"],
        y=[curr_rev, opt_rev],
        text=[f"₹{curr_rev:,.0f}", f"₹{opt_rev:,.0f}"],
        textposition="outside",
        marker_color=["#386aff", "#34e0a1"]
    ))

    fig.update_layout(
        title="Revenue Comparison",
        template=None,
        height=360,
        margin=dict(l=20, r=20, t=55, b=20),
        paper_bgcolor="#08101c",
        plot_bgcolor="#0e1a2e",
        font=dict(color="#eef2ff"),
        showlegend=False
    )
    fig.update_xaxes(showgrid=False, color="#95a9bd")
    fig.update_yaxes(showgrid=True, gridcolor="#1a2638", visible=False)
    return fig


def build_scenario_chart(price, pred_demand, new_price):
    mults = [0.8, 0.9, 1.0, 1.1, 1.2]
    labels = [f"x{m}" for m in mults]
    revenues = [round(m * price * pred_demand, 0) for m in mults]
    opt_m = round(new_price / price, 2)

    colors = []
    for m in mults:
        if abs(m - opt_m) < 0.06:
            colors.append("#34e0a1")
        elif m < 1.0:
            colors.append("#ff4e4e")
        else:
            colors.append("#386aff")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels,
        y=revenues,
        marker_color=colors,
        text=[f"₹{r:,.0f}" for r in revenues],
        textposition="outside"
    ))

    fig.update_layout(
        title="Price Scenarios",
        template=None,
        height=360,
        margin=dict(l=20, r=20, t=55, b=20),
        paper_bgcolor="#08101c",
        plot_bgcolor="#0e1a2e",
        font=dict(color="#eef2ff"),
        showlegend=False,
        annotations=[
            dict(
                text="optimal",
                x=labels[min(range(len(mults)), key=lambda i: abs(mults[i] - opt_m))],
                y=max(revenues) * 1.05,
                showarrow=False,
                font=dict(color="#34e0a1", size=11)
            )
        ]
    )
    fig.update_xaxes(showgrid=False, color="#95a9bd")
    fig.update_yaxes(showgrid=True, gridcolor="#1a2638", visible=False)
    return fig


def build_margin_chart(new_price):
    cost = new_price * 0.70
    margin = new_price * 0.30

    fig = go.Figure(data=[go.Pie(
        labels=["Cost", "Margin"],
        values=[cost, margin],
        hole=0.62,
        marker=dict(colors=["#386aff", "#34e0a1"]),
        textinfo="label+percent"
    )])

    fig.update_layout(
        title="Margin Breakdown",
        template=None,
        height=360,
        margin=dict(l=20, r=20, t=55, b=20),
        paper_bgcolor="#08101c",
        plot_bgcolor="#0e1a2e",
        font=dict(color="#eef2ff"),
        annotations=[
            dict(
                text=f"₹{new_price:.0f}<br><span style='font-size:11px;color:#95a9bd'>optimal price</span>",
                x=0.5, y=0.5,
                font=dict(size=18, color="#eef2ff"),
                showarrow=False
            )
        ]
    )
    return fig


# ══════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════
if "run_analysis" not in st.session_state:
    st.session_state.run_analysis = False


# ══════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;600;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #05080f !important;
    color: #d8e4f0 !important;
    font-family: 'Outfit', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 10% -10%, rgba(56,106,255,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 100%, rgba(52,224,161,0.07) 0%, transparent 55%),
        #05080f !important;
}

[data-testid="stHeader"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
.block-container { max-width: 1450px !important; padding: 0 3rem 3rem !important; }

.topbar {
    display:flex; align-items:center; justify-content:space-between;
    padding: 1.3rem 0 1.2rem;
    border-bottom:1px solid rgba(255,255,255,0.05);
    margin-bottom:2.2rem;
}
.topbar-brand { display:flex; align-items:center; gap:12px; }
.topbar-logo {
    width:38px; height:38px; border-radius:10px;
    display:flex; align-items:center; justify-content:center;
    background: linear-gradient(135deg,#386aff,#34e0a1);
}
.topbar-name { font-size:1.35rem; font-weight:800; color:#eef2ff; }
.topbar-name span { color:#386aff; }
.topbar-pill {
    font-family:'DM Mono', monospace;
    font-size:0.62rem; letter-spacing:0.14em; text-transform:uppercase;
    color:#7097ff;
    background:rgba(56,106,255,0.1);
    border:1px solid rgba(56,106,255,0.2);
    padding:5px 12px; border-radius:999px;
}
.topbar-status {
    display:flex; align-items:center; gap:8px;
    color:rgba(216,228,240,0.45);
    font-family:'DM Mono', monospace;
    font-size:0.72rem;
}
.status-dot {
    width:7px; height:7px; border-radius:50%;
    background:#34e0a1;
}

.sec-label { display:flex; align-items:center; gap:10px; margin-bottom:0.9rem; }
.sec-num {
    font-family:'DM Mono', monospace;
    font-size:0.58rem; letter-spacing:0.12em;
    color:#386aff;
    background:rgba(56,106,255,0.1);
    border:1px solid rgba(56,106,255,0.2);
    padding:3px 8px; border-radius:4px;
}
.sec-title {
    font-family:'DM Mono', monospace;
    font-size:0.62rem; letter-spacing:0.18em; text-transform:uppercase;
    color:rgba(216,228,240,0.42);
}

[data-testid="stTextInput"] > label,
[data-testid="stNumberInput"] > label {
    font-family:'DM Mono', monospace !important;
    font-size:0.64rem !important;
    letter-spacing:0.14em !important;
    text-transform:uppercase !important;
    color:rgba(216,228,240,0.45) !important;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background:rgba(12,20,45,0.82) !important;
    border:1px solid rgba(255,255,255,0.08) !important;
    border-radius:10px !important;
    color:#eef2ff !important;
    font-family:'DM Mono', monospace !important;
}

.stButton > button {
    width:100% !important;
    height:52px !important;
    border:none !important;
    border-radius:12px !important;
    color:#fff !important;
    font-weight:600 !important;
    background:linear-gradient(135deg,#2b58e8 0%,#386aff 50%,#34e0a1 150%) !important;
    box-shadow:0 4px 20px rgba(56,106,255,0.35) !important;
}

[data-testid="metric-container"] {
    background:rgba(255,255,255,0.03) !important;
    border:1px solid rgba(255,255,255,0.07) !important;
    border-radius:14px !important;
    padding:1rem 1rem !important;
}

[data-testid="stMetricLabel"] > div {
    font-family:'DM Mono', monospace !important;
    font-size:0.62rem !important;
    letter-spacing:0.14em !important;
    text-transform:uppercase !important;
    color:rgba(216,228,240,0.4) !important;
}

[data-testid="stMetricValue"] > div {
    font-size:1.7rem !important;
    font-weight:800 !important;
    color:#eef2ff !important;
}

.strategy-banner {
    display:flex; align-items:center; gap:16px;
    background:rgba(56,106,255,0.07);
    border:1px solid rgba(56,106,255,0.18);
    border-radius:14px;
    padding:1.1rem 1.4rem;
    margin:1.2rem 0;
}
.strategy-icon { font-size:1.8rem; }
.strategy-label {
    font-family:'DM Mono', monospace;
    font-size:0.6rem; letter-spacing:0.15em; text-transform:uppercase;
    color:rgba(216,228,240,0.4);
}
.strategy-text { font-size:1.05rem; font-weight:600; }
.strategy-detail {
    font-family:'DM Mono', monospace;
    font-size:0.7rem;
    color:rgba(216,228,240,0.45);
    margin-top:2px;
}

.insight-grid {
    display:grid;
    grid-template-columns: repeat(3, 1fr);
    gap:10px;
    margin-top:1rem;
}
.insight-chip {
    background:rgba(255,255,255,0.03);
    border:1px solid rgba(255,255,255,0.06);
    border-radius:12px;
    padding:0.9rem 1rem;
}
.chip-label {
    font-family:'DM Mono', monospace;
    font-size:0.58rem;
    letter-spacing:0.14em;
    text-transform:uppercase;
    color:rgba(216,228,240,0.35);
    margin-bottom:6px;
}
.chip-value {
    font-size:1.08rem;
    font-weight:600;
    color:#eef2ff;
}
.chip-sub {
    font-family:'DM Mono', monospace;
    font-size:0.62rem;
    color:rgba(216,228,240,0.35);
    margin-top:2px;
}

.empty-state {
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    min-height:380px;
    border:1px dashed rgba(56,106,255,0.18);
    border-radius:20px;
    text-align:center;
    padding:3rem;
}
.empty-icon {
    width:64px; height:64px; border-radius:18px;
    display:flex; align-items:center; justify-content:center;
    background:rgba(56,106,255,0.08);
    border:1px solid rgba(56,106,255,0.15);
    font-size:26px;
    margin-bottom:10px;
}
.empty-title {
    font-size:1rem; font-weight:600;
    color:rgba(216,228,240,0.35);
}
.empty-sub {
    font-family:'DM Mono', monospace;
    font-size:0.68rem;
    color:rgba(216,228,240,0.2);
    letter-spacing:0.08em;
}

.footer-bar {
    display:flex; justify-content:center; gap:24px; flex-wrap:wrap;
    padding:2rem 0 1rem;
    border-top:1px solid rgba(255,255,255,0.04);
    margin-top:3rem;
}
.footer-item {
    font-family:'DM Mono', monospace;
    font-size:0.62rem;
    letter-spacing:0.12em;
    color:rgba(216,228,240,0.2);
    text-transform:uppercase;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# TOP BAR
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="topbar">
    <div class="topbar-brand">
        <div class="topbar-logo">⚡</div>
        <div class="topbar-name">Price<span>IQ</span></div>
        <div class="topbar-pill">Dynamic Pricing Engine</div>
    </div>
    <div class="topbar-status">
        <div class="status-dot"></div>
        XGBoost · Live
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════
left, right = st.columns([1, 1.7], gap="large")

with left:
    st.markdown('<div class="sec-label"><span class="sec-num">01</span><span class="sec-title">Product Parameters</span></div>', unsafe_allow_html=True)

    product_name = st.text_input("Product Name", value="Wireless Headphones")
    c1, c2 = st.columns(2)
    with c1:
        price = st.number_input("Current Price (₹)", min_value=0.0, value=100.0, step=1.0, format="%.2f")
    with c2:
        competitor_price = st.number_input("Competitor Price (₹)", min_value=0.0, value=95.0, step=1.0, format="%.2f")

    c3, c4 = st.columns(2)
    with c3:
        inventory = st.number_input("Inventory Level", min_value=0, value=50, step=1)
    with c4:
        demand_forecast = st.number_input("Demand Forecast", min_value=0, value=60, step=1)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("⚡  Run Pricing Analysis"):
        st.session_state.run_analysis = True

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-label"><span class="sec-num">02</span><span class="sec-title">Live Signals</span></div>', unsafe_allow_html=True)

    price_gap = price - competitor_price
    stock_ratio = round(inventory / (demand_forecast + 1e-5), 2)

    gap_col = "#ff6b6b" if price_gap > 10 else ("#34e0a1" if price_gap < -5 else "#fbbf24")
    sr_col = "#ff6b6b" if stock_ratio < 0.8 else ("#fbbf24" if stock_ratio > 1.5 else "#34e0a1")
    sr_label = "Understock" if stock_ratio < 0.8 else ("Overstock" if stock_ratio > 1.5 else "Balanced")
    gap_dir = "▲" if price_gap > 0 else ("▼" if price_gap < 0 else "•")

    st.markdown(f"""
    <div class="insight-grid">
        <div class="insight-chip">
            <div class="chip-label">Price Gap</div>
            <div class="chip-value" style="color:{gap_col};">{gap_dir} ₹{abs(price_gap):.1f}</div>
            <div class="chip-sub">vs competitor</div>
        </div>
        <div class="insight-chip">
            <div class="chip-label">Stock Ratio</div>
            <div class="chip-value" style="color:{sr_col};">{stock_ratio}x</div>
            <div class="chip-sub">{sr_label}</div>
        </div>
        <div class="insight-chip">
            <div class="chip-label">Est. Margin</div>
            <div class="chip-value">₹{price * 0.3:.1f}</div>
            <div class="chip-sub">30% of price</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


with right:
    st.markdown('<div class="sec-label"><span class="sec-num">03</span><span class="sec-title">AI Insights Dashboard</span></div>', unsafe_allow_html=True)

    if not st.session_state.run_analysis:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">⚡</div>
            <div class="empty-title">Awaiting Analysis</div>
            <div class="empty-sub">Configure parameters and run analysis</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        try:
            if not PLOTLY_OK:
                st.error("Plotly is not installed. Run: pip install plotly")
                st.stop()

            input_df = build_input_df(price, competitor_price, inventory, demand_forecast)
            pred_demand, prediction_note = predict_demand(
                model, input_df, price, competitor_price, inventory, demand_forecast
            )

            new_price, strategy, strat_icon, strat_detail, strat_color = get_strategy(
                price, inventory, pred_demand
            )

            curr_rev = round(price * pred_demand, 2)
            opt_rev = round(new_price * pred_demand, 2)
            rev_lift = round(((opt_rev - curr_rev) / (curr_rev + 1e-5)) * 100, 1)
            net_margin = round(((new_price - price * 0.7) / (new_price + 1e-5)) * 100, 1)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Optimal Price", f"₹{new_price:,.1f}")
            m2.metric("Predicted Demand", f"{pred_demand:,.0f}")
            m3.metric("Expected Revenue", f"₹{opt_rev:,.0f}")
            m4.metric("Revenue Lift", f"{rev_lift:+.1f}%", delta="vs baseline")

            st.markdown(f"""
            <div class="strategy-banner">
                <div class="strategy-icon">{strat_icon}</div>
                <div>
                    <div class="strategy-label">Recommended Strategy</div>
                    <div class="strategy-text" style="color:{strat_color};">{strategy}</div>
                    <div class="strategy-detail">{strat_detail}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            g1, g2, g3 = st.columns(3)
            with g1:
                st.plotly_chart(build_revenue_chart(curr_rev, opt_rev), width="stretch", theme=None)
            with g2:
                st.plotly_chart(build_scenario_chart(price, pred_demand, new_price), width="stretch", theme=None)
            with g3:
                st.plotly_chart(build_margin_chart(new_price), width="stretch", theme=None)

            if inventory < pred_demand:
                st.error(f"**Stockout Risk** — Forecast ({pred_demand:,.0f} units) exceeds inventory ({inventory}). Raise price or reorder.")
            elif inventory > pred_demand * 1.5:
                st.warning(f"**Overstock Alert** — Inventory is {stock_ratio:.1f}× forecast demand. Markdown will accelerate sell-through.")
            else:
                st.success("**Healthy Balance** — Inventory and demand are well-aligned. Minor price increase recommended.")

            st.markdown(f"""
            <div class="insight-grid" style="margin-top:1rem;">
                <div class="insight-chip">
                    <div class="chip-label">Net Margin</div>
                    <div class="chip-value">{net_margin}%</div>
                    <div class="chip-sub">at optimal price</div>
                </div>
                <div class="insight-chip">
                    <div class="chip-label">Price Change</div>
                    <div class="chip-value" style="color:{strat_color};">{((new_price / price) - 1) * 100:+.1f}%</div>
                    <div class="chip-sub">from current</div>
                </div>
                <div class="insight-chip">
                    <div class="chip-label">Cost Floor</div>
                    <div class="chip-value">₹{price * 0.7:.0f}</div>
                    <div class="chip-sub">breakeven point</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if prediction_note:
                st.info(prediction_note)

            with st.expander("Debug details"):
                st.write("Product:", product_name)
                st.write("Plotly available:", PLOTLY_OK)
                st.write("Model loaded:", model is not None)
                st.write("Prediction note:", prediction_note)
                st.write("Input dataframe:")
                st.dataframe(input_df, width="stretch")

        except Exception:
            st.error("Dashboard crashed. Open the debug block below and send me that traceback.")
            st.code(traceback.format_exc())

# ══════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="footer-bar">
    <span class="footer-item">PriceIQ · Dynamic Pricing Engine</span>
    <span class="footer-item">XGBoost · Demand Forecasting</span>
    <span class="footer-item">Realtime Pricing Dashboard</span>
</div>
""", unsafe_allow_html=True)