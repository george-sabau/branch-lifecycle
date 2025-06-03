# Git Branch Lifecycle Analysis Tool

This Python script analyzes the lifecycle duration of feature branches merged into a specified base branch (default is `develop`) in a Git repository. It calculates how long branches typically live from creation (merge base) to merge commit.

---

## Usage

Run the script from the command line:

```bash
python branch_lifecycle.py /path/to/your/repo
```

Replace `/path/to/your/repo` with the path to your local Git repository.

---

## Script Overview

- Uses `gitpython` to analyze Git commits and branches.
- Identifies feature branches merged into the base branch.
- Extracts creation and merge times of branches.
- Calculates durations and averages.
- Detects outliers in branch lifecycles using the IQR method.
- Allows configurable outlier inclusion percentage.
- Caches results in `results.json` for faster repeated runs.

---

## Outlier Analysis

The script uses the Interquartile Range (IQR) method:

- Calculates Q1 (25th percentile) and Q3 (75th percentile) of branch durations.
- Computes IQR = Q3 - Q1.
- Defines outliers as branches with durations outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR].
- You can configure what percentage of the top outliers to include in final average calculations.

---

## Running in IPython

You can run the script or import its functions in an IPython shell or notebook:

```python
from branch_lifecycle import get_branch_lifecycle, analyze_and_print_outliers

results = get_branch_lifecycle('/path/to/repo')
duration_tuples = [(r['branch'], r['duration']) for r in results]

analyze_and_print_outliers(duration_tuples, include_outlier_percent=50)
```

---

## File `branch_lifecycle.py` Summary

- `get_branch_lifecycle(repo_path, base_branch='develop', feature_prefixes=None)`: Main function that extracts branch lifecycle info.
- `analyze_and_print_outliers(results, include_outlier_percent=50)`: Analyzes and prints outliers and averages.
- `serialize_results(results, filename)`: Saves results as JSON.
- `deserialize_results(filename)`: Loads results from JSON.

---

## Notes

- Ensure your repo has Git installed and accessible.
- Run the script in an environment with `gitpython` and `numpy` installed.
- Results are cached in `results.json` to avoid repeated heavy calculations.

---

*Feel free to contribute or raise issues for improvements!*
