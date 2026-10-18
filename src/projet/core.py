"""Configuration, budget, graines, prédictions et apprentissage protégé."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from io import StringIO
import math
import time
from typing import Callable

from lincs import classification as lc
import numpy as np

from .data import Instance


@dataclass(frozen=True)
class Config:
    initializer: str = "uniform"
    heuristic: str = "A1"
    seconds: float = 30.0
    wpb_seconds: float = 1.0
    models_count: int = 9
    breed_count: int = 4
    wpb_max_iterations: int = 10000
    gmm_n_init: int = 5
    gmm_reg_covar: float = 1e-6
    gmm_max_iter: int = 200
    neighbors: int = 16
    ambiguous_fraction: float = 0.01
    stagnation: int = 20
    perturb_fraction: float = 0.01
    perturb_max_fraction: float = 0.10
    perturbations: int = 10
    score_margin: float = 1e-4
    feasibility_tol: float = 1e-8
    integrality_tol: float = 1e-8
    milp_seconds: float = 30.0
    # Bornes de travail facultatives, utiles aux tests reproductibles sans horloge.
    max_calls: int | None = None
    max_restarts: int | None = None

    def __post_init__(self):
        if self.initializer not in {"uniform", "gmm"} or self.heuristic not in {"A0", "A1", "A2", "A3", "A4", "MILP", "single"}:
            raise ValueError("Initialisation ou méthode inconnue.")
        for name in ("seconds", "wpb_seconds", "milp_seconds", "gmm_reg_covar", "score_margin", "feasibility_tol", "integrality_tol"):
            if not math.isfinite(getattr(self, name)) or getattr(self, name) <= 0:
                raise ValueError(f"{name} doit être positif et fini.")
        for name in ("models_count", "wpb_max_iterations", "gmm_n_init", "gmm_max_iter", "neighbors", "stagnation", "perturbations"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise ValueError(f"{name} doit être un entier positif.")
        if not 0 <= self.breed_count < self.models_count:
            raise ValueError("breed_count doit être entre 0 et models_count-1.")
        if not 0 < self.ambiguous_fraction <= 1 or not 0 < self.perturb_fraction <= self.perturb_max_fraction <= 1:
            raise ValueError("Fractions de transfert invalides.")
        if not 0 < self.score_margin < 1 or self.feasibility_tol >= self.score_margin / 10:
            raise ValueError("La tolérance doit être nettement inférieure à la marge de score.")
        for name in ("max_calls", "max_restarts"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 1):
                raise ValueError(f"{name} doit être un entier positif.")


class Exhausted(RuntimeError):
    pass


class FitFailed(RuntimeError):
    pass


@dataclass
class Budget:
    seconds: float
    max_calls: int | None = None
    clock: Callable[[], float] = time.monotonic
    calls: int = 0
    started: float = field(init=False)
    overruns: list[dict] = field(default_factory=list)

    def __post_init__(self):
        self.started = self.clock()

    @property
    def elapsed(self):
        return self.clock() - self.started

    @property
    def remaining(self):
        return max(0.0, self.seconds - self.elapsed)

    def available(self):
        return self.remaining > 0 and (self.max_calls is None or self.calls < self.max_calls)

    def claim(self, cap: float) -> float:
        if not self.available():
            raise Exhausted("Budget épuisé.")
        allowed = min(cap, self.remaining)
        self.calls += 1
        return allowed


class Seeds:
    """Sous-graines stables, indépendantes du hash Python et des autres flux."""

    def __init__(self, seed: int):
        if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
            raise ValueError("La graine doit être un entier positif ou nul.")
        self.root = seed
        self.counters: dict[str, int] = {}
        self.records: list[dict] = []

    def next(self, stream: str):
        index = self.counters.get(stream, 0)
        self.counters[stream] = index + 1
        seed = int.from_bytes(hashlib.sha256(f"{self.root}:{stream}:{index}".encode()).digest()[:8], "big") % 2_000_000_001
        self.records.append({"stream": stream, "index": index, "seed": seed})
        return seed

    def rng(self, stream: str):
        return np.random.default_rng(self.next(stream))


@dataclass(frozen=True)
class Model:
    """Snapshot YAML : pas d'objet natif mutable partagé entre candidats."""

    yaml: str

    @classmethod
    def capture(cls, instance: Instance, native):
        stream = StringIO()
        native.dump(instance.problem(), stream)
        return cls(stream.getvalue())

    def native(self, instance: Instance):
        return lc.Model.load(instance.problem(), StringIO(self.yaml))


def predict(model: Model, instance: Instance, indices=None) -> tuple[int, ...]:
    # classify_alternatives modifie les étiquettes de cet objet temporaire.
    alternatives = instance.alternatives(indices)
    lc.classify_alternatives(instance.problem(), model.native(instance), alternatives)
    return tuple(a.category_index for a in alternatives.alternatives)


def wpb_fit(instance: Instance, indices, seconds: float, seed: int, config: Config) -> Model:
    problem = instance.problem()
    training = instance.alternatives(indices)
    prep = lc.PreprocessedLearningSet(problem, training)
    state = lc.LearnMrsortByWeightsProfilesBreed.ModelsBeingLearned(prep, config.models_count, seed)
    init = lc.InitializeProfilesForProbabilisticMaximalDiscriminationPowerPerCriterion(prep, state)
    weights = lc.OptimizeWeightsUsingGlop(prep, state)
    improve = lc.ImproveProfilesWithAccuracyHeuristicOnCpu(prep, state)
    breed = lc.ReinitializeLeastAccurate(state, init, weights, config.breed_count)
    stop = lc.TerminateWhenAny([
        lc.TerminateAtAccuracy(state, len(training.alternatives)),
        lc.TerminateAfterSeconds(seconds),
        lc.TerminateAfterIterations(state, config.wpb_max_iterations),
    ])
    native = lc.LearnMrsortByWeightsProfilesBreed(prep, state, init, weights, improve, breed, stop).perform()
    return Model.capture(instance, native)


def fit_guarded(instance: Instance, indices, old_model: Model | None, budget: Budget,
                seed: int, config: Config, events: list[dict] | None = None,
                trainer: Callable = wpb_fit) -> Model:
    indices = tuple(indices)
    if not indices:
        raise ValueError("Un groupe d'apprentissage ne peut pas être vide.")
    events = [] if events is None else events
    old_loss = None
    if old_model is not None:
        old_loss = sum(p != instance.y[i] for i, p in zip(indices, predict(old_model, instance, indices)))
    try:
        allowed = budget.claim(config.wpb_seconds)
    except Exhausted:
        if old_model is not None:
            return old_model
        raise
    started = budget.clock()
    try:
        candidate = trainer(instance, indices, allowed, seed, config)
        loss = sum(p != instance.y[i] for i, p in zip(indices, predict(candidate, instance, indices)))
        return candidate if old_loss is None or loss < old_loss else old_model
    except Exception as exc:
        events.append({"event": "fit_failure", "seed": seed, "error": repr(exc)})
        if old_model is not None:
            return old_model
        raise FitFailed(str(exc)) from exc
    finally:
        elapsed = budget.clock() - started
        if elapsed > allowed:
            budget.overruns.append({"call": budget.calls, "allowed": allowed,
                                    "elapsed": elapsed, "excess": elapsed - allowed})


def valid_assignments(assignments, n):
    return len(assignments) == n and all(v in (0, 1) for v in assignments) and set(assignments) == {0, 1}


def partition_key(assignments):
    values = tuple(int(v) for v in assignments)
    return bytes(values if values[0] == 0 else tuple(1-v for v in values))


@dataclass(frozen=True)
class Solution:
    assignments: tuple[int, ...]
    models: tuple[Model, Model]
    predictions: tuple[tuple[int, ...], tuple[int, ...]]
    loss: int


def evaluate(instance: Instance, assignments, model1: Model, model2: Model) -> Solution:
    assignments = tuple(assignments)
    if not valid_assignments(assignments, instance.n):
        raise ValueError("Il faut une partition exclusive en deux groupes non vides.")
    z = tuple(int(v) for v in assignments)
    predictions = (predict(model1, instance), predict(model2, instance))
    loss = sum(predictions[z[i]][i] != instance.y[i] for i in range(instance.n))
    return Solution(z, (model1, model2), predictions, loss)


def solution_payload(solution: Solution, instance: Instance):
    return {"assignments": list(solution.assignments),
            "models": [model.yaml for model in solution.models],
            "predictions": [list(p) for p in solution.predictions],
            "LG": solution.loss, "error_rate": solution.loss / instance.n,
            "group_sizes": [solution.assignments.count(k) for k in (0, 1)],
            "category_counts_by_group": [[sum(z == k and y == c for z, y in zip(solution.assignments, instance.y))
                                          for c in range(instance.C)] for k in (0, 1)]}


def restore_solution(payload: dict, instance: Instance):
    models = tuple(Model(text) for text in payload["models"])
    if len(models) != 2:
        raise ValueError("Deux modèles sont requis.")
    solution = evaluate(instance, payload["assignments"], *models)
    if solution.loss != payload["LG"] or [list(p) for p in solution.predictions] != payload["predictions"]:
        raise ValueError("Score ou prédictions différents après rechargement.")
    return solution
