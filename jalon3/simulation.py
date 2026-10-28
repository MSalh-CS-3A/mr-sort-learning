"""Une partie : A envoie, H brouille, B apprend, puis on évalue B sur des objets neufs."""

from dataclasses import dataclass
import time
import zlib

import numpy as np
from lincs import classification as lc

from jalon2.apprentissage import Donnees
from .interface import Decision, Vue, bornes, classer, donnees, tirer_modele, tirer_objets


@dataclass(frozen=True)
class Instance:
    probleme: lc.Problem
    modele_a: lc.Model
    donnees_a: Donnees
    test: Donnees  # Jamais montré à H ni à B.


def graine_derivee(graine, *elements):
    """Graine stable par élément : hash() de Python change à chaque lancement, crc32 non."""
    return [graine, *(zlib.crc32(str(e).encode()) for e in elements)]


def generer_instance(criteres, categories, taille, graine, taille_test=1000):
    """M_A et le jeu de test ne dépendent pas de `taille` : on peut comparer les tailles."""
    probleme = lc.generate_problem(criteres, categories, graine)
    rng = np.random.default_rng(graine_derivee(graine, "modele", criteres, categories))
    modele = tirer_modele(probleme, rng)
    test = donnees(probleme, *tirer_objets(probleme, modele, taille_test, rng))
    rng = np.random.default_rng(graine_derivee(graine, "donnees_a", criteres, categories, taille))
    return Instance(probleme, modele, donnees(probleme, *tirer_objets(probleme, modele, taille, rng)), test)


def brouiller(instance, strategie, ratio, graine):
    """Données de H, vérifiées : au plus `ratio` donnée par donnée de A, dans le domaine public."""
    nombre = round(ratio * len(instance.donnees_a.y))
    n = len(instance.probleme.criteria)
    if strategie is None or nombre == 0:
        return np.zeros((0, n)), np.zeros(0, dtype=int)
    vue = Vue(instance.probleme, nombre, instance.donnees_a if strategie.voit_donnees_a else None)
    rng = np.random.default_rng(graine_derivee(graine, "hacker", strategie.nom, ratio))
    x, y = strategie.fonction(vue, rng)
    x, y = np.asarray(x, dtype=float), np.asarray(y)
    if x.ndim != 2 or x.shape[1] != n or y.shape != (len(x),) or len(x) > nombre:
        raise ValueError(f"Hacker {strategie.nom} : attendu x de forme (≤{nombre}, {n}) "
                         f"et y de forme (len(x),), reçu {x.shape} et {y.shape}.")
    if len(y) and (not np.issubdtype(y.dtype, np.integer) or y.min() < 0
                   or y.max() >= len(instance.probleme.ordered_categories)):
        raise ValueError(f"Hacker {strategie.nom} : catégories hors de 0..C-1.")
    bas, haut = bornes(instance.probleme)
    if not np.isfinite(x).all() or (x < bas).any() or (x > haut).any():
        raise ValueError(f"Hacker {strategie.nom} : performances hors des bornes du problème.")
    return x, y.astype(int)


def recevoir(instance, x_h, y_h, graine):
    """Mélange hors ligne : ordre aléatoire et noms neutres ; la source reste cachée à B."""
    a = instance.donnees_a
    x = np.vstack([a.x, x_h])
    y = np.concatenate([a.y, y_h])
    source_h = np.concatenate([np.zeros(len(a.y), dtype=bool), np.ones(len(y_h), dtype=bool)])
    ordre = np.random.default_rng(graine_derivee(graine, "melange")).permutation(len(y))
    return donnees(instance.probleme, x[ordre], y[ordre]), source_h[ordre]


def decider(strategie, recu, graine, temps):
    """Appeler la défense et vérifier sa décision ; renvoie aussi le temps réel."""
    debut = time.monotonic()
    decision = strategie.fonction(recu, graine, temps)
    duree = time.monotonic() - debut
    if not isinstance(decision, Decision) or not isinstance(decision.modele, lc.Model):
        raise TypeError(f"Défense {strategie.nom} : il faut renvoyer Decision(modele_lincs, suspects).")
    if decision.suspects is not None and np.shape(decision.suspects) != (len(recu.y),):
        raise ValueError(f"Défense {strategie.nom} : `suspects` doit avoir une valeur par ligne reçue.")
    return decision, duree


def evaluer(instance, decision, source_h):
    """Fidélité à M_A sur le test ; détection si la défense désigne des suspects."""
    test = instance.test
    mesures = {"fidelite": float(np.mean(classer(instance.probleme, decision.modele, test.x) == test.y))}
    if decision.suspects is not None:
        suspects = np.asarray(decision.suspects, dtype=bool)
        if source_h.any():
            mesures["detection_h"] = float(suspects[source_h].mean())
        mesures["rejet_a"] = float(suspects[~source_h].mean())
    return mesures
