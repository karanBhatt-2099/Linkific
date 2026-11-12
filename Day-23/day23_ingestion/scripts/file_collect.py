"""Read CSV / Excel / JSON from data/input, process in batches, store raw in staging."""
import json
import os
import re
import shutil
from pathlib import Path

import pandas as pd

from scripts.common import log, save_raw

INPUT = Path(os.getenv("INPUT_DIR", "/opt/airflow/data/input"))
DONE, FAILED = INPUT / "processed", INPUT / "failed"
BATCH = 1000


def to_records(df):
    return json.loads(df.to_json(orient="records", date_format="iso"))  # NaN -> null, safe types


def process_files():
    DONE.mkdir(exist_ok=True)
    FAILED.mkdir(exist_ok=True)
    errors = 0

    for f in sorted(INPUT.iterdir()):
        if f.suffix not in {".csv", ".xlsx", ".json"}:
            continue
        name = "file_" + re.sub(r"\W", "_", f.stem.lower())
        try:
            if f.suffix == ".csv":
                batches = pd.read_csv(f, chunksize=BATCH)  # reads big CSVs in chunks
            else:
                df = pd.read_excel(f) if f.suffix == ".xlsx" else pd.read_json(f)
                batches = (df[i:i + BATCH] for i in range(0, len(df), BATCH))
            for batch in batches:
                save_raw(name, to_records(batch))
            shutil.move(f, DONE / f.name)
            log.info("Processed %s", f.name)
        except Exception:
            errors += 1
            log.exception("Failed on %s, moving to failed/", f.name)
            shutil.move(f, FAILED / f.name)

    if errors:
        raise RuntimeError(f"{errors} file(s) failed, see logs")
