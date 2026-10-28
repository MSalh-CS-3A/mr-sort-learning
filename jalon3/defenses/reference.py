"""Défenses de référence : B naïf et B avec Inv-2-MR-Sort du jalon 2."""

import time

import numpy as np
import sklearn.mixture  # noqa: F401 - chargé ici, sinon la première partie paie cet import sur son budget.

from jalon2.algorithmes import resoudre
from jalon2.apprentissage import apprendre
from jalon3.interface import Decision, defense

METHODE, INITIALISATION, TEMPS_APPEL = "A2", "gmm", .25


@defense("naif")
def naif(recu, graine, temps):
    """Un seul MR-Sort appris par lincs sur tout ce que B reçoit."""
    rng = np.random.default_rng(graine)
    return Decision(apprendre(recu, np.arange(len(recu.y)), rng, time.monotonic() + temps, temps))


def inv2(recu, graine, temps):
    etat = resoudre(recu, METHODE, INITIALISATION, temps, TEMPS_APPEL, graine).meilleur
    if etat is None:
        raise RuntimeError("Inv-2-MR-Sort n'a produit aucune partition dans le budget.")
    return etat


def garder(etat, groupe):
    return Decision(etat.modeles[groupe], suspects=etat.z != groupe)


@defense("inv2_plus_grand")
def inv2_plus_grand(recu, graine, temps):
    """Inv-2-MR-Sort, puis le plus grand groupe : H envoie au plus autant de données que A."""
    etat = inv2(recu, graine, temps)
    return garder(etat, int(np.argmax(np.bincount(etat.z, minlength=2))))


@defense("inv2_mieux_explique")
def inv2_mieux_explique(recu, graine, temps):
    """Inv-2-MR-Sort, puis le groupe dont le modèle fait le moins d'erreurs sur ses lignes."""
    etat = inv2(recu, graine, temps)
    erreurs = [np.mean(etat.predictions[k, etat.z == k] != recu.y[etat.z == k]) for k in (0, 1)]
    return garder(etat, int(np.argmin(erreurs)))
