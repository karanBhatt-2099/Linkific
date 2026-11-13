"""Extract from a source DB with an incremental load (watermark on updated_at)."""
import os

from sqlalchemy import create_engine, text

from scripts.common import get_watermark, log, save_raw, set_watermark


def extract_orders():
    engine = create_engine(os.environ["SOURCE_DB_URL"])
    last = get_watermark("db_orders") or "1970-01-01 00:00:00"
    log.info("db_orders: loading rows with updated_at > %s", last)

    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT * FROM orders WHERE updated_at > :last ORDER BY updated_at"),
            {"last": last},
        ).mappings().all()
    rows = [dict(r) for r in rows]

    if not rows:
        log.info("db_orders: nothing new")
        return
    save_raw("db_orders", rows)
    set_watermark("db_orders", rows[-1]["updated_at"])  # only moves forward AFTER a successful load
