"""Run the pipeline outside Airflow.

  python scripts/run_pipeline.py --dry-run     # extract+transform+DQ only, no Snowflake needed
  python scripts/run_pipeline.py               # full run into Snowflake (needs .env)
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etl import load, pipeline  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-file", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    bid = load.new_batch_id()
    if a.dry_run:
        print(json.dumps(pipeline.step_extract_transform(bid, a.raw_file), indent=2))
    else:
        print(json.dumps(pipeline.run_all(a.raw_file, bid), indent=2, default=str))
