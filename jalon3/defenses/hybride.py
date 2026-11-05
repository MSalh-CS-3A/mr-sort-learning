"""Sélecteur expérimental : accord sur le mélange + diversité pondérée.

Coefficient réglé sur les anciennes graines 100..104. Les graines 1000..1019
ont déjà été consultées : elles ne sont pas une confirmation de ce sélecteur.
"""

import numpy as np

from jalon3.interface import Decision, classer, defense, objets_uniformes
from .reference import preparer_inv2

COEFFICIENT = .2
POINTS_PUBLICS = 10000


def choisir_candidat(caracteristiques, coefficient=COEFFICIENT):
    """Aucune fidélité à A ni information privée dans les caractéristiques."""
    grand = int(np.argmax([c["taille_groupe"] for c in caracteristiques]))
    scores = [1-c["erreur_melange"]+coefficient*c["entropie_publique"] for c in caracteristiques]
    return 1-grand if scores[1-grand] > scores[grand]+1e-12 else grand


@defense("inv2_hybride_experimental", preparer=preparer_inv2)
def inv2_hybride(recu, graine, temps, preparation=None):
    from jalon3.simulation import graine_derivee

    preparation = preparation if preparation is not None else preparer_inv2(recu, graine, temps)
    categories = len(recu.probleme.ordered_categories)
    # Flux public employé par l'analyse des archives : conserver ce nom pour
    # reproduire exactement le prototype, sans utiliser les points du test.
    rng = np.random.default_rng(graine_derivee(graine, "analyse_publique_v1",
                                              len(recu.probleme.criteria), categories))
    public = objets_uniformes(recu.probleme, POINTS_PUBLICS, rng)
    features, predictions = [], []
    for k, modele in enumerate(preparation.modeles):
        pred = classer(recu.probleme, modele, recu.x)
        predictions.append(pred)
        q = np.bincount(classer(recu.probleme, modele, public), minlength=categories) / len(public)
        q = q[q > 0]
        entropie = float(-np.sum(q*np.log(q))/np.log(categories))
        features.append(dict(taille_groupe=int(np.sum(preparation.segment==k)),
                             erreur_melange=float(np.mean(pred != recu.y)), entropie_publique=entropie))
    choix = choisir_candidat(features)
    details = dict(coefficient=COEFFICIENT, points_publics=POINTS_PUBLICS, caracteristiques=features,
                   scores=[1-c["erreur_melange"]+COEFFICIENT*c["entropie_publique"] for c in features],
                   votes_exclusifs=[int(np.sum((predictions[k]==recu.y) & (predictions[1-k]!=recu.y))) for k in (0,1)])
    return Decision(preparation.modeles[choix], suspects=preparation.segment!=choix,
                    segmentation=preparation, groupe=choix, details=details)
