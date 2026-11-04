"""Run all three generators (creates CSV files in ./data)"""
import runpy
for script in ["generate_ecommerce.py", "generate_hr.py", "generate_finance.py"]:
    print(f"\n>> {script}")
    runpy.run_path(script)
print("\nDone. CSV files are in the data/ folder.")
