The Internal Capability Index (ICI): A Hierarchical Framework for AI Model Evaluation

Executive Summary

The Internal Capability Index (ICI) is an advanced AI model evaluation framework designed to provide a statistically robust, single-measure assessment of model capability. Moving beyond traditional benchmark score averaging, which often proves unstable and prone to "benchmark gaming," the ICI utilizes hierarchical Bayesian modeling to estimate latent capability. This methodology—inspired by Epoch AI’s Economic Competitiveness Index (ECI)—allows organizations to integrate public benchmarks with proprietary enterprise workloads into a unified, comparable scale.

The ICI provides executive-level visibility into AI performance through three primary indices: Global, Public, and Internal. By calculating the "Generalization Gap" (the difference between public performance and internal enterprise performance), the framework identifies models that fail to translate theoretical capability into practical business value. The implementation of the ICI ensures longitudinal stability, more accurate model selection, and a future-proof approach to benchmark governance.


--------------------------------------------------------------------------------


The Limitations of Traditional Averaging

Current enterprise approaches to AI evaluation typically rely on averaging benchmark scores. This methodology presents several critical challenges as AI programs scale:

* Ranking Instability: The introduction of new benchmarks can radically and unpredictably alter model rankings.
* Metric Double-Counting: Multiple metrics within a single benchmark (e.g., BLEU, COMET, BLEURT) are often highly correlated; averaging treats them as independent, leading to skewed results.
* Inconsistent Comparisons: Organizations often struggle to compare industry-standard public evaluations with internal, proprietary benchmarks.
* Benchmark Saturation: As models improve, they hit the upper limits of existing benchmarks, making leading models appear artificially similar.
* Historical Inconsistency: As benchmark suites evolve and benchmarks are retired or added, tracking model progress over time becomes statistically unreliable.


--------------------------------------------------------------------------------


The ICI Architectural Hierarchy

The ICI framework replaces simple aggregation with a four-layer hierarchical latent capability model. This treats benchmark results not as the capability itself, but as measurable observations of an underlying, hidden capability.

Layer	Focus	Description
Layer 1	Metric Capability	Combines individual metrics (Human Ratings, LLM Judge Scores, BLEU, etc.) into latent benchmark-quality estimates to prevent redundancy.
Layer 2	Benchmark Capability	Employs Item Response Theory (IRT) to assess difficulty, discrimination, and information value. Difficult benchmarks are weighted more heavily than saturated ones.
Layer 3	Domain Capability	Groups benchmarks into specific functional areas such as Coding, Reasoning, Agent Workflows, RAG, and Safety.
Layer 4	Global Capability	Synthesizes domain capabilities into the final Internal Capability Index (ICI) score.


--------------------------------------------------------------------------------


Integrating Public and Internal Benchmarking

A core feature of the ICI is its treatment of the benchmark source as a primary dimension. This creates three directly comparable scores derived from the same underlying model:

1. Global ICI: The comprehensive capability score across all available benchmarks.
2. Public ICI: Capability derived specifically from industry-standard public benchmarks.
3. Internal ICI: Capability estimated from proprietary, enterprise-specific workloads.

The Generalization Gap

The framework introduces a critical risk indicator: the Generalization Gap. This is calculated as: Generalization Gap = Public ICI − Internal ICI

A large gap indicates a model that performs exceptionally well on public leaderboards but fails to generalize to the specific tasks required by the enterprise. Smaller gaps signify stronger transferability to real-world workloads.

Comparative Example of Model Performance

Model	Global ICI	Public ICI	Internal ICI	Generalization Gap
GPT-5	91.2	95.1	87.4	7.7
Claude Next	89.7	91.0	88.9	2.1
Gemini Next	88.4	90.2	85.7	4.5


--------------------------------------------------------------------------------


Strategic and Operational Advantages

Implementing the ICI provides several high-level benefits for organizational leadership:

* Accurate Model Selection: Leadership can select models based on actual enterprise performance rather than marketing-driven public leaderboards.
* Mitigation of Benchmark Gaming: The latent model naturally discounts models that have been over-optimized (or "overfit") to public benchmark datasets.
* Investment Optimization: Domain-specific scores (e.g., RAG capability vs. Translation capability) allow organizations to direct investments toward models that solve their specific business needs.
* Objective Vendor Evaluation: Provides a common, statistically rigorous scale for comparing internal models against commercial offerings.
* Long-Term Stability: The system remains consistent even as old benchmarks are retired and new ones are introduced.


--------------------------------------------------------------------------------


Technical Implementation and Execution

The ICI is designed to be implemented as a dedicated "Capability Engine" integrated with existing benchmarking platforms.

Technical Stack

* Benchmark Execution: Inspect-AI
* Data Storage: PostgreSQL
* Statistical Modeling: PyMC and ArviZ (Hierarchical Bayesian Modeling)
* Visualization: Grafana and Streamlit

Execution Frequency

To maintain relevance, the framework supports:

* Nightly recalculation of capabilities as new data arrives.
* On-demand recomputation whenever new benchmarks are added to the suite.


--------------------------------------------------------------------------------


Conclusion

The Internal Capability Index provides a single, trusted source of truth for AI evaluation. By transitioning from simple score averaging to a hierarchical Bayesian model, an organization ensures its AI strategy is grounded in statistical rigor and business-relevant metrics. The result is a governance framework that maintains stability and clarity even as the underlying AI landscape continues to evolve rapidly.
