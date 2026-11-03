# Day 19: Research Methods Practice Project

**Research question:** Is more screen time before bed associated with lower sleep quality in college students?

## Research Framework
```
Identify problem -> Literature review -> Research question -> Hypotheses -> Methodology
      -> Data collection -> Analysis -> Interpretation -> Documentation
```

## Files
| File | Purpose |
|---|---|
| `01_research_proposal.md` | Problem, research question, hypotheses, methodology summary, limitations |
| `02_data_collection_plan.md` | Sampling, survey questions, ethics |
| `03_analysis_methodology.md` | Statistical steps and tests |
| `sample_analysis.py` | Generates synthetic data and runs the analysis |
| `sample_data.csv` | Synthetic data (60 students) |
| `results.txt` | Output of the analysis |

## Run it
```bash
pip install pandas numpy scipy
python sample_analysis.py
```

## Sample Results (synthetic data)
- Mean screen time: 2.08 h; mean sleep quality: 5.86 / 10
- Correlation: **r = -0.73**, p < 0.001 (strong negative relationship)
- Low-screen group mean: 6.80 vs high-screen group: 4.93 (t = 6.78, p < 0.001)
- Effect size: **Cohen's d = 1.75** (large)
- **Conclusion:** Reject H0 in this sample.

## Limitations
- The data is **synthetic**, built for practice. It is not a real finding.
- Real data would be self-reported and correlational, so it could not prove causation.
- Convenience sampling limits generalisation.
