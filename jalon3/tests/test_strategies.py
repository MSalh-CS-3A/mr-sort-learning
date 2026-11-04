"""Contrôles du partage, des règles de sélection et des nouvelles stratégies."""

from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import numpy as np
from lincs import classification as lc

from jalon3.defenses import reference, robustes
from jalon3.interface import Decision, Segmentation, Strategie, charger_strategies, classer, donnees
from jalon3.simulation import Comparaison, brouiller, evaluer, generer_instance


class Constant:
    def __init__(self, categorie):
        self.categorie = categorie

    def predict(self, x):
        return np.full(len(x), self.categorie, dtype=int)

    def error_and_margin(self, x, y):
        erreur = np.abs(self.predict(x) - y)
        return erreur, np.where(erreur > 0, -1., 1.)


class Strategies(unittest.TestCase):
    def setUp(self):
        self.probleme = lc.generate_problem(4, 2, 0)
        self.recu = donnees(self.probleme, np.zeros((10, 4)), [0] * 4 + [1] * 6)

    def test_inv2_partage_une_partition_et_compte_les_temps_honnetement(self):
        segmentation = Segmentation(np.array([0] * 7 + [1] * 3), (Constant(0), Constant(1)))
        preparer = Mock(return_value=segmentation)
        preparer.__module__, preparer.__qualname__ = "test", "inv2"
        a = Strategie("grand", reference.inv2_plus_grand, "test", preparer=preparer)
        b = Strategie("explique", reference.inv2_mieux_explique, "test", preparer=preparer)
        comparaison = Comparaison(self.recu, 0, 10)
        with patch("jalon3.simulation.time.monotonic", side_effect=[0, 5, 5, 5.1, 6, 6.2]):
            d1, t1, c1 = comparaison.decider(a)
            d2, t2, c2 = comparaison.decider(b)
        self.assertEqual(preparer.call_count, 1)
        self.assertEqual((d1.groupe, d2.groupe), (0, 1))
        self.assertIs(d1.segmentation.modeles[0], d2.segmentation.modeles[0])
        np.testing.assert_array_equal(d1.segmentation.segment, d2.segmentation.segment)
        self.assertEqual(c1["preparation_id"], c2["preparation_id"])
        self.assertAlmostEqual(t1, 5.1)
        self.assertAlmostEqual(t2, 5.2)
        self.assertAlmostEqual(c1["temps_calcul_effectif"], 5.1)
        self.assertAlmostEqual(c2["temps_calcul_effectif"], .2)
        Comparaison(self.recu, 0, 10).decider(a)
        self.assertEqual(preparer.call_count, 2)  # Aucun cache global entre conditions.

    def test_echec_partage_ne_relance_pas_le_calcul(self):
        preparer = Mock(side_effect=ValueError("échec contrôlé"))
        preparer.__module__, preparer.__qualname__ = "test", "echec"
        strategie = Strategie("test", reference.inv2_plus_grand, "test", preparer=preparer)
        comparaison = Comparaison(self.recu, 0, 10)
        for _ in range(2):
            with self.assertRaisesRegex(RuntimeError, "échec contrôlé"):
                comparaison.decider(strategie)
        self.assertEqual(preparer.call_count, 1)

    def test_filtre_exclusions_effectivement_utilisees_et_plafond(self):
        recu = donnees(self.probleme, np.arange(40).reshape(10, 4) / 40, [0] * 7 + [1] * 3)
        with patch.object(robustes, "learn", side_effect=[Constant(0), Constant(1)]) as apprendre, \
                patch.object(robustes, "TOURS_MAX", 1), patch.object(robustes.time, "monotonic", return_value=0):
            decision = robustes.filtrage_iteratif(recu, 0, 12)
        self.assertEqual(apprendre.call_count, 2)
        self.assertEqual(decision.suspects.sum(), 2)
        self.assertTrue((recu.y[decision.suspects] == 1).all())
        np.testing.assert_array_equal(apprendre.call_args_list[1].args[1], recu.x[~decision.suspects])
        self.assertEqual(decision.details["nombre_apprentissages"], 2)

    def test_filtre_ne_signale_pas_un_retrait_sans_reentrainement(self):
        with patch.object(robustes, "learn", return_value=Constant(0)) as apprendre, \
                patch.object(robustes.time, "monotonic", side_effect=[0, 100]):
            decision = robustes.filtrage_iteratif(self.recu, 0, 12)
        self.assertEqual(apprendre.call_count, 1)
        self.assertFalse(decision.suspects.any())

    def test_naif_multi_selectionne_sur_le_melange_et_garde_le_premier_depart(self):
        with patch.object(robustes, "learn", side_effect=[Constant(0), Constant(1)]) as apprendre, \
                patch.object(robustes, "REDEMARRAGES_MAX", 2), patch.object(robustes.time, "monotonic", return_value=0):
            decision = robustes.naif_multi(self.recu, 42, 12)
        self.assertEqual(apprendre.call_args_list[0].args[3], 42)
        self.assertEqual(decision.modele.categorie, 1)
        self.assertIsNone(decision.suspects)
        self.assertEqual(decision.details["erreurs_apprentissage"], 4)
        self.assertEqual(decision.details["nombre_apprentissages"], 2)

    def test_diagnostics_oracle_ne_changent_pas_la_decision(self):
        test = donnees(self.probleme, np.zeros((4, 4)), [1] * 4)
        instance = SimpleNamespace(probleme=self.probleme, test=test)
        segmentation = Segmentation(np.array([0, 0, 1, 1]), (Constant(0), Constant(1)))
        decision = Decision(segmentation.modeles[0], segmentation=segmentation, groupe=0)
        mesures = evaluer(instance, decision, np.array([0, 0, 1, 1], dtype=bool), modele_h=Constant(0))
        self.assertEqual(mesures["fidelite"], 0)
        self.assertEqual(mesures["fidelite_oracle_a"], 1)
        self.assertEqual(mesures["perte_selection"], 1)
        self.assertEqual(mesures["reconstruction_paire"], 1)
        self.assertEqual(mesures["inversion_modeles"], 1)
        self.assertEqual(decision.groupe, 0)

    def test_attaques_constantes_apparient_les_performances(self):
        hackers, _ = charger_strategies()
        instance = generer_instance(4, 3, 80, 0, 100)
        bas = brouiller(instance, hackers["classe_basse"], 1, 0)
        haut = brouiller(instance, hackers["classe_haute"], 1, 0)
        np.testing.assert_array_equal(bas.x, haut.x)
        self.assertTrue((bas.y == 0).all())
        self.assertTrue((haut.y == 2).all())

    def test_concentration_coherente_emboitee_et_modele_apparie(self):
        hackers, _ = charger_strategies()
        instance = generer_instance(4, 3, 1000, 0, 100)
        uniforme = brouiller(instance, hackers["mrsort_aleatoire"], 1, 0)
        concentre = brouiller(instance, hackers["mrsort_concentre"], 1, 0)
        petit = brouiller(instance, hackers["mrsort_concentre"], .5, 0)
        np.testing.assert_array_equal(classer(instance.probleme, uniforme.modele, instance.test.x),
                                      classer(instance.probleme, concentre.modele, instance.test.x))
        np.testing.assert_array_equal(petit.x, concentre.x[:500])
        np.testing.assert_array_equal(petit.y, concentre.y[:500])
        np.testing.assert_array_equal(classer(instance.probleme, concentre.modele, concentre.x), concentre.y)
        self.assertGreater(np.all((concentre.x >= .4) & (concentre.x <= .6), axis=1).mean(), .7)


if __name__ == "__main__":
    unittest.main()
