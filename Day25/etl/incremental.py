"""Incremental loading helpers.

Change data capture (CDC) here is timestamp based: a row is "changed" when its
updated_at is newer than the watermark saved after the last successful load.
Deletes arrive as rows with is_deleted = true (soft deletes) and are applied by MERGE.
"""
from pyspark.sql import functions as F

TS_FORMAT = "yyyy-MM-dd HH:mm:ss"


def changed_rows(df, last_watermark):
    """Rows newer than the watermark. No watermark yet means first run: take everything."""
    if last_watermark is None:
        return df
    return df.filter(F.col("updated_at") > F.lit(last_watermark).cast("timestamp"))


def max_updated_at(df):
    """Highest updated_at as a 'yyyy-MM-dd HH:mm:ss' string (the next watermark), or None if empty."""
    return df.agg(F.date_format(F.max("updated_at"), TS_FORMAT)).first()[0]


def build_merge_sql(target, staging, keys, columns):
    """Snowflake upsert: update changed rows, insert new rows, delete rows flagged is_deleted.

    `columns` are the target columns (without is_deleted). The staging table must have is_deleted.
    """
    join_on = " AND ".join(f"t.{k} = s.{k}" for k in keys)
    set_clause = ", ".join(f"t.{c} = s.{c}" for c in columns if c not in keys)
    column_list = ", ".join(columns)
    value_list = ", ".join(f"s.{c}" for c in columns)
    return (
        f"MERGE INTO {target} t USING {staging} s ON {join_on} "
        f"WHEN MATCHED AND s.is_deleted THEN DELETE "
        f"WHEN MATCHED THEN UPDATE SET {set_clause} "
        f"WHEN NOT MATCHED AND NOT s.is_deleted THEN INSERT ({column_list}) VALUES ({value_list})"
    )
