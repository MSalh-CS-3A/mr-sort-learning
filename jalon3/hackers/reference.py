"""Hackers de la partie 1 : bruit pur (E1) et MR-Sort tiré au hasard (E2)."""

from jalon3.interface import hacker, objets_uniformes, tirer_modele, tirer_objets


@hacker("etiquettes_aleatoires")
def etiquettes_aleatoires(vue, rng):
    """Objets uniformes et catégories au hasard : aucun MR-Sort derrière."""
    x = objets_uniformes(vue.probleme, vue.nombre, rng)
    return x, rng.integers(len(vue.probleme.ordered_categories), size=vue.nombre)


@hacker("mrsort_aleatoire")
def mrsort_aleatoire(vue, rng):
    """Agent basique de l'énoncé : M_H tiré et utilisé exactement comme M_A."""
    modele = tirer_modele(vue.probleme, rng)
    return tirer_objets(vue.probleme, modele, vue.nombre, rng)
