"""Step 3: Run the SQL transformation in Snowflake."""
from snowflake_conn import get_connection


def transform(sql_file="sql/02_transform.sql"):
    with open(sql_file) as f:
        sql = f.read()
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql)
        print("ANALYTICS.CATEGORY_SUMMARY created")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    transform()
