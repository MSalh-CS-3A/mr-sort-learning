"""Initialisations et heuristiques A0-A4. Lire resoudre(), puis la méthode choisie."""

from dataclasses import dataclass
import math
import time
import warnings

import numpy as np

from .apprentissage import apprendre, distances_categorie, predire


@dataclass(frozen=True)
class Etat:
    z: np.ndarray                 # Groupe 0 ou 1 de chaque observation.
    modeles: tuple
    predictions: np.ndarray       # Deux lignes : prédictions des deux modèles.
    lg: int


@dataclass
class Resultat:
    meilleur: Etat | None
    temps: float
    arret: str
    trace: list


def partition_valide(z):
    return np.isin(z, [0, 1]).all() and set(z) == {0, 1}


def uniforme(n, rng):
    if n < 2:
        raise ValueError("Il faut au moins deux observations pour former deux groupes.")
    z = rng.integers(0, 2, size=n)
    while not partition_valide(z):
        z = rng.integers(0, 2, size=n)
    return z


def initialiser(donnees, choix, rng, fin):
    if choix == "uniforme":
        return uniforme(len(donnees.y), rng)
    from sklearn.mixture import GaussianMixture

    # Copie normalisée et orientée, uniquement pour le GMM.
    x = donnees.x.copy()
    for j, critere in enumerate(donnees.probleme.criteria):
        domaine = critere.real_values
        etendue = domaine.max_value - domaine.min_value
        x[:, j] = (x[:, j] - domaine.min_value) / etendue if etendue else 0
        if domaine.is_decreasing:
            x[:, j] = 1 - x[:, j]
    z = np.zeros(len(donnees.y), dtype=int)
    for categorie in range(len(donnees.probleme.ordered_categories)):
        if time.monotonic() >= fin:
            raise TimeoutError("Budget épuisé pendant le GMM.")
        indices = np.flatnonzero(donnees.y == categorie)
        if not len(indices):
            continue
        try:
            if len(np.unique(x[indices], axis=0)) < 2:
                raise ValueError("Catégorie trop petite ou constante.")
            gmm = GaussianMixture(n_components=2, covariance_type="diag", n_init=5, reg_covar=1e-6,
                                  max_iter=200, random_state=int(rng.integers(2_000_000_000)))
            gmm.fit(x[indices])
            if not gmm.converged_:
                raise ValueError("GMM non convergé.")
            bas, haut = sorted(range(2), key=lambda k: (
                float(gmm.means_[k].mean()), tuple(gmm.means_[k]), k))
            probabilites = gmm.predict_proba(x[indices])
            z[indices] = probabilites[:, haut] > probabilites[:, bas]
        except (ValueError, FloatingPointError, np.linalg.LinAlgError) as erreur:
            warnings.warn(f"GMM, catégorie {categorie} : recours uniforme ({erreur}).", stacklevel=2)
            z[indices] = rng.integers(0, 2, size=len(indices))
    return z if partition_valide(z) else uniforme(len(z), rng)


def entrainer_partition(donnees, z, rng, fin, temps_appel, ancien=None):
    if len(z) != len(donnees.y) or not partition_valide(z):
        raise ValueError("Il faut deux groupes non vides couvrant toutes les lignes.")
    modeles = tuple(apprendre(donnees, np.flatnonzero(z == k), rng, fin, temps_appel,
                             ancien.modeles[k] if ancien else None) for k in (0, 1))
    predictions = np.array([predire(donnees, modele) for modele in modeles])
    lg = int(np.count_nonzero(predictions[z, np.arange(len(z))] != donnees.y))
    z = z.copy()
    z.setflags(write=False)
    predictions.setflags(write=False)
    return Etat(z, modeles, predictions, lg)


def noter(trace, etat):
    meilleur = min(etat.lg, trace[-1]["meilleur_LG"]) if trace else etat.lg
    trace.append({"temps": time.monotonic(), "LG_courant": etat.lg, "meilleur_LG": meilleur})


def transferts_evidents(donnees, etat):
    z = etat.z.copy()
    correct = etat.predictions == donnees.y
    for i, groupe in enumerate(etat.z):
        if not correct[groupe, i] and correct[1-groupe, i]:
            z[i] = 1-groupe
    if not partition_valide(z):
        # Garder la première observation du groupe qui allait se vider.
        donneur = 1-int(z[0])
        z[np.flatnonzero(etat.z == donneur)[0]] = donneur
    return z


def a1(donnees, etat, rng, fin, temps_appel, trace):
    """Transférer les cas faux-vers-vrai, puis réentraîner les deux groupes."""
    while time.monotonic() < fin and etat.lg > 0:
        z = transferts_evidents(donnees, etat)
        transferts = np.count_nonzero(z != etat.z)
        if not transferts:
            break
        candidat = entrainer_partition(donnees, z, rng, fin, temps_appel, etat)
        if candidat.lg > etat.lg - transferts:
            raise AssertionError("Le garde-fou doit garantir LG' <= LG - transferts.")
        etat = candidat
        noter(trace, etat)
    return etat


def cle_partition(z):
    return tuple(z if z[0] == 0 else 1-z)  # Identifier aussi la permutation globale.


def a2(donnees, etat, rng, fin, temps_appel, trace):
    """A1 et affectations ambiguës par distance MR-Sort, sans tirage de transfert."""
    visites = {cle_partition(etat.z)}
    stagnation = 0
    while time.monotonic() < fin and etat.lg > 0 and stagnation < 20:
        z = transferts_evidents(donnees, etat)
        favorables = np.count_nonzero(z != etat.z)
        correct = etat.predictions == donnees.y
        ambigus = np.flatnonzero(correct[0] == correct[1])
        if len(ambigus):
            try:
                distances = np.array([distances_categorie(donnees, modele, predictions, fin)
                                      for modele, predictions in zip(etat.modeles, etat.predictions)])
            except TimeoutError:
                return etat
            for i in ambigus:
                groupe = etat.z[i]
                actuelle, autre = distances[groupe, i], distances[1-groupe, i]
                if np.isclose(actuelle, autre, rtol=0, atol=1e-12):
                    continue
                # Deux justes : maximiser la robustesse. Deux faux : minimiser
                # la distance pour atteindre exactement la catégorie observée.
                preferable = autre > actuelle if correct[groupe, i] else autre < actuelle
                if preferable:
                    z[i] = 1-groupe
            if not partition_valide(z):
                donneur = 1-int(z[0])
                transferes = ambigus[(etat.z[ambigus] == donneur) & (z[ambigus] != donneur)]
                z[transferes[0]] = donneur  # Départage déterministe par indice.
        if np.array_equal(z, etat.z):
            break
        stagnation += 1
        cle = cle_partition(z)
        # La mémoire bloque les cycles neutres, pas une amélioration évidente.
        if cle in visites and not favorables:
            break
        candidat = entrainer_partition(donnees, z, rng, fin, temps_appel, etat)
        if candidat.lg <= etat.lg:
            if candidat.lg < etat.lg:
                stagnation = 0
            visites.add(cle)
            etat = candidat
            noter(trace, etat)
    return etat


def voisins(donnees, etat, rng):
    """Au plus 8 déplacements et 8 échanges, moitié guidés par les erreurs."""
    erreurs = np.flatnonzero(etat.predictions[etat.z, np.arange(len(etat.z))] != donnees.y)
    vus = {cle_partition(etat.z)}
    for echange in (False, True):
        for numero in range(8):
            for _ in range(30):
                i = int(rng.choice(erreurs)) if numero < 4 and len(erreurs) else int(rng.integers(len(etat.z)))
                z = etat.z.copy()
                z[i] = 1-z[i]
                if echange:
                    j = int(rng.choice(np.flatnonzero(etat.z != etat.z[i])))
                    z[j] = 1-z[j]
                cle = cle_partition(z)
                if partition_valide(z) and cle not in vus:
                    vus.add(cle)
                    yield z
                    break


def a3(donnees, etat, rng, fin, temps_appel, trace):
    """Réentraîner les voisins et adopter la meilleure amélioration évaluée."""
    while time.monotonic() < fin and etat.lg > 0:
        meilleur = etat
        for z in voisins(donnees, etat, rng):
            if time.monotonic() >= fin:
                break
            candidat = entrainer_partition(donnees, z, rng, fin, temps_appel, etat)
            if candidat.lg < meilleur.lg:
                meilleur = candidat
            if meilleur.lg == 0:
                break
        if meilleur is etat:
            break
        etat = meilleur
        noter(trace, etat)
    return etat


def a4(donnees, etat, rng, fin, temps_appel, trace):
    """Descente A3, perturbation de 1 à 10 %, puis nouvelle descente."""
    etat = a3(donnees, etat, rng, fin, temps_appel, trace)
    meilleur, fraction = etat, .01
    for _ in range(10):
        if time.monotonic() >= fin or meilleur.lg == 0:
            break
        nombre = min(len(etat.z)-1, max(1, math.ceil(fraction*len(etat.z))))
        for _ in range(30):
            z = etat.z.copy()
            indices = rng.choice(len(z), size=nombre, replace=False)
            z[indices] = 1-z[indices]
            if partition_valide(z) and cle_partition(z) != cle_partition(etat.z):
                break
        else:
            break
        etat = entrainer_partition(donnees, z, rng, fin, temps_appel, etat)
        noter(trace, etat)  # L'état courant peut se dégrader ; la trace garde le meilleur LG.
        etat = a3(donnees, etat, rng, fin, temps_appel, trace)
        if etat.lg < meilleur.lg:
            meilleur, fraction = etat, .01
        else:
            fraction = min(.10, fraction*2)
    return meilleur


def resoudre(donnees, methode="A1", initialisation="uniforme", temps=30, temps_appel=1, graine=0):
    """Initialiser, apprendre, rechercher, puis redémarrer dans le même budget.

    A0 est exactement cette boucle sans l'étape de recherche de partition.
    Chaque méthode reçoit la même première initialisation pour une même graine.
    """
    if methode not in {"A0", "A1", "A2", "A3", "A4"} or initialisation not in {"uniforme", "gmm"}:
        raise ValueError("Méthode ou initialisation inconnue.")
    if not np.isfinite([temps, temps_appel]).all() or min(temps, temps_appel) <= 0 or graine < 0:
        raise ValueError("Temps positifs et finis et graine positive ou nulle requis.")
    rng = np.random.default_rng(graine)
    debut = time.monotonic()
    fin = debut + temps
    meilleur, trace = None, []
    recherches = {"A1": a1, "A2": a2, "A3": a3, "A4": a4}
    while time.monotonic() < fin:
        try:
            z = initialiser(donnees, initialisation, rng, fin)
            etat = entrainer_partition(donnees, z, rng, fin, temps_appel)
            noter(trace, etat)
            if meilleur is None or etat.lg < meilleur.lg:
                meilleur = etat
            if methode != "A0":
                etat = recherches[methode](donnees, etat, rng, fin, temps_appel, trace)
                if etat.lg < meilleur.lg:
                    meilleur = etat
            if meilleur.lg == 0:
                break
        except TimeoutError:
            break
    for ligne in trace:
        ligne["temps"] -= debut
    arret = "zero_erreur" if meilleur is not None and meilleur.lg == 0 else "budget"
    return Resultat(meilleur, time.monotonic()-debut, arret, trace)
