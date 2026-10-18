"""A0-A4 : propositions transactionnelles, apprentissage protégé, meilleur état."""

from __future__ import annotations

from dataclasses import dataclass, field
import math

import numpy as np
from threadpoolctl import threadpool_limits

from .core import (Budget, Config, Exhausted, FitFailed, Seeds, Solution, evaluate,
                   fit_guarded, partition_key, valid_assignments, wpb_fit)
from .data import Instance
from .initializers import initialize


@dataclass
class SearchResult:
    best: Solution | None
    status: str
    stop_reason: str
    wall_time: float
    trace: list[dict]
    events: list[dict]
    seeds: list[dict]
    counters: dict
    overruns: list[dict]
    extra: dict = field(default_factory=dict)


def obvious_moves(instance: Instance, state: Solution):
    z = list(state.assignments)
    for i, old in enumerate(state.assignments):
        if state.predictions[old][i] != instance.y[i] and state.predictions[1-old][i] == instance.y[i]:
            z[i] = 1-old
    if len(set(z)) == 1:
        donor = 1-z[0]
        # Garder le premier indice transférable dans le groupe devenu vide.
        keep = next(i for i, old in enumerate(state.assignments) if old == donor)
        z[keep] = donor
    return tuple(z), sum(a != b for a, b in zip(z, state.assignments))


def local_neighbors(instance: Instance, state: Solution, rng, limit: int = 16):
    """Huit déplacements / huit échanges à 16, moitié guidés dans chaque type."""
    z = np.array(state.assignments)
    errors = np.array([i for i in range(instance.n) if state.predictions[z[i]][i] != instance.y[i]], dtype=int)
    seen = {partition_key(z)}
    result = []
    sizes = [("move", (limit+1)//2), ("swap", limit//2)]
    for kind, count in sizes:
        for slot in range(count):
            guided = slot < count//2
            for _ in range(max(20, min(instance.n, 100))):
                pool = errors if guided and len(errors) else np.arange(instance.n)
                i = int(rng.choice(pool))
                candidate = z.copy()
                candidate[i] = 1-candidate[i]
                if kind == "swap":
                    j = int(rng.choice(np.flatnonzero(z != z[i])))
                    candidate[j] = 1-candidate[j]
                if not valid_assignments(candidate, instance.n):
                    continue
                key = partition_key(candidate)
                if key in seen:
                    continue
                seen.add(key)
                result.append(tuple(int(v) for v in candidate))
                break
    return result


class Search:
    def __init__(self, instance: Instance, config: Config, seed: int,
                 trainer=wpb_fit, budget: Budget | None = None):
        self.instance, self.config, self.trainer = instance, config, trainer
        self.budget = budget or Budget(config.seconds, config.max_calls)
        self.seeds = Seeds(seed)
        self.best = None
        self.trace, self.events = [], []
        self.counters = {"candidates_evaluated": 0, "accepted_moves": 0,
                         "transfers": 0, "perturbations": 0, "restarts": 0}

    def record(self, state: Solution, event: str):
        if self.best is None or state.loss < self.best.loss:
            self.best = state
        self.trace.append({"time": self.budget.elapsed, "current_LG": state.loss,
                           "best_LG": self.best.loss, "event": event,
                           "group_sizes": [state.assignments.count(k) for k in (0, 1)]})

    def candidate(self, assignments, old: Solution | None = None):
        models = []
        # Pas de candidat fictif réévaluant à l'infini les anciens modèles.
        if not self.budget.available():
            raise Exhausted("Budget épuisé avant une proposition.")
        for k in (0, 1):
            indices = [i for i, z in enumerate(assignments) if z == k]
            model = fit_guarded(self.instance, indices, old.models[k] if old else None,
                                self.budget, self.seeds.next(f"wpb_group_{k}"), self.config,
                                self.events, self.trainer)
            models.append(model)
        self.counters["candidates_evaluated"] += 1
        return evaluate(self.instance, assignments, *models)

    def accept(self, old, new, event):
        self.counters["accepted_moves"] += 1
        self.counters["transfers"] += sum(a != b for a, b in zip(old.assignments, new.assignments))
        self.record(new, event)
        return new

    def a1(self, state):
        while self.budget.available() and state.loss:
            assignments, r = obvious_moves(self.instance, state)
            if not r:
                break
            candidate = self.candidate(assignments, state)
            if candidate.loss > state.loss-r:
                raise AssertionError("Violation de la borne de non-dégradation A1.")
            state = self.accept(state, candidate, "a1_transfer")
        return state

    def a2(self, state):
        visited = {partition_key(state.assignments)}
        stagnant = 0
        rng = self.seeds.rng("proposals")
        while self.budget.available() and state.loss and stagnant < self.config.stagnation:
            assignments, r = obvious_moves(self.instance, state)
            candidate_z = list(assignments)
            ambiguous = [i for i in range(self.instance.n)
                         if (state.predictions[0][i] == self.instance.y[i]) ==
                            (state.predictions[1][i] == self.instance.y[i])]
            count = min(len(ambiguous), max(1, math.ceil(self.instance.n*self.config.ambiguous_fraction)))
            if count:
                for i in rng.choice(ambiguous, count, replace=False):
                    candidate_z[i] = 1-candidate_z[i]
                    if not valid_assignments(candidate_z, self.instance.n):
                        candidate_z[i] = 1-candidate_z[i]
            key = partition_key(candidate_z)
            stagnant += 1
            if key in visited:
                continue
            candidate = self.candidate(candidate_z, state)
            if candidate.loss > state.loss-r:
                raise AssertionError("Violation de la borne de non-dégradation A2.")
            if candidate.loss <= state.loss:
                if candidate.loss < state.loss:
                    stagnant = 0
                visited.add(key)
                state = self.accept(state, candidate, "a2_transfer")
        self.events.append({"event": "a2_stop", "stagnation": stagnant, "visited": len(visited)})
        return state

    def a3(self, state):
        rng = self.seeds.rng("proposals")
        while self.budget.available() and state.loss:
            winner = None
            for assignments in local_neighbors(self.instance, state, rng, self.config.neighbors):
                if not self.budget.available():
                    break
                candidate = self.candidate(assignments, state)
                if candidate.loss < state.loss and (winner is None or candidate.loss < winner.loss):
                    winner = candidate
                if candidate.loss == 0:
                    break
            if winner is None:
                break
            state = self.accept(state, winner, "a3_improvement")
        return state

    def a4(self, state):
        state = self.a3(state)
        fraction = self.config.perturb_fraction
        rng = self.seeds.rng("perturbations")
        for _ in range(self.config.perturbations):
            if not self.budget.available() or self.best.loss == 0:
                break
            previous_best = self.best.loss
            z = list(state.assignments)
            size = min(self.instance.n-1, max(1, math.ceil(fraction*self.instance.n)))
            # Tirage avec refus des perturbations vidant un groupe.
            for _attempt in range(100):
                z = list(state.assignments)
                for i in rng.choice(self.instance.n, size=size, replace=False):
                    z[i] = 1-z[i]
                if valid_assignments(z, self.instance.n) and partition_key(z) != partition_key(state.assignments):
                    break
            else:
                self.events.append({"event": "perturbation_unavailable"})
                break
            candidate = self.candidate(z, state)
            self.counters["perturbations"] += 1
            state = self.accept(state, candidate, "a4_perturbation")
            state = self.a3(state)
            fraction = (self.config.perturb_fraction if self.best.loss < previous_best
                        else min(self.config.perturb_max_fraction, fraction*2))
        return state

    def run(self):
        reason = "budget"
        while self.budget.available():
            if self.config.max_restarts is not None and self.counters["restarts"] >= self.config.max_restarts:
                reason = "max_restarts"
                break
            self.counters["restarts"] += 1
            try:
                assignments = initialize(self.instance, self.config, self.seeds, self.budget, self.events)
                current = self.candidate(assignments)
                self.record(current, "initialization")
                if self.config.heuristic != "A0" and current.loss:
                    current = getattr(self, self.config.heuristic.lower())(current)
                if self.best.loss == 0:
                    reason = "zero_loss"
                    break
            except Exhausted:
                break
            except FitFailed as exc:
                self.events.append({"event": "restart_fit_failed", "error": str(exc)})
        if reason == "budget" and self.config.max_calls is not None and self.budget.calls >= self.config.max_calls:
            reason = "max_calls"
        return SearchResult(self.best, "ok" if self.best else "no_solution", reason,
                            self.budget.elapsed, self.trace, self.events, self.seeds.records,
                            {**self.counters, "wpb_calls": self.budget.calls}, self.budget.overruns)


def solve(instance: Instance, config: Config, seed: int = 0, **kwargs) -> SearchResult:
    if config.heuristic not in {"A0", "A1", "A2", "A3", "A4"}:
        raise ValueError("solve attend une heuristique A0-A4.")
    if instance.n < 2:
        raise ValueError("Deux groupes non vides demandent au moins deux observations.")
    with threadpool_limits(limits=1):
        return Search(instance, config, seed, **kwargs).run()
