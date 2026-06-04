This is one of the biggest architectural changes I would make from the earlier version. Instead of fitting separate ICI models, the README and code should treat **Public** and **Internal** as latent dimensions underneath a single global capability model.

The resulting hierarchy becomes:

```text
Global Capability (ICI)
        │
        ├── Public Capability
        │       ├── Translation
        │       ├── Coding
        │       └── Reasoning
        │
        └── Internal Capability
                ├── Support
                ├── RAG
                ├── Agent Workflows
                └── Enterprise Tasks
```

This ensures:

* One stable scale
* Comparable scores
* No scale drift
* Ability to add benchmarks continuously
* Ability to detect benchmark overfitting

---

## Updated README.md

# Internal Capability Index (ICI)

A hierarchical Bayesian capability measurement system inspired by Epoch AI's ECI but designed for enterprise benchmark platforms.

The system produces:

* Global ICI
* Public ICI
* Internal ICI
* Domain ICIs
* Benchmark ICIs

from a single fitted latent capability model.

---

# Design Goals

Traditional benchmark systems average scores.

This system estimates latent capability.

Benefits:

* Benchmark saturation resistance
* Handles multiple metrics per benchmark
* Handles missing benchmark results
* Supports continual benchmark additions
* Produces uncertainty estimates
* Supports public vs internal benchmark analysis

---

# Capability Hierarchy

```text
Global Capability
        │
        ├── Public Capability
        │
        └── Internal Capability
                │
                ├── Domain Capability
                │
                └── Benchmark Capability
                        │
                        └── Metric Observations
```

---

# Benchmark Taxonomy

Every benchmark must be classified.

```sql
benchmark_id
domain_id
source_type
business_unit
criticality
```

Example:

wmt24
translation
public
external
standard

customer_support_v2
support
internal
support
critical

rag_production
rag
internal
search
critical

---

# Stored Observations

```sql
observation_id
model_id
benchmark_id
domain_id
source_type
metric_name
score
timestamp
```

Example:

GPT5
wmt24
translation
public
COMET
0.91

GPT5
customer_support_v2
support
internal
judge
8.7

---

# Capability Outputs

## Global ICI

Single overall capability estimate.

Example:

GPT5 = 91.4

---

## Public ICI

Capability estimated from public benchmarks.

Example:

GPT5 = 94.2

---

## Internal ICI

Capability estimated from internal workloads.

Example:

GPT5 = 88.1

---

## Domain ICI

Examples:

Translation = 95

Coding = 92

RAG = 89

Support = 84

Agents = 90

---

# Incremental Benchmark Addition

New benchmark workflow:

1. Register benchmark metadata.
2. Run benchmark on anchor models.
3. Fit benchmark parameters.
4. Add benchmark to production.

Historical capability scales remain stable.

---

# Recommended Technology Stack

Execution:

* Inspect-AI

Storage:

* PostgreSQL

Modeling:

* PyMC
* ArviZ

Data Processing:

* Pandas
* NumPy

Visualization:

* Streamlit
* Grafana

---

# Output Tables

model_capability

```sql
model_id
global_ici
public_ici
internal_ici
updated_at
```

domain_capability

```sql
model_id
source_type
domain_id
domain_score
updated_at
```

benchmark_capability

```sql
model_id
benchmark_id
benchmark_score
updated_at
```

This design creates a single coherent capability scale while still supporting public-only and internal-only leaderboards.

---

# Updated Benchmark Metadata Model

```python
from dataclasses import dataclass

@dataclass
class BenchmarkMetadata:
    benchmark_id: str
    domain_id: str
    source_type: str      # public/internal
    business_unit: str
```

---

# Updated Observation Model

```python
from dataclasses import dataclass

@dataclass
class Observation:
    model_id: str
    benchmark_id: str
    domain_id: str
    source_type: str
    metric_name: str
    score: float
```

---

# Source Capability Layer

New layer between Global and Domain.

```python
import pymc as pm

class SourceCapabilityLayer:

    def build(
        self,
        n_models,
        n_sources
    ):

        global_capability = pm.Normal(
            "global_capability",
            0,
            1,
            shape=n_models
        )

        source_loading = pm.Normal(
            "source_loading",
            1,
            0.25,
            shape=n_sources
        )

        source_capability = pm.Normal(
            "source_capability",
            mu=(
                global_capability[:, None]
                * source_loading
            ),
            sigma=.25,
            shape=(n_models, n_sources)
        )

        return (
            global_capability,
            source_capability
        )
```

---

# Domain Layer

Now domains inherit from source capabilities.

```python
domain_capability = pm.Normal(
    "domain_capability",
    mu=source_capability[
        :,
        domain_source_idx
    ],
    sigma=.30,
    shape=(n_models, n_domains)
)
```

Example:

```text
Global
   ↓

Public
Internal

   ↓

Translation
Coding
RAG
Support
Agents
```

---

# Global + Public + Internal Output

```python
def extract_capabilities(trace):

    global_scores = (
        trace.posterior["global_capability"]
        .mean(dim=("chain","draw"))
        .values
    )

    source_scores = (
        trace.posterior["source_capability"]
        .mean(dim=("chain","draw"))
        .values
    )

    return {
        "global": global_scores,
        "public": source_scores[:,0],
        "internal": source_scores[:,1]
    }
```

---

# Updated Pipeline

```python
class ICIPipeline:

    def run(self, observations):

        normalized = normalize_metrics(
            observations
        )

        benchmark_scores = (
            fit_metric_factor_models(
                normalized
            )
        )

        benchmark_capabilities = (
            fit_benchmark_irt(
                benchmark_scores
            )
        )

        model = HierarchicalICI()

        trace = model.fit(
            benchmark_capabilities
        )

        capabilities = (
            extract_capabilities(
                trace
            )
        )

        return capabilities
```

---

# Example Output

```json
{
  "gpt5": {
    "global_ici": 91.2,
    "public_ici": 95.1,
    "internal_ici": 87.4
  },
  "claude_next": {
    "global_ici": 89.7,
    "public_ici": 91.0,
    "internal_ici": 88.9
  }
}
```

A useful extension for your benchmark platform would be to add a fourth score:

```text
Benchmark Generalization Gap

public_ici - internal_ici
```

Example:

```text
GPT5

Public ICI     95
Internal ICI   83

Gap            12
```

That single metric often reveals more about real-world enterprise performance than the overall ICI itself because it highlights whether a model's strength is concentrated on public benchmarks versus your actual workloads.
