"""Initialisations indépendantes des recherches ; aucune source cachée utilisée."""

from __future__ import annotations

import warnings

import numpy as np

from .core import Budget, Config, Exhausted, Seeds, valid_assignments
from .data import Instance


def uniform(n: int, rng) -> tuple[int, ...]:
    if n < 2:
        raise ValueError("Deux groupes non vides demandent au moins deux observations.")
    while True:
        values = tuple(int(v) for v in (rng.random(n) >= 0.5))
        if valid_assignments(values, n):
            return values


def component_order(means):
    return sorted(range(2), key=lambda k: (float(np.mean(means[k])), tuple(means[k]), k))


def initialize(instance: Instance, config: Config, seeds: Seeds,
               budget: Budget | None = None, events: list[dict] | None = None):
    events = [] if events is None else events
    rng = seeds.rng("partition")
    if instance.n < 2:
        raise ValueError("Au moins deux observations sont nécessaires.")
    if budget is not None and not budget.available():
        raise Exhausted("Budget épuisé avant l'initialisation.")
    if config.initializer == "uniform":
        return uniform(instance.n, rng)
    # L'import et l'ajustement font partie du budget de l'initialisation GMM.
    from sklearn.exceptions import ConvergenceWarning
    from sklearn.mixture import GaussianMixture

    problem = instance.problem()
    transformed = np.array(instance.x, dtype=float, copy=True)
    for j, criterion in enumerate(problem.criteria):
        domain = criterion.real_values if criterion.is_real else criterion.integer_values
        span = domain.max_value - domain.min_value
        transformed[:, j] = (transformed[:, j] - domain.min_value) / span if span else 0.0
        if domain.is_decreasing:
            transformed[:, j] = 1.0 - transformed[:, j]
    assignments = np.zeros(instance.n, dtype=int)
    for category in range(instance.C):
        if budget is not None and not budget.available():
            raise Exhausted("Budget épuisé pendant l'initialisation GMM.")
        ids = np.flatnonzero(np.array(instance.y) == category)
        if not len(ids):
            continue
        values = transformed[ids]
        seed = seeds.next("gmm")
        try:
            if len(ids) < 2 or len(np.unique(values, axis=0)) < 2:
                raise ValueError("Catégorie trop petite ou performances constantes.")
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always", ConvergenceWarning)
                gmm = GaussianMixture(n_components=2, covariance_type="diag",
                                      n_init=config.gmm_n_init, reg_covar=config.gmm_reg_covar,
                                      max_iter=config.gmm_max_iter, random_state=seed).fit(values)
            for warning in caught:
                events.append({"event": "gmm_warning", "category": category, "message": str(warning.message)})
            if not gmm.converged_:
                raise ValueError("EM n'a pas convergé.")
            low, high = component_order(gmm.means_)
            responsibilities = gmm.predict_proba(values)
            # Egalité : composante de centre le plus bas, déterministe.
            assignments[ids] = (responsibilities[:, high] > responsibilities[:, low]).astype(int)
        except (ValueError, FloatingPointError, np.linalg.LinAlgError) as exc:
            assignments[ids] = (rng.random(len(ids)) >= 0.5).astype(int)
            events.append({"event": "gmm_fallback", "category": category, "seed": seed, "reason": str(exc)})
    result = tuple(int(v) for v in assignments)
    if not valid_assignments(result, instance.n):
        events.append({"event": "gmm_fallback", "reason": "Groupe final vide ; initialisation uniforme globale."})
        result = uniform(instance.n, rng)
    return result
