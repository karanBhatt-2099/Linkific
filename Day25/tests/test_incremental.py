"""Unit tests for incremental loading helpers."""
from pyspark.sql import functions as F

from etl import incremental


def timestamps(spark, values):
    df = spark.createDataFrame([(i, v) for i, v in enumerate(values)], "id int, updated_at string")
    return df.withColumn("updated_at", F.to_timestamp("updated_at"))


def test_changed_rows_uses_the_watermark(spark):
    df = timestamps(spark, [
        "2026-11-01 08:00:00",
        "2026-11-02 00:00:00",   # exactly at the watermark: already loaded
        "2026-11-02 10:00:00",
        "2026-11-03 09:00:00",
    ])
    changed = incremental.changed_rows(df, "2026-11-02 00:00:00")
    assert sorted(r.id for r in changed.collect()) == [2, 3]


def test_first_run_takes_everything(spark):
    df = timestamps(spark, ["2026-11-01 08:00:00", "2026-11-02 10:00:00"])
    assert incremental.changed_rows(df, None).count() == 2


def test_max_updated_at(spark):
    df = timestamps(spark, ["2026-11-01 08:00:00", "2026-11-03 09:00:00"])
    assert incremental.max_updated_at(df) == "2026-11-03 09:00:00"
    assert incremental.max_updated_at(df.filter("id > 100")) is None


def test_merge_sql_handles_update_insert_and_delete():
    sql = incremental.build_merge_sql("FACT", "FACT_STG", ["id"], ["id", "name", "fee"])

    assert sql.startswith("MERGE INTO FACT t USING FACT_STG s ON t.id = s.id")
    assert "WHEN MATCHED AND s.is_deleted THEN DELETE" in sql                       # delete handling
    assert "WHEN MATCHED THEN UPDATE SET t.name = s.name, t.fee = s.fee" in sql     # update, key left alone
    assert "t.id = s.id," not in sql
    assert "WHEN NOT MATCHED AND NOT s.is_deleted THEN INSERT (id, name, fee) VALUES (s.id, s.name, s.fee)" in sql


def test_merge_sql_with_composite_key():
    sql = incremental.build_merge_sql("T", "T_STG", ["a", "b"], ["a", "b", "v"])
    assert "ON t.a = s.a AND t.b = s.b" in sql
