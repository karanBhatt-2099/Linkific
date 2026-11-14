import shutil
from pathlib import Path

import pytest

from etl import pipeline
from etl.spark_session import get_spark
from tests.fake_sink import FakeSink

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "source"
AS_OF = "2026-11-14"  # fixed date so ages do not change from day to day


@pytest.fixture(scope="session")
def spark():
    session = get_spark("etl-tests", master="local[1]")
    session.conf.set("spark.sql.shuffle.partitions", "1")
    session.sparkContext.setLogLevel("ERROR")
    yield session
    session.stop()


@pytest.fixture
def workspace(tmp_path):
    """A private copy of the sample source files plus an empty staging folder."""
    source = tmp_path / "source"
    shutil.copytree(SAMPLE_DIR, source)
    return source, tmp_path / "staging"


@pytest.fixture(scope="module")
def pipeline_run(spark, tmp_path_factory):
    """Run the whole pipeline once on the sample data and hand back the results."""
    base = tmp_path_factory.mktemp("run")
    source = base / "source"
    shutil.copytree(SAMPLE_DIR, source)
    sink = FakeSink()
    pipeline.run_pipeline(spark, sink, source, base / "staging", as_of=AS_OF)
    return sink, base / "staging"
