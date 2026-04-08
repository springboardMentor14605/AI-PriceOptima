import pandas as pd
from sqlalchemy import create_engine

# ------------------------------
# Step 1: Load Dataset
# ------------------------------
def load_dataset():
    print("Loading dataset...")
    df = pd.read_csv("data/dynamic_pricing_dataset.csv")
    print("Dataset loaded successfully")
    print(df.head())
    return df


# ------------------------------
# Step 2: Clean Dataset
# ------------------------------
def clean_data(df):
    print("Cleaning dataset...")

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Handle missing values
    df = df.fillna(0)

    print("Cleaning completed")
    return df


# ------------------------------
# Step 3: Connect to PostgreSQL
# ------------------------------
def connect_database():

    username = "postgres"
    password = "password"
    host = "localhost"
    port = "5432"
    database = "priceoptima_db"

    connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"

    engine = create_engine(connection_string)

    print("Database connection successful")
    return engine


# ------------------------------
# Step 4: Store Data in Database
# ------------------------------
def store_data(df, engine):

    print("Storing data in PostgreSQL...")

    df.to_sql(
        name="pricing_data",
        con=engine,
        if_exists="replace",
        index=False
    )

    print("Data successfully stored in PostgreSQL")


# ------------------------------
# Main Pipeline
# ------------------------------
def run_pipeline():

    df = load_dataset()

    df = clean_data(df)

    engine = connect_database()

    store_data(df, engine)


# Run the pipeline
if __name__ == "__main__":
    run_pipeline()