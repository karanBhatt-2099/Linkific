"""Thin Snowflake helper: connection + SQL file runner."""
from contextlib import contextmanager
from pathlib import Path

import snowflake.connector

from etl.config import SQL_DIR, snowflake_settings


@contextmanager
def get_connection():
    conn = snowflake.connector.connect(
        **snowflake_settings(),
        session_parameters={"QUERY_TAG": "etl_orders_pipeline"},
    )
    try:
        yield conn
    finally:
        conn.close()


def run_sql(conn, sql: str, params=None):
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        cur.close()


def run_sql_file(conn, name: str, params: dict | None = None):
    """Run a .sql file from /sql. Statements are split on ';' (no ';' inside literals)."""
    text = (Path(SQL_DIR) / name).read_text()
    if params:
        text = text.format(**params)
    for stmt in [s.strip() for s in text.split(";") if s.strip()]:
        run_sql(conn, stmt)
