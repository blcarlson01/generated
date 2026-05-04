# Generated

A collection of LLM evaluation tools, data processing scripts, prompt templates, and UI components built for internal research and experimentation.

---

## Contents

### Code Examples

| File | Description |
|------|-------------|
| [concurrent_calls.txt](concurrent_calls.txt) | Async OpenAI streaming with rate limiting, semaphore-based concurrency control, and exponential backoff retry logic |
| [faiss_example](faiss_example) | FAISS vector index management for semantic search, k-NN classification, and outlier detection via threshold tuning |
| [jira_to_summary.txt](jira_to_summary.txt) | Fetch Jira issues with Smart Checklist progress using PKI certificate authentication |
| [keyword_extractor.txt](keyword_extractor.txt) | Parallel keyword extraction from prompts by category using `ThreadPoolExecutor` and retry backoff |
| [mh_large_messages_example](mh_large_messages_example/) | Mental health conversation analyzer — evaluates user-LLM conversations for concern signals, handles large contexts via chunking |
| [review_files](review_files) | Interactive Jupyter widget for manually reviewing and annotating CSV/JSON files (keep/delete/label) |
| [open_analysis](open_analysis) | Work/non-work and intent classification rules with O*NET IWA taxonomy assignment |

### React Components

| File | Description |
|------|-------------|
| [org_chart_2.txt](org_chart_2.txt) | 5-level org chart with color-coded levels, headcount/budget stats, and animated tiles |
| [org_tiles.txt](org_tiles.txt) | Tile-based org drill-down with navigation history, stat cards, tooltips, and Framer Motion animations |

### Documentation & Design

| File | Description |
|------|-------------|
| [papermill_example.md](papermill_example.md) | Guide for parameterizing and scheduling Jupyter notebooks with Papermill |
| [semantic_notes.md](semantic_notes.md) | Semantic router route quality evaluation framework — `RouteEvaluator` class, confusion detection, margin/confusion rate metrics |
| [topic_modeling_ideas.txt](topic_modeling_ideas.txt) | Architecture notes for a 100k+ prompt topic clustering pipeline using HDBSCAN, FAISS, and drift detection |
| [topic_prompt.txt](topic_prompt.txt) | LLM system prompt for strict single-topic classification (2-4 word output) |

### Prompt Templates

| File | Description |
|------|-------------|
| [prompts/summary_prompt.txt](prompts/summary_prompt.txt) | Summary faithfulness evaluation prompt (0–5 scale) |
| [prompts/translation_judge.txt](prompts/translation_judge.txt) | Reference-based translation quality judge (0–5 scale) |
| [prompts/translation_judge_no_reference.txt](prompts/translation_judge_no_reference.txt) | Reference-free translation evaluation on adequacy and fluency |
| [prompts/old/language_grader](prompts/old/language_grader) | Strict 100-point translation grader (Accuracy 40 + Fluency 30 + Style 30; pass ≥ 70) |
| [prompts/old/language_test_taker.txt](prompts/old/language_test_taker.txt) | LLM prompt for producing student-like translations |

### Other

| File | Description |
|------|-------------|
| [relay_roar.txt](relay_roar.txt) | Short story — "Rocky's Relay Roar" |
| [images/](images/) | Raccoon mascot artwork, icons, and screenshots |
| [video/](video/) | Generated video clips |

---

## Themes

- **LLM Evaluation** — translation quality, summarization scoring, route confusion detection
- **Semantic Classification** — topic modeling, intent detection, work/non-work labeling
- **Scalable Data Processing** — concurrent API calls, FAISS indexes, large-context chunking
- **Tooling & Integration** — Jira, Papermill, interactive Jupyter widgets
- **React UI** — org charts, drill-down dashboards
