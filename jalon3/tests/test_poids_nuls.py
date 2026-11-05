"""Régression : LINCS peut apprendre une règle constante de poids tous nuls."""

from pathlib import Path
import tempfile
import unittest

import numpy as np
from lincs import classification as lc
from threadpoolctl import threadpool_limits

from jalon2.jalon2_deux_mrsort import MRSort, learn
from jalon3.interface import Decision, Segmentation, Strategie, classer, donnees
from jalon3.simulation import decider
from jalon3.validation_comparaisons import charger_modele


class PoidsNuls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.probleme = lc.generate_problem(4, 3, 0)
        profils = [lc.AcceptedValues(lc.AcceptedValues.RealThresholds([.25, .75])) for _ in range(4)]
        cls.profils = profils
        cls.x = np.vstack((np.zeros(4), np.ones(4), np.full(4, .25), np.full(4, .75),
                          np.random.default_rng(0).uniform(size=(100, 4))))

    def modele_lincs(self, poids):
        coalitions = lc.SufficientCoalitions(lc.SufficientCoalitions.Weights(poids))
        return lc.Model(self.probleme, self.profils, [coalitions, coalitions])

    def test_poids_nuls_preservent_les_predictions_lincs_et_les_marges(self):
        source = self.modele_lincs([0.] * 4)
        with np.errstate(divide="raise", invalid="raise"):
            converti = MRSort.from_lincs(source)
            erreurs, marges = converti.error_and_margin(self.x, np.arange(len(self.x)) % 3)
        np.testing.assert_array_equal(converti.predict(self.x), classer(self.probleme, source, self.x))
        np.testing.assert_array_equal(converti.predict(self.x), np.zeros(len(self.x), dtype=int))
        self.assertTrue(np.isfinite(marges).all())
        self.assertTrue(np.isfinite(converti.w).all() and np.isfinite(converti.lam))
        np.testing.assert_array_equal(erreurs, np.arange(len(self.x)) % 3)

    def test_poids_non_nuls_conservent_les_predictions_aux_frontieres(self):
        for poids in ([.5, .5, .5, .5], [.25, .25, .25, .25], [.1, .2, .15, .05]):
            with self.subTest(poids=poids):
                source = self.modele_lincs(poids)
                converti = MRSort.from_lincs(source)
                np.testing.assert_array_equal(converti.predict(self.x), classer(self.probleme, source, self.x))
                self.assertAlmostEqual(converti.w.sum(), 1.)

    def test_apprentissage_reel_classe_basse_constante(self):
        x = np.random.default_rng(1).uniform(size=(40, 4))
        y = np.zeros(len(x), dtype=int)
        with threadpool_limits(limits=1), np.errstate(divide="raise", invalid="raise"):
            modele = learn(self.probleme, x, y, 1)
        self.assertTrue(np.isfinite(modele.w).all() and np.isfinite(modele.lam))
        np.testing.assert_array_equal(modele.predict(x), y)

    def test_modele_constant_est_accepte_par_l_audit_sans_relacher_ses_controles(self):
        modele = MRSort.from_lincs(self.modele_lincs([0.] * 4))
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "modele.npz"
            np.savez_compressed(chemin, b=modele.b, w=modele.w, lam=modele.lam)
            recharge = charger_modele(chemin)
            np.testing.assert_array_equal(recharge.predict(self.x), modele.predict(self.x))
            np.savez_compressed(chemin, b=modele.b, w=np.full(4, np.nan), lam=np.inf)
            with self.assertRaises(AssertionError):
                charger_modele(chemin)

    def test_refus_immediat_du_modele_retenu_ou_d_un_candidat_non_fini(self):
        sain = MRSort.from_lincs(self.modele_lincs([0.] * 4))
        invalide = MRSort(sain.b, np.full(4, np.nan), np.inf)
        recu = donnees(self.probleme, self.x, np.zeros(len(self.x), dtype=int))
        for decision in (Decision(invalide),
                         Decision(sain, segmentation=Segmentation(np.arange(len(self.x)) % 2,
                                                                  (sain, invalide)), groupe=0)):
            with self.subTest(segmentation=decision.segmentation is not None):
                strategie = Strategie("non_fini", lambda *_: decision, "test")
                with self.assertRaisesRegex(ValueError, "non finis"):
                    decider(strategie, recu, 0, 1)


if __name__ == "__main__":
    unittest.main()
