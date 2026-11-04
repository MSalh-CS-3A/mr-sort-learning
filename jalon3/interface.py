"""Ce qu'une stratégie reçoit et renvoie, et les outils pour en écrire une.

Un hacker est une fonction f(vue, rng) -> (x, y), enregistrée avec @hacker.
Une défense est une fonction f(recu, graine, temps) -> Decision, enregistrée avec @defense.
Les catégories sont les indices lincs 0, ..., C-1, comme dans le jalon 2.
Un modèle est un modèle lincs ou tout objet doté de predict(x), comme le MRSort du jalon 2.
"""

from dataclasses import dataclass
import importlib
import inspect

import numpy as np
from lincs import classification as lc


@dataclass(frozen=True)
class Donnees:
    """Objets reçus ou générés : performances x (m, n) et catégories y, en lecture seule."""
    probleme: lc.Problem
    noms: tuple
    x: np.ndarray
    y: np.ndarray


@dataclass(frozen=True)
class Vue:
    """Ce que H sait : le problème public et le nombre de données qu'il peut envoyer."""
    probleme: lc.Problem
    nombre: int
    donnees_a: Donnees | None = None  # Seulement pour un hacker enregistré avec voit_donnees_a=True.


@dataclass(frozen=True)
class Decision:
    modele: object                      # Le modèle que B attribue à A : lincs ou doté de predict(x).
    suspects: np.ndarray | None = None  # Facultatif : True si B pense que la ligne vient de H.
    segmentation: object | None = None  # Sortie de B pour les diagnostics ; jamais une vérité cachée.
    groupe: int | None = None           # Groupe dont B conserve le modèle.
    details: dict | None = None


@dataclass(frozen=True)
class Segmentation:
    segment: np.ndarray
    modeles: tuple


@dataclass(frozen=True)
class Brouillage:
    """Injection de H ; le modèle facultatif est réservé au simulateur, jamais à B.

    L'itération conserve le contrat historique ``x, y = brouillage``.
    Une attaque peut toujours renvoyer le simple couple (x, y).
    """
    x: np.ndarray
    y: np.ndarray
    modele: object | None = None

    def __iter__(self):
        yield self.x
        yield self.y


@dataclass(frozen=True)
class Strategie:
    nom: str
    fonction: object
    fichier: str
    voit_donnees_a: bool = False
    preparer: object | None = None  # (recu, graine, temps) -> Segmentation, partagé dans une condition.
    groupe_alea: str | None = None  # Facultatif : appariement de deux variantes d'une attaque.


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


def hacker(nom, voit_donnees_a=False, groupe_alea=None):
    """Enregistrer f(vue, rng) -> (x, y) : au plus vue.nombre objets et leurs catégories."""
    return lambda fonction: _enregistrer(HACKERS, nom, fonction, voit_donnees_a=voit_donnees_a,
                                         groupe_alea=groupe_alea)


def defense(nom, preparer=None):
    """Enregistrer f(recu, graine, temps) -> Decision. `recu` ne dit pas qui a envoyé chaque ligne."""
    return lambda fonction: _enregistrer(DEFENSES, nom, fonction, preparer=preparer)


def charger_strategies():
    """Importer les dossiers hackers/ et defenses/ remplit les deux registres."""
    importlib.import_module("jalon3.hackers")
    importlib.import_module("jalon3.defenses")
    return HACKERS, DEFENSES


def donnees(probleme, x, y, noms=None):
    """Jeu en lecture seule, avec des noms neutres par défaut."""
    y = np.array(y, dtype=int)
    x = np.array(x, dtype=float).reshape(len(y), len(probleme.criteria))
    noms = tuple(noms) if noms is not None else tuple(f"objet {i + 1}" for i in range(len(y)))
    x.setflags(write=False)
    y.setflags(write=False)
    return Donnees(probleme, noms, x, y)


def classer(probleme, modele, x):
    """Catégories attribuées à des performances x par un modèle lincs ou doté de predict(x)."""
    x = np.asarray(x, dtype=float)
    if not len(x):
        return np.zeros(0, dtype=int)
    if not isinstance(modele, lc.Model):
        return np.asarray(modele.predict(x), dtype=int)
    objets = lc.Alternatives(probleme, [
        lc.Alternative(f"objet {i + 1}", [lc.Performance(lc.Performance.Real(float(v))) for v in ligne], 0)
        for i, ligne in enumerate(x)])
    lc.classify_alternatives(probleme, modele, objets)
    return np.array([a.category_index for a in objets.alternatives], dtype=int)


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

    Filtre symétrique A/H : au moins 0,5 % par catégorie sur un contrôle
    uniforme de 2 000 points, distinct de l'apprentissage et du test.
    C'est un seuil empirique, pas une garantie sur les probabilités réelles.
    """
    essai = objets_uniformes(probleme, 2000, rng)
    categories = len(probleme.ordered_categories)
    for _ in range(essais):
        modele = lc.generate_mrsort_model(probleme, int(rng.integers(2_000_000_000)))
        parts = np.bincount(classer(probleme, modele, essai), minlength=categories) / len(essai)
        if parts.min() >= part_minimale:
            return modele
    raise RuntimeError(f"Aucun modèle sans catégorie quasi vide en {essais} essais.")


def tirer_objets(probleme, modele, nombre, rng):
    """Performances uniformes indépendantes ; classes exactes, sans équilibrage.

    À état initial de rng identique, les petits jeux sont les préfixes des grands.
    """
    x = objets_uniformes(probleme, nombre, rng)
    return x, classer(probleme, modele, x)
