import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from generate_sample_data import generate  # noqa: E402


@pytest.fixture
def good_row():
    return {"order_id": "ORD1", "customer_id": "C1", "product": "Desk Lamp", "category": "home",
            "quantity": "2", "unit_price": "10.50", "order_date": "2026-11-01",
            "status": "completed", "country": "in"}


@pytest.fixture
def make_raw(good_row):
    import pandas as pd

    def _make(*overrides):
        rows = [{**good_row, **o} for o in overrides] or [good_row]
        return pd.DataFrame(rows).astype(str).replace({"None": None})
    return _make


@pytest.fixture(scope="session")
def sample_csv(tmp_path_factory):
    p = tmp_path_factory.mktemp("raw") / "orders.csv"
    generate(1000, 0.02).to_csv(p, index=False)
    return p
