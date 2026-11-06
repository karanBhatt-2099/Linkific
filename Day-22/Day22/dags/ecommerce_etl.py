"""
Day 22 – E-commerce ETL pipeline

extract_and_load_raw -> data_quality_checks -> build_dimensions -> build_fact_sales
(API -> Snowflake RAW)  (Great Expectations)  (RAW -> dim tables)  (RAW -> fact table)
"""
import os
from datetime import datetime

import great_expectations as gx
import great_expectations.expectations as gxe
import pandas as pd
import requests
import snowflake.connector
from airflow import DAG
from airflow.operators.python import PythonOperator

API = "https://fakestoreapi.com"


# ---------- helpers ----------
def get_conn():
    """Connect to Snowflake using settings from the .env file."""
    settings = dict(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
    )

    key_path = os.environ.get("SNOWFLAKE_PRIVATE_KEY_PATH")
    if key_path:  # key-pair login
        from cryptography.hazmat.primitives import serialization

        with open(key_path, "rb") as f:
            key = serialization.load_pem_private_key(f.read(), password=None)
        settings["private_key"] = key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    else:  # password login
        settings["password"] = os.environ["SNOWFLAKE_PASSWORD"]

    return snowflake.connector.connect(**settings)


def run_sql(statements):
    """Run a list of SQL statements in Snowflake."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        for sql in statements:
            cur.execute(sql)
    finally:
        conn.close()


def get_json(path):
    response = requests.get(f"{API}/{path}", timeout=30)
    response.raise_for_status()
    return response.json()


# ---------- task 1: API -> RAW ----------
def extract_and_load_raw():
    products = get_json("products")
    users = get_json("users")
    carts = get_json("carts")

    # reshape the JSON into simple rows
    product_rows = [
        (p["id"], p["title"], p["price"], p["category"], p["rating"]["rate"], p["rating"]["count"])
        for p in products
    ]
    user_rows = [
        (u["id"], u["email"], u["name"]["firstname"], u["name"]["lastname"], u["address"]["city"])
        for u in users
    ]
    cart_rows = [
        (c["id"], c["userId"], c["date"][:10], item["productId"], item["quantity"])
        for c in carts
        for item in c["products"]
    ]

    # full refresh: empty the raw tables, then insert today's data
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE RAW.PRODUCTS")
        cur.execute("TRUNCATE TABLE RAW.USERS")
        cur.execute("TRUNCATE TABLE RAW.CART_ITEMS")
        cur.executemany(
            "INSERT INTO RAW.PRODUCTS (id, title, price, category, rating_rate, rating_count) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            product_rows,
        )
        cur.executemany(
            "INSERT INTO RAW.USERS (id, email, first_name, last_name, city) "
            "VALUES (%s, %s, %s, %s, %s)",
            user_rows,
        )
        cur.executemany(
            "INSERT INTO RAW.CART_ITEMS (cart_id, user_id, cart_date, product_id, quantity) "
            "VALUES (%s, %s, %s, %s, %s)",
            cart_rows,
        )
    finally:
        conn.close()

    print(f"Loaded {len(product_rows)} products, {len(user_rows)} users, {len(cart_rows)} cart items")


# ---------- task 2: data quality checks (Great Expectations) ----------
def read_table(table):
    """Read a Snowflake table into a pandas DataFrame (lowercase column names)."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table}")
        columns = [col[0].lower() for col in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=columns)
    finally:
        conn.close()


def validate(name, df, expectations):
    """Run Great Expectations checks on a DataFrame. Returns a list of failed checks."""
    context = gx.get_context(mode="ephemeral")  # in-memory, no config files needed
    asset = context.data_sources.add_pandas(f"source_{name}").add_dataframe_asset(name)
    batch = asset.add_batch_definition_whole_dataframe("whole").get_batch(
        batch_parameters={"dataframe": df}
    )

    failed = []
    for check in expectations:
        if not batch.validate(check).success:
            failed.append(f"{name}: {type(check).__name__}({getattr(check, 'column', '')})")
    return failed


def data_quality_checks():
    products = read_table("RAW.PRODUCTS")
    users = read_table("RAW.USERS")
    cart_items = read_table("RAW.CART_ITEMS")

    failed = []

    failed += validate("products", products, [
        gxe.ExpectTableRowCountToBeBetween(min_value=1),
        gxe.ExpectColumnValuesToNotBeNull(column="id"),
        gxe.ExpectColumnValuesToBeUnique(column="id"),
        gxe.ExpectColumnValuesToNotBeNull(column="title"),
        gxe.ExpectColumnValuesToBeBetween(column="price", min_value=0, strict_min=True),
        gxe.ExpectColumnValuesToBeBetween(column="rating_rate", min_value=0, max_value=5),
    ])

    failed += validate("users", users, [
        gxe.ExpectTableRowCountToBeBetween(min_value=1),
        gxe.ExpectColumnValuesToNotBeNull(column="id"),
        gxe.ExpectColumnValuesToBeUnique(column="id"),
        gxe.ExpectColumnValuesToNotBeNull(column="email"),
    ])

    failed += validate("cart_items", cart_items, [
        gxe.ExpectTableRowCountToBeBetween(min_value=1),
        gxe.ExpectColumnValuesToNotBeNull(column="cart_id"),
        gxe.ExpectColumnValuesToNotBeNull(column="cart_date"),
        gxe.ExpectColumnValuesToBeBetween(column="quantity", min_value=0, strict_min=True),
        # every order line must point to a real product and a real customer
        gxe.ExpectColumnValuesToBeInSet(column="product_id", value_set=products["id"].tolist()),
        gxe.ExpectColumnValuesToBeInSet(column="user_id", value_set=users["id"].tolist()),
    ])

    if failed:
        raise ValueError("Data quality checks failed:\n" + "\n".join(failed))
    print("All data quality checks passed")


# ---------- task 3: RAW -> dimensions ----------
def build_dimensions():
    run_sql([
        """
        INSERT OVERWRITE INTO ANALYTICS.DIM_PRODUCT
        SELECT id, title, category, price, rating_rate
        FROM RAW.PRODUCTS
        """,
        """
        INSERT OVERWRITE INTO ANALYTICS.DIM_CUSTOMER
        SELECT id, first_name || ' ' || last_name, email, city
        FROM RAW.USERS
        """,
        """
        INSERT OVERWRITE INTO ANALYTICS.DIM_DATE
        SELECT TO_NUMBER(TO_CHAR(d, 'YYYYMMDD')), d, YEAR(d), QUARTER(d),
               MONTH(d), MONTHNAME(d), DAYNAME(d)
        FROM (
            SELECT DATEADD(day, SEQ4(), '2020-01-01'::DATE) AS d
            FROM TABLE(GENERATOR(ROWCOUNT => 3000))
        )
        """,
    ])


# ---------- task 4: RAW -> fact ----------
def build_fact_sales():
    run_sql([
        """
        INSERT OVERWRITE INTO ANALYTICS.FACT_SALES
        SELECT c.cart_id,
               TO_NUMBER(TO_CHAR(c.cart_date, 'YYYYMMDD')),
               c.user_id,
               c.product_id,
               c.quantity,
               p.price,
               c.quantity * p.price
        FROM RAW.CART_ITEMS c
        JOIN RAW.PRODUCTS p ON c.product_id = p.id
        """,
    ])


# ---------- the DAG ----------
with DAG(
    dag_id="ecommerce_etl",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["day22", "ecommerce"],
) as dag:
    load_raw = PythonOperator(task_id="extract_and_load_raw", python_callable=extract_and_load_raw)
    checks = PythonOperator(task_id="data_quality_checks", python_callable=data_quality_checks)
    dims = PythonOperator(task_id="build_dimensions", python_callable=build_dimensions)
    fact = PythonOperator(task_id="build_fact_sales", python_callable=build_fact_sales)

    load_raw >> checks >> dims >> fact
