import pandas as pd

from src import config
from src.utils.logger import get_logger

log = get_logger("extract.file")


def extract_order_items() -> pd.DataFrame:
    """Read the CSV as text so cleaning decisions are made in the transform step."""
    if not config.CSV_PATH.exists():
        raise FileNotFoundError(f"CSV source not found: {config.CSV_PATH}")
    df = pd.read_csv(config.CSV_PATH, dtype=str)
    log.info("Extracted %d rows from %s", len(df), config.CSV_PATH.name)
    return df
