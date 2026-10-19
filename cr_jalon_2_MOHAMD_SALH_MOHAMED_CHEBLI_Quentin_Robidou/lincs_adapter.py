"""Module d'adaptation et d'interface pour la bibliothèque LINCS (MR-Sort).

Ce module fournit une abstraction Python propre autour de liblincs :
- Chargement robuste des fichiers de problème (YAML) et des alternatives (CSV).
- Apprentissage d'un modèle unitaire MR-Sort via l'heuristique génétique (Sobrie et al.).
- Extraction transparente des paramètres mathématiques (poids normalisés, profils frontières, seuil).
- Prédiction et évaluation fine des performances (exactitude, matrice de confusion).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import io
import math
from pathlib import Path
from typing import Sequence
import numpy as np
import pandas as pd
import lincs.classification as lc


@dataclass(frozen=True)
class ProblemDefinition:
    """Représentation structurée d'un problème de tri multicritère MR-Sort."""
    criteria_names: tuple[str, ...]
    categories_names: tuple[str, ...]
    n_criteria: int
    n_categories: int
    native_problem: lc.Problem

    @classmethod
    def from_yaml_file(cls, path: str | Path) -> ProblemDefinition:
        """Charge un fichier problème YAML, en s'assurant de la présence de kind."""
        path = Path(path)
        content = path.read_text(encoding="utf-8")
        if not content.startswith("kind:"):
            content = "kind: classification-problem\n" + content
        prob = lc.Problem.load(io.StringIO(content))
        crit_names = tuple(c.name for c in prob.criteria)
        cat_names = tuple(cat.name for cat in prob.ordered_categories)
        return cls(
            criteria_names=crit_names,
            categories_names=cat_names,
            n_criteria=len(crit_names),
            n_categories=len(cat_names),
            native_problem=prob,
        )


@dataclass(frozen=True)
class MRSortParameters:
    """Paramètres complets d'un modèle MR-Sort (normalisés)."""
    weights: tuple[float, ...]               # Poids des critères sommant à 1
    raw_weights: tuple[float, ...]           # Poids bruts LINCS (seuil implicite = 1.0)
    boundaries: tuple[tuple[float, ...], ...] # (p-1) profils frontières b^1, ..., b^{p-1}
    majority_threshold: float                # Seuil de majorité lambda = 1 / sum(raw_weights)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SingleMRSortResult:
    """Résultat de l'apprentissage d'un modèle MR-Sort unitaire."""
    parameters: MRSortParameters
    training_accuracy: float
    total_samples: int
    correct_samples: int
    predictions: list[int]
    category_predictions: list[str]
    runtime_seconds: float
    native_model: lc.Model

    def to_dict(self) -> dict:
        return {
            "parameters": self.parameters.to_dict(),
            "training_accuracy": self.training_accuracy,
            "total_samples": self.total_samples,
            "correct_samples": self.correct_samples,
            "runtime_seconds": self.runtime_seconds,
        }


def dataframe_to_alternatives(problem: lc.Problem, df: pd.DataFrame) -> lc.Alternatives:
    """Convertit un DataFrame pandas en objet Alternatives LINCS."""
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return lc.Alternatives.load(problem, buf)


def parse_category_int(cat_val: str | int) -> int:
    """Convertit une catégorie ('1 (worst)', '2', '3 (best)' ou entier) en int 1..p."""
    if isinstance(cat_val, (int, np.integer)):
        return int(cat_val)
    s = str(cat_val).strip()
    return int(s.split()[0])


def extract_parameters(prob_def: ProblemDefinition, model: lc.Model) -> MRSortParameters:
    """Extrait les paramètres mathématiques d'un modèle LINCS entraîné."""
    n_crit = prob_def.n_criteria
    n_cat = prob_def.n_categories
    
    # 1. Poids bruts
    raw_weights = tuple(float(w) for w in model.sufficient_coalitions[0].weights.criterion_weights)
    sum_w = math.fsum(raw_weights)
    if sum_w <= 0:
        sum_w = 1.0
    norm_weights = tuple(w / sum_w for w in raw_weights)
    threshold = 1.0 / sum_w
    
    # 2. Seuils frontières b^h_i
    # Chaque critère i possède p-1 seuils
    thresholds_per_crit = []
    for i in range(n_crit):
        av = model.accepted_values[i]
        if av.is_real and av.is_thresholds:
            t = [float(v) for v in av.real_thresholds.thresholds]
        else:
            t = [0.5] * (n_cat - 1)
        thresholds_per_crit.append(t)
        
    # Transposition pour obtenir (p-1) profils frontières chacun de taille n_crit
    boundaries = []
    for h in range(n_cat - 1):
        b_h = tuple(thresholds_per_crit[i][h] for i in range(n_crit))
        boundaries.append(b_h)
        
    return MRSortParameters(
        weights=norm_weights,
        raw_weights=raw_weights,
        boundaries=tuple(boundaries),
        majority_threshold=threshold,
    )


def train_single_mrsort(
    prob_def: ProblemDefinition,
    df: pd.DataFrame,
    *,
    seed: int = 42,
    max_iterations: int = 30,
    models_count: int = 10,
    time_limit_sec: float | None = None,
) -> SingleMRSortResult:
    """Apprend un modèle MR-Sort unitaire sur un DataFrame via LINCS."""
    import time
    t0 = time.perf_counter()
    
    alts = dataframe_to_alternatives(prob_def.native_problem, df)
    prep = lc.PreprocessedLearningSet(prob_def.native_problem, alts)
    mbl = lc.LearnMrsortByWeightsProfilesBreed.ModelsBeingLearned(prep, models_count, seed)
    
    init = lc.InitializeProfilesForProbabilisticMaximalDiscriminationPowerPerCriterion(prep, mbl)
    w_opt = lc.OptimizeWeightsUsingGlop(prep, mbl)
    p_opt = lc.ImproveProfilesWithAccuracyHeuristicOnCpu(prep, mbl)
    breed = lc.ReinitializeLeastAccurate(mbl, init, w_opt, max(1, int(0.2 * models_count)))
    
    terms = [
        lc.TerminateAtAccuracy(mbl, len(alts.alternatives)),
        lc.TerminateAfterIterations(mbl, max_iterations),
    ]
    if time_limit_sec is not None and time_limit_sec > 0:
        terms.append(lc.TerminateAfterSeconds(time_limit_sec))
        
    term_strat = lc.TerminateWhenAny(terms)
    learner = lc.LearnMrsortByWeightsProfilesBreed(prep, mbl, init, w_opt, p_opt, breed, term_strat)
    
    model = learner.perform()
    runtime = time.perf_counter() - t0
    
    # Évaluation sur le jeu
    lc.classify_alternatives(prob_def.native_problem, model, alts)
    pred_cats = [prob_def.native_problem.ordered_categories[a.category_index].name for a in alts.alternatives]
    pred_ints = [parse_category_int(c) for c in pred_cats]
    
    if "category" in df.columns:
        y_true = [parse_category_int(c) for c in df["category"]]
        correct = sum(p == y for p, y in zip(pred_ints, y_true))
        acc = correct / len(df)
    else:
        correct = len(df)
        acc = 1.0
        
    params = extract_parameters(prob_def, model)
    return SingleMRSortResult(
        parameters=params,
        training_accuracy=acc,
        total_samples=len(df),
        correct_samples=correct,
        predictions=pred_ints,
        category_predictions=pred_cats,
        runtime_seconds=runtime,
        native_model=model,
    )


def predict_with_model(
    prob_def: ProblemDefinition,
    model: lc.Model,
    df: pd.DataFrame,
) -> tuple[list[int], list[str]]:
    """Prédit les catégories pour un DataFrame avec un modèle LINCS."""
    alts = dataframe_to_alternatives(prob_def.native_problem, df)
    lc.classify_alternatives(prob_def.native_problem, model, alts)
    pred_cats = [prob_def.native_problem.ordered_categories[a.category_index].name for a in alts.alternatives]
    pred_ints = [parse_category_int(c) for c in pred_cats]
    return pred_ints, pred_cats
