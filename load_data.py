import pandas as pd
from sqlalchemy import create_engine

# PostgreSQL connection details
username = "postgres"
password = "123"
host = "localhost"
port = "5432"
database = "india_data_project"

# Create connection
engine = create_engine(f"postgresql://{username}:{password}@{host}:{port}/{database}")

print("Connected to PostgreSQL successfully!")

# Load dataset
df = pd.read_csv("data/Updated_dynamic-pricing-dataset (1).csv")


# Upload dataset to PostgreSQL table
df.to_sql("india_dataset", engine, if_exists="replace", index=False)

print("Dataset uploaded successfully!")