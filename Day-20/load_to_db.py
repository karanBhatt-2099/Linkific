"""Create databases in PostgreSQL, bulk load CSVs (COPY), create indexes."""
import os
import psycopg2
from config import *


def connect(dbname):
    return psycopg2.connect(dbname=dbname, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)


def run_sql_file(cur, name):
    with open(os.path.join(SQL_DIR, name), encoding="utf-8") as f:
        cur.execute(f.read())


for db, tables in DATABASES.items():
    print(f"\n=== {db} ===")

    # 1. (re)create the empty database
    conn = connect("postgres")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {db}")
    cur.execute(f"CREATE DATABASE {db}")
    conn.close()

    # 2. create tables
    conn = connect(db)
    cur = conn.cursor()
    prefix = db.replace("_db", "")
    run_sql_file(cur, f"{prefix}_schema.sql")
    conn.commit()

    # 3. bulk insert with COPY (much faster than INSERT)
    for table in tables:
        path = os.path.join(DATA_DIR, db, table + ".csv")
        with open(path, encoding="utf-8") as f:
            cur.copy_expert(f"COPY {table} FROM STDIN WITH CSV HEADER", f)
        # keep SERIAL counters in sync with the loaded ids
        id_col = {"customers": "customer_id", "products": "product_id", "orders": "order_id",
                  "order_items": "item_id", "departments": "dept_id", "employees": "emp_id",
                  "attendance": "att_id", "accounts": "account_id", "transactions": "txn_id"}[table]
        cur.execute(f"SELECT setval(pg_get_serial_sequence('{table}','{id_col}'), (SELECT MAX({id_col}) FROM {table}))")
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"  loaded {table}: {cur.fetchone()[0]:,} rows")
    conn.commit()

    # 4. indexes after loading (faster than indexing while inserting)
    run_sql_file(cur, f"{prefix}_indexes.sql")
    cur.execute("ANALYZE")
    conn.commit()
    conn.close()
    print("  indexes created")

print("\nAll databases loaded. Open pgAdmin and refresh the Databases node.")
