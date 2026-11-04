"""Vérifier le compromis du sélecteur et l'absence d'appel d'apprentissage après préparation."""

import unittest
from unittest.mock import patch

import numpy as np
from lincs import classification as lc

from jalon3.defenses.hybride import choisir_candidat, inv2_hybride
from jalon3.interface import Segmentation, donnees


class Constant:
    def predict(self, x):
        return np.full(len(x), 2, dtype=int)


class TroisCategories:
    def predict(self, x):
        return np.minimum((3*x[:,0]).astype(int), 2)


class SelectionHybride(unittest.TestCase):
    def test_un_fort_accord_protege_un_modele_moins_divers(self):
        candidats=[dict(taille_groupe=60,erreur_melange=.1,entropie_publique=.2),
                   dict(taille_groupe=40,erreur_melange=.5,entropie_publique=1.)]
        self.assertEqual(choisir_candidat(candidats),0)

    def test_la_diversite_peut_corriger_un_groupe_constant_majoritaire(self):
        candidats=[dict(taille_groupe=60,erreur_melange=.4,entropie_publique=0.),
                   dict(taille_groupe=40,erreur_melange=.45,entropie_publique=.8)]
        self.assertEqual(choisir_candidat(candidats),1)
        self.assertEqual(choisir_candidat(candidats[::-1]),0)

    def test_egalite_conserve_le_plus_grand_groupe(self):
        candidats=[dict(taille_groupe=40,erreur_melange=.2,entropie_publique=.6),
                   dict(taille_groupe=60,erreur_melange=.2,entropie_publique=.6)]
        self.assertEqual(choisir_candidat(candidats),1)

    def test_preparation_reutilisee_et_decision_sans_verite_privee(self):
        problem=lc.generate_problem(2,3,0)
        x=np.array([[.1,0],[.2,0],[.4,0],[.5,0],[.8,0],[.9,0]])
        recu=donnees(problem,x,[0,0,1,1,2,2])
        models=(Constant(),TroisCategories())
        prep=Segmentation(np.array([0,0,0,0,1,1]),models)
        with patch('jalon3.defenses.hybride.preparer_inv2',side_effect=AssertionError('réapprentissage interdit')):
            result=inv2_hybride(recu,42,12,preparation=prep)
        self.assertIs(result.modele,models[1])
        self.assertIs(result.segmentation,prep)
        self.assertEqual(result.details['votes_exclusifs'],[0,4])
        np.testing.assert_array_equal(result.suspects,prep.segment!=1)


if __name__=='__main__':
    unittest.main()
