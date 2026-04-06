from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

df = pd.read_csv("ml_price_predictions.csv")
df["best_model"] = "XGBoost"

@app.get("/")
def home():
    return {"message": "AI PriceOptima API Running Successfully 🚀"}

@app.get("/kpi")
def get_kpi():
    return {
        "avg_predicted_price": float(df["optimal_price"].mean()),
        "max_price": float(df["optimal_price"].max()),
        "min_price": float(df["optimal_price"].min())
    }

@app.get("/predictions")
def get_predictions():
    clean_df = df.fillna(0)
    return clean_df.head(10).astype(str).to_dict(orient="records")