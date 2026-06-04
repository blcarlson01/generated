At this point we're moving from a "proof of concept" into something that looks very much like a research-grade capability measurement system.

For 100+ benchmarks, multiple metrics per benchmark, dozens of models, and continual benchmark additions, I would implement a **4-level Bayesian hierarchical model**.

The key design principle is:

> Never average anything if you can infer a latent variable.

---

# Overall Model

```text
Raw Metric Observations
        │
        ▼
Metric Layer
(Bayesian Factor Model)
        │
        ▼
Benchmark Layer
(2PL IRT)
        │
        ▼
Domain Layer
(Hierarchical Bayesian IRT)
        │
        ▼
Global Layer
(Latent Capability Model)
        │
        ▼
ICI Score
```

---

# Database Structure

Everything begins with observations.

```sql
observation_id
model_id
benchmark_id
domain_id
metric_name
score
timestamp
```

Example:

```text
GPT-5
WMT24
translation
BLEU
43.2
```

```text
GPT-5
WMT24
translation
COMET
0.92
```

```text
GPT-5
WMT24
translation
Judge
8.8
```

---

# Layer 1: Bayesian Metric Factor Model

Goal:

```text
BLEU
COMET
BLEURT
Judge
Human
```

↓

```text
Translation Quality
```

rather than counting each metric separately.

---

## Statistical Form

For benchmark (b)

Metric observation:

[
y_{m,b,k}
]

where:

* m = model
* b = benchmark
* k = metric

Assume:

[
y_{m,b,k}
=========

\lambda_k F_{m,b}
+
\epsilon
]

Where:

* (F_{m,b}) = latent benchmark quality
* (\lambda_k) = metric loading

---

## PyMC Example

```python
with pm.Model():

    factor = pm.Normal(
        "factor",
        0,
        1,
        shape=(n_models,)
    )

    loading = pm.Normal(
        "loading",
        1,
        0.5,
        shape=(n_metrics,)
    )

    sigma = pm.HalfNormal(
        "sigma",
        1,
        shape=(n_metrics,)
    )

    mu = factor[:, None] * loading

    pm.Normal(
        "obs",
        mu=mu,
        sigma=sigma,
        observed=metric_matrix
    )

    trace = pm.sample()
```

Output:

```text
TranslationQuality
CodingQuality
AgentQuality
```

per benchmark.

---

# Layer 2: Benchmark Layer (2PL IRT)

Now every benchmark becomes an item.

---

## Example

Benchmarks:

```text
WMT24
FLORES
SWE-Bench
Aider
MMLU
GPQA
```

Each benchmark has:

```text
difficulty
discrimination
```

and each model has:

```text
benchmark capability
```

---

## Model

Epoch's approach is similar.

Probability:

P(X_{mb}=1)=\sigma\left(a_b(\theta_m-b_b)\right)

where:

* (a_b) = discrimination
* (b_b) = difficulty
* (\theta_m) = capability

---

## Continuous Benchmark Scores

Since benchmark scores are continuous:

[
y_{mb}
\sim
Normal(
a_b(\theta_m-b_b),
\sigma_b
)
]

---

## PyMC

```python
with pm.Model():

    theta = pm.Normal(
        "theta",
        0,
        1,
        shape=n_models
    )

    difficulty = pm.Normal(
        "difficulty",
        0,
        1,
        shape=n_benchmarks
    )

    discrimination = pm.LogNormal(
        "discrimination",
        0,
        0.5,
        shape=n_benchmarks
    )

    mu = (
        discrimination *
        (
            theta[:, None]
            - difficulty
        )
    )

    pm.Normal(
        "obs",
        mu=mu,
        sigma=.25,
        observed=benchmark_matrix
    )
```

Output:

```text
Model ↔ Benchmark capability estimates
```

---

# Layer 3: Domain Hierarchical IRT

Now we introduce domains.

---

## Structure

```text
Translation
    WMT24
    FLORES
    MTBench

Coding
    SWE
    Aider
    HumanEval

Reasoning
    GPQA
    MMLU
```

---

## Hierarchical Prior

Benchmark capabilities inherit from domain capability.

[
\theta_{m,b}
\sim
Normal(
\phi_{m,d},
\sigma_d
)
]

Where:

* (\phi_{m,d}) = domain capability

---

## PyMC

```python
domain_capability = pm.Normal(
    "domain_capability",
    0,
    1,
    shape=(n_models, n_domains)
)

benchmark_capability = pm.Normal(
    "benchmark_capability",
    mu=domain_capability[
        :,
        benchmark_domain_idx
    ],
    sigma=0.3,
    shape=(n_models, n_benchmarks)
)
```

---

## Result

Instead of:

```text
GPT5 = 91
```

You obtain:

```text
GPT5

Translation 95
Coding 89
Reasoning 92
Agents 90
Safety 88
```

This is enormously useful operationally.

---

# Layer 4: Global Latent Capability Model

Now estimate:

```text
Overall Capability
```

from domain capability.

---

## Model

[
\phi_{m,d}
==========

\alpha_d G_m
+
\epsilon
]

Where:

* (G_m) = global capability
* (\alpha_d) = domain loading

---

## Interpretation

Some domains matter more.

Example:

```text
Coding
loading = 1.3

Reasoning
loading = 1.5

Translation
loading = 0.7
```

The model learns these automatically.

---

## PyMC

```python
global_capability = pm.Normal(
    "global_capability",
    0,
    1,
    shape=n_models
)

domain_loading = pm.Normal(
    "domain_loading",
    1,
    .5,
    shape=n_domains
)

domain_sigma = pm.HalfNormal(
    "domain_sigma",
    .3,
    shape=n_domains
)

pm.Normal(
    "domain_obs",
    mu=(
        global_capability[:, None]
        * domain_loading
    ),
    sigma=domain_sigma,
    observed=domain_scores
)
```

Output:

```text
ICI
```

---

# Final Hierarchical Graph

```text
Global Capability
       │
       ▼
Domain Capability
       │
       ▼
Benchmark Capability
       │
       ▼
Metric Factors
       │
       ▼
Raw Scores
```

---

# What I Would Actually Use In Production

If I were implementing this for your Inspect-AI platform today:

### v1

* Metric Layer → Bayesian Factor Analysis
* Benchmark Layer → 2PL IRT
* Domain Layer → Hierarchical Gaussian Model
* Global Layer → Single latent factor

### v2

Replace the entire stack with one unified model:

```text
Raw Metrics
    ↓
Metric Factors
    ↓
Benchmark Latents
    ↓
Domain Latents
    ↓
Global Capability
```

fit simultaneously in a single PyMC model.

That allows uncertainty to propagate all the way from BLEU/COMET/Judge scores up to the final ICI score and gives you credible intervals for:

```text
ICI
Translation Capability
Coding Capability
Reasoning Capability
Benchmark Difficulty
Benchmark Discrimination
```

which is very close to what a modern research organization would build if designing an internal successor to ECI from scratch.
