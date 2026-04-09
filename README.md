# AI: PriceOptima - Dynamic Pricing System

This project implements a machine learning–driven dynamic pricing system that adjusts prices in real-time based on historical sales, inventory levels, and demand predictions.

## 🚀 How to Run the Project

Follow these steps to set up and run the pricing engine and API server.

### 1. Prerequisites
Ensure you have Python 3.8+ installed. It is recommended to use a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On macOS/Linux
```

### 2. Install Dependencies
Install all required libraries using the provided requirements file:

```bash
pip install -r requirements.txt
```

### 3. Train and Serialize Models
Before running the API, you must train the ML models (XGBoost & LightGBM) and save the feature metadata:

```bash
python src/train_and_save.py
```
*This will create the models in the `models/` directory.*

### 4. Run the API Server
Start the FastAPI serving layer. By default, it runs on `http://localhost:8000`.

```bash
python src/api/main.py
```

### 5. Verify the System
You can test the API endpoints (Health and Recommendation) using the built-in test script:

```bash
python tests/test_api.py
```

---

## 🏗️ Project Structure
- `src/api/main.py`: The FastAPI application and endpoints.
- `src/pricing/baseline_engine.py`: The rule-based pricing logic.
- `src/train_and_save.py`: Script to train and save ML models.
- `data/`: Directory for input datasets.
- `models/`: Directory for serialized model artifacts (`.joblib`).
- `tests/`: Scripts for verification and comparison.

## 📊 API Usage
### POST `/recommend-price`
**Payload:**
```json
{
  "category": "Electronics",
  "region": "South",
  "inventory_level": 15,
  "price": 450.0
}
```
**Response:**
Returns recommendations from both the **Baseline Engine** and the **ML Ensemble**.
