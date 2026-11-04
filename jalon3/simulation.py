"""Une partie : A envoie, H brouille, B apprend, puis on évalue B sur des objets neufs."""

from dataclasses import dataclass
import hashlib
import time
import zlib

import numpy as np
from lincs import classification as lc

from .interface import Brouillage, Decision, Donnees, Vue, bornes, classer, donnees, tirer_modele, tirer_objets


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
    """Modèle et test fixes ; données A emboîtées lorsque `taille` varie."""
    probleme = lc.generate_problem(criteres, categories, graine)
    rng = np.random.default_rng(graine_derivee(graine, "modele", criteres, categories))
    modele = tirer_modele(probleme, rng)
    rng = np.random.default_rng(graine_derivee(graine, "test", criteres, categories))
    test = donnees(probleme, *tirer_objets(probleme, modele, taille_test, rng))
    rng = np.random.default_rng(graine_derivee(graine, "donnees_a", criteres, categories))
    return Instance(probleme, modele, donnees(probleme, *tirer_objets(probleme, modele, taille, rng)), test)


def brouiller(instance, strategie, ratio, graine):
    """Données de H, vérifiées : au plus `ratio` donnée par donnée de A, dans le domaine public."""
    nombre = round(ratio * len(instance.donnees_a.y))
    if not 0 <= ratio <= 1:
        raise ValueError("Le ratio H/A doit être entre 0 et 1.")
    n = len(instance.probleme.criteria)
    if strategie is None or nombre == 0:
        return Brouillage(np.zeros((0, n)), np.zeros(0, dtype=int))
    vue = Vue(instance.probleme, nombre, instance.donnees_a if strategie.voit_donnees_a else None)
    rng = np.random.default_rng(graine_derivee(graine, "hacker", strategie.groupe_alea or strategie.nom,
                                            len(instance.probleme.criteria),
                                            len(instance.probleme.ordered_categories)))
    resultat = strategie.fonction(vue, rng)
    x, y = resultat
    modele = resultat.modele if isinstance(resultat, Brouillage) else None
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
    if modele is not None and not np.array_equal(classer(instance.probleme, modele, x), y):
        raise ValueError(f"Hacker {strategie.nom} : les classes contredisent le modèle déclaré.")
    jeu = donnees(instance.probleme, x, y)
    return Brouillage(jeu.x, jeu.y, modele)


def recevoir(instance, x_h, y_h, graine):
    """Mélange hors ligne : ordre aléatoire et noms neutres ; la source reste cachée à B."""
    a = instance.donnees_a
    x = np.vstack([a.x, x_h])
    y = np.concatenate([a.y, y_h])
    source_h = np.concatenate([np.zeros(len(a.y), dtype=bool), np.ones(len(y_h), dtype=bool)])
    ordre = np.random.default_rng(graine_derivee(graine, "melange")).permutation(len(y))
    return donnees(instance.probleme, x[ordre], y[ordre]), source_h[ordre]


def decider(strategie, recu, graine, temps, preparation=None):
    """Appeler la défense et vérifier sa décision ; renvoie aussi le temps réel."""
    debut = time.monotonic()
    decision = (strategie.fonction(recu, graine, temps) if preparation is None else
                strategie.fonction(recu, graine, temps, preparation=preparation))
    duree = time.monotonic() - debut
    if not isinstance(decision, Decision) or not (
            isinstance(decision.modele, lc.Model) or callable(getattr(decision.modele, "predict", None))):
        raise TypeError(f"Défense {strategie.nom} : il faut renvoyer Decision(modele, suspects), "
                        "avec un modèle lincs ou doté de predict(x).")
    if decision.suspects is not None and np.shape(decision.suspects) != (len(recu.y),):
        raise ValueError(f"Défense {strategie.nom} : `suspects` doit avoir une valeur par ligne reçue.")
    if decision.segmentation is not None:
        partition = np.asarray(decision.segmentation.segment)
        if (partition.shape != (len(recu.y),) or not np.isin(partition, [0, 1]).all()
                or len(decision.segmentation.modeles) != 2 or decision.groupe not in (0, 1)):
            raise ValueError(f"Défense {strategie.nom} : segmentation binaire et groupe choisi 0 ou 1 requis.")
    modeles = [decision.modele]
    if decision.segmentation is not None:
        modeles.extend(decision.segmentation.modeles)
    for modele in modeles:
        if all(hasattr(modele, attribut) for attribut in ("b", "w", "lam")):
            if not all(np.isfinite(getattr(modele, attribut)).all() for attribut in ("b", "w", "lam")):
                raise ValueError(f"Défense {strategie.nom} : paramètres MR-Sort non finis (NaN ou infini).")
    return decision, duree


class Comparaison:
    """Cache limité à un mélange : une préparation commune, plusieurs sélections.

    Chaque défense est créditée du coût COMPLET de préparation pour comparer
    ses temps ; le coût réellement exécuté n'est compté qu'une fois à part.
    Une erreur de préparation est conservée pour les autres sélections.
    """
    def __init__(self, recu, graine, temps):
        self.recu, self.graine, self.temps = recu, graine, temps
        self.preparations = {}

    def decider(self, strategie):
        preparer = strategie.preparer
        if preparer is None:
            decision, duree = decider(strategie, self.recu, self.graine, self.temps)
            return decision, duree, dict(temps_preparation=0., temps_selection=duree,
                                         temps_calcul_effectif=duree)
        nouveau = preparer not in self.preparations
        if nouveau:
            debut = time.monotonic()
            try:
                resultat, erreur = preparer(self.recu, self.graine, self.temps), None
            except Exception as cause:
                resultat, erreur = None, cause
            duree = time.monotonic() - debut
            nom = preparer.__module__ + "." + preparer.__qualname__
            empreinte = hashlib.sha256(nom.encode() + str((self.graine, self.temps)).encode()
                                       + self.recu.x.tobytes() + self.recu.y.tobytes()).hexdigest()
            self.preparations[preparer] = resultat, duree, erreur, empreinte
        resultat, duree_preparation, erreur, empreinte = self.preparations[preparer]
        if erreur is not None:
            raise RuntimeError(f"Préparation partagée : {type(erreur).__name__}: {erreur}") from erreur
        decision, duree_selection = decider(strategie, self.recu, self.graine, self.temps, preparation=resultat)
        return decision, duree_preparation + duree_selection, dict(
            preparation_id=empreinte, temps_preparation=duree_preparation, temps_selection=duree_selection,
            temps_calcul_effectif=duree_selection + (duree_preparation if nouveau else 0.))


def evaluer(instance, decision, source_h, modele_h=None):
    """Fidélité à M_A sur le test ; détection si la défense désigne des suspects."""
    test = instance.test
    correct = classer(instance.probleme, decision.modele, test.x) == test.y
    categories = len(instance.probleme.ordered_categories)
    effectifs = np.bincount(test.y, minlength=categories)
    rappels = [float(correct[test.y == c].mean()) if effectifs[c] else None for c in range(categories)]
    mesures = {"fidelite": float(correct.mean()),
               # Une classe absente ne devient ni un zéro, ni une classe oubliée de la moyenne.
               "fidelite_equilibree": float(np.mean(rappels)) if effectifs.all() else None,
               "effectifs_test": effectifs.tolist(), "fidelites_categories": rappels,
               "reference_majoritaire": float(effectifs.max() / len(test.y))}
    if decision.suspects is not None:
        suspects = np.asarray(decision.suspects, dtype=bool)
        if source_h.any():
            mesures["detection_h"] = float(suspects[source_h].mean())
        mesures["rejet_a"] = float(suspects[~source_h].mean())
    if decision.segmentation is not None:
        segmentation = decision.segmentation
        partition_correcte = np.asarray(segmentation.segment) == source_h.astype(int)
        mesures["partition_appariee"] = float(max(partition_correcte.mean(), 1 - partition_correcte.mean()))
        predictions = [classer(instance.probleme, m, test.x) for m in segmentation.modeles]
        fidelites_a = [float(np.mean(p == test.y)) for p in predictions]
        mesures["fidelite_oracle_a"] = max(fidelites_a)
        mesures["perte_selection"] = max(fidelites_a) - mesures["fidelite"]
        if modele_h is not None:
            verite_h = classer(instance.probleme, modele_h, test.x)
            fidelites_h = [float(np.mean(p == verite_h)) for p in predictions]
            alignements = [(fidelites_a[0] + fidelites_h[1]) / 2,
                           (fidelites_a[1] + fidelites_h[0]) / 2]
            mesures["reconstruction_paire"] = max(alignements)
            if not np.isclose(alignements[0], alignements[1], rtol=0, atol=1e-12):
                mesures["inversion_modeles"] = int(decision.groupe != int(np.argmax(alignements)))
    return mesures
