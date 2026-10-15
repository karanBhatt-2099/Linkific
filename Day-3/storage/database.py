"""SQLite storage."""
import sqlite3
from contextlib import closing

import pandas as pd

import config


def save_df(df: pd.DataFrame, table: str, db_path=config.DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as con:
        df.to_sql(table, con, if_exists="replace", index=False)


def load_clean_into_db(db_path=config.DB_PATH) -> list[str]:
    tables = []
    for csv in sorted(config.CLEAN_DIR.glob("*.csv")):
        save_df(pd.read_csv(csv), csv.stem, db_path)
        tables.append(csv.stem)
    return tables


def query(sql: str, params=(), db_path=config.DB_PATH) -> pd.DataFrame:
    with closing(sqlite3.connect(db_path)) as con:
        return pd.read_sql_query(sql, con, params=params)
