"""Combine cleaned datasets from different sites into one unified schema."""
import logging

import pandas as pd

import config
from storage.database import save_df
from storage.files import save_both

log = logging.getLogger("aggregate")

# dataset -> (content_type, title column, url column, extra column)
MAPPING = {
    "books":        ("product", "title", "url", "category"),
    "news":         ("article", "title", "url", "site"),
    "jobs":         ("job",     "title", "apply_url", "company"),
    "quotes_js":    ("quote",   "text",  None, "author"),
    "quotes_login": ("quote",   "text",  None, "author"),
}


def aggregate() -> pd.DataFrame:
    frames = []
    for name, (ctype, title, url, extra) in MAPPING.items():
        path = config.CLEAN_DIR / f"{name}.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path)
        frames.append(pd.DataFrame({
            "source": name,
            "content_type": ctype,
            "title": df[title],
            "url": df[url] if url else None,
            "extra": df[extra],
        }))
    if not frames:
        raise FileNotFoundError("No cleaned datasets found. Run: python main.py clean")
    unified = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["content_type", "title"])
    save_both(unified, config.CLEAN_DIR, "unified")
    save_df(unified, "unified")
    log.info("unified: %d rows from %d sources", len(unified), len(frames))
    return unified
