"""Heuristique d'apprentissage d'un mélange de deux modèles MR-Sort (inv-2-MR-Sort).

Ce module implémente une heuristique d'optimisation alternée de type k-Means / Hard EM
couplée à un schéma multi-départ (Multi-Start Alternating Optimization) pour résoudre
le problème inv-2-MR-Sort :
    max_{L1, L2, M1, M2} (1 / |L|) * [ sum_{x in L1} 1{M1(x) = c(x)} + sum_{x in L2} 1{M2(x) = c(x)} ]

Auteurs : Mohamed SALH, Mohamed CHEBLI, Quentin Robidou
Projet SDP - Jalon 2 - Mention IA, CentraleSupélec
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import sys
import time
from typing import Literal

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from lincs_adapter import (
    MRSortParameters,
    ProblemDefinition,
    SingleMRSortResult,
    parse_category_int,
    predict_with_model,
    train_single_mrsort,
)


@dataclass
class Inv2MRSortResult:
    """Résultat complet de l'inférence inv-2-MR-Sort."""
    model_1: MRSortParameters
    model_2: MRSortParameters
    joint_accuracy: float
    baseline_accuracy_1_mrsort: float
    accuracy_gain: float
    total_samples: int
    segment_1_size: int
    segment_2_size: int
    segment_1_proportion: float
    segment_2_proportion: float
    segment_assignments: list[int]      # 1 ou 2 pour chaque objet
    joint_predictions: list[int]        # Prédiction du modèle du segment attribué
    observed_categories: list[int]      # Classes réelles
    convergence_iterations: int
    chosen_initialization: str
    intermediate_accuracies: list[float]
    runtime_seconds: float
    criteria_names: list[str]
    category_names: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


class Inv2MRSortHeuristic:
    """Heuristique d'optimisation alternée multi-départ pour inv-2-MR-Sort."""

    def __init__(
        self,
        problem_def: ProblemDefinition,
        *,
        init_strategy: Literal["multi-start", "kmeans", "residual", "random"] = "multi-start",
        max_alternating_iterations: int = 5,
        lincs_max_iterations: int = 25,
        lincs_models_count: int = 10,
        n_restarts: int = 3,
        seed: int = 42,
        verbose: bool = False,
    ) -> None:
        self.problem_def = problem_def
        self.init_strategy = init_strategy
        self.max_alternating_iterations = max_alternating_iterations
        self.lincs_max_iterations = lincs_max_iterations
        self.lincs_models_count = lincs_models_count
        self.n_restarts = n_restarts
        self.seed = seed
        self.verbose = verbose

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(f"[inv-2-MR-Sort] {msg}", flush=True)

    def _evaluate_partition_and_models(
        self,
        df: pd.DataFrame,
        m1_res: SingleMRSortResult,
        m2_res: SingleMRSortResult,
        assignments: np.ndarray,
    ) -> tuple[float, np.ndarray, np.ndarray]:
        """Calcule l'exactitude conjointe selon l'affectation aux segments."""
        y_true = np.array([parse_category_int(c) for c in df["category"]])
        p1, _ = predict_with_model(self.problem_def, m1_res.native_model, df)
        p2, _ = predict_with_model(self.problem_def, m2_res.native_model, df)
        p1 = np.array(p1)
        p2 = np.array(p2)

        joint_pred = np.where(assignments == 1, p1, p2)
        joint_acc = float((joint_pred == y_true).mean())
        return joint_acc, p1, p2

    def _run_single_alternating(
        self,
        df: pd.DataFrame,
        init_mode: str,
        seed: int,
        baseline_m0: SingleMRSortResult | None = None,
    ) -> dict:
        n = len(df)
        y_true = np.array([parse_category_int(c) for c in df["category"]])
        features = df.iloc[:, 1:-1].to_numpy(dtype=float)
        rng = np.random.RandomState(seed)

        # 1. Étape d'initialisation
        if init_mode == "kmeans":
            # Clustering non supervisé sur l'espace des caractéristiques produit X (sans labels)
            km = KMeans(n_clusters=2, random_state=seed, n_init=10).fit(features)
            assignments = km.labels_ + 1
        elif init_mode == "residual":
            if baseline_m0 is None:
                baseline_m0 = train_single_mrsort(
                    self.problem_def,
                    df,
                    seed=seed,
                    max_iterations=self.lincs_max_iterations,
                    models_count=self.lincs_models_count,
                )
            p0 = np.array(baseline_m0.predictions)
            corr = (p0 == y_true)
            assignments = np.where(corr, 1, 2)
            if (assignments == 2).sum() < 5:
                # Si le modèle de base explique déjà presque tout, partition aléatoire équilibrée
                perm = rng.permutation(n)
                assignments = np.ones(n, dtype=int)
                assignments[perm[n // 2:]] = 2
        elif init_mode.startswith("random"):
            perm = rng.permutation(n)
            split_ratio = rng.choice([0.5, 0.6, 0.75])
            split_idx = int(n * split_ratio)
            assignments = np.ones(n, dtype=int)
            assignments[perm[split_idx:]] = 2
        else:
            raise ValueError(f"Stratégie d'initialisation inconnue : {init_mode}")

        best_acc = -1.0
        best_m1_res = None
        best_m2_res = None
        best_assignments = assignments.copy()
        history_acc = []

        # 2. Boucle d'optimisation alternée (k-MRSort / Hard EM)
        for it in range(self.max_alternating_iterations):
            idx_1 = np.where(assignments == 1)[0]
            idx_2 = np.where(assignments == 2)[0]

            if len(idx_1) < 5 or len(idx_2) < 5:
                break

            # Étape M : Apprentissage des deux modèles MR-Sort par LINCS
            m1_res = train_single_mrsort(
                self.problem_def,
                df.iloc[idx_1],
                seed=seed + 10 * it,
                max_iterations=self.lincs_max_iterations,
                models_count=self.lincs_models_count,
            )
            m2_res = train_single_mrsort(
                self.problem_def,
                df.iloc[idx_2],
                seed=seed + 10 * it + 1,
                max_iterations=self.lincs_max_iterations,
                models_count=self.lincs_models_count,
            )

            # Évaluation conjointe
            joint_acc, p1, p2 = self._evaluate_partition_and_models(df, m1_res, m2_res, assignments)
            history_acc.append(joint_acc)

            # Également tester l'exactitude optimale par oracle (si chaque point va au modèle qui le classe le mieux)
            c1 = (p1 == y_true)
            c2 = (p2 == y_true)
            oracle_acc = float((c1 | c2).mean())

            if oracle_acc > best_acc:
                best_acc = oracle_acc
                best_m1_res = m1_res
                best_m2_res = m2_res
                # Affectation optimale instantanée
                best_assignments = np.where(c1, 1, np.where(c2, 2, assignments))

            if joint_acc >= 0.999 or oracle_acc >= 0.999:
                break

            # Étape E : Réaffectation des alternatives au segment minimisant l'erreur
            e1 = np.abs(p1 - y_true)
            e2 = np.abs(p2 - y_true)

            new_assignments = np.zeros(n, dtype=int)
            for i in range(n):
                if e1[i] < e2[i]:
                    new_assignments[i] = 1
                elif e2[i] < e1[i]:
                    new_assignments[i] = 2
                else:
                    # Égalité d'erreur : maintien de l'affectation précédente pour stabilité
                    new_assignments[i] = assignments[i]

            # Vérification de convergence (point fixe sur la partition)
            if np.array_equal(new_assignments, assignments):
                break
            assignments = new_assignments

        return {
            "best_acc": best_acc,
            "best_m1_res": best_m1_res,
            "best_m2_res": best_m2_res,
            "best_assignments": best_assignments,
            "history_acc": history_acc,
            "iterations": len(history_acc),
            "init_mode": init_mode,
        }

    def fit(self, df: pd.DataFrame) -> Inv2MRSortResult:
        """Lance l'inférence complète inv-2-MR-Sort selon la stratégie choisie."""
        t_start = time.perf_counter()
        n = len(df)
        y_true = [parse_category_int(c) for c in df["category"]]

        # 0. Entraînement du modèle MR-Sort unitaire (baseline de référence)
        self._log("Entraînement du modèle MR-Sort unitaire (baseline)...")
        baseline_m0 = train_single_mrsort(
            self.problem_def,
            df,
            seed=self.seed,
            max_iterations=self.lincs_max_iterations,
            models_count=self.lincs_models_count,
        )
        baseline_acc = baseline_m0.training_accuracy
        self._log(f"Exactitude 1-MR-Sort baseline : {baseline_acc * 100:.2f}%")

        # 1. Sélection des stratégies de départ
        candidates_runs = []
        if self.init_strategy == "multi-start":
            strategies = ["kmeans", "residual"] + [f"random_{k}" for k in range(self.n_restarts)]
        else:
            strategies = [self.init_strategy]

        best_run = None
        best_overall_acc = -1.0

        for s_idx, strat in enumerate(strategies):
            self._log(f"Exécution départ {s_idx + 1}/{len(strategies)} avec stratégie : {strat}...")
            run_res = self._run_single_alternating(
                df,
                strat,
                seed=self.seed + 100 * s_idx,
                baseline_m0=baseline_m0 if strat == "residual" else None,
            )
            self._log(f"  -> Résultat : {run_res['best_acc'] * 100:.2f}% (en {run_res['iterations']} itérations)")
            if run_res["best_acc"] > best_overall_acc:
                best_overall_acc = run_res["best_acc"]
                best_run = run_res

        total_runtime = time.perf_counter() - t_start

        # Extraction des résultats finaux
        m1_res = best_run["best_m1_res"]
        m2_res = best_run["best_m2_res"]
        final_assignments = best_run["best_assignments"]

        # Garantie théorique : le modèle à deux segments ne doit jamais faire moins bien que le modèle unique
        if best_overall_acc < baseline_acc:
            self._log("Raffinement résiduel garanti à partir du modèle baseline M0...")
            p0 = np.array(baseline_m0.predictions)
            corr = (p0 == np.array(y_true))
            idx_res = np.where(~corr)[0]
            if len(idx_res) >= 5:
                m2_res_fallback = train_single_mrsort(
                    self.problem_def,
                    df.iloc[idx_res],
                    seed=self.seed + 999,
                    max_iterations=self.lincs_max_iterations,
                    models_count=self.lincs_models_count,
                )
                p2_fb, _ = predict_with_model(self.problem_def, m2_res_fallback.native_model, df)
                p2_fb = np.array(p2_fb)
                c_fb = (p2_fb == np.array(y_true))
                fb_acc = float((corr | c_fb).mean())
                if fb_acc >= best_overall_acc:
                    best_overall_acc = fb_acc
                    m1_res = baseline_m0
                    m2_res = m2_res_fallback
                    final_assignments = np.where(corr, 1, 2)

        p1, _ = predict_with_model(self.problem_def, m1_res.native_model, df)
        p2, _ = predict_with_model(self.problem_def, m2_res.native_model, df)
        joint_predictions = [
            p1[i] if final_assignments[i] == 1 else p2[i]
            for i in range(n)
        ]

        n1 = int((final_assignments == 1).sum())
        n2 = int((final_assignments == 2).sum())

        return Inv2MRSortResult(
            model_1=m1_res.parameters,
            model_2=m2_res.parameters,
            joint_accuracy=best_overall_acc,
            baseline_accuracy_1_mrsort=baseline_acc,
            accuracy_gain=best_overall_acc - baseline_acc,
            total_samples=n,
            segment_1_size=n1,
            segment_2_size=n2,
            segment_1_proportion=n1 / n,
            segment_2_proportion=n2 / n,
            segment_assignments=final_assignments.tolist(),
            joint_predictions=joint_predictions,
            observed_categories=y_true,
            convergence_iterations=best_run["iterations"],
            chosen_initialization=best_run["init_mode"],
            intermediate_accuracies=best_run["history_acc"],
            runtime_seconds=total_runtime,
            criteria_names=list(self.problem_def.criteria_names),
            category_names=list(self.problem_def.categories_names),
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inférence de deux modèles MR-Sort par segment client (inv-2-MR-Sort)."
    )
    parser.add_argument("dataset", type=Path, help="Fichier CSV du jeu de données.")
    parser.add_argument("--problem", type=Path, help="Fichier YAML du problème (déduit si omis).")
    parser.add_argument(
        "--init",
        choices=["multi-start", "kmeans", "residual", "random"],
        default="multi-start",
        help="Stratégie d'initialisation de la partition (défaut : multi-start).",
    )
    parser.add_argument("--restarts", type=int, default=3, help="Nombre de départs aléatoires si multi-start.")
    parser.add_argument("--max-alt-iter", type=int, default=5, help="Nombre max d'itérations alternées.")
    parser.add_argument("--lincs-iter", type=int, default=25, help="Nombre max d'itérations LINCS par ajustement.")
    parser.add_argument("--seed", type=int, default=42, help="Graine aléatoire.")
    parser.add_argument("--output", type=Path, help="Enregistrer les résultats détaillés au format JSON.")
    parser.add_argument("--verbose", action="store_true", help="Afficher les détails de la progression.")

    args = parser.parse_args()

    # Détection et résolution robuste du chemin du dataset
    dataset_path = args.dataset
    if not dataset_path.exists():
        if (Path("..") / dataset_path).exists():
            dataset_path = Path("..") / dataset_path
        elif (Path(__file__).resolve().parent.parent / dataset_path).exists():
            dataset_path = Path(__file__).resolve().parent.parent / dataset_path

    # Déduction du fichier problème si non spécifié
    prob_path = args.problem
    if prob_path is None:
        candidate = dataset_path.parent / "problem.yml"
        if candidate.exists():
            prob_path = candidate
        else:
            print("Erreur : Aucun fichier problem.yml spécifié ou trouvé dans le dossier.", file=sys.stderr)
            return 2

    try:
        prob_def = ProblemDefinition.from_yaml_file(prob_path)
        df = pd.read_csv(dataset_path)

        heuristic = Inv2MRSortHeuristic(
            prob_def,
            init_strategy=args.init,
            max_alternating_iterations=args.max_alt_iter,
            lincs_max_iterations=args.lincs_iter,
            n_restarts=args.restarts,
            seed=args.seed,
            verbose=args.verbose,
        )

        res = heuristic.fit(df)
        payload = res.to_dict()

        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        # Résumé console
        print("\n" + "=" * 65)
        print("          RÉSULTATS DE L'INFÉRENCE inv-2-MR-Sort")
        print("=" * 65)
        print(f"Jeu de données             : {args.dataset.name}")
        print(f"Critères / Catégories      : {prob_def.n_criteria} critères / {prob_def.n_categories} catégories")
        print(f"Nombre d'objets            : {res.total_samples}")
        print(f"Exactitude 1-MR-Sort       : {res.baseline_accuracy_1_mrsort * 100:.2f}%")
        print(f"Exactitude 2-MR-Sort       : {res.joint_accuracy * 100:.2f}%")
        print(f"Gain d'exactitude          : +{res.accuracy_gain * 100:.2f} points de pourcentage")
        print(f"Répartition des segments   : S1={res.segment_1_size} ({res.segment_1_proportion*100:.1f}%) | S2={res.segment_2_size} ({res.segment_2_proportion*100:.1f}%)")
        print(f"Stratégie retenue          : {res.chosen_initialization}")
        print(f"Itérations d'alternance    : {res.convergence_iterations}")
        print(f"Temps total de calcul      : {res.runtime_seconds:.2f} secondes")
        print("=" * 65)
        print("\nModèle Segment 1 :")
        print(f"  Poids normalisés       : {[round(w, 4) for w in res.model_1.weights]}")
        print(f"  Seuil de majorité      : {res.model_1.majority_threshold:.4f}")
        print("Modèle Segment 2 :")
        print(f"  Poids normalisés       : {[round(w, 4) for w in res.model_2.weights]}")
        print(f"  Seuil de majorité      : {res.model_2.majority_threshold:.4f}")
        print("=" * 65)

        return 0
    except Exception as exc:
        print(f"Erreur d'exécution : {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
