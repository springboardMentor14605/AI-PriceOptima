# 📊 Dynamic Pricing Analysis – EDA Project

## 📌 Overview
This project performs **Exploratory Data Analysis (EDA)** on a dynamic pricing dataset to uncover patterns, relationships, and insights that influence product pricing, sales, and revenue.

The analysis helps understand how factors like pricing, discounts, inventory, competition, and customer behavior affect sales performance.

---

## 📁 Dataset
The dataset used:
clean_dynamic_pricing_dataset.csv

### Key Features:
- `price` – Product price  
- `units_sold` – Number of units sold  
- `inventory_level` – Available stock  
- `competitor_pricing` – Competitor product price  
- `customer_visits` – Number of customers visiting  
- `discount` – Discount applied  
- `cost_price` – Cost of product  
- `category`, `region` – Product classification  
- `seasonality`, `weather_condition`, `holiday`  
- `date` – Transaction date  

---

## ⚙️ Technologies Used
- Python 🐍
- Pandas – Data manipulation
- Matplotlib & Seaborn – Data visualization

---

## 🔍 EDA Pipeline

### 1. Data Understanding
- Dataset shape and structure
- Data types and missing values
- Statistical summary

### 2. Data Visualization
- Histograms for distribution
- Scatter plots for relationships:
  - Price vs Units Sold
  - Inventory vs Units Sold
  - Customer Visits vs Sales
- Bar charts for categorical insights
- Boxplots for seasonal and weather effects

### 3. Correlation Analysis
- Heatmap to identify relationships between variables

---

## 🧠 Feature Engineering

New features created to enhance analysis:

- **Discounted Price**
  discounted_price = price × (1 - discount)

- **Revenue**
  revenue = units_sold × discounted_price

- **Profit Margin**
  profit_margin = price - cost_price

- **Conversion Rate**
  conversion_rate = units_sold / customer_visits

- **Inventory Pressure**
  inventory_pressure = units_sold / inventory_level

- **Time-based Features**
  - Month
  - Day of week
  - Weekend indicator

---

## 📈 Key Insights (Example)
- Higher discounts generally increase sales volume
- Customer visits strongly influence units sold
- Competitor pricing impacts pricing strategy
- Seasonal and holiday factors affect demand patterns
- Inventory levels can limit sales performance

---

## 📅 Time Series Analysis
- Sales trends over time
- Monthly average sales
- Weekend vs weekday performance

---

## 🚀 How to Run

1. Install dependencies:
pip install pandas matplotlib seaborn

2. Run the notebook:
jupyter notebook

3. Open the `.ipynb` file and execute cells

---

## 📌 Use Cases
- Dynamic pricing strategy optimization  
- Demand forecasting  
- Revenue maximization  
- Business intelligence dashboards  

---

## 📎 Future Improvements
- Apply Machine Learning models for price prediction  
- Build real-time pricing system  
- Deploy as a web application  
