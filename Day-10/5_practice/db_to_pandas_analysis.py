# Read data from the database and analyse it with pandas
import sys; sys.path.append("..")
import pandas as pd
from sqlalchemy import create_engine
from config import DB_URL

engine = create_engine(DB_URL)
df = pd.read_sql_query("SELECT * FROM employees", engine)

print("Average salary:", df["salary"].mean())
print("\nAverage salary by department:")
print(df.groupby("department")["salary"].mean())
print("\nEmployees per city:")
print(df["city"].value_counts())
print("\nTop 3 earners:")
print(df.nlargest(3, "salary")[["name", "salary"]])
