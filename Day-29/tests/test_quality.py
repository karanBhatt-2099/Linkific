"""Data-quality validation tests."""
import pytest

from etl.quality import DataQualityError, check_dataframe
from etl.transform import transform_orders


def test_dq_passes_on_sample_data(sample_csv):
    from etl.extract import extract_orders
    raw = extract_orders(sample_csv)
    clean, rejects = transform_orders(raw)
    m = check_dataframe(clean, rejects, raw_rows=len(raw))
    assert m["clean_rows"] + m["reject_rows"] == m["raw_rows"]
    assert m["reject_ratio"] < 0.20


def test_dq_fails_when_reject_ratio_too_high(make_raw):
    raw = make_raw({"order_id": "1"}, {"order_id": "2", "quantity": "-1"}, {"order_id": "3", "quantity": "-1"})
    clean, rejects = transform_orders(raw)
    with pytest.raises(DataQualityError, match="reject ratio"):
        check_dataframe(clean, rejects, raw_rows=len(raw))


def test_dq_fails_when_nothing_valid(make_raw):
    raw = make_raw({"quantity": "-1"})
    clean, rejects = transform_orders(raw)
    with pytest.raises(DataQualityError):
        check_dataframe(clean, rejects, raw_rows=1, max_reject_ratio=1.0)


def test_dq_detects_row_loss(make_raw):
    clean, rejects = transform_orders(make_raw({"order_id": "1"}))
    with pytest.raises(DataQualityError, match="reconciliation"):
        check_dataframe(clean, rejects, raw_rows=5, max_reject_ratio=1.0)


def test_dq_detects_duplicate_keys(make_raw):
    import pandas as pd
    clean, rejects = transform_orders(make_raw({"order_id": "1"}))
    clean = pd.concat([clean, clean], ignore_index=True)
    with pytest.raises(DataQualityError, match="duplicate"):
        check_dataframe(clean, rejects, raw_rows=2, max_reject_ratio=1.0)
