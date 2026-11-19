"""Extract: read the raw orders CSV and validate its schema."""
from pathlib import Path

import pandas as pd

from etl.config import REQUIRED_COLUMNS


class SchemaError(ValueError):
    pass


def extract_orders(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Raw file not found: {path}")
    # Read everything as string: typing/cleaning is the transform step's job.
    df = pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[""])
    df.columns = [c.strip().lower() for c in df.columns]
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise SchemaError(f"Missing columns in {path.name}: {missing}")
    return df[REQUIRED_COLUMNS]
