
import argparse
import sys
import traceback

from src import pipeline
from src.utils.alerts import send_failure_email
from src.utils.logger import get_logger

log = get_logger("main")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="ignore watermark and reload everything")
    args = parser.parse_args()
    try:
        pipeline.run_all(full_refresh=args.full)
        log.info("Pipeline finished successfully")
    except Exception as exc:
        log.exception("Pipeline FAILED")
        send_failure_email("ETL pipeline failed", f"{exc}\n\n{traceback.format_exc()}")
        sys.exit(1)
