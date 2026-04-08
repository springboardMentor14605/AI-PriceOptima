import pandas as pd
import psycopg2

# Load the feature engineered dataset
df = pd.read_csv(r"../feature-engineering/feature_engineered_dataset.csv")
# Convert NaN to None for PostgreSQL
df = df.where(pd.notnull(df), None)

# Connect to PostgreSQL
conn = psycopg2.connect(
    database="priceoptima",
    user="postgres",
    password="Mani@6264",   
    host="localhost",
    port="5432"
)

cursor = conn.cursor()

# Handle special characters in column names
columns = list(df.columns)
col_names = ','.join([f'"{col}"' for col in columns])
placeholders = ','.join(['%s'] * len(columns))

query = f"INSERT INTO sales_data ({col_names}) VALUES ({placeholders})"

# Insert row by row
for _, row in df.iterrows():
    cursor.execute(query, tuple(row))

conn.commit()
cursor.close()
conn.close()

print("Data ingestion completed successfully!")