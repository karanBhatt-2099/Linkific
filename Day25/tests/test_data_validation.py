"""Data validation tests: check the data that actually landed in the warehouse."""
import re

from pyspark.sql import functions as F

from etl import quality

KEYS = {
    "DIM_PATIENTS": "patient_id",
    "DIM_DOCTORS": "doctor_id",
    "FACT_APPOINTMENTS": "appointment_id",
}


def test_keys_are_present_and_unique(pipeline_run):
    sink, _ = pipeline_run
    for table, key in KEYS.items():
        values = [r[key] for r in sink.rows(table)]
        assert values and all(v is not None for v in values), table
        assert len(values) == len(set(values)), f"duplicate keys in {table}"


def test_referential_integrity_in_warehouse(pipeline_run):
    sink, _ = pipeline_run
    patients = {r["patient_id"] for r in sink.rows("DIM_PATIENTS")}
    doctors = {r["doctor_id"] for r in sink.rows("DIM_DOCTORS")}
    for fact in sink.rows("FACT_APPOINTMENTS"):
        assert fact["patient_id"] in patients
        assert fact["doctor_id"] in doctors


def test_values_are_in_range_and_well_formed(pipeline_run):
    sink, _ = pipeline_run
    for p in sink.rows("DIM_PATIENTS"):
        assert 0 <= p["age"] <= 120
        assert re.match(quality.EMAIL_PATTERN, p["email"])
        assert re.match(quality.PHONE_PATTERN, p["phone"])
        assert p["gender"] in {"Male", "Female", "Unknown"}
    for f in sink.rows("FACT_APPOINTMENTS"):
        assert 0 <= f["fee"] <= 100000
        assert re.match(quality.STATUS_PATTERN, f["status"])
        assert f["fee_band"] in {"Low", "Medium", "High"}
        assert f["revenue"] in (0.0, f["fee"])


def test_summary_reconciles_with_fact_table(pipeline_run):
    sink, _ = pipeline_run
    facts = sink.rows("FACT_APPOINTMENTS")
    summary = sink.rows("DOCTOR_MONTHLY_SUMMARY")
    assert sum(s["total_appointments"] for s in summary) == len(facts)
    assert sum(s["total_revenue"] for s in summary) == sum(f["revenue"] for f in facts)
    assert sum(s["completed"] + s["cancelled"] + s["no_shows"] for s in summary) <= len(facts)


def test_no_rows_are_lost_between_clean_good_and_rejected(spark, pipeline_run):
    _, staging = pipeline_run
    for table in ("patients", "doctors", "appointments"):
        clean = spark.read.parquet(str(staging / "clean" / table)).count()
        good = spark.read.parquet(str(staging / "good" / table)).count()
        rejected = spark.read.parquet(str(staging / "rejected" / table)).count()
        assert good + rejected == clean, table


def test_every_rejected_row_has_a_reason(spark, pipeline_run):
    _, staging = pipeline_run
    for table in ("patients", "doctors", "appointments"):
        rejected = spark.read.parquet(str(staging / "rejected" / table))
        assert rejected.filter((F.col("dq_errors").isNull()) | (F.col("dq_errors") == "")).count() == 0
