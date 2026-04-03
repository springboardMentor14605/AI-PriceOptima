import pandas as pd
import psycopg2

# Load CSV generated from Google Colab
df = pd.read_csv("ml_price_predictions.csv")

# PostgreSQL connection
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="Harini@30"
)

cur = conn.cursor()

# Insert each row into PostgreSQL
for _, row in df.iterrows():

    # Remove P from product_id like P0013 -> 13
    product_id_clean = int(str(row['product_id']).replace('P', ''))

    cur.execute("""
        INSERT INTO price_predictions 
        (product_id, predicted_price, best_model)
        VALUES (%s, %s, %s)
    """, (
        product_id_clean,
        float(row['optimal_price']),
        "XGBoost"
    ))

conn.commit()
cur.close()
conn.close()

print("Predictions saved successfully into PostgreSQL.")