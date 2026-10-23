# Query two different databases and combine results in pandas
import sys; sys.path.append("..")
import pandas as pd
from sqlalchemy import create_engine
from config import DB_URL

# Database 1: PostgreSQL (employees)
pg_engine = create_engine(DB_URL)
employees = pd.read_sql_query("SELECT name, department FROM employees", pg_engine)

# Database 2: SQLite file (bonus info) - created here for the demo
sqlite_engine = create_engine("sqlite:///bonus.db")
bonus = pd.DataFrame({
    "name": ["Asha", "Ravi", "Neha", "Priya"],
    "bonus": [5000, 6000, 3000, 7000],
})
bonus.to_sql("bonus", sqlite_engine, if_exists="replace", index=False)
bonus_data = pd.read_sql_query("SELECT * FROM bonus", sqlite_engine)

# Combine in pandas
merged = employees.merge(bonus_data, on="name", how="inner")
print(merged)
