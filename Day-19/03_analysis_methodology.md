# Analysis Methodology

1. **Clean data:** remove incomplete or impossible values (e.g. screen time > 24h).
2. **Descriptive statistics:** mean, median, standard deviation, min/max for both variables.
3. **Pearson correlation (r):** direction and strength of the relationship.
4. **Group comparison:** split students at the median screen time (low vs high), run Welch's independent t-test on sleep quality.
5. **Statistical significance:** α = 0.05. If p < 0.05, reject H0.
6. **Effect size:** Cohen's d (0.2 small, 0.5 medium, 0.8 large). Significance tells us *whether* there is an effect; effect size tells us *how big*.
7. **Interpretation:** report results in plain language and state limitations (self-report, no causation).

**Tools:** Python (pandas, scipy). See `sample_analysis.py`.
