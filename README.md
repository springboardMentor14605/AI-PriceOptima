# 📊 PriceOptima – AI-Based Dynamic Pricing System

## 🚀 Project Overview

**PriceOptima** is a comprehensive **AI-powered dynamic pricing system** designed to intelligently adjust product prices in a retail environment. The system leverages **data analytics, rule-based logic, and machine learning models** to recommend optimal pricing strategies.

Traditional pricing methods often rely on static or manual adjustments, which fail to capture real-time market dynamics. This project solves that problem by building a **data-driven pricing pipeline** that adapts to:

* Changing customer demand
* Inventory availability
* Competitor pricing strategies
* Seasonal trends and external factors

👉 The ultimate objective is to **maximize revenue, improve inventory turnover, and maintain competitive pricing** in a dynamic retail environment.

---

## 🎯 Project Objectives

The key objectives of this project include:

* 📌 Designing a **scalable pricing framework** for retail businesses
* 📌 Developing a **rule-based pricing engine** for baseline optimization
* 📌 Implementing **machine learning models** to predict demand accurately
* 📌 Simulating multiple pricing scenarios to identify optimal prices
* 📌 Comparing **Static vs Rule-Based vs ML-Based pricing strategies**
* 📌 Visualizing insights to support business decision-making

---

## 📂 Dataset Description

### 🗃️ Dataset Used:

**Retail Store Inventory Dataset**

### 📊 Dataset Overview:

The dataset contains detailed records of retail operations, including:

* Product-level information (price, cost, category)
* Inventory levels
* Sales (units sold)
* Customer footfall / visits
* Competitor pricing
* Seasonal and time-based attributes

### 🔍 Key Columns:

* `product_id` – Unique identifier for products
* `price` – Current selling price
* `cost_price` – Cost of the product
* `inventory_level` – Available stock
* `units_sold` – Number of units sold
* `competitor_price` – Market competitor price
* `customer_visits` – Store/online traffic
* `date` – Timestamp for trend analysis

👉 This dataset enables **realistic simulation of retail pricing strategies**.

---

## 🧩 Project Workflow

### 1️⃣ Data Ingestion

The system begins by loading the Retail Store Inventory dataset from CSV format into the processing pipeline.

* Data is validated for structure and completeness
* Initial inspection is performed using Pandas
* Data types and formats are standardized

---

### 2️⃣ Data Preprocessing

Data preprocessing ensures the dataset is clean and suitable for analysis and modeling.

#### 🔧 Steps Performed:

* Handling missing values using imputation techniques
* Removing duplicate records
* Fixing inconsistent or invalid values:

  * Negative inventory corrected
  * Price anomalies handled
* Outlier detection using **IQR (Interquartile Range)**
* Data normalization and scaling where required

👉 This step improves **data quality and model performance**.

---

### 3️⃣ Exploratory Data Analysis (EDA)

EDA is performed to extract meaningful insights and understand patterns in the dataset.

#### 📊 Analysis Includes:

* Distribution of prices, sales, and inventory
* Relationship analysis:

  * Price vs Units Sold
  * Customer Visits vs Sales
* Seasonal trends and demand fluctuations
* Competitor pricing impact analysis
* Correlation heatmap for feature relationships

👉 Helps in identifying **key drivers of demand and pricing decisions**.

---

## 🧠 Feature Engineering

To enhance predictive power, several new features are created:

### 🔑 Engineered Features:

* **Discounted Price** → Effective selling price after discount
* **Revenue** → `price × units_sold`
* **Profit Margin** → `(price - cost_price) / price`
* **Conversion Rate** → `units_sold / customer_visits`
* **Inventory Pressure** → Demand relative to stock
* **Demand Ratio** → Units sold vs expected demand
* **Competitor Gap** → Difference between own price and competitor price
* **Time Features**:

  * Month
  * Day of Week
  * Weekend Indicator

👉 These features allow the model to **capture complex business dynamics**.

---

## ⚙️ Rule-Based Pricing Engine

The rule-based engine serves as a **baseline pricing strategy** before applying machine learning.

### 📌 Pricing Logic:

* 🔹 **High Demand + Low Inventory → Increase Price**
* 🔹 **Low Demand + High Inventory → Decrease Price**
* 🔹 **Competitor Lower Price → Adjust Downwards**
* 🔹 **High Traffic (Weekends) → Slight Price Increase**
* 🔹 **Seasonal Demand → Adjust accordingly**

### 🛡️ Constraints Applied:

* Minimum profit margin enforced (Cost + 10%)
* Price variation limited within ±30%
* Avoid extreme fluctuations

👉 Ensures **realistic and business-safe pricing decisions**.

---

## 🤖 Machine Learning Model

To improve accuracy, ML models are used to predict demand and optimize pricing.

### 🧠 Models Implemented:

* XGBoost Regressor
* LightGBM Regressor

### ⚙️ Training Strategy:

* Time-based train-test split (prevents data leakage)
* Feature scaling and selection
* Cross-validation

### 🔍 Hyperparameter Tuning:

* RandomizedSearchCV
* Optuna (Bayesian Optimization)

👉 Ensures **high-performance and robust models**.

---

## 🧮 ML-Based Pricing Strategy

Instead of fixed rules, ML enables dynamic optimization:

### 📌 Approach:

1. Predict demand using trained model
2. Simulate multiple price points
3. Calculate expected revenue for each price
4. Select price that maximizes revenue/profit

👉 This creates a **smart pricing engine that adapts automatically**.

---

## 📊 Results & Evaluation

### 📈 Pricing Strategies Compared:

* Static Pricing
* Rule-Based Pricing
* ML-Based Pricing

### 📊 Metrics Used:

* Revenue Lift (%)
* RMSE (Root Mean Square Error)
* MAE (Mean Absolute Error)
* R² Score

### 🏆 Outcome:

* ML-based pricing showed **highest revenue optimization**
* Rule-based provided **stable baseline improvements**

---

## 📈 Visualizations

The project includes rich visual insights:

* 📊 Revenue comparison charts
* 📉 Price vs Demand graphs
* 📦 Category-wise performance
* 📅 Seasonal trends
* 📌 Feature importance plots
* 🔍 SHAP explainability graphs

👉 Helps stakeholders **understand and trust the system**.

---

## 🏗️ System Architecture

```text
Data Collection → Preprocessing → Feature Engineering →
EDA → Rule-Based Engine → ML Model →
Price Simulation → API → Dashboard
```

---

## 🛠️ Tech Stack

### 🔹 Programming & Data

* Python
* Pandas, NumPy

### 🔹 Machine Learning

* Scikit-learn
* XGBoost
* LightGBM
* Optuna
* SHAP

### 🔹 Visualization

* Matplotlib
* Seaborn
* Plotly

### 🔹 Backend & Deployment

* FastAPI
* Docker

### 🔹 Frontend

* React.js

---

## 📁 Project Structure

```text
PriceOptima/
│
├── data/
├── notebooks/
├── src/
├── outputs/
├── api/
├── dashboard/
├── requirements.txt
└── README.md
```

---

## ▶️ How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Pipeline

```bash
python preprocessing.py
python rule_engine.py
python model_training.py
```

### 3. Start API

```bash
uvicorn main:app --reload
```

---

## 🌐 API Example

**POST /predict-price**

```json
{
  "price": 100,
  "inventory": 50,
  "competitor_price": 110
}
```

**Response:**

```json
{
  "recommended_price": 108
}
```

---

## 📌 Use Cases

* E-commerce platforms
* Retail chains
* Inventory clearance optimization
* Competitive pricing systems

---

## 🔮 Future Enhancements

* Reinforcement Learning-based pricing
* Real-time streaming data (Kafka)
* Cloud deployment (AWS/GCP)
* Personalized pricing strategies

---

## 👨‍💻 Author

**Shivamruth Reddy Yella**
CSE Student | AI & ML Enthusiast

---

## ⭐ Final Note

This project demonstrates a **complete real-world AI pipeline**, covering:
✔ Data Processing
✔ Business Logic
✔ Machine Learning
✔ Deployment