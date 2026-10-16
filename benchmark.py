"""Protocole du jalon 1 : apprendre puis tester sur des objets indépendants."""

import argparse
import json
from pathlib import Path
import random
import statistics

from mrsort import LearningSet, MRSortModel, train


def random_model(rng: random.Random, n: int, p: int) -> MRSortModel:
    raw_weights = [rng.random() + 0.01 for _ in range(n)]
    weights = tuple(w / sum(raw_weights) for w in raw_weights)
    columns = [sorted(rng.uniform(10, 90) for _ in range(p - 1)) for _ in range(n)]
    boundaries = tuple(tuple(columns[i][h] for i in range(n)) for h in range(p - 1))
    return MRSortModel(weights, boundaries, rng.uniform(0.5, 0.85), numerical_tolerance=0)


def run_benchmark(*, runs: int = 20, n: int = 3, p: int = 2,
                  train_size: int = 30, test_size: int = 200,
                  seed: int = 42, time_limit: float = 10) -> dict:
    if min(runs, n, train_size, test_size) < 1 or p < 2:
        raise ValueError("Tailles positives et au moins deux catégories requises.")
    results = []
    for run in range(runs):
        rng = random.Random(seed + run)
        ground_truth = random_model(rng, n, p)
        learning = tuple(tuple(rng.uniform(0,100) for _ in range(n)) for _ in range(train_size))
        labels = tuple(ground_truth.predict(row) for row in learning)
        data = LearningSet(tuple(f"x{j}" for j in range(train_size)), tuple(f"crit{i}" for i in range(n)),
                           learning, labels, p)
        result = train(data, seed=seed + run, time_limit=time_limit)
        # Nouveaux tirages, jamais donnés au solveur.
        test = tuple(tuple(rng.uniform(0,100) for _ in range(n)) for _ in range(test_size))
        accuracy = sum(ground_truth.predict(row) == result.model.predict(row) for row in test) / test_size
        results.append({"run": run + 1, "seed": seed + run,
                        "ground_truth": {"weights": ground_truth.weights, "boundaries": ground_truth.boundaries,
                                         "majority_threshold": ground_truth.majority_threshold},
                        "learned_model": result.to_dict()["model"],
                        "status": result.status, "optimal": result.optimal, "objective": result.objective,
                        "mip_gap": result.mip_gap, "training_accuracy": result.training_accuracy,
                        "test_accuracy": accuracy, "runtime_seconds": result.runtime_seconds})
    return {"configuration": {"runs": runs, "n": n, "p": p, "train_size": train_size, "test_size": test_size,
                               "seed": seed, "time_limit_seconds": time_limit},
            "mean_test_accuracy": statistics.mean(r["test_accuracy"] for r in results),
            "std_test_accuracy": statistics.pstdev(r["test_accuracy"] for r in results),
            "mean_training_accuracy": statistics.mean(r["training_accuracy"] for r in results),
            "optimal_runs": sum(r["optimal"] for r in results), "results": results}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=20)
    parser.add_argument("--criteria", type=int, default=3)
    parser.add_argument("--categories", type=int, default=2)
    parser.add_argument("--train-size", type=int, default=30)
    parser.add_argument("--test-size", type=int, default=200)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--time-limit", type=float, default=10)
    parser.add_argument("--output", type=Path, default=Path("results/jalon1/resultat_benchmark.json"),
                        help="Fichier JSON de sortie (défaut : results/jalon1/resultat_benchmark.json).")
    args = parser.parse_args()
    try:
        report = run_benchmark(runs=args.runs, n=args.criteria, p=args.categories, train_size=args.train_size,
                               test_size=args.test_size, seed=args.seed, time_limit=args.time_limit)
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(2, f"Erreur : {exc}\n")
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "results"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
