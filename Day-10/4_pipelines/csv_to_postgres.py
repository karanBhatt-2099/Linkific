# Simple ETL: CSV -> clean with pandas -> PostgreSQL
import sys; sys.path.append("..")
import pandas as pd
from sqlalchemy import create_engine
from config import DB_URL

def extract():
    return pd.read_csv("../data/employees.csv")

def transform(df):
    df = df.drop_duplicates()
    df["name"] = df["name"].str.upper()
    df["salary_k"] = df["salary"] / 1000
    return df

def load(df, engine):
    df.to_sql("employees_clean", engine, if_exists="replace", index=False)

if __name__ == "__main__":
    engine = create_engine(DB_URL)
    data = extract()
    data = transform(data)
    load(data, engine)
    print("Loaded", len(data), "rows into employees_clean")
