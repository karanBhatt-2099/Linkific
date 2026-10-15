# NumPy Day Task

## Folder contents
```
numpy_day_task/
├── numpy_operations.ipynb   # 60+ numbered examples, already executed with outputs
└── README.md                # this file: NumPy patterns cheat sheet
```

## How to run
```bash
pip install numpy matplotlib jupyter
jupyter notebook numpy_operations.ipynb
```
Run the cells top to bottom (Kernel -> Restart & Run All).

## Notebook outline
| Part | Topics | Examples |
|---|---|---|
| 1. Fundamentals | zeros/ones/arange/linspace, indexing, slicing, reshape, broadcasting | 1-15 |
| 2. Array operations | element-wise ops, math, mean/median/std/percentile, sort, search, unique | 16-30 |
| 3. Boolean indexing | masks, conditions, `np.where`, fancy indexing | 31-39 |
| 4. Performance | loops vs vectorization, memory, dtypes, views vs copies, chart | 40-45 |
| 5. Projects | statistical analysis, cleaning pipeline, benchmarks, 10M-row dataset | 46-62 |

## Results from my run (1M elements, your numbers will vary)
| Task | Python loop | NumPy | Speedup |
|---|---|---|---|
| Sum of squares | 0.058 s | 0.0018 s | ~32x |
| Add two arrays | 0.051 s | 0.0012 s | ~44x |
| Mean and std | 0.148 s | 0.0024 s | ~62x |
| 200x200 matrix multiply | 0.587 s | 0.0004 s | ~1400x |

Memory for 1M integers: Python list ~36 MB vs NumPy array 8 MB.

## NumPy patterns cheat sheet

### Create
```python
np.array([1, 2, 3])
np.zeros((2, 3));  np.ones(5);  np.full((2, 2), 7);  np.eye(3)
np.arange(0, 10, 2)          # stop excluded
np.linspace(0, 1, 5)         # stop included
rng = np.random.default_rng(42); rng.random(3); rng.integers(1, 10, 5)
```

### Index, slice, reshape
```python
a[1:4]   a[::-1]   m[1, 2]   m[:, 0]   m[0:2, 1:3]
a.reshape(3, -1)   a.T   a.flatten()   a[:, np.newaxis]
```

### Broadcasting rule
Compare shapes from the right. Dimensions are compatible if equal or one is 1.
```python
matrix + row_vector      # (2,3) + (3,)   -> (2,3)
col + row                # (3,1) + (1,3) -> (3,3)
```

### Statistics
```python
a.mean()  np.median(a)  a.std()  a.var()  np.percentile(a, [25, 50, 75])
m.mean(axis=0)   # per column
m.sum(axis=1)    # per row
np.corrcoef(x, y)
```

### Sort, search, unique
```python
np.sort(a)   np.argsort(a)   a.argmax()   np.searchsorted(sorted_a, v)
vals, counts = np.unique(a, return_counts=True)
```

### Filter
```python
a[a > 5]
a[(a > 1) & (a < 9)]         # & | ~ with parentheses
np.where(a > 5, "high", "low")
a[[0, 2, 4]]                 # fancy indexing
people[people[:, 1] > 55000] # filter rows by a column
```

### Cleaning data
```python
data = data[data[:, 0] > 0]                              # drop invalid rows
data = np.where(np.isnan(data), np.nanmean(data, axis=0), data)   # fill NaN
scaled = (data - data.min(0)) / (data.max(0) - data.min(0))       # min-max
z = (data - data.mean(0)) / data.std(0)                           # z-score
```
