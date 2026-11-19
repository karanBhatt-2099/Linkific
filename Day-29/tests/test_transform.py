"""Unit + edge-case tests for extract/transform."""
import pandas as pd
import pytest

from etl.extract import SchemaError, extract_orders
from etl.transform import transform_orders


def reasons(rejects):
    return set(rejects["reject_reason"])


def test_happy_path_normalises_and_derives(make_raw):
    clean, rejects = transform_orders(make_raw({"status": " COMPLETED ", "country": "in"}))
    assert len(clean) == 1 and rejects.empty
    r = clean.iloc[0]
    assert r["status"] == "completed" and r["country"] == "IN" and r["category"] == "Home"
    assert r["gross_amount"] == 21.0 and r["net_revenue"] == 21.0


@pytest.mark.parametrize("status", ["cancelled", "refunded", "pending"])
def test_net_revenue_zero_for_non_completed(make_raw, status):
    clean, _ = transform_orders(make_raw({"status": status}))
    assert clean.iloc[0]["gross_amount"] == 21.0
    assert clean.iloc[0]["net_revenue"] == 0.0


@pytest.mark.parametrize("override,reason", [
    ({"quantity": "0"}, "invalid_quantity"),
    ({"quantity": "-3"}, "invalid_quantity"),
    ({"quantity": "1.5"}, "invalid_quantity"),
    ({"quantity": "abc"}, "invalid_quantity"),
    ({"quantity": None}, "invalid_quantity"),
    ({"unit_price": "-1"}, "invalid_unit_price"),
    ({"unit_price": "free"}, "invalid_unit_price"),
    ({"order_date": "not-a-date"}, "invalid_order_date"),
    ({"order_date": None}, "invalid_order_date"),
    ({"status": "shipped"}, "invalid_status"),
    ({"customer_id": None}, "missing_customer_id"),
    ({"order_id": None}, "missing_order_id"),
    ({"order_id": "   "}, "missing_order_id"),
])
def test_invalid_rows_rejected_with_reason(make_raw, override, reason):
    clean, rejects = transform_orders(make_raw(override))
    assert clean.empty
    assert reasons(rejects) == {reason}


def test_duplicates_keep_last(make_raw):
    clean, rejects = transform_orders(make_raw(
        {"order_id": "A", "quantity": "1"}, {"order_id": "A", "quantity": "5"}))
    assert len(clean) == 1 and clean.iloc[0]["quantity"] == 5
    assert reasons(rejects) == {"duplicate_order_id"}


def test_zero_price_allowed(make_raw):
    clean, rejects = transform_orders(make_raw({"unit_price": "0"}))
    assert len(clean) == 1 and rejects.empty


def test_missing_optional_fields_get_defaults(make_raw):
    clean, _ = transform_orders(make_raw({"country": None, "category": None, "product": None}))
    r = clean.iloc[0]
    assert (r["country"], r["category"], r["product"]) == ("UNKNOWN", "Uncategorized", "Unknown")


def test_every_row_accounted_for(make_raw):
    raw = make_raw({"order_id": "1"}, {"order_id": "2", "quantity": "-1"},
                   {"order_id": "3"}, {"order_id": "3"}, {"order_id": "4", "status": "x"})
    clean, rejects = transform_orders(raw)
    assert len(clean) + len(rejects) == len(raw)


def test_unicode_and_whitespace_ids(make_raw):
    clean, _ = transform_orders(make_raw({"order_id": "  ORD-é1  ", "product": "Café Mug"}))
    assert clean.iloc[0]["order_id"] == "ORD-é1"


def test_empty_input_returns_empty_frames(make_raw):
    raw = make_raw().iloc[0:0]
    clean, rejects = transform_orders(raw)
    assert clean.empty and rejects.empty


def test_extract_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        extract_orders(tmp_path / "nope.csv")


def test_extract_missing_columns(tmp_path):
    p = tmp_path / "bad.csv"
    pd.DataFrame({"order_id": ["1"]}).to_csv(p, index=False)
    with pytest.raises(SchemaError):
        extract_orders(p)


def test_extract_header_case_and_whitespace(tmp_path, good_row):
    p = tmp_path / "o.csv"
    df = pd.DataFrame([good_row])
    df.columns = [f" {c.upper()} " for c in df.columns]
    df.to_csv(p, index=False)
    assert list(extract_orders(p).columns)[0] == "order_id"
