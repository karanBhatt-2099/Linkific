# API -> pandas -> database, with incremental loading + error handling
import sys; sys.path.append("..")
import requests
import pandas as pd
from sqlalchemy import create_engine, inspect, text
from config import DB_URL

API_URL = "https://jsonplaceholder.typicode.com/users"
TABLE = "api_users"

# EXTRACT
def extract():
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()          # error if status is not 200
    return response.json()

# TRANSFORM
def transform(raw):
    df = pd.DataFrame(raw)
    df = df[["id", "name", "username", "email", "phone"]].copy()
    df["email"] = df["email"].str.lower()
    df["loaded_at"] = pd.Timestamp.now().isoformat()
    return df

# LOAD (incremental: only insert ids we don't already have)
def load(df, engine):
    if inspect(engine).has_table(TABLE):
        existing = pd.read_sql_query(text(f"SELECT id FROM {TABLE}"), engine)["id"]
        df = df[~df["id"].isin(existing)]

    if df.empty:
        print("No new rows to load.")
        return 0

    df.to_sql(TABLE, engine, if_exists="append", index=False)
    return len(df)

if __name__ == "__main__":
    try:
        engine = create_engine(DB_URL)
        raw = extract()
        df = transform(raw)
        count = load(df, engine)
        print(f"Pipeline done. New rows loaded: {count}")
    except requests.exceptions.RequestException as e:
        print("API error:", e)
    except Exception as e:
        print("Pipeline failed:", e)
