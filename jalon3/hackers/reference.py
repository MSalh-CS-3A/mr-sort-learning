"""Hackers de la partie 1 : bruit pur (E1) et MR-Sort tiré au hasard (E2)."""

import numpy as np

from jalon3.interface import Brouillage, bornes, hacker, objets_uniformes, tirer_modele, tirer_objets


@hacker("etiquettes_aleatoires")
def etiquettes_aleatoires(vue, rng):
    """Objets uniformes et catégories au hasard : aucun MR-Sort derrière."""
    rng_x, rng_y = [np.random.default_rng(int(rng.integers(2_000_000_000))) for _ in range(2)]
    x = objets_uniformes(vue.probleme, vue.nombre, rng_x)
    return x, rng_y.integers(len(vue.probleme.ordered_categories), size=vue.nombre)


@hacker("mrsort_aleatoire")
def mrsort_aleatoire(vue, rng):
    """H aveugle : un unique M_H indépendant, puis y_H = M_H(x_H), sans bruit."""
    modele = tirer_modele(vue.probleme, rng)
    return Brouillage(*tirer_objets(vue.probleme, modele, vue.nombre, rng), modele=modele)


@hacker("classe_basse", groupe_alea="classes_constantes")
def classe_basse(vue, rng):
    """Performances uniformes ; toutes les classes sont 0, sans accès à A."""
    return objets_uniformes(vue.probleme, vue.nombre, rng), np.zeros(vue.nombre, dtype=int)


@hacker("classe_haute", groupe_alea="classes_constantes")
def classe_haute(vue, rng):
    """Performances uniformes ; toutes les classes sont C-1, sans accès à A."""
    return (objets_uniformes(vue.probleme, vue.nombre, rng),
            np.full(vue.nombre, len(vue.probleme.ordered_categories) - 1, dtype=int))


@hacker("mrsort_concentre", groupe_alea="mrsort_aleatoire")
def mrsort_concentre(vue, rng):
    """Unique M_H indépendant ; 80 % des performances dans la boîte centrale [0,4 ; 0,6]^d.

    Les 20 % restants restent uniformes sur tout le domaine. Paramètres publics
    fixés avant les essais ; aucune sélection selon le vrai M_A.
    """
    from jalon3.interface import classer

    modele = tirer_modele(vue.probleme, rng)
    rng_x, rng_zone = [np.random.default_rng(int(rng.integers(2_000_000_000))) for _ in range(2)]
    x = objets_uniformes(vue.probleme, vue.nombre, rng_x)
    bas, haut = bornes(vue.probleme)
    centre = rng_zone.random(vue.nombre) < .8
    x[centre] = bas + (.4 + .2 * (x[centre] - bas) / (haut - bas)) * (haut - bas)
    return Brouillage(x, classer(vue.probleme, modele, x), modele)
