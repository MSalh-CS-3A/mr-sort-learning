"""Benchmark systématique pour le Jalon 2 : comparaison 1-MR-Sort vs 2-MR-Sort.

Ce script évalue les performances sur les jeux de données supermarket :
- Variations de dimensions (6 cr / 3 ca, 8 cr / 4 ca, 10 cr / 5 ca)
- Variations de taille d'échantillon (n = 300, 600, 1200)
- Variations de proportion de mélange (50-50 vs 75-25)
- Niveaux de bruit (bruit 0% vs bruit 10%)
- Typologies de données (type_a et type_b)

Auteurs : Mohamed SALH, Mohamed CHEBLI, Quentin Robidou
Projet SDP - Jalon 2 - Mention IA, CentraleSupélec
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
import time

import pandas as pd

from lincs_adapter import ProblemDefinition
from inv2_mrsort import Inv2MRSortHeuristic


# Matrice représentative de banc d'essai
BENCHMARK_SUITE = [
    # type_a : cr06_ca03
    ("type_a", "cr06_ca03", "n0300_rep50-50_noise00.csv"),
    ("type_a", "cr06_ca03", "n0300_rep50-50_noise10.csv"),
    ("type_a", "cr06_ca03", "n0300_rep75-25_noise00.csv"),
    ("type_a", "cr06_ca03", "n0300_rep75-25_noise10.csv"),
    ("type_a", "cr06_ca03", "n0600_rep50-50_noise00.csv"),
    ("type_a", "cr06_ca03", "n0600_rep50-50_noise10.csv"),
    ("type_a", "cr06_ca03", "n1200_rep50-50_noise00.csv"),

    # type_a : cr08_ca04
    ("type_a", "cr08_ca04", "n0300_rep50-50_noise00.csv"),
    ("type_a", "cr08_ca04", "n0300_rep50-50_noise10.csv"),
    ("type_a", "cr08_ca04", "n0300_rep75-25_noise00.csv"),
    ("type_a", "cr08_ca04", "n0600_rep50-50_noise00.csv"),

    # type_a : cr10_ca05
    ("type_a", "cr10_ca05", "n0300_rep50-50_noise00.csv"),
    ("type_a", "cr10_ca05", "n0300_rep50-50_noise10.csv"),
    ("type_a", "cr10_ca05", "n0300_rep75-25_noise00.csv"),
    ("type_a", "cr10_ca05", "n0600_rep50-50_noise00.csv"),

    # type_b : cr06_ca03
    ("type_b", "cr06_ca03", "n0300_rep50-50_noise00.csv"),
    ("type_b", "cr06_ca03", "n0300_rep50-50_noise10.csv"),
    ("type_b", "cr06_ca03", "n0300_rep75-25_noise00.csv"),
    ("type_b", "cr06_ca03", "n0300_rep75-25_noise10.csv"),
    ("type_b", "cr06_ca03", "n0600_rep50-50_noise00.csv"),

    # type_b : cr08_ca04 & cr10_ca05
    ("type_b", "cr08_ca04", "n0300_rep50-50_noise00.csv"),
    ("type_b", "cr08_ca04", "n0300_rep75-25_noise00.csv"),
    ("type_b", "cr10_ca05", "n0300_rep50-50_noise00.csv"),
    ("type_b", "cr10_ca05", "n0300_rep75-25_noise00.csv"),
]


def run_benchmark(
    base_dir: Path,
    output_path: Path,
    init_mode: str = "kmeans",
    max_alt_iter: int = 5,
    lincs_iter: int = 25,
    seed: int = 42,
) -> dict:
    """Exécute la suite de benchmark et sauvegarde les résultats au fil de l'eau."""
    results = []
    
    print("=" * 110, flush=True)
    print(f"{'#':<3} | {'Configuration':<32} | {'1-MR-Sort':<10} | {'2-MR-Sort':<10} | {'Gain':<8} | {'S1 / S2 (%)':<15} | {'Temps':<8} | {'Iter'}", flush=True)
    print("=" * 110, flush=True)

    t_suite_start = time.perf_counter()

    for idx, (data_type, dim_folder, filename) in enumerate(BENCHMARK_SUITE, start=1):
        ds_dir = base_dir / data_type / dim_folder
        prob_file = ds_dir / "problem.yml"
        csv_file = ds_dir / filename

        if not csv_file.exists() or not prob_file.exists():
            print(f"Fichier manquant : {csv_file}", file=sys.stderr)
            continue

        prob_def = ProblemDefinition.from_yaml_file(prob_file)
        df = pd.read_csv(csv_file)

        # Parse tags from filename
        # e.g. n0300_rep50-50_noise00.csv
        parts = filename.replace(".csv", "").split("_")
        n_samples = int(parts[0].replace("n", ""))
        rep_ratio = parts[1].replace("rep", "")
        noise_level = int(parts[2].replace("noise", ""))

        heuristic = Inv2MRSortHeuristic(
            prob_def,
            init_strategy=init_mode,
            max_alternating_iterations=max_alt_iter,
            lincs_max_iterations=lincs_iter,
            seed=seed,
            verbose=False,
        )

        res = heuristic.fit(df)

        tag = f"{data_type}/{dim_folder}/{filename[:15]}"
        s1_s2_str = f"{res.segment_1_proportion*100:.0f}% / {res.segment_2_proportion*100:.0f}%"
        gain_str = f"+{res.accuracy_gain*100:.1f}%"
        t_str = f"{res.runtime_seconds:.1f}s"

        print(
            f"{idx:<3} | {tag:<32} | {res.baseline_accuracy_1_mrsort*100:>8.2f}% | "
            f"{res.joint_accuracy*100:>8.2f}% | {gain_str:>8} | {s1_s2_str:<15} | {t_str:<8} | {res.convergence_iterations}",
            flush=True,
        )

        record = {
            "index": idx,
            "data_type": data_type,
            "dimension": dim_folder,
            "filename": filename,
            "n_criteria": prob_def.n_criteria,
            "n_categories": prob_def.n_categories,
            "n_samples": n_samples,
            "rep_ratio": rep_ratio,
            "noise_level_pct": noise_level,
            "accuracy_1_mrsort": res.baseline_accuracy_1_mrsort,
            "accuracy_2_mrsort": res.joint_accuracy,
            "accuracy_gain": res.accuracy_gain,
            "segment_1_size": res.segment_1_size,
            "segment_2_size": res.segment_2_size,
            "segment_1_proportion": res.segment_1_proportion,
            "segment_2_proportion": res.segment_2_proportion,
            "convergence_iterations": res.convergence_iterations,
            "runtime_seconds": res.runtime_seconds,
            "model_1": {
                "weights": list(res.model_1.weights),
                "majority_threshold": res.model_1.majority_threshold,
                "boundaries": [list(b) for b in res.model_1.boundaries],
            },
            "model_2": {
                "weights": list(res.model_2.weights),
                "majority_threshold": res.model_2.majority_threshold,
                "boundaries": [list(b) for b in res.model_2.boundaries],
            },
        }
        results.append(record)

        # Sauvegarde incrémentale
        output_payload = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_configurations": len(BENCHMARK_SUITE),
                "completed_configurations": len(results),
                "init_mode": init_mode,
                "lincs_max_iterations": lincs_iter,
                "max_alternating_iterations": max_alt_iter,
            },
            "results": results,
        }
        output_path.write_text(json.dumps(output_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    total_suite_time = time.perf_counter() - t_suite_start
    print("=" * 110, flush=True)
    if not results:
        print(f"Erreur : Aucun fichier de données trouvé dans le répertoire : {base_dir}", file=sys.stderr)
        print("Veuillez vérifier le chemin de Datasets-Step2 ou le préciser avec --base-dir.", file=sys.stderr)
        return {}

    print(f"Suite terminée avec succès en {total_suite_time:.1f} secondes. Résultats enregistrés dans {output_path}", flush=True)

    # Synthèses globales
    mean_acc_1 = sum(r["accuracy_1_mrsort"] for r in results) / len(results)
    mean_acc_2 = sum(r["accuracy_2_mrsort"] for r in results) / len(results)
    mean_gain = sum(r["accuracy_gain"] for r in results) / len(results)
    print(f"Exactitude moyenne 1-MR-Sort : {mean_acc_1*100:.2f}%", flush=True)
    print(f"Exactitude moyenne 2-MR-Sort : {mean_acc_2*100:.2f}%", flush=True)
    print(f"Gain moyen absolu            : +{mean_gain*100:.2f} points de pourcentage", flush=True)
    print("=" * 110, flush=True)

    return output_payload


def resolve_base_dir(specified_path: Path | None) -> Path:
    """Détecte automatiquement l'emplacement de Datasets-Step2/Datasets-Step2."""
    if specified_path is not None and specified_path.exists() and (specified_path / "type_a").exists():
        return specified_path

    script_dir = Path(__file__).resolve().parent
    candidates = [
        specified_path,
        Path.cwd() / "Datasets-Step2" / "Datasets-Step2",
        Path.cwd() / "Datasets-Step2",
        Path.cwd().parent / "Datasets-Step2" / "Datasets-Step2",
        Path.cwd().parent / "Datasets-Step2",
        script_dir / "Datasets-Step2" / "Datasets-Step2",
        script_dir / "Datasets-Step2",
        script_dir.parent / "Datasets-Step2" / "Datasets-Step2",
        script_dir.parent / "Datasets-Step2",
    ]
    for c in candidates:
        if c is not None and c.exists() and (c / "type_a").exists():
            return c
    return specified_path or Path("Datasets-Step2/Datasets-Step2")


def resolve_output_path(specified_path: Path | None) -> Path:
    """Détermine le chemin d'enregistrement du JSON selon le dossier d'exécution."""
    default_name = "resultat_benchmark_jalon2.json"
    if specified_path is not None:
        p = specified_path
        # Si on est déjà dans le dossier cr_jalon_2, ne pas créer de sous-dossier éponyme
        if Path.cwd().name.startswith("cr_jalon_2") and "cr_jalon_2" in str(p.parent):
            return Path.cwd() / p.name
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    return Path.cwd() / default_name


def main() -> None:
    parser = argparse.ArgumentParser(description="Exécuter le benchmark Jalon 2.")
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=None,
        help="Répertoire racine des données Step 2 (détecté automatiquement si omis).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Chemin de sortie JSON (détecté automatiquement si omis).",
    )
    parser.add_argument("--init", default="residual", choices=["kmeans", "residual", "multi-start"])
    parser.add_argument("--max-alt-iter", type=int, default=4)
    parser.add_argument("--lincs-iter", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()
    base_dir = resolve_base_dir(args.base_dir)
    output_path = resolve_output_path(args.output)

    run_benchmark(
        base_dir,
        output_path,
        init_mode=args.init,
        max_alt_iter=args.max_alt_iter,
        lincs_iter=args.lincs_iter,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
