from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pickle

app = FastAPI()

# ✅ ADD THIS (CORS FIX)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
model = pickle.load(open("model.pkl", "rb"))

@app.get("/")
def home():
    return {"message": "ML API is running 🚀"}

@app.post("/predict")
def predict(data: dict):
    try:
        features = list(data.values())
        prediction = model.predict([features])[0]

        return {"predicted_demand": float(prediction)}

    except Exception as e:
        return {"error": str(e)}