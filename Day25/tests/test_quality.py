"""Unit tests for the data quality framework."""
from datetime import datetime

import pytest
from pyspark.sql import functions as F

from etl import config, quality


def flagged_ids(df, check):
    """ids of the rows a single check marks as failing."""
    out = check(df)
    flag = [c for c in out.columns if c.startswith(quality.FAIL)][0]
    return sorted(r["id"] for r in out.filter(F.col(flag)).collect())


def test_not_null(spark):
    df = spark.createDataFrame([(1, "a"), (2, None)], "id int, name string")
    assert flagged_ids(df, quality.not_null("name")) == [2]


def test_range_check_ignores_nulls(spark):
    df = spark.createDataFrame([(1, 50.0), (2, -1.0), (3, 500.0), (4, None)], "id int, fee double")
    assert flagged_ids(df, quality.in_range("fee", 0, 100)) == [2, 3]


def test_format_check(spark):
    df = spark.createDataFrame(
        [(1, "ok@mail.com"), (2, "not-an-email"), (3, "a@b"), (4, None)], "id int, email string"
    )
    assert flagged_ids(df, quality.matches("email", quality.EMAIL_PATTERN)) == [2, 3]

    phones = spark.createDataFrame([(1, "9876543210"), (2, "12345"), (3, "98765abcde")], "id int, phone string")
    assert flagged_ids(phones, quality.matches("phone", quality.PHONE_PATTERN)) == [2, 3]


def test_duplicate_check_keeps_newest(spark):
    df = spark.createDataFrame(
        [(1, "K", datetime(2026, 1, 1)), (2, "K", datetime(2026, 2, 1)), (3, "X", datetime(2026, 1, 1))],
        "id int, key string, updated_at timestamp",
    )
    assert flagged_ids(df, quality.no_duplicates("key")) == [1]


def test_referential_integrity(spark):
    df = spark.createDataFrame([(1, "P1"), (2, "P2"), (3, "P99"), (4, None)], "id int, patient_id string")
    patients = spark.createDataFrame([("P1",), ("P2",)], "patient_id string")
    assert flagged_ids(df, quality.exists_in("patient_id", patients, "patient_id")) == [3]


def test_run_checks_splits_good_and_rejected(spark):
    df = spark.createDataFrame(
        [(1, "a", 10.0), (2, None, 10.0), (3, "c", -5.0), (4, None, -5.0)], "id int, name string, fee double"
    )
    good, rejected, report = quality.run_checks(df, [quality.not_null("name"), quality.in_range("fee", 0, 100)])

    assert [r.id for r in good.collect()] == [1]
    reasons = {r.id: r.dq_errors for r in rejected.collect()}
    assert reasons[2] == "null_name"
    assert reasons[3] == "range_fee"
    assert set(reasons[4].split(",")) == {"null_name", "range_fee"}
    assert report == {"null_name": 2, "range_fee": 2}
    assert "dq_errors" not in good.columns


def test_reject_limit(monkeypatch):
    monkeypatch.setattr(config, "MAX_REJECT_RATIO", 0.3)
    quality.enforce_reject_limit("t", 10, 2)       # 20%: fine
    quality.enforce_reject_limit("empty", 0, 0)    # nothing to judge
    with pytest.raises(quality.DataQualityError):
        quality.enforce_reject_limit("t", 10, 4)   # 40%: too many
