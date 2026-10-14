from pathlib import Path

import pandas as pd


def _df(data) -> pd.DataFrame:
    return data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)


def save_csv(data, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _df(data).to_csv(path, index=False, encoding="utf-8")
    return path


def save_json(data, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _df(data).to_json(path, orient="records", force_ascii=False, indent=2, date_format="iso")
    return path


def save_both(data, directory: Path, name: str):
    save_csv(data, directory / f"{name}.csv")
    save_json(data, directory / f"{name}.json")
