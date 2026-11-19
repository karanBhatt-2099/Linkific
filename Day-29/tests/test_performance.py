"""Performance tests for the transform step (the CPU-bound part of the pipeline).

Thresholds are deliberately generous so they catch regressions (e.g. a row-by-row loop)
without being flaky on slow CI machines.
"""
import time

import pytest

from generate_sample_data import generate
from etl.transform import transform_orders


@pytest.mark.parametrize("rows,max_seconds", [(10_000, 2.0), (100_000, 10.0)])
def test_transform_scales(rows, max_seconds):
    raw = generate(rows, 0.02)
    t = time.perf_counter()
    clean, rejects = transform_orders(raw)
    elapsed = time.perf_counter() - t
    print(f"\ntransform {len(raw):,} rows in {elapsed:.2f}s ({len(raw)/elapsed:,.0f} rows/s)")
    assert elapsed < max_seconds
    assert len(clean) + len(rejects) == len(raw)
