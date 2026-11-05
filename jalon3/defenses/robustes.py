"""Filtrage sans vérité cachée et contrôle de l'effort d'optimisation.

Réglages fixés avant les essais : retrait maximal de 20 %, deux réentraînements.
Chaque appel utilise le même learn du jalon 2, à seuil nominal de 4 secondes.
Les budgets sont souples : un appel en cours n'est pas interrompu.
"""

import time

import numpy as np

from jalon2.jalon2_deux_mrsort import LINCS_SECONDS, learn
from jalon3.interface import Decision, defense
from jalon3.simulation import graine_derivee

RETRAIT_MAX = .2
TOURS_MAX = 2
REDEMARRAGES_MAX = 32


def score(modele, x, y):
    erreurs = np.abs(modele.predict(x) - y)
    return int(np.count_nonzero(erreurs)), int(erreurs.sum())


@defense("naif_multi")
def naif_multi(recu, graine, temps):
    """Redémarrages sur tout le mélange ; sélection par erreur d'apprentissage, sans filtrage.

    Contrôle de calcul, pas une défense supposée robuste. Le premier départ
    utilise la même graine que naif. Les autres viennent d'un flux distinct.
    """
    debut = time.monotonic()
    rng = np.random.default_rng(graine_derivee(graine, "naif_multi"))
    modele = learn(recu.probleme, recu.x, recu.y, graine)
    meilleur = score(modele, recu.x, recu.y)
    appels = 1
    while (meilleur[0] > 0 and appels < REDEMARRAGES_MAX
           and temps - (time.monotonic() - debut) >= LINCS_SECONDS):
        candidat = learn(recu.probleme, recu.x, recu.y, int(rng.integers(2_000_000_000)))
        appels += 1
        cout = score(candidat, recu.x, recu.y)
        if cout < meilleur:
            modele, meilleur = candidat, cout
    return Decision(modele, details={"nombre_apprentissages": appels, "erreurs_apprentissage": meilleur[0],
                                     "budget_demande": temps, "type": "controle_optimisation"})


@defense("filtrage_iteratif")
def filtrage_iteratif(recu, graine, temps):
    """Retirer au plus 20 % des lignes mal classées puis réapprendre, au plus deux fois.

    Classement par écart de catégorie décroissant, puis marge croissante, puis
    indice pour trancher les égalités. Ni ratio, ni origine, ni test n'interviennent.
    La sortie ne signale que les exclusions effectivement utilisées pour apprendre.
    """
    debut = time.monotonic()
    rng = np.random.default_rng(graine_derivee(graine, "filtrage_iteratif"))
    modele = learn(recu.probleme, recu.x, recu.y, graine)
    suspects = np.zeros(len(recu.y), dtype=bool)
    appels = 1
    for _ in range(TOURS_MAX):
        if temps - (time.monotonic() - debut) < LINCS_SECONDS:
            break
        erreurs, marges = modele.error_and_margin(recu.x, recu.y)
        candidats = np.flatnonzero(erreurs > 0)
        nombre = min(int(RETRAIT_MAX * len(recu.y)), len(candidats))
        if nombre == 0:
            break
        ordre = np.lexsort((candidats, marges[candidats], -erreurs[candidats]))
        nouveau = np.zeros(len(recu.y), dtype=bool)
        nouveau[candidats[ordre[:nombre]]] = True
        if np.array_equal(nouveau, suspects) or np.unique(recu.y[~nouveau]).size < 2:
            break
        candidat = learn(recu.probleme, recu.x[~nouveau], recu.y[~nouveau], int(rng.integers(2_000_000_000)))
        modele, suspects = candidat, nouveau
        appels += 1
    return Decision(modele, suspects=suspects,
                    details={"nombre_apprentissages": appels, "exclusions": int(suspects.sum()),
                             "retrait_max": RETRAIT_MAX, "tours_max": TOURS_MAX, "budget_demande": temps})
