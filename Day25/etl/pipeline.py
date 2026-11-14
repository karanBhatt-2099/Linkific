"""The four ETL steps. Each step reads the previous step's parquet files from the staging
folder, so Airflow can run them as separate tasks:

    extract -> quality_check -> transform_data -> load_data
"""
from pathlib import Path

from etl import config, incremental, quality, transform
from etl.alerts import send_alert
from etl.logger import get_logger

log = get_logger(__name__)

# stage name -> (Snowflake table, key columns)
TARGETS = {
    "patients": ("DIM_PATIENTS", ["patient_id"]),
    "doctors": ("DIM_DOCTORS", ["doctor_id"]),
    "appointments": ("FACT_APPOINTMENTS", ["appointment_id"]),
}
SUMMARY_TABLE = "DOCTOR_MONTHLY_SUMMARY"


def _path(staging_dir, folder, name):
    return str(Path(staging_dir or config.STAGING_DIR) / folder / name)


def _save(df, staging_dir, folder, name):
    """Write to parquet and return the re-read DataFrame (cuts the lineage between steps)."""
    path = _path(staging_dir, folder, name)
    df.write.mode("overwrite").parquet(path)
    return df.sparkSession.read.parquet(path)


def _read(spark, staging_dir, folder, name):
    return spark.read.parquet(_path(staging_dir, folder, name))


# ---------- 1. extract + clean ----------
def extract(spark, source_dir=None, staging_dir=None):
    source_dir = Path(source_dir or config.SOURCE_DIR)
    cleaners = {
        "patients": transform.clean_patients,
        "doctors": transform.clean_doctors,
        "appointments": transform.clean_appointments,
    }
    for name, clean in cleaners.items():
        raw = spark.read.option("header", True).csv(str(source_dir / f"{name}.csv"))
        cleaned = _save(clean(raw), staging_dir, "clean", name)
        log.info("Extracted %s: %d rows", name, cleaned.count())


# ---------- 2. data quality ----------
def _check_table(name, df, checks, staging_dir):
    good, rejected, report = quality.run_checks(df, checks)
    good = _save(good, staging_dir, "good", name)
    rejected = _save(rejected, staging_dir, "rejected", name)

    total, n_rejected = good.count() + rejected.count(), rejected.count()
    log.info("Quality %s: %d rows, %d rejected, failed checks %s",
             name, total, n_rejected, {k: v for k, v in report.items() if v})
    quality.enforce_reject_limit(name, total, n_rejected)
    return good


def quality_check(spark, staging_dir=None):
    clean = {name: _read(spark, staging_dir, "clean", name) for name in TARGETS}
    # patients and doctors first: appointments are checked against the rows that passed
    good_patients = _check_table("patients", clean["patients"], quality.patient_checks(), staging_dir)
    good_doctors = _check_table("doctors", clean["doctors"], quality.doctor_checks(), staging_dir)
    _check_table(
        "appointments",
        clean["appointments"],
        quality.appointment_checks(good_patients, good_doctors),
        staging_dir,
    )


# ---------- 3. transform + pick the changed rows ----------
def transform_data(spark, sink, staging_dir=None, as_of=None):
    patients = transform.add_patient_features(_read(spark, staging_dir, "good", "patients"), as_of)
    doctors = _read(spark, staging_dir, "good", "doctors")
    appointments = _read(spark, staging_dir, "good", "appointments")

    fact = transform.build_fact_appointments(appointments, patients, doctors)
    summary = transform.build_doctor_monthly_summary(fact)

    for name, df in {"patients": patients, "doctors": doctors, "appointments": fact}.items():
        table = TARGETS[name][0]
        changed = incremental.changed_rows(df, sink.get_watermark(table))
        changed = _save(changed, staging_dir, "out", name)
        log.info("Changed rows for %s: %d", table, changed.count())

    _save(summary, staging_dir, "out", "summary")


# ---------- 4. load ----------
def load_data(spark, sink, staging_dir=None):
    sink.replace(_read(spark, staging_dir, "out", "summary"), SUMMARY_TABLE)

    for name, (table, keys) in TARGETS.items():
        changed = _read(spark, staging_dir, "out", name)
        if changed.count() == 0:
            log.info("No changes for %s", table)
            continue
        sink.upsert(changed, table, keys)
        # The watermark moves only after the MERGE succeeded. If the load fails, the next
        # run picks up the same rows again, and MERGE makes that safe to repeat.
        sink.set_watermark(table, incremental.max_updated_at(changed))


# ---------- run everything (used locally and by the tests) ----------
def run_pipeline(spark, sink, source_dir=None, staging_dir=None, as_of=None):
    try:
        extract(spark, source_dir, staging_dir)
        quality_check(spark, staging_dir)
        transform_data(spark, sink, staging_dir, as_of)
        load_data(spark, sink, staging_dir)
        log.info("Pipeline finished")
    except Exception as exc:
        log.exception("Pipeline failed")
        send_alert("Hospital ETL failed", f"{type(exc).__name__}: {exc}")
        raise


if __name__ == "__main__":
    from etl.snowflake_io import SnowflakeSink
    from etl.spark_session import get_spark

    run_pipeline(get_spark(with_snowflake=True), SnowflakeSink())
