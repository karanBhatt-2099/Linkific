"""Day 19 - Sample analysis: screen time before bed vs. sleep quality.
NOTE: the data is SYNTHETIC (generated for practice), not real survey data."""
import numpy as np, pandas as pd
from scipy import stats

# 1. Generate synthetic sample data (n = 60 students)
rng = np.random.default_rng(42)
n = 60
screen = np.round(rng.uniform(0, 4, n), 1)                 # hours of screen time in the hour(s) before bed
sleep = np.clip(np.round(8 - 0.9 * screen + rng.normal(0, 1.3, n), 1), 1, 10)  # sleep quality, 1-10
df = pd.DataFrame({"student_id": range(1, n + 1), "screen_hours": screen, "sleep_quality": sleep})
df.to_csv("sample_data.csv", index=False)

# 2. Descriptive statistics
print("DESCRIPTIVE STATISTICS")
print(df[["screen_hours", "sleep_quality"]].describe().round(2), "\n")

# 3. Hypothesis test 1: Pearson correlation
r, p_r = stats.pearsonr(df.screen_hours, df.sleep_quality)
print(f"CORRELATION: r = {r:.2f}, p = {p_r:.4f}")

# 4. Hypothesis test 2: compare low vs high screen-time groups (split at median)
median = df.screen_hours.median()
low = df[df.screen_hours <= median].sleep_quality
high = df[df.screen_hours > median].sleep_quality
t, p_t = stats.ttest_ind(low, high, equal_var=False)
pooled_sd = np.sqrt((low.var(ddof=1) + high.var(ddof=1)) / 2)
d = (low.mean() - high.mean()) / pooled_sd                  # Cohen's d
print(f"T-TEST: low-screen mean = {low.mean():.2f}, high-screen mean = {high.mean():.2f}")
print(f"        t = {t:.2f}, p = {p_t:.4f}, Cohen's d = {d:.2f}")

# 5. Interpretation
alpha = 0.05
print("\nINTERPRETATION")
print("Reject H0" if p_r < alpha else "Fail to reject H0", f"(alpha = {alpha}).")
print("Effect size:", "small" if abs(d) < 0.5 else "medium" if abs(d) < 0.8 else "large")
