You are generating training utterances for a semantic routing system.

Your goal is to create a high-quality set of example utterances for ONE route (category) that will be used in embedding-based classification.

## Route Definition

Route Name: {ROUTE_NAME}

Route Description:
{ROUTE_DESCRIPTION}

## Other Routes (for contrast — VERY IMPORTANT)

{LIST_OF_OTHER_ROUTES_WITH_DESCRIPTIONS}

---

## Instructions

Generate {N_UTTERANCES} utterances that clearly belong to the target route and NOT to any of the other routes.

### Requirements

1. **Diversity**

   * Include paraphrases, different sentence structures, and vocabulary
   * Vary length (short queries, long prompts, questions, commands)

2. **Realistic User Language**

   * Use natural, messy phrasing (like real users)
   * Include casual tone, incomplete sentences, and slight ambiguity

3. **Coverage**
   Include a mix of:

   * Clear / obvious examples (40%)
   * Moderate / indirect phrasing (40%)
   * Edge cases (20%) — still correct, but close to other routes

4. **Disambiguation**

   * Avoid phrases that could reasonably belong to other routes
   * If a phrase is ambiguous, bias it MORE toward the target route

5. **No Generic Fillers**

   * Avoid vague phrases like “help me with this”
   * Avoid utterances that could apply to multiple categories

6. **No Duplicates or Minor Variations**

   * Each utterance must be meaningfully distinct

---

## Output Format (STRICT)

Return ONLY a JSON array of strings:

[
"utterance 1",
"utterance 2",
...
]

Do not include explanations or any extra text.


📊 How to interpret results
✅ Healthy routes
Margin: > 0.15
Confusion: < 5%
⚠️ Needs improvement
Margin: 0.05 – 0.15
Confusion: 5–15%
🚨 Problematic
Margin: < 0.05
Confusion: > 15%
🔥 What to do when a route fails
Low margin?

→ Add more diverse utterances
→ Remove overly generic ones

High confusion?

→ Compare with the conflicting route
→ Add disambiguation examples

route-eval/
├── route_eval/
│   ├── __init__.py
│   ├── evaluator.py
│   ├── cli.py
│   └── utils.py
├── pyproject.toml
└── README.md

⚙️ evaluator.py
import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class RouteMetrics:
    route_name: str
    intra_similarity: float
    nearest_other_similarity: float
    margin: float
    confusion_rate: float


class RouteEvaluator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True)

    def evaluate(self, routes: Dict[str, List[str]]) -> List[RouteMetrics]:
        route_embeddings = {}
        centroids = {}

        # Embed
        for route, utts in routes.items():
            emb = self.embed(utts)
            route_embeddings[route] = emb
            centroids[route] = np.mean(emb, axis=0)

        metrics = []

        for route, emb in route_embeddings.items():
            intra_sim = np.mean(cosine_similarity(emb, emb))

            other_routes = [r for r in routes if r != route]
            other_centroids = np.array([centroids[r] for r in other_routes])

            sims_to_others = cosine_similarity(emb, other_centroids)
            nearest_other_sim = np.mean(np.max(sims_to_others, axis=1))

            margin = intra_sim - nearest_other_sim

            own_centroid = centroids[route].reshape(1, -1)
            own_sim = cosine_similarity(emb, own_centroid).flatten()
            max_other_sim = np.max(sims_to_others, axis=1)

            confusion = np.mean(max_other_sim > own_sim)

            metrics.append(RouteMetrics(
                route,
                float(intra_sim),
                float(nearest_other_sim),
                float(margin),
                float(confusion)
            ))

        return metrics

    def find_confusions(self, routes: Dict[str, List[str]]):
        embeddings = {}
        centroids = {}

        for route, utts in routes.items():
            emb = self.embed(utts)
            embeddings[route] = emb
            centroids[route] = np.mean(emb, axis=0)

        results = []

        for route, emb in embeddings.items():
            own_centroid = centroids[route].reshape(1, -1)

            for i, vec in enumerate(emb):
                own_sim = cosine_similarity([vec], own_centroid)[0][0]

                for other, other_centroid in centroids.items():
                    if other == route:
                        continue

                    other_sim = cosine_similarity([vec], [other_centroid])[0][0]

                    if other_sim > own_sim:
                        results.append({
                            "utterance": routes[route][i],
                            "expected": route,
                            "closer_to": other
                        })

        return results

        🧪 utils.py
        import json
import yaml
from pathlib import Path


def load_routes(path: str):
    path = Path(path)

    if path.suffix in [".yaml", ".yml"]:
        with open(path) as f:
            return yaml.safe_load(f)
    elif path.suffix == ".json":
        with open(path) as f:
            return json.load(f)
    else:
        raise ValueError("Unsupported file format. Use JSON or YAML.")


def save_json(data, path: str):
    with open(path, "w") as f:
        json.dump(data, f, indent=2).

        🖥️ cli.py
        import click
from route_eval.evaluator import RouteEvaluator
from route_eval.utils import load_routes, save_json


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--model", default="all-MiniLM-L6-v2", help="Embedding model")
@click.option("--json-out", default=None, help="Save JSON report")
@click.option("--show-confusions", is_flag=True, help="Print confusion examples")
def main(input_file, model, json_out, show_confusions):
    """Evaluate semantic router route quality"""

    routes = load_routes(input_file)

    evaluator = RouteEvaluator(model_name=model)
    metrics = evaluator.evaluate(routes)

    click.echo("\n=== Route Quality Report ===\n")

    results = []

    for m in metrics:
        click.echo(f"Route: {m.route_name}")
        click.echo(f"  Intra Similarity:         {m.intra_similarity:.3f}")
        click.echo(f"  Nearest Other Similarity: {m.nearest_other_similarity:.3f}")
        click.echo(f"  Margin:                   {m.margin:.3f}")
        click.echo(f"  Confusion Rate:           {m.confusion_rate:.2%}\n")

        results.append(m.__dict__)

    if json_out:
        save_json(results, json_out)
        click.echo(f"\nSaved JSON report to {json_out}")

    if show_confusions:
        click.echo("\n=== Confusions ===\n")
        confusions = evaluator.find_confusions(routes)

        for c in confusions[:50]:  # limit output
            click.echo(f"{c['utterance']}")
            click.echo(f"  expected: {c['expected']}")
            click.echo(f"  closer to: {c['closer_to']}\n")


if __name__ == "__main__":
    main()


    📦 pyproject.toml.

    [project]
name = "route-eval"
version = "0.1.0"
description = "Semantic router route quality evaluator"
dependencies = [
    "click",
    "numpy",
    "scikit-learn",
    "sentence-transformers",
    "pyyaml"
]

[project.scripts]
route-eval = "route_eval.cli:main"

🧪 Example Input (routes.yaml)
billing:
  - i want a refund
  - why was i charged twice
  - cancel my subscription

tech_support:
  - app keeps crashing
  - i can't log in
  - getting an error message

sales:
  - do you offer enterprise plans
  - pricing for teams
  - volume discounts available?

🚀 Usage
Install locally
pip install -e .
Run evaluation
route-eval routes.yaml
With extras
route-eval routes.yaml \
  --json-out report.json \
  --show-confusions
🔥 Example Output
=== Route Quality Report ===

Route: billing
  Intra Similarity:         0.82
  Nearest Other Similarity: 0.61
  Margin:                   0.21
  Confusion Rate:           2.00%
