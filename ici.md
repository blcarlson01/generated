For a production system, I would actually split this into **three repositories/services**:

```text
benchmark-platform/
├── benchmark-runner/      # Inspect-AI execution
├── capability-engine/     # ICI computation
└── benchmark-ui/          # Dashboard
```

The code below focuses on the **capability-engine**, which computes:

```text
Metric Scores
      ↓
Metric Calibration
      ↓
Metric Factor Models
      ↓
Benchmark Scores
      ↓
Domain Scores
      ↓
Global ICI
```

---

# README.md

# Internal Capability Index (ICI)

A hierarchical capability scoring system inspired by Epoch AI's ECI methodology but extended for enterprise benchmark platforms containing:

* Hundreds of benchmarks
* Multiple benchmark domains
* Multiple metrics per benchmark
* Missing benchmark observations
* New models added over time
* New benchmarks added over time

The goal is to estimate latent model capability rather than averaging benchmark scores.

---

# Architecture

```text
Raw Metrics
     ↓
Metric Normalization
     ↓
Metric Factor Analysis
     ↓
Benchmark Latent Scores
     ↓
Domain Latent Scores
     ↓
Global Capability Score (ICI)
```

Example:

Translation Benchmark

BLEU
COMET
BLEURT
LLM Judge
Human Rating

becomes

Translation Capability

rather than counting each metric independently.

---

# Data Model

Every observation is stored independently.

```sql
model_id
benchmark_id
domain_id
metric_name
score
timestamp
```

Example:

GPT5
wmt24
translation
comet
0.91

GPT5
wmt24
translation
bleu
43.1

````

Never store only aggregated scores.

---

# Computation Pipeline

## Stage 1: Metric Normalization

Each metric is converted into a percentile score.

Output:

```text
0.0 → 1.0
````

This avoids issues with different metric scales.

---

## Stage 2: Metric Factor Models

Metrics inside a benchmark are reduced into latent benchmark dimensions.

Example:

BLEU
COMET
BLEURT
Judge

becomes:

Translation Quality

using factor analysis.

---

## Stage 3: Benchmark IRT

Estimate:

* benchmark difficulty
* benchmark discrimination
* model benchmark capability

using Bayesian IRT.

Output:

Benchmark latent scores.

---

## Stage 4: Domain Aggregation

Benchmark scores within domains are combined.

Domains:

* translation
* coding
* reasoning
* agents
* safety
* multimodal

Output:

Domain capability estimates.

---

## Stage 5: Global ICI

Domain scores become inputs into a second-level latent model.

Output:

Single Internal Capability Index.

---

# Incremental Updates

New benchmarks:

1. Run benchmark on anchor models.
2. Estimate benchmark parameters.
3. Add benchmark into production.

New models:

1. Run subset of anchor benchmarks.
2. Infer capability using overlap.

No need to rerun all historical benchmarks.

---

# Recommended Stack

Python

Libraries:

* pandas
* numpy
* scipy
* scikit-learn
* pymc
* arviz
* sqlalchemy

Storage:

* PostgreSQL

Visualization:

* Grafana
* Superset
* Streamlit

Benchmark Execution:

* Inspect-AI

---

# Output Tables

model_capability

```text
model_id
ici_score
updated_at
```

domain_capability

```text
model_id
domain
score
updated_at
```

benchmark_capability

```text
model_id
benchmark
score
updated_at
```

This enables leaderboard generation at all hierarchy levels.

# Python Implementation Skeleton

## data_models.py

```python
from dataclasses import dataclass

@dataclass
class BenchmarkObservation:
    model_id: str
    benchmark_id: str
    domain_id: str
    metric_name: str
    score: float
```

---

## normalize.py

```python
import pandas as pd

def percentile_normalize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts all metrics to percentile ranks.
    """

    result = df.copy()

    result["normalized_score"] = (
        result.groupby("metric_name")["score"]
        .rank(pct=True)
    )

    return result
```

---

## benchmark_factor_model.py

```python
import pandas as pd
from sklearn.decomposition import FactorAnalysis

class BenchmarkFactorModel:

    def fit_transform(self, benchmark_df: pd.DataFrame):

        matrix = benchmark_df.pivot_table(
            index="model_id",
            columns="metric_name",
            values="normalized_score"
        )

        matrix = matrix.fillna(matrix.mean())

        fa = FactorAnalysis(
            n_components=1,
            random_state=42
        )

        latent = fa.fit_transform(matrix)

        scores = pd.DataFrame({
            "model_id": matrix.index,
            "benchmark_score": latent[:, 0]
        })

        return scores
```

---

## domain_aggregation.py

```python
import pandas as pd

def aggregate_domains(
    benchmark_scores: pd.DataFrame,
    benchmark_metadata: pd.DataFrame
):

    merged = benchmark_scores.merge(
        benchmark_metadata,
        on="benchmark_id"
    )

    domain_scores = (
        merged.groupby(
            ["model_id", "domain_id"]
        )["benchmark_score"]
        .mean()
        .reset_index()
    )

    return domain_scores
```

---

## hierarchical_irt.py

This is where the real value exists.

```python
import pymc as pm
import numpy as np

class HierarchicalICI:

    def fit(
        self,
        score_matrix,
    ):

        n_models = score_matrix.shape[0]
        n_domains = score_matrix.shape[1]

        with pm.Model():

            capability = pm.Normal(
                "capability",
                mu=0,
                sigma=1,
                shape=n_models
            )

            difficulty = pm.Normal(
                "difficulty",
                mu=0,
                sigma=1,
                shape=n_domains
            )

            discrimination = pm.HalfNormal(
                "discrimination",
                sigma=1,
                shape=n_domains
            )

            mu = (
                discrimination
                * (
                    capability[:, None]
                    - difficulty
                )
            )

            pm.Normal(
                "obs",
                mu=mu,
                sigma=0.5,
                observed=score_matrix
            )

            trace = pm.sample(
                draws=2000,
                tune=1000,
                target_accept=0.95
            )

        return trace
```

---

## ici_pipeline.py

```python
class ICIPipeline:

    def run(self, raw_df):

        normalized = percentile_normalize(raw_df)

        benchmark_scores = []

        for benchmark_id in normalized.benchmark_id.unique():

            subset = normalized[
                normalized.benchmark_id == benchmark_id
            ]

            scores = (
                BenchmarkFactorModel()
                .fit_transform(subset)
            )

            scores["benchmark_id"] = benchmark_id

            benchmark_scores.append(scores)

        benchmark_scores = pd.concat(
            benchmark_scores
        )

        domain_scores = aggregate_domains(
            benchmark_scores,
            benchmark_metadata
        )

        matrix = (
            domain_scores
            .pivot_table(
                index="model_id",
                columns="domain_id",
                values="benchmark_score"
            )
            .fillna(0)
            .values
        )

        ici_model = HierarchicalICI()

        trace = ici_model.fit(matrix)

        return trace
```

---

# What I'd Build Next (Production Version)

After this prototype works, I would replace the simple factor-analysis layer with:

```text
Metric Layer
    Bayesian Factor Model

Benchmark Layer
    2PL IRT

Domain Layer
    Hierarchical Bayesian IRT

Global Layer
    Latent Capability Model
```

using either:

* PyMC
* Stan
* NumPyro

The end result is an ECI-style system that scales cleanly to:

* 100–500 benchmarks
* 20–100 models
* thousands of metric observations
* rolling benchmark additions
* partial benchmark coverage

while producing stable, interpretable ICI scores that remain comparable as your benchmark suite evolves over time.
