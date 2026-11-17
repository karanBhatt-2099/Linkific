# Day 27: Testing & Optimization Report

## Files
| File | Purpose |
|---|---|
| `generate_data.py` | Synthetic orders with labelled bad rows (any volume) |
| `pipeline.py` | Optimized pipeline: CSV → validate → SQLite (`orders`, `rejects`) |
| `test_pipeline.py` | 10 tests: end-to-end, incremental, error, rules, false +/- |
| `perf_test.py` | Baseline vs optimized, index and parallel experiments |
| `orders.csv`, `orders_truth.csv` | Sample 10k-row test data and its ground truth |

Run: `python generate_data.py 10000 && python test_pipeline.py && python perf_test.py`

## Test data scenarios
Normal rows plus 5% injected defects: null/duplicate order_id, negative/zero/non-numeric/huge amounts,
malformed emails, impossible/future/blank dates, unknown status. Volumes: 10k, 100k, 1M rows.

## Test results (10/10 pass)
| Area | Test | Result |
|---|---|---|
| End-to-end | loaded + rejected = total; DB counts match | Pass |
| Incremental | re-run same file adds nothing; new file adds only new rows | Pass |
| Error scenarios | all rows bad, empty file, duplicates across chunks, missing file | Pass |
| Validation rules | each of 6 rules tested incl. boundaries (0.01, 100000, 100001) | Pass |
| False positives | 50k rows vs ground truth: 0 good rows wrongly rejected | Pass |
| False negatives | < 1% of injected defects missed (limit set in test) | Pass |

## Performance
| Rows | Baseline | Optimized | Throughput |
|---|---|---|---|
| 10,000 | 6.46 s | 0.08 s | 132,798 rows/s |
| 100,000 | 59.82 s | 0.88 s | 114,131 rows/s |
| 1,000,000 | not run (~10 min est.) | 9.76 s | 102,487 rows/s |

Query `WHERE order_date = ...` on 1M rows: **4.6 ms with index vs 83.5 ms without** (about 18x).

## Bottlenecks found and fixes
1. **Per-row `commit`** in baseline was the main cost → one `executemany` + one commit per chunk.
2. **Python row loop validation** → vectorized pandas checks.
3. **No primary key** → `order_id PRIMARY KEY` + `INSERT OR REPLACE` makes loads idempotent.
4. **Full scans on date filters** → index on `order_date`.
5. **Memory** → read in 100k-row chunks.

Result: ~70x faster at 100k rows (59.8 s → 0.88 s).

## Parallel processing
Validating 1M rows: serial 1.93 s vs 4 processes 3.80 s. **Parallel was slower**: copying chunks
between processes costs more than the vectorized validation itself. Not adopted. Revisit only if
validation becomes much heavier.

## Known issues
- A one-off duplicate check only sees ids loaded in the current run (`seen` set is in memory); a
  later file re-using an old id will overwrite that row (upsert) instead of being rejected.
- The `seen` set grows with the file (memory at very large volumes).
- Throughput drops slightly at 1M rows (~102k vs ~133k rows/s) due to larger SQLite index and `seen` set.
- Baseline not run at 1M rows because it would take about 10 minutes.
- "Future date" check uses today's date, so tests depending on it are time-sensitive only for dates near today.
