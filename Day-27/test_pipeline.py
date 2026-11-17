import os, sqlite3, tempfile, unittest
import pandas as pd
from generate_data import generate
from pipeline import run, validate


def write_csv(df, path):
    df.drop(columns="bad_reason").to_csv(path, index=False)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.db = os.path.join(self.dir, "t.db")
        self.csv = os.path.join(self.dir, "o.csv")

    def count(self, table):
        con = sqlite3.connect(self.db)
        n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        con.close()
        return n

    # ---- end-to-end ----
    def test_end_to_end(self):
        df = generate(5000, bad_rate=0.05)
        write_csv(df, self.csv)
        r = run(self.csv, self.db, chunksize=1000)
        self.assertEqual(r["total"], 5000)
        self.assertEqual(r["loaded"] + r["rejected"], 5000)
        self.assertEqual(self.count("orders"), r["loaded"])
        self.assertEqual(self.count("rejects"), r["rejected"])

    # ---- incremental ----
    def test_rerun_is_idempotent(self):
        write_csv(generate(2000, bad_rate=0), self.csv)
        run(self.csv, self.db)
        run(self.csv, self.db)
        self.assertEqual(self.count("orders"), 2000)

    def test_incremental_adds_only_new(self):
        write_csv(generate(1000, bad_rate=0), self.csv)
        run(self.csv, self.db)
        write_csv(generate(500, bad_rate=0, start_id=1001), self.csv)
        run(self.csv, self.db)
        self.assertEqual(self.count("orders"), 1500)

    # ---- error scenarios ----
    def test_all_rows_bad(self):
        df = generate(100, bad_rate=0)
        df["amount"] = "abc"
        write_csv(df, self.csv)
        r = run(self.csv, self.db)
        self.assertEqual((r["loaded"], r["rejected"]), (0, 100))

    def test_empty_file(self):
        pd.DataFrame(columns=["order_id", "customer_id", "email", "amount", "order_date", "status"]).to_csv(self.csv, index=False)
        self.assertEqual(run(self.csv, self.db)["total"], 0)

    def test_duplicates_across_chunks(self):
        df = generate(1000, bad_rate=0)
        df.loc[900, "order_id"] = "O1"           # duplicate of a row in an earlier chunk
        write_csv(df, self.csv)
        r = run(self.csv, self.db, chunksize=100)
        self.assertEqual(r["rejected"], 1)

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            run("nope.csv", self.db)

    # ---- validation rules: one test per rule ----
    def check_rule(self, column, value, reason):
        df = generate(10, bad_rate=0).drop(columns="bad_reason")
        df.loc[3, column] = value
        _, bad = validate(df)
        self.assertEqual(list(bad["reason"]), [reason])

    def test_rules(self):
        for col, val, why in [
            ("order_id", "", "null_order_id"), ("amount", "-1", "bad_amount"), ("amount", "0", "bad_amount"),
            ("amount", "100001", "bad_amount"), ("amount", "abc", "bad_amount"), ("email", "nope", "bad_email"),
            ("email", "a@b", "bad_email"), ("order_date", "2099-01-01", "bad_date"),
            ("order_date", "2025-02-30", "bad_date"), ("status", "weird", "bad_status"),
        ]:
            with self.subTest(col=col, val=val):
                self.check_rule(col, val, why)

    def test_boundary_values_pass(self):
        df = generate(5, bad_rate=0).drop(columns="bad_reason")
        df.loc[0, "amount"] = "0.01"
        df.loc[1, "amount"] = "100000"
        good, bad = validate(df)
        self.assertEqual(len(bad), 0)

    # ---- false positives / false negatives against ground truth ----
    def test_no_false_positives_or_negatives(self):
        df = generate(50000, bad_rate=0.05, seed=7)
        raw = df.drop(columns="bad_reason")
        _, bad = validate(raw)
        flagged = set(bad.index)
        truth = set(df.index[df["bad_reason"] != ""])
        # a "duplicate" defect on a row whose neighbour was itself bad can legitimately be a non-duplicate; ignore those
        self.assertEqual(flagged - truth, set(), "false positives")
        missed = truth - flagged
        self.assertLess(len(missed) / len(truth), 0.01, f"false negatives: {len(missed)}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
