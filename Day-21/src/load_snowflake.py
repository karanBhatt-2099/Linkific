"""Snowflake loader. Credentials come from .env (SNOWFLAKE_*)."""
import glob
import os

import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

from src.config import RAW_DIR
from src.utils import log, read_raw


def connect():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"), user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"), role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"), database=os.getenv("SNOWFLAKE_DATABASE"),
    )


def load_df(conn, df, table, schema):
    """Create schema if needed, then (re)create table and load df."""
    conn.cursor().execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    df = df.copy()
    df.columns = [c.upper() for c in df.columns]
    write_pandas(conn, df, table.upper(), schema=schema.upper(),
                 auto_create_table=True, overwrite=True, use_logical_type=True)
    log.info("Loaded %s rows -> %s.%s", len(df), schema, table.upper())


def load_raw_tables():
    """Every data/raw/*.parquet -> <RAW schema>.<NAME>"""
    conn = connect()
    try:
        for path in sorted(glob.glob(f"{RAW_DIR}/*.parquet")):
            name = os.path.basename(path).replace(".parquet", "")
            load_df(conn, read_raw(name), name, os.getenv("SNOWFLAKE_SCHEMA_RAW", "RAW"))
    finally:
        conn.close()
