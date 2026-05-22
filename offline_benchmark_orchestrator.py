"""
Offline Benchmark Orchestrator for Inspect AI & MLflow
======================================================
This production-grade script automates the migration of Jupyter Notebook (.ipynb)
benchmarks into clean Python scripts, validates the environment, and executes 
a matrix of evaluations over local offline model endpoints.

Requirements:
    pip install inspect-ai inspect-mlflow nbformat nbconvert pandas
"""

import os
import re
import sys
import glob
import shutil
import subprocess
import logging
from typing import List, Dict, Any
import nbformat
from nbconvert import PythonExporter

# Configure clean, beautiful console logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("offline_orchestrator")


class Config:
    # Directories
    NOTEBOOK_DIR = "./notebook_benchmarks"  # Where your 100+ .ipynb files live
    PRODUCTION_DIR = "./production_benchmarks"  # Where converted .py files will be saved
    
    # Offline Server Endpoints
    MLFLOW_TRACKING_URI = "http://10.0.1.55:5000"  # Local/on-prem MLflow server
    MLFLOW_EXPERIMENT_NAME = "core-offline-matrix-v1"
    VLLM_BASE_URL = "http://10.0.1.60:8000/v1"  # Local vLLM/Ollama OpenAI API wrapper
    
    # Execution Matrix Parameters
    TARGET_MODELS = [
        "openai/llama-3-70b-instruct",
        "openai/mistral-large",
        "openai/phi-3-medium"
    ]
    MAX_CONCURRENT_TASKS = 4  # Max benchmarks to evaluate at the same time
    SAMPLES_LIMIT = None      # Set an integer (e.g., 10) for smoke testing, or None for full datasets


def get_local_git_sha() -> str:
    """
    Retrieves the short Git commit hash of your local repository.
    This provides immutability metadata to verify exactly which version
    of code ran which benchmark, even when completely offline.
    """
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], 
            stderr=subprocess.DEVNULL
        ).decode("ascii").strip()
        return sha
    except Exception:
        logger.warning("Git repository not detected. Running without version hash.")
        return "local-untracked"


def sanitize_code(code_content: str) -> str:
    """
    Cleans Jupyter Notebook artifacts to create a production-safe python file.
    Specifically:
      - Comments out command line escapes (e.g., !pip install)
      - Comments out Jupyter magic commands (e.g., %matplotlib inline)
      - Safely comments out interactive execution triggers (like eval() calls)
        so that Inspect's search engine won't execute them on discovery.
    """
    sanitized_lines = []
    lines = code_content.splitlines()
    
    for line in lines:
        stripped = line.strip()
        
        # 1. Skip notebook shell escape commands and magic commands
        if stripped.startswith('!') or stripped.startswith('%'):
            sanitized_lines.append(f"# [Cleaned Notebook Command] {line}")
            
        # 2. Prevent notebook-level eval calls from double-firing
        elif "eval(" in stripped and any(kw in stripped for kw in ["task", "Task", "benchmark"]):
            sanitized_lines.append(f"# [Prevented Auto-Execution Trigger] {line}")
            
        else:
            sanitized_lines.append(line)
            
    return "\n".join(sanitized_lines)


def convert_notebooks_to_scripts() -> List[str]:
    """
    Scans the notebook directory, reads every notebook, extracts Python source cells,
    sanitizes them, and writes standard .py tasks into the production directory.
    """
    notebooks = glob.glob(os.path.join(Config.NOTEBOOK_DIR, "**/*.ipynb"), recursive=True)
    
    if not notebooks:
        logger.error(f"No notebooks found in '{Config.NOTEBOOK_DIR}'. Please create this folder or drop files in.")
        return []
        
    logger.info(f"Discovered {len(notebooks)} notebooks. Starting conversion clean-ups...")
    os.makedirs(Config.PRODUCTION_DIR, exist_ok=True)
    
    converted_files = []
    exporter = PythonExporter()
    
    for nb_path in notebooks:
        try:
            # Read notebooks securely from disk
            with open(nb_path, "r", encoding="utf-8") as f:
                nb_node = nbformat.read(f, as_version=4)
                
            # Convert raw notebook node structure to clean Python syntax
            raw_script, _ = exporter.from_notebook_node(nb_node)
            clean_script = sanitize_code(raw_script)
            
            # Save files mapping to their clean name
            file_name = os.path.splitext(os.path.basename(nb_path))[0]
            output_path = os.path.join(Config.PRODUCTION_DIR, f"{file_name}.py")
            
            with open(output_path, "w", encoding="utf-8") as f:
                # Add file metadata header for logging
                f.write(f'# Generated dynamically from Jupyter Notebook: {os.path.basename(nb_path)}\n\n')
                f.write(clean_script)
                
            converted_files.append(output_path)
            logger.info(f"Successfully converted: {os.path.basename(nb_path)} -> {os.path.basename(output_path)}")
            
        except Exception as e:
            logger.error(f"Failed to process {nb_path}. Error: {str(e)}")
            
    return converted_files


def execute_evaluation_matrix():
    """
    Bootstraps the environmental settings for MLflow offline logs, 
    dynamically imports the newly converted tasks, and schedules the matrix.
    """
    # 1. Dynamically configure environment variables for the offline run
    os.environ["MLFLOW_TRACKING_URI"] = Config.MLFLOW_TRACKING_URI
    os.environ["MLFLOW_EXPERIMENT_NAME"] = Config.MLFLOW_EXPERIMENT_NAME
    
    # VERY IMPORTANT at 1,200 permutations scale: Disable verbose step-by-step
    # trace dumps to keep the local database fast and lean.
    os.environ["MLFLOW_INSPECT_TRACING"] = "false"
    
    # 2. Let Inspect discovery framework index the newly generated directory
    from inspect_ai import eval, list_tasks
    
    try:
        discovered_tasks = list_tasks(Config.PRODUCTION_DIR)
    except Exception as e:
        logger.critical(f"Failed to discover tasks in {Config.PRODUCTION_DIR}. Detail: {str(e)}")
        return
        
    if not discovered_tasks:
        logger.error("No valid @task structures were discovered in the converted scripts.")
        return
        
    logger.info(f"Loaded {len(discovered_tasks)} benchmarks for evaluation matrix.")
    logger.info(f"Targeting models: {Config.TARGET_MODELS}")
    
    # 3. Pull Git metadata for execution provenance mapping
    git_hash = get_local_git_sha()
    
    logger.info("Executing evaluations async engine...")
    try:
        # Trigger the programmatic matrix sweep
        results = eval(
            tasks=discovered_tasks,
            model=Config.TARGET_MODELS,
            max_tasks=Config.MAX_CONCURRENT_TASKS,
            model_base_url=Config.VLLM_BASE_URL,
            limit=Config.SAMPLES_LIMIT,
            
            # Custom tags appended directly to the MLflow run for easy tracking
            tags={
                "git_commit_sha": git_hash,
                "orchestrator": "offline_notebook_converter_v1.0",
                "execution_type": "automated_sweep"
            }
        )
        logger.info(f"Evaluation suite complete. All outputs routed directly to MLflow: {Config.MLFLOW_TRACKING_URI}")
        return results
        
    except Exception as e:
        logger.error(f"Matrix run encountered an exception: {str(e)}")


def main():
    print("""
    ===================================================
    OFFLINE BENCHMARK MATRICES SYSTEM AUTOMATOR 
    ===================================================
    """)
    
    # 1. Run quick checks to ensure mock directories exist or files are ready
    if not os.path.exists(Config.NOTEBOOK_DIR):
        logger.info(f"First-run helper: Creating '{Config.NOTEBOOK_DIR}' directory. Please drop your .ipynb benchmarks inside.")
        os.makedirs(Config.NOTEBOOK_DIR, exist_ok=True)
        # Creating a small mock file to let the user run it safely immediately.
        create_mock_notebook()

    # 2. Trigger Extraction & Clean conversion
    converted = convert_notebooks_to_scripts()
    
    if not converted:
        logger.error("Abort: No benchmarks were prepared.")
        return
        
    # 3. Trigger Parallel Execution Suite
    execute_evaluation_matrix()


def create_mock_notebook():
    """Generates a sample Jupyter notebook if the directories are empty for testing."""
    mock_path = os.path.join(Config.NOTEBOOK_DIR, "sample_addition_benchmark.ipynb")
    # Quick raw JSON implementation of a minimal Jupyter notebook task
    notebook_json = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [],
                "source": [
                    "from inspect_ai import Task, task\n",
                    "from inspect_ai.dataset import json_dataset\n",
                    "from inspect_ai.solver import generate\n",
                    "from inspect_ai.scorer import exact\n",
                    "\n",
                    "# We use standard @task marker for programmatic discovery\n",
                    "@task\n",
                    "def sample_benchmark():\n",
                    "    # Simulating a dataset load\n",
                    "    return Task(\n",
                    "        dataset=[\n",
                    "            {\"input\": \"What is 1 + 1?\", \"target\": \"2\"}\n",
                    "        ],\n",
                    "        solver=[generate()],\n",
                    "        scorer=exact()\n",
                    "    )"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Interactive verification block that our script will strip out\n",
                    "!pip install -q some-unneeded-dependency\n",
                    "eval(sample_benchmark(), model='openai/gpt-4o')"
                ]
            }
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 2
    }
    
    with open(mock_path, "w", encoding="utf-8") as f:
        import json
        json.dump(notebook_json, f, indent=2)
    logger.info(f"Created a test mock notebook at '{mock_path}' so you can run the script immediately.")


if __name__ == "__main__":
    main()