# Day 9 - Advanced SQL

JOINs, aggregations, window functions, subqueries/CTEs, and query optimization on a
small e-commerce dataset (SQLite). **50 analytic queries + 10 optimization experiments**,
all executed and verified.

## Quick start

```bash
python scripts/build_db.py          # builds data/sales.db (deterministic, seed=42)
python scripts/run_all.py           # runs Q01-Q50 -> output/query_results.md   (50/50 pass)
python scripts/optimization_demo.py # before/after plans + timings -> output/optimization_report.md
# or interactively:
sqlite3 data/sales.db ".read queries/03_window_functions.sql"
```

Requires Python 3 with the standard library only. SQLite >= 3.39 is needed for `RIGHT`/`FULL OUTER JOIN`
(tested on 3.45). The data (`data/01_schema.sql` + `data/02_seed.sql`) is plain SQL and loads into PostgreSQL/MySQL with minor syntax changes.

## Project layout

```
day9_advanced_sql/
├── README.md
├── data/
│   ├── 01_schema.sql        7 tables (regions, employees, customers, categories, products, orders, order_items)
│   ├── 02_seed.sql          portable INSERT statements
│   └── sales.db             ready-to-query SQLite database
├── queries/
│   ├── 01_joins.sql                Q01-Q10   all JOIN types
│   ├── 02_aggregations.sql         Q11-Q18   GROUP BY, HAVING, DISTINCT, ROLLUP/CUBE
│   ├── 03_window_functions.sql     Q19-Q28   ranking, running totals, LAG/LEAD, moving avg
│   ├── 04_subqueries_ctes.sql      Q29-Q41   subqueries, correlated, CTEs, recursive CTEs
│   ├── 05_sales_analysis.sql       Q42-Q50   multi-table + time-based business analysis
│   ├── 06_optimization.sql         OPT1-OPT10 reference (indexes + rewrites)
│   └── 07_native_rollup_cube_postgres.sql  native ROLLUP/CUBE/GROUPING SETS (NOT executed, see below)
├── scripts/                 build_db.py, run_all.py, optimization_demo.py
└── output/                  query_results.md, optimization_report.md
```

## The dataset

| Table | Rows | Notes |
|---|---:|---|
| orders | 500 | Jan 2024 - Dec 2025; status: completed / cancelled / returned |
| order_items | 1,242 | quantity, unit_price, discount |
| customers | 60 | `referred_by` self-reference; **customers 56-60 never ordered** (for anti-joins) |
| products | 18 | **product 18 never sells** (for RIGHT/anti-joins) |
| categories | 9 | 3-level hierarchy via `parent_id` (recursive CTE) |
| employees | 11 | `manager_id` self-reference (org chart) |
| regions | 4 | North, South, East, West |

Revenue everywhere = `quantity * unit_price * (1 - discount)`, usually restricted to `status = 'completed'`.
The data is synthetic and random, so business "insights" (e.g. the late-2025 decline in Q25) reflect how it was generated, not real trends.

## Coverage map (task -> queries)

| Task | Queries |
|---|---|
| INNER JOIN | Q01 |
| LEFT / RIGHT / FULL OUTER JOIN | Q02, Q03 (anti-join), Q04, Q05 |
| CROSS JOIN | Q06 (region x category grid), Q37 |
| Self joins | Q07 (manager), Q08 (referrals), Q09 (product pairs), Q47 (basket) |
| Multiple table joins | Q10 (7 tables), Q43, Q50 |
| GROUP BY / HAVING | Q11, Q12, Q16 |
| Multiple aggregations / COUNT DISTINCT | Q13, Q14, Q15 |
| ROLLUP and CUBE | Q17, Q18 (emulated), file 07 (native) |
| ROW_NUMBER / RANK / DENSE_RANK | Q19, Q20, Q43, Q45, Q50 |
| PARTITION BY | Q20, Q23, Q26, Q28 |
| Running totals | Q22, Q23, Q48 |
| LAG / LEAD | Q24, Q25, Q26 |
| Moving averages | Q27 |
| Subqueries WHERE / SELECT / FROM | Q29-Q30, Q31, Q32 |
| Correlated subqueries | Q33, Q34, Q35 |
| CTEs, multiple CTEs | Q36, Q37 (+ most later queries) |
| Recursive CTEs | Q38 (org chart), Q39 (category tree), Q40 (date spine), Q41 (referral depth) |
| Sales analysis / time-based | Q22-Q25, Q42-Q49 |
| Optimization | OPT1-OPT10 |

## SQL patterns cheat sheet

### JOINs
| Need | Pattern |
|---|---|
| Only matching rows | `A INNER JOIN B ON ...` |
| Keep all of A | `A LEFT JOIN B ON ...` |
| "A with no B" (anti-join) | `A LEFT JOIN B ON ... WHERE B.id IS NULL`  (or `NOT EXISTS`) |
| Every combination | `A CROSS JOIN B` (grids, date spines) |
| Hierarchy / pairs | self join with aliases; `a.id < b.id` to avoid duplicate pairs |

**Gotcha:** put filters on the *right* table of a LEFT JOIN in the `ON` clause, not `WHERE`, or you silently turn it into an INNER JOIN.

### Aggregation
- `WHERE` filters rows *before* grouping; `HAVING` filters groups *after*.
- Conditional aggregates: `COUNT(*) FILTER (WHERE ...)` or `SUM(CASE WHEN ... THEN 1 ELSE 0 END)`.
- `COUNT(DISTINCT x)` after a join counts unique values; plain `COUNT(*)` counts the fan-out.
- ROLLUP = hierarchical subtotals; CUBE = all combinations. Emulate with `UNION ALL` of grouping levels.

### Window functions
```sql
fn() OVER (PARTITION BY group_col ORDER BY sort_col ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)
```
| Goal | Pattern |
|---|---|
| Top-N per group | `ROW_NUMBER() OVER (PARTITION BY g ORDER BY m DESC)` then filter `rn <= N` in an outer query |
| Ties | `ROW_NUMBER` unique; `RANK` ties + gaps; `DENSE_RANK` ties, no gaps |
| Share of total | `x / SUM(x) OVER ()` |
| Running total | `SUM(x) OVER (ORDER BY t)`; add `PARTITION BY` to reset per group |
| Period-over-period | `x - LAG(x[, n]) OVER (ORDER BY t)` |
| Next event | `LEAD(date) OVER (PARTITION BY customer ORDER BY date)` |
| Moving average | `AVG(x) OVER (ORDER BY t ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)` |
| Buckets | `NTILE(4) OVER (ORDER BY x)` |

**Gotchas:** window functions can't appear in `WHERE`, so wrap in a CTE/subquery. With `ORDER BY` and no frame, the default frame is `RANGE UNBOUNDED PRECEDING` (ties are included together), which matters for running totals; use `ROWS` for row-exact behavior.

### Subqueries and CTEs
- Scalar subquery in `SELECT` / `WHERE`: one value. `IN`: set membership. `EXISTS`: any match (use `NOT EXISTS`, not `NOT IN`, which breaks on NULLs).
- Correlated subquery references the outer row and re-runs per row; fine for small data, consider a window function or join at scale.
- CTEs (`WITH a AS (...), b AS (...)`) name steps so queries read top to bottom; chain them instead of nesting.
- Recursive CTE = anchor + `UNION ALL` + recursive member joining back to the CTE: org charts, trees, date generation. Always make sure it terminates.

### Optimization checklist
1. Read the plan first (`EXPLAIN QUERY PLAN` here, `EXPLAIN (ANALYZE)` in PostgreSQL). Look for `SCAN` on big tables.
2. Index join keys and frequent filters; composite index = equality columns first, then range/sort column.
3. Keep predicates SARGable: `date >= X AND date < Y`, not `strftime('%Y', date) = '2025'`.
4. Aggregate before joining when the join multiplies rows.
5. `EXISTS` over `IN`/`DISTINCT` joins for existence checks; `UNION ALL` over `UNION` when duplicates are OK.
6. Keyset pagination (`WHERE id > :last`) over big `OFFSET`s.
7. Select only the columns you need (enables covering indexes).
8. **Measure.** See the OPT5 result below.

## Optimization results

From `scripts/optimization_demo.py` on a ~40k-order benchmark copy (best of 3; timings vary by machine, ratios are what matter; the report has the full plans):

| Experiment | Speed-up |
|---|---:|
| OPT1 index on filter column | ~50x |
| OPT2 composite index (filter + sort) | ~7x |
| OPT3 covering index | ~1.4x |
| OPT4 SARGable date range | ~15x |
| **OPT5 correlated subquery vs window function** | **~0.5x (window was *slower*)** |
| OPT6 aggregate before join | ~1.3x |
| OPT7 UNION -> UNION ALL | ~1.2x |
| OPT8 OFFSET -> keyset | ~20x |
| OPT9 IN -> EXISTS (with index) | ~34x |
| OPT10 WHERE instead of HAVING | ~1.2x |

Every pair returns identical results (checked in the script). Two honest notes:

- **OPT5 is a trade-off, not a win.** With an index on `(customer_id, order_date)`, SQLite resolves each correlated `MAX()` with one index seek, which beat the window function's full sort. Without that index the correlated form is O(n^2) and loses badly. "Window functions are always faster" is a myth; check the plan.
- OPT3, 6, 7, 10 show small gains at this size; the effect grows with data volume.

## Known limitations

- SQLite has no native `ROLLUP`/`CUBE`; Q17/Q18 emulate them. `queries/07_native_rollup_cube_postgres.sql` has the standard-SQL versions, **which I did not execute** (no PostgreSQL available in this environment).
- Date functions (`strftime`, `julianday`, `date(x, '+1 month')`) are SQLite-specific; in PostgreSQL use `to_char`, `EXTRACT`, `date_trunc`, and interval arithmetic.
- Row counts in the optimization benchmark are modest; absolute timings will differ on real databases.
