import pandas as pd
import psycopg2

# Load dataset
df = pd.read_csv("updated_retail_inventory.csv")

# Connect PostgreSQL
conn = psycopg2.connect(
    database="priceoptima",
    user="postgres",
    password="Harini@30",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()

# Insert all rows
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO sales_data (
            date, store_id, product_id, category, region,
            inventory_level, units_sold, units_ordered,
            demand_forecast, price, discount,
            weather_condition, holiday_promotion,
            competitor_pricing, seasonality, cost, visitors
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        row["Date"],
        row["Store ID"],
        row["Product ID"],
        row["Category"],
        row["Region"],
        row["Inventory Level"],
        row["Units Sold"],
        row["Units Ordered"],
        row["Demand Forecast"],
        row["Price"],
        row["Discount"],
        row["Weather Condition"],
        row["Holiday/Promotion"],
        row["Competitor Pricing"],
        row["Seasonality"],
        row["cost"],
        row["visitors"]
    ))

# Save
conn.commit()

print("Data inserted successfully")

# Close
cursor.close()
conn.close()