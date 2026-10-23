# pandas with SQL: to_sql, read_sql_query, read_sql_table, chunks
import sys; sys.path.append("..")
import pandas as pd
from sqlalchemy import create_engine, text
from config import DB_URL

engine = create_engine(DB_URL)

# to_sql: DataFrame -> table
df = pd.read_csv("../data/employees.csv")
df.to_sql("employees", engine, if_exists="replace", index=False)
print("Saved", len(df), "rows to 'employees'")

# read_sql_query: run any SQL
high = pd.read_sql_query("SELECT * FROM employees WHERE salary > 60000", engine)
print("\nSalary > 60000:\n", high)

# read_sql_query with a parameter (:name style works on every database)
dept = pd.read_sql_query(
    text("SELECT * FROM employees WHERE department = :d"),
    engine, params={"d": "Sales"},
)
print("\nSales dept:\n", dept)

# read_sql_table: read a whole table
all_rows = pd.read_sql_table("employees", engine)
print("\nWhole table shape:", all_rows.shape)

# Chunk processing: read big tables in small pieces
total = 0
for chunk in pd.read_sql_query("SELECT * FROM employees", engine, chunksize=3):
    total += len(chunk)
    print("Chunk of", len(chunk), "rows")
print("Total rows processed:", total)
