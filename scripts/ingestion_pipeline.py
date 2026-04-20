import sys
import os
import pandas as pd
import logging
from datetime import datetime


# FIX IMPORT PATH

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from config.db_config import engine

# PATHS

data_path = os.path.join(BASE_DIR, "data", "clean_dynamic_pricing_dataset.csv")
log_dir = os.path.join(BASE_DIR, "logs")

# Create logs folder if not exists
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, "pipeline.log")

# -------------------------
# LOGGING
# -------------------------
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

print("📂 Data path:", data_path)
print("📝 Log path:", log_file)

# -------------------------
# INGESTION FUNCTION
# -------------------------
def ingest_data():
    try:
        logging.info("Ingestion started")

        # Load dataset
        df = pd.read_csv(data_path)

        # -------------------------
        # DEBUG + CLEAN COLUMN NAMES
        # -------------------------
        print("Original Columns:", df.columns)

        df.columns = df.columns.str.strip().str.lower()

        print("Cleaned Columns:", df.columns)

        # -------------------------
        # HANDLE COLUMN MAPPING
        # -------------------------
        # Detect demand column
        if 'demand' in df.columns:
            demand_col = 'demand'
        elif 'units_sold' in df.columns:
            demand_col = 'units_sold'
        elif 'sales' in df.columns:
            demand_col = 'sales'
        else:
            raise Exception("No demand-related column found!")

        # Detect inventory column
        if 'inventory' in df.columns:
            inventory_col = 'inventory'
        elif 'stock' in df.columns:
            inventory_col = 'stock'
        else:
            inventory_col = None

        # -------------------------
        # CLEANING
        # -------------------------
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)

        if 'price' in df.columns:
            df['price'] = pd.to_numeric(df['price'], errors='coerce')

        if demand_col:
            df[demand_col] = pd.to_numeric(df[demand_col], errors='coerce')

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')

        # -------------------------
        # SALES TABLE
        # -------------------------
        sales_cols = ['product_id', 'price', demand_col, 'date']

        # add optional columns if exist
        if 'category' in df.columns:
            sales_cols.append('category')

        if 'competitor_price' in df.columns:
            sales_cols.append('competitor_price')

        sales = df[sales_cols].copy()

        # rename demand column to standard name
        sales.rename(columns={demand_col: 'demand'}, inplace=True)

        # -------------------------
        # INVENTORY TABLE
        # -------------------------
        if inventory_col:
            inventory = df[['product_id', inventory_col]].copy()
            inventory.rename(columns={inventory_col: 'inventory_level'}, inplace=True)
            inventory['last_updated'] = datetime.now()

            inventory.to_sql('inventory_data', engine, if_exists='append', index=False)

        # -------------------------
        # LOAD TO DATABASE
        # -------------------------
        sales.to_sql('sales_history', engine, if_exists='append', index=False)

        # -------------------------
        # METRICS
        # -------------------------
        metrics = pd.DataFrame({
            "records_ingested": [len(df)],
            "status": ["SUCCESS"],
            "run_time": [datetime.now()]
        })

        metrics.to_sql("ingestion_metrics", engine, if_exists="append", index=False)

        logging.info("Ingestion successful")
        print("✅ Data ingestion successful")

    except Exception as e:
        logging.error(f"Error: {e}")
        print("❌ Error:", e)


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    ingest_data()