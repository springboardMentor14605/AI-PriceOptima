# Project PriceOptima: Milestone 6 - Production Deployment & Dashboard

## System Architecture

The AI Price Optima pipeline has been successfully upgraded from an offline ML experiment into a fully decoupled, production-ready system consisting of three core tiers:

1.  **AI Engine (Models & Business Logic)**
    *   **Core Logic:** `optimization.py` applies the rule constraints, loads the XGBoost / LightGBM models securely, encodes inputs exactly mimicking the historical time-series matrices, predicts simulated demand points dynamically, and solves for maximum Expected Revenue while ensuring profit margins remain above variable costs.
    *   **Models Storage:** Models and feature configurations have been neatly isolated within the `models/` subdirectory (`best_pricing_model.pkl`, etc.).
2.  **API Layer (FastAPI)**
    *   **File Location:** `api/app.py`
    *   **Responsibilities:** Exposed high-throughput REST API that translates HTTP requests into DataFrame inputs. Provides health signals (`/`), single real-time inference (`/predict-price`), batch optimization (`/batch-predict`), and model instrumentation metrics (`/model-info`).
    *   **Concurrency:** Built using `uvicorn` and Python async workers ensuring that concurrent price lookups map directly into the tree-estimators without bottlenecking system resources.
3.  **Client Application (React Dashboard)**
    *   **File Location:** `frontend/`
    *   **Tech Stack:** React 18 + Vite, styled with modern CSS features (glassmorphism UI patterns), interacting with Axios for API ingestion, and utilizing Recharts for dynamic visual simulations of "Pricing versus Demand/Revenue Lift".
4.  **Containerization (Docker)**
    *   **File Location:** `Dockerfile`
    *   **Deployment Mechanism:** Fully self-contained python environment specifying all operational ML distributions (`xgboost`, `lightgbm`, etc.), guaranteeing deterministic performance uniformly whether on local, AWS, or GCP.

---

## Model Performance

The current active state of the application draws directly into the established and highest-performing estimator configured during Milestone 5.

*   **Model Type:** XGBoost / LightGBM (Selected dynamically during training evaluation).
*   **Performance Metrics:** Refer to the logged endpoint `GET /model-info` to securely access the computed test RMSE score from when `model.py` was instantiated. Overfitting measures strictly maintained the accuracy band safely within 1.5x constraint variance.

## Enterprise Revenue Lift

Using the row-by-row comprehensive backtesting module from Milestone 5, the model consistently proved its capability for outperforming static rule limitations:

*   **Strategic Advantage:** By isolating specific item elasticity matrices contextually across individual stores and timeline intervals, the ML logic yields an explicitly tracked **positive lift percentage** over rule-based threshold constraints alone.
*   The results are inherently reproducible locally by running `python backtesting.py`, capturing precise demand forecasts matched up against 80-120% variance bands.

---

## Dashboard & System Visualization

Our React application ensures that operational business users (Marketing, Inventory Managers) can securely invoke AI pricing decisions.

**Key Dashboard Capabilities:**
*   **Real-time Yield Adjustments:** Direct input modeling taking factors like predicted Store Walk-In Visitors, Local Competitor Price tracking, and live Inventory Levels.
*   **Instant Result Visualization:** Calculates optimal "Shelf Price", returning both exactly how many units will sell and the aggregate expected top-line Revenue lift.
*   **Dual-Axis Validation Chart:** Implemented with `recharts` to seamlessly benchmark the proposed AI pricing tactic natively against standard projections (Demand vs Revenue Axis Comparison).

---

## API Usage Examples

The `FastAPI` instance natively supports localized inference tasks:

**Start the Server Locally** (or build via `docker build -t ai-price-optima .`)
```bash
python -m uvicorn api.app:app --reload
```

**Single Product Price Prediction (`POST /predict-price`)**
```bash
curl -X POST "http://127.0.0.1:8000/predict-price" \
     -H "Content-Type: application/json" \
     -d '{
           "product_id": "P123",
           "price": 100,
           "cost": 70,
           "inventory_level": 50,
           "demand_forecast": 40,
           "competitor_pricing": 95,
           "visitors": 200,
           "date": "2023-10-10"
         }'
```
**Example Response:**
```json
{
  "optimal_price": 112.50,
  "predicted_demand": 38,
  "expected_revenue": 4275.00
}
```

**Fetch Instrumentation Logs (`GET /model-info`)**
```bash
curl -X GET "http://127.0.0.1:8000/model-info"
```
**Example Response:**
```json
{
  "model_type": "LGBMRegressor",
  "rmse": 14.52,
  "features_used": ["Price", "Cost", "Competitor Pricing", "Is_Weekend", "..."]
}
```

### Complete
This concludes Milestone 6! The AI engine successfully bridges standard tabular statistics with high-availability product operations.
