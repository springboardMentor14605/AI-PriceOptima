from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import joblib

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
model = joblib.load("new_price_model.pkl")

@app.get("/")
def home():
    return {"message": "AI PriceOptima Advanced API Running 🚀"}


# 🔥 Recommendation Engine
def get_recommendation(predicted_price, competitor_price):
    if predicted_price > competitor_price:
        return "Increase Price 🔺"
    elif predicted_price < competitor_price:
        return "Decrease Price 🔻"
    else:
        return "Maintain Price ⚖️"


# 🔥 Prediction API
@app.post("/predict")
def predict_price(data: dict):
    try:
        df = pd.DataFrame([data])
        df = df.fillna(0)

        df["inventory_pressure"] = df["units_sold"] / (df["inventory_level"] + 1)
        df["demand_ratio"] = df["units_sold"] / (df["demand_forecast"] + 1)

        features = [
            "inventory_level",
            "units_sold",
            "demand_forecast",
            "competitor_pricing",
            "discount",
            "visitors",
            "profit_margin",
            "conversion_rate",
            "inventory_pressure",
            "demand_ratio"
        ]

        df = df[features]

        # 🔥 FIX HERE
        prediction = float(model.predict(df)[0])

        competitor_price = float(data.get("competitor_pricing", 1))
        revenue_lift = ((prediction - competitor_price) / competitor_price) * 100

        return {
            "predicted_price": round(prediction, 2),
            "recommendation": get_recommendation(prediction, competitor_price),
            "revenue_lift": round(float(revenue_lift), 2)
        }

    except Exception as e:
        print("🔥 ERROR:", e)
        return {"error": str(e)}