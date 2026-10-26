"""Staging area: raw extracted data is stored as Parquet files between Extract and Transform."""
import pandas as pd

from src import config


def stage(df: pd.DataFrame, name: str) -> None:
    config.STAGING_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(config.STAGING_DIR / f"{name}.parquet", index=False)


def read_stage(name: str) -> pd.DataFrame:
    return pd.read_parquet(config.STAGING_DIR / f"{name}.parquet")
