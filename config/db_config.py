from sqlalchemy import create_engine

# 👉 Replace password with your PostgreSQL password
DB_URL = "postgresql://postgres:Shivansh%401803@localhost:5432/priceoptima"

engine = create_engine(DB_URL)