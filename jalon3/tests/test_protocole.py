"""Invariants scientifiques : emboîtement, cohérence, absence de fuite et appariement."""

from dataclasses import replace
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from lincs import classification as lc

from jalon3.analyse import apparier, resumer
from jalon3.interface import Brouillage, Decision, Strategie, classer, donnees, objets_uniformes
from jalon3.hackers.reference import mrsort_aleatoire
from jalon3.simulation import brouiller, evaluer, generer_instance


class Protocole(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.instance = generer_instance(4, 3, 100, 2, 300)
        cls.hacker = Strategie("mrsort_aleatoire", mrsort_aleatoire, "reference")

    def test_a_emboite_et_test_independant_des_tailles(self):
        petit = generer_instance(4, 3, 30, 2, 150)
        np.testing.assert_array_equal(petit.donnees_a.x, self.instance.donnees_a.x[:30])
        np.testing.assert_array_equal(petit.donnees_a.y, self.instance.donnees_a.y[:30])
        np.testing.assert_array_equal(petit.test.x, self.instance.test.x[:150])
        np.testing.assert_array_equal(petit.test.y, self.instance.test.y[:150])
        np.testing.assert_array_equal(classer(petit.probleme, petit.modele_a, self.instance.test.x), self.instance.test.y)
        self.assertFalse(np.array_equal(petit.donnees_a.x, petit.test.x[:30]))

    def test_h_coherent_modele_fixe_et_injections_emboitees(self):
        grand = brouiller(self.instance, self.hacker, 1, 2)
        petit = brouiller(self.instance, self.hacker, .25, 2)
        instance_courte = replace(self.instance, donnees_a=donnees(self.instance.probleme,
                                  self.instance.donnees_a.x[:50], self.instance.donnees_a.y[:50]))
        autre = brouiller(instance_courte, self.hacker, .5, 2)
        for injection in (grand, petit, autre):
            np.testing.assert_array_equal(classer(self.instance.probleme, injection.modele, injection.x), injection.y)
            np.testing.assert_array_equal(classer(self.instance.probleme, injection.modele, self.instance.test.x),
                                          classer(self.instance.probleme, grand.modele, self.instance.test.x))
        np.testing.assert_array_equal(petit.x, grand.x[:25])
        np.testing.assert_array_equal(petit.y, grand.y[:25])
        np.testing.assert_array_equal(autre.x, petit.x)

    def test_h_ne_recoit_pas_les_donnees_a(self):
        def aveugle(vue, rng):
            self.assertIsNone(vue.donnees_a)
            self.assertEqual(set(vars(vue)), {"probleme", "nombre", "donnees_a"})
            x = objets_uniformes(vue.probleme, vue.nombre, rng)
            return x, np.zeros(len(x), dtype=int)
        brouiller(self.instance, Strategie("aveugle", aveugle, "test"), .5, 2)

    def test_refus_d_un_modele_h_incoherent(self):
        def incoherent(vue, rng):
            x = objets_uniformes(vue.probleme, vue.nombre, rng)
            y = (classer(vue.probleme, self.instance.modele_a, x) + 1) % 3
            return Brouillage(x, y, self.instance.modele_a)
        with self.assertRaisesRegex(ValueError, "contredisent"):
            brouiller(self.instance, Strategie("incoherent", incoherent, "test"), .5, 2)

    def test_macro_accuracy_et_classe_absente(self):
        class Constant:
            def predict(self, x):
                return np.zeros(len(x), dtype=int)
        probleme = lc.generate_problem(2, 2, 0)
        test = donnees(probleme, np.zeros((4, 2)), [0, 0, 0, 1])
        instance = SimpleNamespace(probleme=probleme, test=test)
        mesure = evaluer(instance, Decision(Constant()), np.zeros(4, dtype=bool))
        self.assertEqual(mesure["fidelite"], .75)
        self.assertEqual(mesure["fidelite_equilibree"], .5)
        instance.test = donnees(probleme, np.zeros((4, 2)), [0, 0, 0, 0])
        self.assertIsNone(evaluer(instance, Decision(Constant()), np.zeros(4, dtype=bool))["fidelite_equilibree"])

    def test_deltas_apparies_par_graine_taille_defense_et_erreurs_visibles(self):
        def ligne(graine, ratio, fidelite=None, statut="ok", taille=100, defense="naif"):
            return dict(criteres=4, categories=3, graine=graine, taille=taille, defense=defense,
                        hacker="aucun" if ratio == 0 else "h", ratio=ratio,
                        fidelite=fidelite, statut=statut)
        lignes = apparier([ligne(0, 0, .9), ligne(1, 0, .7), ligne(0, 1, .6), ligne(1, 1, .8),
                           ligne(2, 1, statut="erreur"), ligne(0, 1, .5, taille=300)])
        self.assertAlmostEqual(lignes[2]["delta_attaque"], .3)
        self.assertAlmostEqual(lignes[3]["delta_attaque"], -.1)
        self.assertIsNone(lignes[4]["delta_attaque"])
        self.assertIsNone(lignes[5]["delta_attaque"])
        resume = next(r for r in resumer(lignes) if r["taille"] == 100 and r["ratio"] == 1)
        self.assertEqual((resume["parties"], resume["echecs"], resume["delta_attaque_n"]), (2, 1, 2))
        self.assertAlmostEqual(resume["delta_attaque_moyenne"], .1)

    def test_tournoi_partage_les_melanges_et_ne_duplique_pas_la_reference(self):
        from jalon3.experiences import jouer_instance

        recus = []
        class Constant:
            def predict(self, x):
                return np.zeros(len(x), dtype=int)
        def apprendre(recu, graine, temps):
            self.assertEqual(set(vars(recu)), {"probleme", "noms", "x", "y"})
            recus.append((recu.x.copy(), recu.y.copy()))
            return Decision(Constant())
        def attaquer(vue, rng):
            x = objets_uniformes(vue.probleme, vue.nombre, rng)
            return x, np.zeros(len(x), dtype=int)
        hackers = {nom: Strategie(nom, attaquer, "test") for nom in ("h1", "h2")}
        defenses = {nom: Strategie(nom, apprendre, "test") for nom in ("b1", "b2")}
        with tempfile.TemporaryDirectory() as dossier:
            config = dict(sortie=dossier, tailles=[8, 16], ratios=[0, .5, 1],
                          hackers=list(hackers), defenses=list(defenses), taille_test=80, temps=1)
            with patch("jalon3.experiences.charger_strategies", return_value=(hackers, defenses)), patch("builtins.print"):
                lignes = jouer_instance(config, (4, 2), 0)
        self.assertEqual(len(lignes), 20)  # 2 tailles * (1 référence + 2 ratios * 2 hackers) * 2 défenses
        self.assertTrue(all(l["statut"] == "ok" for l in lignes))
        self.assertEqual(sum(l["ratio"] == 0 for l in lignes), 4)
        self.assertTrue(all(l.get("desaccord") is None for l in lignes))
        for i in range(0, len(recus), 2):
            np.testing.assert_array_equal(recus[i][0], recus[i + 1][0])
            np.testing.assert_array_equal(recus[i][1], recus[i + 1][1])


if __name__ == "__main__":
    unittest.main()
