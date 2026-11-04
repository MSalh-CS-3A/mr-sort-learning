"""Défenses fondées sur la variante A0-A4 du jalon 2 (A2 par distance, départ GMM)."""

import numpy as np
import sklearn.mixture  # noqa: F401 - chargé ici, sinon la première partie paie cet import sur son budget.

from jalon2.variante_a0_a4.algorithmes import resoudre
from jalon3.interface import Decision, Segmentation, defense

METHODE, INITIALISATION, TEMPS_APPEL = "A2", "gmm", .25


def inv2(recu, graine, temps):
    etat = resoudre(recu, METHODE, INITIALISATION, temps, TEMPS_APPEL, graine).meilleur
    if etat is None:
        raise RuntimeError("Inv-2-MR-Sort n'a produit aucune partition dans le budget.")
    return etat


def garder(etat, groupe):
    return Decision(etat.modeles[groupe], suspects=etat.z != groupe,
                    segmentation=Segmentation(etat.z, tuple(etat.modeles)), groupe=groupe)


def preparer_inv2(recu, graine, temps):
    return inv2(recu, graine, temps)


@defense("variante_plus_grand", preparer=preparer_inv2)
def variante_plus_grand(recu, graine, temps, preparation=None):
    """Variante A2 dans le budget `temps`, puis le plus grand groupe."""
    etat = preparation if preparation is not None else inv2(recu, graine, temps)
    return garder(etat, int(np.argmax(np.bincount(etat.z, minlength=2))))


@defense("variante_mieux_explique", preparer=preparer_inv2)
def variante_mieux_explique(recu, graine, temps, preparation=None):
    """Variante A2 dans le budget `temps`, puis le groupe dont le modèle fait le moins d'erreurs."""
    etat = preparation if preparation is not None else inv2(recu, graine, temps)
    erreurs = [np.mean(etat.predictions[k, etat.z == k] != recu.y[etat.z == k]) for k in (0, 1)]
    return garder(etat, int(np.argmin(erreurs)))
