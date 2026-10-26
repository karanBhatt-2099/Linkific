import pandas as pd
import requests

from src import config
from src.utils.logger import get_logger
from src.utils.retry import retry

log = get_logger("extract.api")


@retry(max_attempts=3, delay=2)
def _get_page(skip: int) -> dict:
    resp = requests.get(
        config.API_URL,
        params={"limit": config.API_PAGE_SIZE, "skip": skip,
                "select": "title,category,brand,price"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def extract_products() -> pd.DataFrame:
    """Pull every product, following limit/skip pagination until `total` is reached."""
    rows, skip = [], 0
    while True:
        data = _get_page(skip)
        batch = data.get("products", [])
        rows.extend(batch)
        skip += config.API_PAGE_SIZE
        log.info("API page fetched: %d / %d products", len(rows), data["total"])
        if not batch or skip >= data["total"]:
            break
    return pd.DataFrame(rows)
