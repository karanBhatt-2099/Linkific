"""Integration test: the real PySpark pipeline against an in-memory Snowflake, over several runs."""
from etl import pipeline
from tests.conftest import AS_OF
from tests.fake_sink import FakeSink


def replace_line(path, starts_with, new_line):
    lines = path.read_text().splitlines()
    index = next(i for i, line in enumerate(lines) if line.startswith(starts_with))
    lines[index] = new_line
    path.write_text("\n".join(lines) + "\n")


def append_line(path, new_line):
    path.write_text(path.read_text() + new_line + "\n")


def facts(sink):
    return {r["appointment_id"]: r for r in sink.rows("FACT_APPOINTMENTS")}


def test_first_load_second_load_and_changes(spark, workspace):
    source, staging = workspace
    sink = FakeSink()

    def run():
        sink.upsert_log.clear()
        pipeline.run_pipeline(spark, sink, source, staging, as_of=AS_OF)

    # ---- run 1: full load ----
    run()
    assert len(sink.rows("DIM_PATIENTS")) == 11
    assert len(sink.rows("DIM_DOCTORS")) == 4
    assert len(facts(sink)) == 13
    assert len(sink.rows("DOCTOR_MONTHLY_SUMMARY")) == 8
    assert sink.watermarks == {
        "DIM_PATIENTS": "2026-11-07 09:00:00",
        "DIM_DOCTORS": "2026-10-01 08:15:00",
        "FACT_APPOINTMENTS": "2026-11-09 12:30:00",
    }
    assert facts(sink)["A002"]["status"] == "completed"
    assert "A003" in facts(sink)

    # ---- run 2: nothing changed, so nothing is loaded ----
    run()
    assert sink.upsert_log == []
    assert len(facts(sink)) == 13

    # ---- run 3: one update, one delete, one insert, one patient change ----
    replace_line(source / "appointments.csv", "A002,", "A002,P002,D01,2026-10-06,800,cancelled,2026-11-12 08:00:00,false")
    replace_line(source / "appointments.csv", "A003,", "A003,P003,D02,2026-10-07,1500,completed,2026-11-12 08:00:00,true")
    append_line(source / "appointments.csv", "A021,P012,D04,2026-11-12,400,completed,2026-11-12 08:00:00,false")
    replace_line(source / "patients.csv", "P004,", "P004,Vikram Singh,2001-11-05,M,9000022222,vikram@mail.com,2026-11-12 08:00:00,false")
    run()

    # only the changed rows were sent: P004, and the facts A002, A003 (delete), A021, A004 (P004's visit)
    assert sorted(sink.upsert_log) == [("DIM_PATIENTS", 1), ("FACT_APPOINTMENTS", 4)]

    fact = facts(sink)
    assert fact["A002"]["status"] == "cancelled"        # updated
    assert fact["A002"]["revenue"] == 0.0
    assert "A003" not in fact                           # deleted
    assert "A021" in fact                               # inserted
    assert len(fact) == 13                              # 13 - 1 deleted + 1 new
    patient = {r["patient_id"]: r for r in sink.rows("DIM_PATIENTS")}
    assert patient["P004"]["phone"] == "9000022222"

    # summary is recomputed from all data: D01 Oct = A001 completed, A002 cancelled, A005 no-show
    summary = {(r["doctor_id"], r["appointment_month"]): r for r in sink.rows("DOCTOR_MONTHLY_SUMMARY")}
    d01 = summary[("D01", "2026-10")]
    assert (d01["completed"], d01["cancelled"], d01["no_shows"]) == (1, 1, 1)
    assert d01["total_revenue"] == 800.0
    assert summary[("D02", "2026-10")]["total_appointments"] == 1   # A003 deleted, only A007 left

    assert sink.watermarks["FACT_APPOINTMENTS"] == "2026-11-12 08:00:00"

    # ---- run 4: the same data again is a no-op ----
    run()
    assert sink.upsert_log == []


def test_rejected_rows_are_kept_for_review(spark, workspace):
    source, staging = workspace
    pipeline.run_pipeline(spark, FakeSink(), source, staging, as_of=AS_OF)

    rejected = spark.read.parquet(str(staging / "rejected" / "appointments"))
    reasons = {r.appointment_id: r.dq_errors for r in rejected.collect()}
    assert reasons == {
        "A001": "duplicate_appointment_id",
        "A013": "range_fee",
        "A014": "null_fee",
        "A015": "missing_patient_id",
        "A016": "missing_doctor_id",
        "A017": "format_status",
        "A018": "null_appointment_date",
    }
