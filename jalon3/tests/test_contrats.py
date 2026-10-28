"""Contrôles de toutes les stratégies enregistrées, à lancer avant de partager une stratégie."""

import unittest

import numpy as np

from jalon3.interface import Strategie, charger_strategies
from jalon3.simulation import brouiller, decider, evaluer, generer_instance, recevoir

HACKERS, DEFENSES = charger_strategies()


class Contrats(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.instance = generer_instance(4, 3, 60, graine=0, taille_test=200)

    def test_chaque_hacker_respecte_le_format_et_le_budget(self):
        for nom, strategie in HACKERS.items():
            with self.subTest(hacker=nom):
                x, y = brouiller(self.instance, strategie, 1, graine=0)  # Vérifie forme, bornes et catégories.
                self.assertLessEqual(len(y), len(self.instance.donnees_a.y))

    def test_chaque_defense_renvoie_une_decision_evaluable(self):
        x, y = brouiller(self.instance, HACKERS["mrsort_aleatoire"], 1, graine=0)
        recu, source_h = recevoir(self.instance, x, y, graine=0)
        for nom, strategie in DEFENSES.items():
            with self.subTest(defense=nom):
                decision, _ = decider(strategie, recu, graine=0, temps=4)
                self.assertTrue(0 <= evaluer(self.instance, decision, source_h)["fidelite"] <= 1)

    def test_b_ne_voit_ni_la_source_ni_l_ordre_d_envoi(self):
        x, y = brouiller(self.instance, HACKERS["etiquettes_aleatoires"], 1, graine=0)
        recu, source_h = recevoir(self.instance, x, y, graine=0)
        self.assertEqual(recu.noms[0], "objet 1")
        self.assertTrue(source_h[:60].any() and not source_h[:60].all())

    def test_un_hacker_trop_bavard_est_refuse(self):
        def bavard(vue, rng):
            return np.zeros((vue.nombre + 1, 4)), np.zeros(vue.nombre + 1, dtype=int)

        with self.assertRaisesRegex(ValueError, "bavard"):
            brouiller(self.instance, Strategie("bavard", bavard, "test"), .5, graine=0)

    def test_sans_brouillage_b_naif_retrouve_bien_m_a(self):
        instance = generer_instance(6, 3, 300, graine=0)
        recu, source_h = recevoir(instance, *brouiller(instance, None, 0, graine=0), graine=0)
        decision, _ = decider(DEFENSES["naif"], recu, graine=0, temps=5)
        self.assertGreater(evaluer(instance, decision, source_h)["fidelite"], .8)


if __name__ == "__main__":
    unittest.main()
