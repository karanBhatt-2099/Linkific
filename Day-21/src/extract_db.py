"""2 database types: PostgreSQL (relational) and MongoDB (document)."""
import os

import pandas as pd
import psycopg2
from pymongo import MongoClient

from src.utils import save_raw


def _pg_query(sql):
    conn = psycopg2.connect(
        host=os.getenv("SRC_PG_HOST"), port=os.getenv("SRC_PG_PORT", "5432"),
        dbname=os.getenv("SRC_PG_DB"), user=os.getenv("SRC_PG_USER"),
        password=os.getenv("SRC_PG_PASSWORD"),
    )
    try:
        cur = conn.cursor()
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=cols)
    finally:
        conn.close()


def postgres():
    save_raw(_pg_query("SELECT * FROM customers"), "pg_customers", "postgres")
    orders = _pg_query("SELECT * FROM orders")
    orders["amount"] = orders["amount"].astype(float)  # Decimal -> float
    save_raw(orders, "pg_orders", "postgres")


def mongo():
    db = MongoClient(os.getenv("MONGO_URI"))[os.getenv("MONGO_DB")]
    for coll in ["products", "reviews"]:
        df = pd.DataFrame(list(db[coll].find({}, {"_id": 0})))
        save_raw(df, f"mongo_{coll}", "mongodb")
