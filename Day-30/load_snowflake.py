"""Step 2: Upload the CSV to a Snowflake stage and COPY it into RAW.PRODUCTS."""
from snowflake_conn import get_connection


def load(path="products.csv"):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("TRUNCATE TABLE RAW.PRODUCTS")   # idempotent: safe to re-run
        cur.execute(f"PUT file://{path} @RAW.PRODUCT_STAGE OVERWRITE=TRUE")
        cur.execute("""
            COPY INTO RAW.PRODUCTS (id, title, category, price, stock, rating)
            FROM @RAW.PRODUCT_STAGE/products.csv.gz
            FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"')
        """)
        print("Loaded data into RAW.PRODUCTS")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    load()
