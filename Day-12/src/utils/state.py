import json
from datetime import datetime

from src import config

DEFAULT_WATERMARK = "1970-01-01 00:00:00"


def get_watermark() -> str:
    """Last successfully loaded orders.updated_at value."""
    if config.STATE_FILE.exists():
        return json.loads(config.STATE_FILE.read_text()).get("orders_watermark", DEFAULT_WATERMARK)
    return DEFAULT_WATERMARK


def set_watermark(value) -> None:
    config.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.STATE_FILE.write_text(
        json.dumps({"orders_watermark": str(value), "saved_at": datetime.now().isoformat()}, indent=2)
    )


def reset_watermark() -> None:
    if config.STATE_FILE.exists():
        config.STATE_FILE.unlink()
