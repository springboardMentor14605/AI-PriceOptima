import pandas as pd
import psycopg2

# Load dataset
df = pd.read_csv(r"C:\Users\Princy Jessica\AI-PriceOptima\DynamicPricingProject\data\feature_engineered_dataset.csv")

# Connect to PostgreSQL
conn = psycopg2.connect(
    database="priceoptima",
    user="postgres",
    password="blessyjadzia@300106",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales_data (
    id SERIAL PRIMARY KEY,
    date DATE,
    store_id VARCHAR(10),
    product_id VARCHAR(10),
    category VARCHAR(50),
    region VARCHAR(50),
    inventory_level INT,
    units_sold INT,
    price FLOAT
);
""")

# Insert data
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO sales_data
        (date, store_id, product_id, category, region, inventory_level, units_sold, price)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        row["date"], row["store_id"], row["product_id"],
        row["category"], row["region"],
        row["inventory_level"], row["units_sold"], row["price"]
    ))

# Commit and close
conn.commit()
cursor.close()
conn.close()

print(" Data Ingested Successfully!")