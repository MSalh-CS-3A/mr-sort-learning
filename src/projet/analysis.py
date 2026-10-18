"""Synthèse des sorties sauvegardées ; aucune nouvelle recherche."""

from __future__ import annotations

from collections import defaultdict
import csv
import json
from itertools import combinations
from pathlib import Path
import statistics

import numpy as np

from .data import write_json


def quantile(values, p):
    return float(np.quantile(values, p))


def csv_table(path, rows):
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def anytime_statistics(curves, grid, total_runs):
    """Séparer la médiane partielle de celle d'une cohorte finale constante."""
    result = []
    for moment, column in zip(grid, zip(*curves)):
        valid = np.array(column)[np.isfinite(column)]
        median = float(np.median(valid)) if len(valid) else None
        result.append({"time": float(moment), "available_runs": len(valid),
                       "total_runs": total_runs, "valid_final_runs": len(curves),
                       "median_best_error_rate": median,
                       "median_complete_cohort_error_rate": median if len(valid) == len(curves) else None})
    return result


def analyze(input_dir, output_dir):
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    all_runs = [json.loads(p.read_text()) for p in sorted(Path(input_dir).rglob("result.json"))]
    attempted_groups, attempted_instances, attempted_strata = defaultdict(list), defaultdict(list), defaultdict(list)
    failures = []
    for run in all_runs:
        if not run.get("completed") or run["method"] == "single":
            continue
        method = f"{run['method']}-{run['initializer']}"
        cfg, d = run["identity"]["config"], run["dataset"]
        budget = cfg["milp_seconds"] if run["method"] == "MILP" else cfg["seconds"]
        attempted_groups[method, budget].append(run)
        attempted_instances[d["path"], method, budget].append(run)
        attempted_strata[method, budget, d.get("type"), d.get("configuration"), d.get("announced_noise"), d.get("announced_ratio")].append(run)
        if run.get("status") != "ok" or not run.get("solution"):
            failures.append({"dataset_path": d["path"], "method": method,
                             "seed": run["seed"], "budget": budget,
                             "status": run["status"], "stop_reason": run["stop_reason"],
                             "wall_time": run["wall_time"]})
    runs = [r for r in all_runs if r.get("completed") and r.get("status") == "ok"
            and r.get("solution") and r["method"] != "single"]
    rows, grouped, strata, paired, by_instance = [], defaultdict(list), defaultdict(list), defaultdict(dict), defaultdict(list)
    for run in runs:
        d, s, cfg = run["dataset"], run["solution"], run["identity"]["config"]
        method = f"{run['method']}-{run['initializer']}"
        budget = cfg["milp_seconds"] if run["method"] == "MILP" else cfg["seconds"]
        validated_trace = [t for t in run["trace"] if t["event"] != "milp_incumbent_unvalidated"]
        row = {"run_id": run["run_id"], "dataset_path": d["path"], "dataset_hash": d["hash"],
               "type": d.get("type"), "configuration": d.get("configuration"),
               "noise": d.get("announced_noise"), "ratio": d.get("announced_ratio"),
               "N": d["N"], "m": d["m"], "C": d["C"], "method": method, "seed": run["seed"],
               "budget": budget, "LG": s["LG"], "error_rate": s["error_rate"],
               "wall_time": run["wall_time"], "group0": s["group_sizes"][0], "group1": s["group_sizes"][1],
               "wpb_calls": run["counters"].get("wpb_calls", 0), "stop_reason": run["stop_reason"],
               "overrun_count": len(run["overruns"])}
        for target in (0, .05, .10):
            row[f"time_to_rate_{target:g}"] = next((t["time"] for t in validated_trace if t["best_LG"]/d["N"] <= target), None)
        rows.append(row)
        grouped[method, budget].append(row)
        strata[method, budget, d.get("type"), d.get("configuration"), d.get("announced_noise"), d.get("announced_ratio")].append(row)
        by_instance[d["path"], method, budget].append(row)
        pair_key = (d["hash"], run["identity"]["problem_hash"], run["seed"], budget)
        if method in paired[pair_key]:
            raise ValueError("Plusieurs configurations pour un même appariement : analyser les campagnes séparément.")
        paired[pair_key][method] = row

    def summary(items, attempted=None):
        attempted = len(items) if attempted is None else attempted
        rates = [r["error_rate"] for r in items]
        return {"attempted_runs": attempted, "runs": len(items),
                "missing_or_invalid_runs": attempted-len(items),
                "solution_frequency": len(items)/attempted if attempted else 0,
                "median_error_rate": statistics.median(rates) if rates else None,
                "q25": quantile(rates, .25) if rates else None,
                "q75": quantile(rates, .75) if rates else None,
                "best_error_rate": min(rates) if rates else None,
                "zero_frequency": sum(v == 0 for v in rates)/attempted if attempted else 0,
                "median_wall_time": statistics.median(r["wall_time"] for r in items) if items else None}

    summaries = [{"method": method, "budget": budget, **summary(grouped.get((method, budget), []), len(attempts))}
                 for (method, budget), attempts in sorted(attempted_groups.items())]
    stratified = [{"method": k[0], "budget": k[1], "type": k[2], "configuration": k[3],
                   "noise": k[4], "ratio": k[5], **summary(strata[k], len(attempts))}
                  for k, attempts in sorted(attempted_strata.items(), key=lambda kv: str(kv[0]))]
    differences = []
    for key, methods in paired.items():
        for baseline, method in combinations(sorted(methods), 2):
            differences.append({"dataset_hash": key[0], "seed": key[2], "budget": key[3],
                                "method": method, "baseline": baseline,
                                "error_rate_difference": methods[method]["error_rate"]-methods[baseline]["error_rate"]})
    instance_summaries = [{"dataset_path": key[0], "method": key[1], "budget": key[2],
                           **summary(by_instance[key], len(attempts))}
                          for key, attempts in sorted(attempted_instances.items())]
    csv_table(output / "runs.csv", rows)
    csv_table(output / "summary.csv", summaries)
    csv_table(output / "stratified.csv", stratified)
    csv_table(output / "paired_differences.csv", differences)
    csv_table(output / "instance_summary.csv", instance_summaries)
    csv_table(output / "failures.csv", failures)
    report = {"total_results": len(all_runs), "valid_two_model_runs": len(runs),
              "statuses": {status: sum(r.get("status") == status for r in all_runs)
                           for status in sorted({r.get("status", "unknown") for r in all_runs})},
              "summary": summaries, "stratified": stratified,
              "notes": ["Les répétitions mesurent l'aléa algorithmique sur les CSV fournis.",
                        "Les bornes MILP concernent uniquement la formulation à marge.",
                        "Les exécutions invalides et sans solution sont exclues des métriques de qualité.",
                        "La courbe de qualité utilise une cohorte finale constante après sa première couverture complète ; le panneau inférieur indique la disponibilité sur toutes les tentatives."]}
    write_json(output / "summary.json", report)
    if not rows:
        return report
    labels = [f"{method} ({budget:g}s)" for method, budget in sorted(grouped)]
    fig, ax = plt.subplots(figsize=(max(8, len(labels)*1.2), 4.5), layout="constrained")
    ax.boxplot([[r["error_rate"] for r in grouped[key]] for key in sorted(grouped)], tick_labels=labels)
    ax.set_ylabel("LG / N")
    ax.tick_params(axis="x", rotation=25)
    ax.set_title("Erreurs finales et variabilité sur les instances fournies")
    fig.savefig(output / "final_quality.png", dpi=160)
    plt.close(fig)
    fig, (ax, coverage_ax) = plt.subplots(2, 1, figsize=(10, 7), sharex=True,
                                         gridspec_kw={"height_ratios": [3, 1]}, layout="constrained")
    anytime = []
    for method, budget in sorted(grouped):
        grid = np.linspace(0, max(budget, max(r["wall_time"] for r in grouped[method, budget])), 101)
        curves = []
        for run in runs:
            if f"{run['method']}-{run['initializer']}" != method:
                continue
            cfg = run["identity"]["config"]
            actual_budget = cfg["milp_seconds"] if run["method"] == "MILP" else cfg["seconds"]
            if actual_budget != budget:
                continue
            trace = [t for t in run["trace"] if t["event"] != "milp_incumbent_unvalidated"]
            curves.append([next((t["best_LG"]/run["dataset"]["N"] for t in reversed(trace) if t["time"] <= moment), np.nan)
                           for moment in grid])
        # Les nouvelles instances difficiles ne doivent pas faire remonter une
        # courbe "meilleur LG" par simple changement de population.
        attempts = len(attempted_groups[method, budget])
        stats = anytime_statistics(curves, grid, attempts)
        anytime.extend({"method": method, "budget": budget, **row} for row in stats)
        medians = [row["median_complete_cohort_error_rate"] if row["median_complete_cohort_error_rate"] is not None else np.nan for row in stats]
        ax.step(grid, medians, where="post", label=f"{method} ({budget:g}s, n={len(curves)}/{attempts})")
        coverage_ax.step(grid, [row["available_runs"]/attempts for row in stats], where="post")
    ax.set(ylabel="Médiane du meilleur LG / N", title="Qualité sur une cohorte constante de solutions valides")
    coverage_ax.set(xlabel="Temps total (s)", ylabel="Disponibilité", ylim=(0, 1.05))
    ax.legend(fontsize=8)
    fig.savefig(output / "quality_time.png", dpi=160)
    plt.close(fig)
    csv_table(output / "anytime.csv", anytime)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    for ax, factor in zip(axes.flat, ("type", "configuration", "noise", "ratio")):
        levels = sorted({str(r[factor]) for r in rows})
        for method, budget in sorted(grouped):
            rates = [[r["error_rate"] for r in grouped[method, budget] if str(r[factor]) == level] for level in levels]
            ax.plot(levels, [statistics.median(v) if v else np.nan for v in rates], marker="o", label=f"{method} ({budget:g}s)")
        ax.set(title=factor, ylabel="Médiane LG / N")
    axes[0, 0].legend(fontsize=7)
    fig.savefig(output / "factors.png", dpi=160)
    plt.close(fig)
    return report
