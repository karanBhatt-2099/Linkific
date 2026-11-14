"""PySpark transformations: cleaning, type conversion, business logic, joins, aggregation."""
from pyspark.sql import functions as F

TS_FORMAT = "yyyy-MM-dd HH:mm:ss"


# ---------- small helpers ----------
def _blank_to_null(column):
    """Trim text and turn empty strings into null."""
    return F.when(F.trim(column) == "", None).otherwise(F.trim(column))


def _to_bool(name):
    return F.coalesce(F.lower(F.trim(F.col(name))).isin("true", "1", "yes", "y"), F.lit(False))


# ---------- cleaning + type conversion (all raw columns arrive as strings) ----------
def clean_patients(df):
    gender = F.lower(F.trim(F.col("gender")))
    return df.select(
        F.upper(_blank_to_null(F.col("patient_id"))).alias("patient_id"),
        F.initcap(_blank_to_null(F.col("full_name"))).alias("full_name"),
        F.to_date("dob", "yyyy-MM-dd").alias("dob"),
        F.when(gender.isin("m", "male"), "Male")
        .when(gender.isin("f", "female"), "Female")
        .otherwise("Unknown")
        .alias("gender"),
        _blank_to_null(F.regexp_replace(F.col("phone"), r"[^0-9]", "")).alias("phone"),
        F.lower(_blank_to_null(F.col("email"))).alias("email"),
        F.to_timestamp("updated_at", TS_FORMAT).alias("updated_at"),
        _to_bool("is_deleted").alias("is_deleted"),
    )


def clean_doctors(df):
    return df.select(
        F.upper(_blank_to_null(F.col("doctor_id"))).alias("doctor_id"),
        F.initcap(_blank_to_null(F.col("doctor_name"))).alias("doctor_name"),
        F.initcap(_blank_to_null(F.col("department"))).alias("department"),
        F.to_timestamp("updated_at", TS_FORMAT).alias("updated_at"),
        _to_bool("is_deleted").alias("is_deleted"),
    )


def clean_appointments(df):
    # "No-show", "no show" and "NO_SHOW" all become "no_show"
    status = F.regexp_replace(F.lower(F.trim(F.col("status"))), r"[\s-]+", "_")
    return df.select(
        F.upper(_blank_to_null(F.col("appointment_id"))).alias("appointment_id"),
        F.upper(_blank_to_null(F.col("patient_id"))).alias("patient_id"),
        F.upper(_blank_to_null(F.col("doctor_id"))).alias("doctor_id"),
        F.to_date("appointment_date", "yyyy-MM-dd").alias("appointment_date"),
        F.trim(F.col("fee")).cast("double").alias("fee"),
        _blank_to_null(status).alias("status"),
        F.to_timestamp("updated_at", TS_FORMAT).alias("updated_at"),
        _to_bool("is_deleted").alias("is_deleted"),
    )


# ---------- business logic ----------
def add_patient_features(df, as_of=None):
    """Add age and age group. Pass as_of='yyyy-MM-dd' to make the result repeatable in tests."""
    today = F.to_date(F.lit(as_of)) if as_of else F.current_date()
    age = F.floor(F.months_between(today, F.col("dob")) / 12).cast("int")
    return df.withColumn("age", age).withColumn(
        "age_group",
        F.when(F.col("age") < 18, "Child")
        .when(F.col("age") < 60, "Adult")
        .when(F.col("age") >= 60, "Senior"),
    )


def build_fact_appointments(appointments, patients, doctors):
    """Join appointments with patient and doctor details and add fee / revenue logic."""
    p = patients.select(
        "patient_id",
        F.col("full_name").alias("patient_name"),
        F.col("age_group").alias("patient_age_group"),
        F.col("updated_at").alias("patient_updated_at"),
    )
    d = doctors.select(
        "doctor_id",
        "doctor_name",
        "department",
        F.col("updated_at").alias("doctor_updated_at"),
    )

    return (
        appointments.join(p, "patient_id", "inner")
        .join(d, "doctor_id", "inner")
        .withColumn("appointment_month", F.date_format("appointment_date", "yyyy-MM"))
        .withColumn(
            "fee_band",
            F.when(F.col("fee") < 500, "Low").when(F.col("fee") < 1500, "Medium").otherwise("High"),
        )
        # only completed visits earn revenue
        .withColumn("revenue", F.when(F.col("status") == "completed", F.col("fee")).otherwise(F.lit(0.0)))
        # a change to the patient or doctor also counts as a change to the appointment row
        .withColumn(
            "updated_at",
            F.greatest("updated_at", "patient_updated_at", "doctor_updated_at"),
        )
        .select(
            "appointment_id",
            "patient_id",
            "patient_name",
            "patient_age_group",
            "doctor_id",
            "doctor_name",
            "department",
            "appointment_date",
            "appointment_month",
            "status",
            "fee",
            "fee_band",
            "revenue",
            "updated_at",
            "is_deleted",
        )
    )


# ---------- aggregation ----------
def build_doctor_monthly_summary(fact):
    live = fact.filter(~F.col("is_deleted"))

    def count_status(name):
        return F.sum(F.when(F.col("status") == name, 1).otherwise(0))

    return (
        live.groupBy("doctor_id", "doctor_name", "department", "appointment_month")
        .agg(
            F.count("*").alias("total_appointments"),
            count_status("completed").alias("completed"),
            count_status("cancelled").alias("cancelled"),
            count_status("no_show").alias("no_shows"),
            F.sum("revenue").alias("total_revenue"),
            F.round(F.avg("fee"), 2).alias("avg_fee"),
            F.countDistinct("patient_id").alias("unique_patients"),
        )
        .withColumn("cancellation_rate", F.round(F.col("cancelled") / F.col("total_appointments"), 2))
    )
