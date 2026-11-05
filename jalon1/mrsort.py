"""Apprentissage de MR-Sort par un MILP GUROBI (critères à maximiser)."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import sys
from typing import Sequence


@dataclass(frozen=True)
class LearningSet:
    names: tuple[str, ...]
    criteria: tuple[str, ...]
    performances: tuple[tuple[float, ...], ...]
    categories: tuple[int, ...]
    n_categories: int

    def __post_init__(self) -> None:
        if not self.criteria or not self.performances:
            raise ValueError("Le jeu d'apprentissage doit contenir des critères et des objets.")
        if self.n_categories < 2:
            raise ValueError("Il faut au moins deux catégories ordonnées.")
        if len(self.names) != len(self.performances) or len(self.categories) != len(self.names):
            raise ValueError("Chaque objet doit avoir un nom, des performances et une classe.")
        if len(set(self.names)) != len(self.names):
            raise ValueError("Les noms des objets doivent être uniques.")
        for row, category in zip(self.performances, self.categories):
            if len(row) != len(self.criteria) or not all(math.isfinite(x) for x in row):
                raise ValueError("Les performances doivent être finies et avoir la bonne dimension.")
            if isinstance(category, bool) or not isinstance(category, int) or not 1 <= category <= self.n_categories:
                raise ValueError("Les classes doivent être des entiers entre 1 et p.")


def load_dataset(path: str | Path, n_categories: int | None = None) -> LearningSet:
    """Lit le tableau du cours : nom, n performances, catégorie (séparateurs blancs)."""
    lines = [line.split() for line in Path(path).read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    if len(lines) < 2 or len(lines[0]) < 2:
        raise ValueError("En-tête ou données manquants.")
    # L'en-tête fourni n'a pas de titre pour la colonne des noms.
    header = lines[0]
    has_name_header = header[0].lower() in {"id", "nom", "name", "objet"}
    criteria = tuple(header[1:-1] if has_name_header else header[:-1])
    names, rows, categories = [], [], []
    for number, tokens in enumerate(lines[1:], start=2):
        if len(tokens) != len(criteria) + 2:
            raise ValueError(f"Ligne {number} : nombre de colonnes incorrect.")
        try:
            rows.append(tuple(float(value.replace(",", ".")) for value in tokens[1:-1]))
            categories.append(int(tokens[-1]))
        except ValueError as exc:
            raise ValueError(f"Ligne {number} : performance ou catégorie invalide.") from exc
        names.append(tokens[0])
    p = n_categories if n_categories is not None else max(2, max(categories))
    return LearningSet(tuple(names), criteria, tuple(rows), tuple(categories), p)


@dataclass(frozen=True)
class MRSortModel:
    weights: tuple[float, ...]
    boundaries: tuple[tuple[float, ...], ...]
    majority_threshold: float
    numerical_tolerance: float = 1e-7

    def __post_init__(self) -> None:
        if not self.weights or not self.boundaries:
            raise ValueError("Poids ou frontières manquants.")
        tol = self.numerical_tolerance
        if not math.isfinite(tol) or tol < 0:
            raise ValueError("Tolérance numérique invalide.")
        if not all(math.isfinite(w) and -tol <= w <= 1 + tol for w in self.weights):
            raise ValueError("Poids invalides.")
        if abs(math.fsum(self.weights) - 1) > max(tol, 1e-8):
            raise ValueError("La somme des poids doit valoir 1.")
        if not math.isfinite(self.majority_threshold) or not -tol <= self.majority_threshold <= 1 + tol:
            raise ValueError("Seuil de majorité invalide.")
        if any(len(b) != len(self.weights) or not all(math.isfinite(v) for v in b) for b in self.boundaries):
            raise ValueError("Frontières invalides.")
        if any(a > b + tol for lower, upper in zip(self.boundaries, self.boundaries[1:]) for a, b in zip(lower, upper)):
            raise ValueError("Les frontières doivent être ordonnées sur chaque critère.")

    def scores(self, performances: Sequence[float]) -> tuple[float, ...]:
        if len(performances) != len(self.weights) or not all(math.isfinite(x) for x in performances):
            raise ValueError("Vecteur de performances invalide.")
        tol = self.numerical_tolerance
        return tuple(math.fsum(w for x, b, w in zip(performances, boundary, self.weights) if x >= b - tol)
                     for boundary in self.boundaries)

    def predict(self, performances: Sequence[float]) -> int:
        """Classe 1 = plus basse ; égalité à une frontière/majorité = côté supérieur.

        La tolérance ne compense que les arrondis de la solution GUROBI. La fixer
        à zéro permet d'appliquer littéralement les comparaisons mathématiques.
        """
        return 1 + sum(score >= self.majority_threshold - self.numerical_tolerance
                       for score in self.scores(performances))


@dataclass(frozen=True)
class TrainingResult:
    model: MRSortModel
    status: str
    optimal: bool
    objective: int
    objective_bound: float
    mip_gap: float
    runtime_seconds: float
    solver_variables: int
    solver_constraints: int
    relaxed_objects: tuple[str, ...]
    predictions: tuple[int, ...]
    misclassified_objects: tuple[str, ...]
    training_accuracy: float
    performance_margin: float
    score_margin: float

    def to_dict(self) -> dict:
        return asdict(self)


def train(
    data: LearningSet,
    *,
    lower_bound: float = 0,
    upper_bound: float = 100,
    performance_margin: float = 1e-4,
    score_margin: float = 1e-4,
    time_limit: float = 60,
    seed: int = 0,
    threads: int = 1,
    log: bool = False,
    export_lp: str | Path | None = None,
) -> TrainingResult:
    """Minimise le nombre d'objets dont les contraintes de classe sont relâchées.

    Pour un objet de classe c : il doit franchir b^(c-1) si c>1, et ne pas
    franchir b^c si c<p. Les autres frontières sont implicites par monotonie.
    """
    if not all(math.isfinite(v) for v in (lower_bound, upper_bound, performance_margin, score_margin, time_limit)):
        raise ValueError("Les bornes, marges et durée doivent être finies.")
    if lower_bound >= upper_bound or not 1e-6 <= performance_margin <= upper_bound - lower_bound:
        raise ValueError("Bornes invalides ou marge de performance hors intervalle [1e-6, u-l].")
    if not 1e-6 <= score_margin <= 1 or time_limit <= 0:
        raise ValueError("La marge de score doit être dans [1e-6, 1] et la durée positive.")
    if not isinstance(threads, int) or threads < 1 or not isinstance(seed, int) or not 0 <= seed <= 2_000_000_000:
        raise ValueError("Threads ou graine invalides.")
    if any(not lower_bound <= x <= upper_bound for row in data.performances for x in row):
        raise ValueError("Les performances sortent des bornes choisies.")
    try:
        import gurobipy as gp
        from gurobipy import GRB
    except ImportError as exc:
        raise RuntimeError("Installer gurobipy dans l'environnement du projet (voir README.md).") from exc

    n, p, m = len(data.criteria), data.n_categories, len(data.names)
    # h=0 représente b^1, la frontière entre les classes 1 et 2.
    relevant = [tuple(h for h in (c - 2, c - 1) if 0 <= h < p - 1) for c in data.categories]
    # Deux objets ayant la même performance ont le même indicateur et la même
    # contribution pour une frontière et un critère donnés. Partage exact.
    keys = sorted({(h, i, row[i]) for row, hs in zip(data.performances, relevant) for h in hs for i in range(n)})
    M = upper_bound - lower_bound + performance_margin
    B = 1 + score_margin
    statuses = {GRB.OPTIMAL: "OPTIMAL", GRB.TIME_LIMIT: "TIME_LIMIT", GRB.INFEASIBLE: "INFEASIBLE",
                GRB.INF_OR_UNBD: "INF_OR_UNBD", GRB.INTERRUPTED: "INTERRUPTED", GRB.SUBOPTIMAL: "SUBOPTIMAL"}
    try:
        with gp.Env(empty=True) as env:
            env.setParam("OutputFlag", int(log))
            env.start()
            with gp.Model("learn_mrsort", env=env) as problem:
                problem.Params.TimeLimit = time_limit
                problem.Params.Seed = seed
                problem.Params.Threads = threads
                # Pas de choix manuel du simplexe/barrière ni de réglage des
                # coupes : GUROBI décide automatiquement pour ce MILP.
                problem.Params.MIPGap = 0
                problem.Params.MIPGapAbs = 0
                problem.Params.FeasibilityTol = 1e-8
                problem.Params.IntFeasTol = 1e-8
                weights = problem.addVars(n, lb=0, ub=1, name="w")
                boundaries = problem.addVars(p - 1, n, lb=lower_bound, ub=upper_bound, name="b")
                threshold = problem.addVar(lb=0, ub=1, name="lambda")
                indicators = problem.addVars(keys, vtype=GRB.BINARY, name="delta")
                contributions = problem.addVars(keys, lb=0, ub=1, name="contribution")
                errors = problem.addVars(m, vtype=GRB.BINARY, name="error")

                problem.addConstr(weights.sum() == 1, name="normalize_weights")
                for h in range(p - 2):
                    for i in range(n):
                        problem.addConstr(boundaries[h, i] <= boundaries[h + 1, i], name=f"ordered_boundary[{h},{i}]")
                for k, key in enumerate(keys):
                    h, i, value = key
                    d, z = indicators[key], contributions[key]
                    problem.addConstr(boundaries[h, i] - value <= M * (1 - d), name=f"criterion_pass[{k}]")
                    problem.addConstr(boundaries[h, i] - value >= performance_margin - M * d, name=f"criterion_fail[{k}]")
                    # z >= 0 est déjà la borne inférieure de la variable.
                    problem.addConstr(z <= weights[i], name=f"contribution_weight[{k}]")
                    problem.addConstr(z <= d, name=f"contribution_indicator[{k}]")
                    problem.addConstr(z >= d + weights[i] - 1, name=f"contribution_lower[{k}]")
                for j, (row, category) in enumerate(zip(data.performances, data.categories)):
                    if category > 1:
                        lower_score = gp.quicksum(contributions[category - 2, i, row[i]] for i in range(n))
                        problem.addConstr(lower_score >= threshold - B * errors[j], name=f"lower_class[{j}]")
                    if category < p:
                        upper_score = gp.quicksum(contributions[category - 1, i, row[i]] for i in range(n))
                        problem.addConstr(upper_score <= threshold - score_margin + B * errors[j], name=f"upper_class[{j}]")
                problem.setObjective(errors.sum(), GRB.MINIMIZE)
                if export_lp is not None:
                    problem.write(str(export_lp))
                problem.optimize()
                status = statuses.get(problem.Status, f"STATUS_{problem.Status}")
                if problem.SolCount == 0:
                    raise RuntimeError(f"GUROBI n'a trouvé aucune solution exploitable (statut {status}).")
                learned = MRSortModel(
                    tuple(weights[i].X for i in range(n)),
                    tuple(tuple(boundaries[h, i].X for i in range(n)) for h in range(p - 1)),
                    threshold.X,
                )
                predictions = tuple(learned.predict(row) for row in data.performances)
                wrong = tuple(name for name, predicted, expected in zip(data.names, predictions, data.categories) if predicted != expected)
                relaxed = tuple(data.names[j] for j in range(m) if errors[j].X > 0.5)
                # Un objet non relâché doit être classé comme annoncé après
                # extraction : détecte notamment une incohérence numérique.
                if set(wrong) - set(relaxed):
                    raise RuntimeError("La prédiction extraite contredit des contraintes satisfaites ; vérifier les marges numériques.")
                return TrainingResult(
                    learned, status, problem.Status == GRB.OPTIMAL,
                    round(problem.ObjVal), problem.ObjBound, problem.MIPGap, problem.Runtime,
                    problem.NumVars, problem.NumConstrs, relaxed, predictions, wrong,
                    (m - len(wrong)) / m, performance_margin, score_margin,
                )
    except gp.GurobiError as exc:
        message = f"GUROBI : {exc}"
        if exc.errno == 10010:
            message += " Une licence académique complète est nécessaire pour cette taille de modèle."
        raise RuntimeError(message) from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Apprendre MR-Sort avec GUROBI, classes ordonnées de 1 à p.")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--categories", type=int, help="Nombre de catégories ; sinon déduit de la classe maximale.")
    parser.add_argument("--lower-bound", type=float, default=0)
    parser.add_argument("--upper-bound", type=float, default=100)
    parser.add_argument("--performance-margin", type=float, default=1e-4)
    parser.add_argument("--score-margin", type=float, default=1e-4)
    parser.add_argument("--time-limit", type=float, default=60)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--log", action="store_true", help="Afficher la progression de GUROBI.")
    parser.add_argument("--export-lp", type=Path, help="Exporter le MILP pour inspection.")
    parser.add_argument("--output", type=Path, help="Enregistrer paramètres, prédictions et diagnostics en JSON.")
    args = parser.parse_args()
    try:
        data = load_dataset(args.dataset, args.categories)
        result = train(data, lower_bound=args.lower_bound, upper_bound=args.upper_bound,
                       performance_margin=args.performance_margin, score_margin=args.score_margin,
                       time_limit=args.time_limit, seed=args.seed, threads=args.threads,
                       log=args.log, export_lp=args.export_lp)
        payload = result.to_dict()
        payload.update({"criteria": data.criteria, "objects": data.names, "observed_categories": data.categories,
                        "n_categories": data.n_categories})
        serialized = json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)
        if args.output:
            args.output.write_text(serialized + "\n", encoding="utf-8")
        print(serialized)
        return 0
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
