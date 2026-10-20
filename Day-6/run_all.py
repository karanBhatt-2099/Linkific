"""Run the whole project in order:  python run_all.py"""
import subprocess
import sys

steps = [
    "scripts/00_generate_data.py",
    "scripts/01_merge_examples.py",
    "scripts/03_excel_automation.py",
    "scripts/04_performance_optimization.py",
    "scripts/05_process_large_csv.py",
]
for s in steps:
    print(f"\n>>>>>> Running {s}")
    subprocess.run([sys.executable, s], check=True)

print("\nDone! Open output/sales_report.xlsx and notebooks/02_time_series_analysis.ipynb")
