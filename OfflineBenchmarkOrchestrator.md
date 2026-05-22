Offline Benchmark Orchestrator

An enterprise-grade, air-gapped pipeline for migrating interactive Jupyter Notebook (.ipynb) benchmarks into highly optimized, production-ready Python tasks, and executing automated matrix sweeps across multiple offline LLM endpoints using Inspect AI and MLflow.

Key Features

Automated Jupyter-to-Python Migration: Scans directory trees, programmatically extracts Python cells, strips out interactive notebook artifacts (shell escapes, Jupyter magic commands), and formats them for production discovery.

Auto-Execution Prevention: Intelligently comments out cell-level .eval() or manual trigger blocks inside raw notebooks to prevent double-execution during automated sweeps.

Air-Gapped Matrix Sweeps: Automatically schedules and runs $N \times M$ evaluation permutations ($N$ benchmarks $\times$ $M$ models) over internal inference engines (like vLLM, Ollama, or TGI).

Offline MLflow Lifecycle Logging: Generates structured experiment trees with automatic Parent-Child tracking (one parent sweep run $\rightarrow$ multiple child task runs) without needing an active internet connection.

Immutable Provenance Tracking: Captures internal git commit hashes and generates fast local data file hashes to establish dataset lineage in your secure database.

System Architecture

       [ Secure Local Workstation / Lab Environment ]
 ┌──────────────────────────────────────────────────────────┐
 │                                                          │
 │  1. Dropped Jupyter Notebooks (.ipynb)                   │
 │     └── ./notebook_benchmarks/                           │
 │                                                          │
 │  2. Orchestrator Processing (offline_orchestrator.py)    │
 │     ├── Strip %magic & !pip                              │
 │     ├── Prevent duplicate eval() triggers                │
 │     └── Output to ./production_benchmarks/*.py          │
 │                                                          │
 │  3. Programmatic Inspect AI Engine                        │
 │     ├── Read clean tasks                                 │
 │     └── Async batch processing                           │
 │                                                          │
 └──────────────┬────────────────────────────┬──────────────┘
                │                            │
  (Local API Requests)                (Artifacts & Metrics)
                ▼                            ▼
 ┌──────────────────────────┐      ┌──────────────────────────┐
 │  Local vLLM / Ollama     │      │  Local MLflow Server     │
 │  Inference Cluster       │      │  (Backend: PostgreSQL)   │
 │  e.g., http://10.0.1.60  │      │  e.g., http://10.0.1.55  │
 └──────────────────────────┘      └──────────────────────────┘


Quick Start (Offline Deployment)

1. Prerequisites

Ensure your air-gapped machine has the following packages installed:

pip install inspect-ai inspect-mlflow nbformat nbconvert pandas


2. File Organization

Create the target structure inside your workspace directory:

.
├── offline_benchmark_orchestrator.py
├── README.md
├── notebook_benchmarks/        # Place your 100+ raw notebook tasks here
└── production_benchmarks/      # Automatically populated by the orchestrator


3. Pipeline Configuration

Open offline_benchmark_orchestrator.py and modify the Config block to reflect your local lab's IP network allocation:

class Config:
    # Directories
    NOTEBOOK_DIR = "./notebook_benchmarks"
    PRODUCTION_DIR = "./production_benchmarks"
    
    # On-Prem Infrastructure Endpoints
    MLFLOW_TRACKING_URI = "http://10.0.1.55:5000"  # Your offline MLflow instance
    MLFLOW_EXPERIMENT_NAME = "core-offline-matrix-v1"
    VLLM_BASE_URL = "http://10.0.1.60:8000/v1"      # Your private vLLM API server
    
    # Execution Grid
    TARGET_MODELS = [
        "openai/llama-3-70b-instruct",
        "openai/mistral-large",
        "openai/phi-3-medium"
    ]
    MAX_CONCURRENT_TASKS = 4  # Concurrency limit to prevent local OOMs
    SAMPLES_LIMIT = None      # Use an integer (e.g., 5) for quick dry-runs


4. Execute the Automation

Run the orchestrator from your terminal:

python offline_benchmark_orchestrator.py


Note: On first execution, if your notebook_benchmarks folder is empty, the script will generate a working mock notebook to safely test the migration and execution pipeline.

Enterprise Scaling & Performance Optimization Guide

Executing a matrix sweep at this scale (e.g., 100 benchmarks across 12 models results in 1,200 distinct runs) requires conscious resource management in air-gapped infrastructures.

1. GPU VRAM & Concurrency Limits

While Inspect is asynchronous and fast, firing too many tasks simultaneously can cause out-of-memory (OOM) failures on your local GPU serving nodes.

Manage concurrency using the MAX_CONCURRENT_TASKS parameter in the script configuration.

Adjust the serving engine’s queue limits (such as vLLM’s --max-model-len or continuous batching parameters) to match your hardware profile.

2. Log and Database Bloat Prevention

By default, logging every span, trace step, and metadata variable for 1,200 massive runs will rapidly exhaust PostgreSQL memory and inflate your MLflow DB to hundreds of gigabytes.

Keep MLFLOW_INSPECT_TRACING configured to "false" in production runs.

Only toggle MLFLOW_INSPECT_TRACING = "true" when you are actively isolating a specific model failure within a subset of tasks.

3. Dataset Lineage & Version Control (Avoid Network File Shares)

Storing active datasets on traditional shared folders (like Samba/NFS) invites file locking issues and accidental modifications.

Check text-based or JSON datasets directly into your internal Git server using Git LFS.

For larger datasets, host files on a local, private MinIO bucket (S3-compatible) and log the immutable Object Version IDs or local Git SHAs in your Inspect metadata tags to guarantee absolute reproducibility.

4. Custom API Reporting & Leaderboards

Because all metadata and scores are channeled directly into MLflow as structured metrics, you do not need to scroll through the primary MLflow UI to analyze matrices.

You can pull the structured data programmatically to feed a local Streamlit dashboard using Python:

import mlflow
import pandas as pd

mlflow.set_tracking_uri("http://10.0.1.55:5000")
experiment = mlflow.get_experiment_by_name("core-offline-matrix-v1")
df = mlflow.search_runs(experiment_ids=[experiment.experiment_id])

# Filter and construct a clean Model vs. Benchmark Grid
grid = df.pivot(
    index="params.model", 
    columns="tags.inspect_task", 
    values="metrics.accuracy"
)
