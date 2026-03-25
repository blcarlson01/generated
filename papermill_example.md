Here’s a clean, copy-pasteable `papermill.md` you can drop into your repo:

---

# Papermill Guide: Parameterizing & Scheduling Jupyter Notebooks

## Overview

This guide shows how to convert an existing Jupyter notebook into a parameterized, schedulable workflow using Papermill.

Papermill allows you to:

* Inject parameters at runtime
* Execute notebooks non-interactively
* Save outputs for debugging and auditing
* Run on a schedule (cron / Task Scheduler)
* Combine with timeouts to prevent runaway jobs

---

## 1. Starting Point

Assume you have a notebook that runs cleanly using **“Run All”**.

Example structure:

### Cell 1

```python
run_date = "2026-03-25"
input_file = "data.csv"
threshold = 0.8
```

### Cell 2

```python
import pandas as pd

df = pd.read_csv(input_file)
```

### Cell 3

```python
filtered = df[df["score"] > threshold]
```

---

## 2. Convert to a Parameterized Notebook

Modify the first cell:

```python
# Parameters
run_date = "2026-03-25"
input_file = "data.csv"
threshold = 0.8
```

### Add Required Tag

In Jupyter:

1. Select the cell
2. Open **Cell Toolbar → Tags**
3. Add the tag:

```
parameters
```

This tells Papermill where to inject runtime values.

---

## 3. Install Papermill

```bash
pip install papermill
```

---

## 4. Running the Notebook with Parameters

Basic usage:

```bash
papermill input.ipynb output.ipynb
```

Override parameters:

```bash
papermill input.ipynb output.ipynb \
  -p run_date 2026-03-26 \
  -p input_file new_data.csv \
  -p threshold 0.9
```

---

## 5. What Papermill Does

Papermill injects a new cell before execution:

```python
run_date = "2026-03-26"
input_file = "new_data.csv"
threshold = 0.9
```

Then executes the notebook top-to-bottom.

---

## 6. Output Notebook

Papermill generates:

```
output.ipynb
```

This file contains:

* Executed cells
* Printed output
* Errors (if any)
* Parameter values used

Useful for:

* Debugging
* Logging
* Reproducibility

---

## 7. Scheduling the Notebook

### macOS / Linux (cron)

Edit crontab:

```bash
crontab -e
```

Example: run daily at 2am

```bash
0 2 * * * papermill /path/input.ipynb /path/output.ipynb
```

---

### Dynamic Parameters (e.g., date)

```bash
0 2 * * * papermill /path/input.ipynb /path/output_$(date +\%F).ipynb \
  -p run_date $(date +\%F)
```

---

## 8. Add a Timeout (Kill Long Runs)

Prevent runaway execution using `timeout`:

```bash
0 2 * * * timeout 2h papermill /path/input.ipynb /path/output.ipynb
```

This will terminate execution after 2 hours.

---

## 9. Best Practices

### 9.1 Keep All Parameters in One Cell

All configurable values should be in the tagged `parameters` cell.

---

### 9.2 Do Not Reassign Parameters Later

Avoid:

```python
threshold = 0.8  # parameters cell

threshold = 0.5  # later cell (overrides runtime input)
```

---

### 9.3 Use Absolute Paths

Scheduled jobs often run in a different working directory.

```python
input_file = "/full/path/to/data.csv"
```

---

### 9.4 Remove Interactive Input

Replace:

```python
value = input("Enter value: ")
```

With:

```python
# Parameters
value = "default"
```

---

### 9.5 Add Logging

```python
print(f"Running for {run_date}")
print(f"Using file: {input_file}")
```

---

## 10. Recommended Template

### Cell 1 (Parameters)

```python
# Parameters
run_date = "2026-03-25"
input_file = "/data/data.csv"
threshold = 0.8
```

### Cell 2 (Setup)

```python
import pandas as pd

print(f"Run date: {run_date}")
```

### Cell 3+ (Logic)

```python
df = pd.read_csv(input_file)
filtered = df[df["score"] > threshold]
```

---

## 11. When to Use Papermill

Use Papermill when you:

* Already have working notebooks
* Want minimal refactoring
* Need scheduled execution
* Want reproducible outputs
* Prefer notebooks over scripts

---

## 12. Summary

| Task                      | Effort    |
| ------------------------- | --------- |
| Add parameters cell       | Very easy |
| Run with Papermill        | Easy      |
| Schedule with cron        | Easy      |
| Add timeout               | Easy      |
| Production-ready pipeline | Moderate  |

Papermill is the fastest path from **interactive notebook → automated job** with minimal code changes.

---

## 13. Next Steps (Optional)

* Add logging to file
* Store outputs in structured folders
* Wrap Papermill in a shell or Python runner script
* Integrate with workflow tools (Airflow, Prefect)

---

If needed, this can be extended into a full “production runner” with:

* retries
* alerting
* structured logs
* parameter configs (YAML/JSON)

---
