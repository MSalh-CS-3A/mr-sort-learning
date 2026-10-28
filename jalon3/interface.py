"""Ce qu'une stratégie reçoit et renvoie, et les outils pour en écrire une.

Un hacker est une fonction f(vue, rng) -> (x, y), enregistrée avec @hacker.
Une défense est une fonction f(recu, graine, temps) -> Decision, enregistrée avec @defense.
Les catégories sont les indices lincs 0, ..., C-1, comme dans le jalon 2.
"""

from dataclasses import dataclass
import importlib
import inspect

import numpy as np
from lincs import classification as lc

from jalon2.apprentissage import Donnees, predire


@dataclass(frozen=True)
class Vue:
    """Ce que H sait : le problème public et le nombre de données qu'il peut envoyer."""
    probleme: lc.Problem
    nombre: int
    donnees_a: Donnees | None = None  # Seulement pour un hacker enregistré avec voit_donnees_a=True.


@dataclass(frozen=True)
class Decision:
    modele: lc.Model                    # Le modèle que B attribue à A.
    suspects: np.ndarray | None = None  # Facultatif : True si B pense que la ligne vient de H.


@dataclass(frozen=True)
class Strategie:
    nom: str
    fonction: object
    fichier: str
    voit_donnees_a: bool = False


HACKERS = {}
DEFENSES = {}


def _enregistrer(registre, nom, fonction, **options):
    fichier = inspect.getmodule(fonction).__name__.rsplit(".", 1)[-1]
    if nom == "aucun":
        raise ValueError("« aucun » est réservé à la référence sans brouillage (ratio 0).")
    if nom in registre:
        raise ValueError(f"Nom déjà pris par {registre[nom].fichier}.py : {nom}")
    registre[nom] = Strategie(nom, fonction, fichier, **options)
    return fonction


def hacker(nom, voit_donnees_a=False):
    """Enregistrer f(vue, rng) -> (x, y) : au plus vue.nombre objets et leurs catégories."""
    return lambda fonction: _enregistrer(HACKERS, nom, fonction, voit_donnees_a=voit_donnees_a)


def defense(nom):
    """Enregistrer f(recu, graine, temps) -> Decision. `recu` ne dit pas qui a envoyé chaque ligne."""
    return lambda fonction: _enregistrer(DEFENSES, nom, fonction)


def charger_strategies():
    """Importer les dossiers hackers/ et defenses/ remplit les deux registres."""
    importlib.import_module("jalon3.hackers")
    importlib.import_module("jalon3.defenses")
    return HACKERS, DEFENSES


def donnees(probleme, x, y, noms=None):
    """Jeu au format du jalon 2, en lecture seule, avec des noms neutres par défaut."""
    y = np.array(y, dtype=int)
    x = np.array(x, dtype=float).reshape(len(y), len(probleme.criteria))
    noms = tuple(noms) if noms is not None else tuple(f"objet {i + 1}" for i in range(len(y)))
    x.setflags(write=False)
    y.setflags(write=False)
    return Donnees(None, probleme, noms, x, y)


def classer(probleme, modele, x):
    """Catégories attribuées par un modèle lincs à des performances x."""
    x = np.asarray(x, dtype=float)
    if not len(x):
        return np.zeros(0, dtype=int)
    return predire(donnees(probleme, x, np.zeros(len(x), dtype=int)), modele)


def bornes(probleme):
    criteres = probleme.criteria
    return (np.array([c.real_values.min_value for c in criteres]),
            np.array([c.real_values.max_value for c in criteres]))


def objets_uniformes(probleme, nombre, rng):
    """Performances tirées uniformément dans les bornes publiques."""
    bas, haut = bornes(probleme)
    return bas + rng.random((nombre, len(bas))) * (haut - bas)


def tirer_modele(probleme, rng, part_minimale=.005, essais=100):
    """MR-Sort aléatoire de lincs dont aucune catégorie n'est quasi vide.

    Sur des objets uniformes, un modèle tiré au hasard laisse souvent une
    catégorie presque vide ; le générateur équilibré de lincs peut alors
    chercher très longtemps des objets de cette catégorie.
    """
    essai = objets_uniformes(probleme, 2000, rng)
    categories = len(probleme.ordered_categories)
    for _ in range(essais):
        modele = lc.generate_mrsort_model(probleme, int(rng.integers(2_000_000_000)))
        parts = np.bincount(classer(probleme, modele, essai), minlength=categories) / len(essai)
        if parts.min() >= part_minimale:
            return modele
    raise RuntimeError(f"Aucun modèle sans catégorie quasi vide en {essais} essais.")


def tirer_objets(probleme, modele, nombre, rng, desequilibre=.2):
    """Objets classés par `modele`, chaque catégorie à ±20 % de l'équilibre (générateur lincs)."""
    if nombre == 0:
        return np.zeros((0, len(probleme.criteria))), np.zeros(0, dtype=int)
    objets = lc.generate_alternatives(probleme, modele, nombre, int(rng.integers(2_000_000_000)),
                                      max_imbalance=desequilibre).alternatives
    x = np.array([[v.real.value for v in a.profile] for a in objets], dtype=float)
    y = np.array([a.category_index for a in objets], dtype=int)
    return x, y
