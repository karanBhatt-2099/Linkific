"""Unit tests for the PySpark transformations."""
from datetime import date, datetime

from etl import transform


def strings(spark, columns, rows):
    return spark.createDataFrame(rows, ", ".join(f"{c} string" for c in columns))


def test_clean_patients(spark):
    columns = ["patient_id", "full_name", "dob", "gender", "phone", "email", "updated_at", "is_deleted"]
    raw = strings(spark, columns, [
        ("p001", "  asha RAO ", "1985-03-12", "F", "98765-43210", " ASHA@Mail.COM ", "2026-11-01 09:00:00", "TRUE"),
        ("P002", "   ", "bad-date", "other", "", None, "2026-11-01 09:05:00", None),
    ])
    rows = {r.patient_id: r for r in transform.clean_patients(raw).collect()}

    good = rows["P001"]
    assert good.full_name == "Asha Rao"
    assert good.dob == date(1985, 3, 12)
    assert good.gender == "Female"
    assert good.phone == "9876543210"
    assert good.email == "asha@mail.com"
    assert good.updated_at is not None
    assert good.is_deleted is True

    messy = rows["P002"]
    assert messy.full_name is None      # blank text becomes null
    assert messy.dob is None            # unparseable date becomes null
    assert messy.gender == "Unknown"
    assert messy.phone is None
    assert messy.email is None
    assert messy.is_deleted is False    # missing flag means not deleted


def test_clean_appointments_normalises_status_fee_and_date(spark):
    columns = ["appointment_id", "patient_id", "doctor_id", "appointment_date", "fee", "status", "updated_at", "is_deleted"]
    raw = strings(spark, columns, [
        ("a1", "p1", "d1", "2026-10-05", " 800 ", "No-show", "2026-10-05 12:00:00", "false"),
        ("A2", "P1", "D1", "2026-13-45", "abc", " Completed ", "2026-10-05 12:00:00", "false"),
        ("A3", "P1", "D1", "2026-10-07", "1500", "no show", "2026-10-05 12:00:00", "false"),
    ])
    rows = {r.appointment_id: r for r in transform.clean_appointments(raw).collect()}

    assert rows["A1"].status == "no_show"
    assert rows["A1"].fee == 800.0
    assert rows["A1"].patient_id == "P1"
    assert rows["A2"].status == "completed"
    assert rows["A2"].fee is None
    assert rows["A2"].appointment_date is None
    assert rows["A3"].status == "no_show"


def test_age_and_age_group(spark):
    df = spark.createDataFrame(
        [("a", date(2015, 4, 2)), ("b", date(2008, 11, 14)), ("c", date(1965, 9, 18)),
         ("d", date(1966, 11, 15)), ("e", None)],
        "id string, dob date",
    )
    rows = {r.id: r for r in transform.add_patient_features(df, as_of="2026-11-14").collect()}

    assert (rows["a"].age, rows["a"].age_group) == (11, "Child")
    assert (rows["b"].age, rows["b"].age_group) == (18, "Adult")    # turns 18 today
    assert (rows["c"].age, rows["c"].age_group) == (61, "Senior")
    assert (rows["d"].age, rows["d"].age_group) == (59, "Adult")    # turns 60 tomorrow
    assert rows["e"].age is None and rows["e"].age_group is None


def _fact_inputs(spark):
    patients = spark.createDataFrame(
        [("P1", "Asha", "Adult", datetime(2026, 11, 1)), ("P2", "Imran", "Senior", datetime(2026, 9, 1))],
        "patient_id string, full_name string, age_group string, updated_at timestamp",
    )
    doctors = spark.createDataFrame(
        [("D1", "Dr. Sharma", "Cardiology", datetime(2026, 9, 1))],
        "doctor_id string, doctor_name string, department string, updated_at timestamp",
    )
    appointments = spark.createDataFrame(
        [
            ("A1", "P1", "D1", date(2026, 10, 5), 800.0, "completed", datetime(2026, 10, 5), False),
            ("A2", "P1", "D1", date(2026, 10, 6), 300.0, "cancelled", datetime(2026, 10, 6), False),
            ("A3", "P2", "D1", date(2026, 10, 7), 2000.0, "completed", datetime(2026, 10, 7), False),
            ("A4", "P2", "D1", date(2026, 10, 8), 500.0, "no_show", datetime(2026, 10, 8), True),
            ("A5", "P9", "D1", date(2026, 10, 9), 500.0, "completed", datetime(2026, 10, 9), False),
        ],
        "appointment_id string, patient_id string, doctor_id string, appointment_date date, fee double, "
        "status string, updated_at timestamp, is_deleted boolean",
    )
    return appointments, patients, doctors


def test_fact_join_and_business_rules(spark):
    fact = transform.build_fact_appointments(*_fact_inputs(spark))
    rows = {r.appointment_id: r for r in fact.collect()}

    assert "A5" not in rows                                     # unknown patient is dropped by the join
    assert rows["A1"].patient_name == "Asha"
    assert rows["A1"].department == "Cardiology"
    assert rows["A1"].appointment_month == "2026-10"
    assert [rows[a].fee_band for a in ("A1", "A2", "A3")] == ["Medium", "Low", "High"]
    assert [rows[a].revenue for a in ("A1", "A2", "A3")] == [800.0, 0.0, 2000.0]  # only completed earns
    assert rows["A1"].updated_at == datetime(2026, 11, 1)       # newer patient change wins
    assert rows["A3"].updated_at == datetime(2026, 10, 7)


def test_doctor_monthly_summary(spark):
    fact = transform.build_fact_appointments(*_fact_inputs(spark))
    summary = transform.build_doctor_monthly_summary(fact).collect()

    assert len(summary) == 1
    row = summary[0]
    # A4 is soft-deleted, so only A1, A2 and A3 are counted
    assert row.total_appointments == 3
    assert (row.completed, row.cancelled, row.no_shows) == (2, 1, 0)
    assert row.total_revenue == 2800.0
    assert row.avg_fee == 1033.33
    assert row.unique_patients == 2
    assert row.cancellation_rate == 0.33
