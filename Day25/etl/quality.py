"""Small data quality framework.

Each check is a function: DataFrame -> DataFrame with one extra boolean column named
"_fail_<check>" that is True for rows that break the rule. run_checks() applies all
checks, then splits the data into good rows and rejected rows (with the reasons listed).
"""
from datetime import date

from pyspark.sql import Window
from pyspark.sql import functions as F

from etl import config
from etl.logger import get_logger

log = get_logger(__name__)

FAIL = "_fail_"

EMAIL_PATTERN = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
PHONE_PATTERN = r"^[0-9]{10}$"
STATUS_PATTERN = r"^(scheduled|completed|cancelled|no_show)$"


class DataQualityError(Exception):
    pass


# ---------- the checks ----------
def not_null(*columns):
    def check(df):
        for c in columns:
            df = df.withColumn(f"{FAIL}null_{c}", F.col(c).isNull())
        return df

    return check


def in_range(column, low, high):
    def check(df):
        outside = ~F.col(column).between(low, high)
        # nulls are not "out of range"; not_null() reports those
        return df.withColumn(f"{FAIL}range_{column}", F.coalesce(outside, F.lit(False)))

    return check


def matches(column, pattern):
    def check(df):
        bad_format = F.col(column).isNotNull() & ~F.col(column).rlike(pattern)
        return df.withColumn(f"{FAIL}format_{column}", bad_format)

    return check


def no_duplicates(key, order_by="updated_at"):
    """Keep the newest row per key; older copies are flagged as duplicates."""

    def check(df):
        newest_first = Window.partitionBy(key).orderBy(F.col(order_by).desc_nulls_last())
        return df.withColumn(f"{FAIL}duplicate_{key}", F.row_number().over(newest_first) > 1)

    return check


def exists_in(column, reference_df, reference_column):
    """Referential integrity: every value must exist in the reference table."""

    def check(df):
        known = reference_df.select(F.col(reference_column).alias(column)).distinct()
        known = known.withColumn("_found", F.lit(True))
        joined = df.join(known, on=column, how="left")
        missing = F.col(column).isNotNull() & F.col("_found").isNull()
        return joined.withColumn(f"{FAIL}missing_{column}", missing).drop("_found")

    return check


# ---------- the runner ----------
def run_checks(df, checks):
    """Return (good_rows, rejected_rows, report) where report maps check name -> failing row count."""
    for check in checks:
        df = check(df)
    df = df.cache()

    fail_columns = [c for c in df.columns if c.startswith(FAIL)]
    reasons = F.concat_ws(",", *[F.when(F.col(c), F.lit(c[len(FAIL):])) for c in fail_columns])
    df = df.withColumn("dq_errors", reasons)

    counts = df.agg(*[F.sum(F.col(c).cast("int")).alias(c[len(FAIL):]) for c in fail_columns]).first()
    report = {name: int(value or 0) for name, value in counts.asDict().items()}

    good = df.filter(F.col("dq_errors") == "").drop("dq_errors", *fail_columns)
    rejected = df.filter(F.col("dq_errors") != "").drop(*fail_columns)
    return good, rejected, report


def enforce_reject_limit(table, total, rejected):
    """Stop the run if a suspiciously large share of the table was rejected."""
    if total and rejected / total > config.MAX_REJECT_RATIO:
        raise DataQualityError(
            f"{table}: {rejected} of {total} rows rejected, limit is {config.MAX_REJECT_RATIO:.0%}"
        )


# ---------- rules per table ----------
def patient_checks():
    return [
        not_null("patient_id", "full_name", "dob", "updated_at"),
        no_duplicates("patient_id"),
        in_range("dob", "1900-01-01", date.today().isoformat()),
        matches("phone", PHONE_PATTERN),
        matches("email", EMAIL_PATTERN),
    ]


def doctor_checks():
    return [
        not_null("doctor_id", "doctor_name", "department", "updated_at"),
        no_duplicates("doctor_id"),
    ]


def appointment_checks(good_patients, good_doctors):
    return [
        not_null("appointment_id", "patient_id", "doctor_id", "appointment_date", "fee", "status", "updated_at"),
        no_duplicates("appointment_id"),
        in_range("fee", 0, 100000),
        matches("status", STATUS_PATTERN),
        exists_in("patient_id", good_patients, "patient_id"),
        exists_in("doctor_id", good_doctors, "doctor_id"),
    ]
