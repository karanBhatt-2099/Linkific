"""Small helpers: logging + saving/reading the 'raw' landing zone."""
import logging
import os
from datetime import datetime, timezone

import pandas as pd

from src.config import RAW_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("pipeline")


def save_raw(df, name, source):
    """Add lineage columns and write df to data/raw/<name>.parquet."""
    os.makedirs(RAW_DIR, exist_ok=True)
    df = df.copy()
    df["_source"] = source
    df["_ingested_at"] = datetime.now(timezone.utc).isoformat()
    df.to_parquet(f"{RAW_DIR}/{name}.parquet", index=False)
    log.info("Saved %s rows from '%s' -> raw/%s.parquet", len(df), source, name)


def read_raw(name):
    return pd.read_parquet(f"{RAW_DIR}/{name}.parquet")
