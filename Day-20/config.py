"""Shared settings. Connection details are read from the .env file."""
import os, csv
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

DATA_DIR = os.path.join(BASE_DIR, "data")
SQL_DIR = os.path.join(BASE_DIR, "sql")

# database name -> tables in load order (parents first, so foreign keys work)
DATABASES = {
    "ecommerce_db": ["customers", "products", "orders", "order_items"],
    "hr_db": ["departments", "employees", "attendance"],
    "finance_db": ["accounts", "transactions"],
}


def write_csv(db, table, header, rows):
    folder = os.path.join(DATA_DIR, db)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, table + ".csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  {db}.{table}: {len(rows):,} rows")
