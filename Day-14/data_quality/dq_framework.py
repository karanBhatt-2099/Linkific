"""A very small data quality framework for PySpark DataFrames.

Usage:
    dq = DataQuality(df)
    dq.not_null("order_id").unique("order_id").in_range("quantity", 1, 100)
    dq.report()
"""
import json
from pyspark.sql import functions as F


class DataQuality:
    def __init__(self, df, name="dataset"):
        self.df = df
        self.name = name
        self.total = df.count()
        self.results = []

    def _add(self, check, column, bad_rows):
        self.results.append({
            "check": check,
            "column": column,
            "failed_rows": bad_rows,
            "status": "PASS" if bad_rows == 0 else "FAIL",
        })
        return self      # lets us chain checks

    # ---- Completeness ----
    def not_null(self, col):
        return self._add("not_null", col, self.df.filter(F.col(col).isNull()).count())

    # ---- Uniqueness ----
    def unique(self, col):
        dupes = self.total - self.df.select(col).distinct().count()
        return self._add("unique", col, dupes)

    # ---- Validity ----
    def in_range(self, col, low, high):
        bad = self.df.filter((F.col(col) < low) | (F.col(col) > high)).count()
        return self._add(f"range[{low},{high}]", col, bad)

    def in_set(self, col, allowed):
        bad = self.df.filter(~F.col(col).isin(allowed)).count()
        return self._add("in_set", col, bad)

    def matches(self, col, regex):
        bad = self.df.filter(~F.col(col).cast("string").rlike(regex)).count()
        return self._add("regex", col, bad)

    # ---- Volume ----
    def min_rows(self, n):
        return self._add(f"min_rows>={n}", "*", 0 if self.total >= n else 1)

    # ---- Report ----
    def report(self, save_to=None):
        print(f"\n=== Data Quality Report: {self.name} ({self.total} rows) ===")
        print(f"{'CHECK':<22}{'COLUMN':<14}{'FAILED':>8}  STATUS")
        for r in self.results:
            print(f"{r['check']:<22}{r['column']:<14}{r['failed_rows']:>8}  {r['status']}")
        passed = sum(r["status"] == "PASS" for r in self.results)
        print(f"Summary: {passed}/{len(self.results)} checks passed")
        if save_to:
            with open(save_to, "w") as f:
                json.dump({"dataset": self.name, "rows": self.total, "results": self.results}, f, indent=2)
            print("Report saved to", save_to)
        return passed == len(self.results)
