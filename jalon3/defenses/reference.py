"""Défenses de référence : B naïf et B avec l'Inv-2-MR-Sort officiel du jalon 2.

La version officielle a son propre arrêt (8 itérations au plus, 4 s par
apprentissage lincs) : ces défenses ne lisent pas `temps`.
"""

import numpy as np

from jalon2.jalon2_deux_mrsort import inv_two_mrsort_misclassified, learn
from jalon3.interface import Decision, defense


@defense("naif")
def naif(recu, graine, temps):
    """Un seul MR-Sort appris par lincs sur tout ce que B reçoit."""
    return Decision(learn(recu.probleme, recu.x, recu.y, graine))


def inv2(recu, graine):
    """Inv-2-MR-Sort du jalon 2, départ « mal classés » : renvoie la partition et les deux modèles."""
    resultat = inv_two_mrsort_misclassified(recu.probleme, recu.x, recu.y, np.random.default_rng(graine))
    return resultat["segment"], resultat["models"]


def garder(segment, modeles, groupe):
    return Decision(modeles[groupe], suspects=segment != groupe)


@defense("inv2_plus_grand")
def inv2_plus_grand(recu, graine, temps):
    """Inv-2-MR-Sort, puis le plus grand groupe : H envoie au plus autant de données que A."""
    segment, modeles = inv2(recu, graine)
    return garder(segment, modeles, int(np.argmax(np.bincount(segment, minlength=2))))


@defense("inv2_mieux_explique")
def inv2_mieux_explique(recu, graine, temps):
    """Inv-2-MR-Sort, puis le groupe dont le modèle fait le moins d'erreurs sur ses lignes."""
    segment, modeles = inv2(recu, graine)
    erreurs = [np.mean(modeles[k].predict(recu.x[segment == k]) != recu.y[segment == k]) for k in (0, 1)]
    return garder(segment, modeles, int(np.argmin(erreurs)))
