"""Charger les CSV du projet, prédire et apprendre un MR-Sort avec lincs."""

from dataclasses import dataclass
from io import StringIO
from pathlib import Path
import re
import time
import warnings

import numpy as np
from lincs import classification as lc


@dataclass(frozen=True)
class Donnees:
    chemin: Path
    probleme: lc.Problem
    noms: tuple
    x: np.ndarray
    y: np.ndarray


def charger(chemin):
    """Les catégories sont les indices lincs 0, ..., C-1, jamais des sources."""
    chemin = Path(chemin)
    texte = (chemin.parent / "problem.yml").read_text(encoding="utf-8-sig")
    if not re.search(r"^kind\s*:", texte, re.MULTILINE):
        texte = "kind: classification-problem\n" + texte
    probleme = lc.Problem.load(StringIO(texte))
    if any(not c.is_real or not (c.real_values.is_increasing or c.real_values.is_decreasing)
           for c in probleme.criteria):
        raise ValueError("Cette version cible les critères réels monotones des CSV du projet.")
    with chemin.open(encoding="utf-8-sig") as fichier:
        objets = lc.Alternatives.load(probleme, fichier).alternatives
    noms = tuple(a.name for a in objets)
    x = np.array([[v.real.value for v in a.profile] for a in objets], dtype=float)
    y = np.array([a.category_index for a in objets], dtype=int)
    if len(y) < 2 or len(set(noms)) != len(y) or not np.isfinite(x).all():
        raise ValueError("Il faut au moins deux lignes, des noms uniques et des valeurs finies.")
    # Les algorithmes déplacent les indices ; ils ne modifient pas les données.
    x.setflags(write=False)
    y.setflags(write=False)
    return Donnees(chemin, probleme, noms, x, y)


def alternatives(donnees, indices):
    """Créer une copie : classifier avec lincs modifie les catégories de l'objet."""
    return lc.Alternatives(donnees.probleme, [
        lc.Alternative(donnees.noms[i], [lc.Performance(lc.Performance.Real(v))
                                       for v in donnees.x[i]], int(donnees.y[i]))
        for i in indices
    ])


def predire(donnees, modele, indices=None):
    indices = range(len(donnees.y)) if indices is None else indices
    objets = alternatives(donnees, indices)
    lc.classify_alternatives(donnees.probleme, modele, objets)
    return np.array([a.category_index for a in objets.alternatives], dtype=int)


def apprendre(donnees, indices, rng, fin, temps_appel, ancien=None):
    """WPB, puis garder l'ancien modèle s'il fait aussi bien sur le nouveau groupe.

    `fin` est l'échéance globale, lue avec time.monotonic(). La limite WPB est
    coopérative : une itération peut dépasser le temps demandé.
    """
    indices = np.asarray(indices, dtype=int)
    if not len(indices):
        raise ValueError("Un groupe ne peut pas être vide.")
    if time.monotonic() >= fin:
        if ancien is not None:
            return ancien
        raise TimeoutError("Budget épuisé avant l'apprentissage des deux modèles.")
    try:
        jeu = alternatives(donnees, indices)
        preparation = lc.PreprocessedLearningSet(donnees.probleme, jeu)
        population = lc.LearnMrsortByWeightsProfilesBreed.ModelsBeingLearned(
            preparation, 9, int(rng.integers(2_000_000_000)))
        profils = lc.InitializeProfilesForProbabilisticMaximalDiscriminationPowerPerCriterion(
            preparation, population)
        poids = lc.OptimizeWeightsUsingGlop(preparation, population)
        amelioration = lc.ImproveProfilesWithAccuracyHeuristicOnCpu(preparation, population)
        renouvellement = lc.ReinitializeLeastAccurate(population, profils, poids, 4)
        restant = fin - time.monotonic()
        if restant <= 0:
            raise TimeoutError("Budget épuisé pendant la préparation WPB.")
        arret = lc.TerminateWhenAny([
            lc.TerminateAtAccuracy(population, len(indices)),
            lc.TerminateAfterSeconds(min(temps_appel, restant)),
            lc.TerminateAfterIterations(population, 10_000),
        ])
        candidat = lc.LearnMrsortByWeightsProfilesBreed(
            preparation, population, profils, poids, amelioration, renouvellement, arret).perform()
        erreurs = np.count_nonzero(predire(donnees, candidat, indices) != donnees.y[indices])
    except Exception as erreur:
        if ancien is None:
            raise
        warnings.warn(f"Ancien modèle conservé après échec WPB : {erreur}", stacklevel=2)
        return ancien
    if ancien is not None:
        erreurs_ancien = np.count_nonzero(predire(donnees, ancien, indices) != donnees.y[indices])
        if erreurs_ancien <= erreurs:
            return ancien
    return candidat
