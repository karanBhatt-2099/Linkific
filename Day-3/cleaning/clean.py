"""Cleaning: trim text, empty -> NaN, types, missing values, duplicates."""
import logging
import re

import numpy as np
import pandas as pd

import config
from storage.files import save_both

log = logging.getLogger("clean")


def _base(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in df.columns:
        if pd.api.types.is_object_dtype(df[c]) or pd.api.types.is_string_dtype(df[c]):
            df[c] = df[c].str.replace(r"\s+", " ", regex=True).str.strip()
    return df.replace(r"^\s*$", np.nan, regex=True)


def clean_books(df):
    df = _base(df)
    df["price_gbp"] = pd.to_numeric(df["price"].str.replace(r"[^\d.]", "", regex=True), errors="coerce")
    df = df.drop(columns="price").dropna(subset=["title", "price_gbp"])
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").astype("Int64")
    for col in ("description", "category"):
        if col in df:
            df[col] = df[col].fillna("")
    return df.drop_duplicates(subset="url")


def clean_news(df):
    df = _base(df).dropna(subset=["title", "url"])
    for col in ("points", "comments"):
        df[col] = pd.to_numeric(df[col].str.extract(r"(\d+)")[0], errors="coerce").fillna(0).astype(int)
    df["posted"] = pd.to_datetime(df["posted"], errors="coerce")
    return df.drop_duplicates(subset="url")


def clean_jobs(df):
    df = _base(df).dropna(subset=["title", "company"])
    df["date_posted"] = pd.to_datetime(df["date_posted"], errors="coerce")
    df["state"] = df["location"].str.split(",").str[-1].str.strip()
    return df.drop_duplicates(subset=["title", "company", "location"])


def clean_hockey(df):
    def snake(c):
        return re.sub(r"[^0-9a-z]+", "_", c.lower().replace("%", "pct")).strip("_") or "plus_minus"

    df = _base(df)
    df.columns = [snake(c) for c in df.columns]
    df = df.dropna(subset=["team_name"])
    for c in df.columns.difference(["team_name", "scraped_at"]):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    if "ot_losses" in df:
        df["ot_losses"] = df["ot_losses"].fillna(0)  # pre-OT seasons have no value
    return df.drop_duplicates(subset=["team_name", "year"])


def clean_quotes(df):
    df = _base(df).dropna(subset=["text", "author"])
    df["text"] = df["text"].str.strip("“”\" ")
    df["tags"] = df["tags"].fillna("")
    return df.drop_duplicates(subset=["text", "author"])


CLEANERS = {
    "books": clean_books,
    "news": clean_news,
    "jobs": clean_jobs,
    "hockey": clean_hockey,
    "quotes_js": clean_quotes,
    "quotes_login": clean_quotes,
}


def clean_all() -> list[str]:
    done = []
    for name, fn in CLEANERS.items():
        raw = config.RAW_DIR / f"{name}.csv"
        if not raw.exists():
            log.info("No raw file for %s, skipping", name)
            continue
        before = pd.read_csv(raw)
        after = fn(before)
        save_both(after, config.CLEAN_DIR, name)
        log.info("%s: %d -> %d rows", name, len(before), len(after))
        done.append(name)
    return done
