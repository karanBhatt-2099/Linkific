import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

from src import config
from src.utils.logger import get_logger
from src.utils.retry import retry

log = get_logger("load")


@retry(max_attempts=3, delay=3)
def get_connection():
    sf = config.SNOWFLAKE
    params = {k: sf[k] for k in ("account", "user", "password", "warehouse") if sf[k]}
    if sf["role"]:
        params["role"] = sf["role"]
    conn = snowflake.connector.connect(**params)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {sf['database']}")
    cur.execute(f"USE DATABASE {sf['database']}")
    return conn


def setup_objects(conn) -> None:
    """Create schemas and target tables if they do not exist yet."""
    ddl = config.SNOWFLAKE_DDL.read_text()
    cur = conn.cursor()
    for stmt in [s.strip() for s in ddl.split(";") if s.strip()]:
        cur.execute(stmt)
    log.info("Snowflake schemas and tables are ready")


def _upper(df):
    df = df.copy()
    df.columns = [c.upper() for c in df.columns]
    for col in df.select_dtypes(include=["datetime", "datetimetz"]).columns:
        df[col] = df[col].astype("datetime64[ns]")
    return df


@retry(max_attempts=3, delay=3)
def upsert(conn, df, table: str, keys: list[str]) -> None:
    """Load df into STAGING.STG_<table>, then MERGE into ANALYTICS.<table> (insert new, update changed)."""
    if df.empty:
        log.info("%s: nothing to load", table)
        return
    df = _upper(df)
    keys = [k.upper() for k in keys]
    db = config.SNOWFLAKE["database"]
    stg = f"STG_{table}"

    write_pandas(conn, df, stg, database=db, schema="STAGING",
                 auto_create_table=True, overwrite=True, use_logical_type=True)

    cols = list(df.columns)
    on = " AND ".join(f"t.{k} = s.{k}" for k in keys)
    set_clause = ", ".join(f"t.{c} = s.{c}" for c in cols if c not in keys)
    insert_cols = ", ".join(cols)
    insert_vals = ", ".join(f"s.{c}" for c in cols)
    sql = (
        f"MERGE INTO ANALYTICS.{table} t USING STAGING.{stg} s ON {on} "
        f"WHEN MATCHED THEN UPDATE SET {set_clause} "
        f"WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})"
    )
    conn.cursor().execute(sql)
    log.info("%s: upserted %d rows", table, len(df))


@retry(max_attempts=3, delay=3)
def truncate_and_load(conn, df, table: str) -> None:
    """Full refresh: empty the table and reload it."""
    df = _upper(df)
    db = config.SNOWFLAKE["database"]
    conn.cursor().execute(f"TRUNCATE TABLE ANALYTICS.{table}")
    write_pandas(conn, df, table, database=db, schema="ANALYTICS", use_logical_type=True)
    log.info("%s: truncated and loaded %d rows", table, len(df))


def refresh_daily_aggregate(conn) -> None:
    """Aggregation: rebuild daily sales summary from the fact table."""
    conn.cursor().execute("""
        CREATE OR REPLACE TABLE ANALYTICS.AGG_DAILY_SALES AS
        SELECT ORDER_DATE::DATE            AS SALES_DATE,
               COUNT(DISTINCT ORDER_ID)    AS TOTAL_ORDERS,
               SUM(QUANTITY)               AS UNITS_SOLD,
               SUM(NET_AMOUNT)             AS NET_REVENUE
        FROM ANALYTICS.FACT_SALES
        WHERE ORDER_STATUS <> 'CANCELLED'
        GROUP BY 1
        ORDER BY 1
    """)
    log.info("AGG_DAILY_SALES refreshed")
