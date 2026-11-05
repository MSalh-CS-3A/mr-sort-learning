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


def coalitions_extremes(poids):
    """Coalitions gagnantes minimales et perdantes maximales au seuil lincs 1.

    On énumère les 2**m coalitions : les données du projet ont 6 à 10 critères.
    Une somme float32 dans l'ordre des critères reproduit la règle de lincs.
    """
    numeros = np.arange(2**len(poids))
    bits = 1 << np.arange(len(poids))
    masques = (numeros[:, None] & bits) != 0
    sommes = np.cumsum(np.where(masques, np.asarray(poids, dtype=np.float32), 0),
                       axis=1, dtype=np.float32)[:, -1]
    gagnantes = sommes >= 1
    minimales, maximales = gagnantes.copy(), ~gagnantes
    for bit in bits:
        minimales &= ~(((numeros & bit) != 0) & gagnantes[numeros & ~bit])
        maximales &= ~(((numeros & bit) == 0) & ~gagnantes[numeros | bit])
    return masques[minimales], masques[maximales]


def distances_categorie(donnees, modele, predictions, fin=float("inf")):
    """Distance L-inf normalisée à la sortie/entrée de la catégorie observée.

    Si la prédiction est juste : distance minimale pour devenir incorrect.
    Sinon : distance minimale pour atteindre exactement la catégorie observée.
    Les distances sont des infimums : rejeter un seuil exige une inégalité
    stricte. Une région inaccessible dans le domaine public donne +inf.
    Aucune performance ni aucun modèle n'est modifié.
    """
    x = donnees.x.copy()
    seuils = np.empty((len(modele.sufficient_coalitions), x.shape[1]))
    for j, critere in enumerate(donnees.probleme.criteria):
        domaine = critere.real_values
        etendue = domaine.max_value - domaine.min_value
        x[:, j] = (x[:, j] - domaine.min_value) / etendue if etendue else 0
        for h, seuil in enumerate(modele.accepted_values[j].real_thresholds.thresholds):
            valeur = (seuil - domaine.min_value) / etendue if etendue and seuil is not None else 0
            if domaine.is_decreasing and etendue:
                valeur = 1-valeur
            seuils[h, j] = valeur if seuil is not None else np.inf
        if domaine.is_decreasing and etendue:
            x[:, j] = 1-x[:, j]

    profils = []
    for seuil, coalition in zip(seuils, modele.sufficient_coalitions):
        if time.monotonic() >= fin:
            raise TimeoutError("Budget épuisé pendant le calcul des distances A2.")
        gagnantes, perdantes = coalitions_extremes(coalition.weights.criterion_weights)
        # Atteindre une coalition gagnante exige les critères de son masque.
        cout_entree = np.maximum(seuil-x, 0)
        entrees = np.max(np.where(gagnantes[None, :, :], cout_entree[:, None, :], 0), axis=2)
        # Pour rester dans une coalition perdante, rejeter les autres critères.
        # Un seuil à la borne favorable minimale est impossible à rejeter.
        cout_sortie = np.where(seuil > 0, np.maximum(x-seuil, 0), np.inf)
        sorties = np.max(np.where(~perdantes[None, :, :], cout_sortie[:, None, :], 0), axis=2)
        profils.append((gagnantes, perdantes, entrees, sorties))

    distances = np.full(len(x), np.inf)
    for categorie in np.unique(donnees.y):
        indices = np.flatnonzero(donnees.y == categorie)
        justes = predictions[indices] == categorie
        # Sortir par le bas ou par le haut ; les catégories extrêmes n'ont
        # qu'une frontière de sortie. On garde la plus proche des deux.
        if categorie > 0:
            distances[indices[justes]] = profils[categorie-1][3][indices[justes]].min(axis=1, initial=np.inf)
        if categorie < len(profils):
            haut = profils[categorie][2][indices[justes]].min(axis=1, initial=np.inf)
            distances[indices[justes]] = np.minimum(distances[indices[justes]], haut)

        indices = indices[~justes]
        if not len(indices):
            continue
        bas = profils[categorie-1] if categorie > 0 else None
        haut = profils[categorie] if categorie < len(profils) else None
        gagnantes = bas[0] if bas else np.zeros((1, x.shape[1]), dtype=bool)
        perdantes = haut[1] if haut else np.ones((1, x.shape[1]), dtype=bool)
        entrees = bas[2][indices] if bas else np.zeros((len(indices), 1))
        sorties = haut[3][indices] if haut else np.zeros((len(indices), 1))
        for s, gagnante in enumerate(gagnantes):
            if time.monotonic() >= fin:
                raise TimeoutError("Budget épuisé pendant le calcul des distances A2.")
            # Atteindre le profil inférieur ET rejeter le supérieur. Si leurs
            # seuils sont égaux, un même critère ne peut satisfaire les deux
            # exigences opposées. Cela détecte aussi les catégories vides.
            compatibles = np.ones(len(perdantes), dtype=bool)
            if bas is not None and haut is not None:
                conflits = gagnante & (seuils[categorie-1] >= seuils[categorie])
                compatibles = ~np.any(conflits & ~perdantes, axis=1)
            sortie = sorties[:, compatibles].min(axis=1, initial=np.inf)
            distance = np.maximum(entrees[:, s], sortie)
            distances[indices] = np.minimum(distances[indices], distance)
    return distances


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
