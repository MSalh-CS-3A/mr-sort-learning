"""Les contrastes conservent l'appariement et refusent les répétitions manquantes."""

from pathlib import Path
import tempfile
import unittest

import numpy as np

from jalon3.analyse import identifiant
from jalon3.campagne import cles_attendues, plan
from jalon3.confirmation import contrastes, verifier_appariement


class Confirmation(unittest.TestCase):
    def configuration(self, dossier):
        return dict(plan("confirmation", dossier), tailles=[300], ratios=[0., .5, 1.])

    def lignes(self, config):
        lignes = []
        for cle in sorted(cles_attendues(config)):
            d, c, s, n, r, h, b = cle
            base = .3 + .01 * (s - 1000)
            fidelite = base + (.2 if b == "inv2_plus_grand" else 0)
            if h == "classe_haute":
                fidelite -= .3 if b == "inv2_plus_grand" else .1
            if r == 0:
                fidelite = base + (.1 if b == "inv2_plus_grand" else .2)
            lignes.append(dict(zip(("criteres", "categories", "graine", "taille", "ratio", "hacker", "defense"), cle),
                               statut="ok", fidelite=fidelite))
        return lignes

    def test_differences_appariees_avant_bootstrap(self):
        config = self.configuration("/tmp/confirmation-test")
        resultat = contrastes(self.lignes(config), config)
        attendu = dict(cout_defense_sans_attaque=10., gain_inv2_hacker_basique=20.,
                       effet_classe_haute_sur_inv2=30., effet_classe_haute_sur_naif=10.,
                       interaction_attaque_defense=20.)
        for r in resultat:
            self.assertEqual(r["n"], 20)
            for cle in ("moyenne_points", "ic95_bas_points", "ic95_haut_points"):
                # Les performances varient fortement entre graines, leur différence reste constante.
                self.assertAlmostEqual(r[cle], attendu[r["effet"]])
        self.assertEqual(sum(r["principal"] for r in resultat), 2)

    def test_aucune_graine_manquante_dupliquee_ou_en_echec_nest_masquee(self):
        config = self.configuration("/tmp/confirmation-test")
        lignes = self.lignes(config)
        for invalides in (lignes[:-1], lignes + lignes[:1], [dict(l, statut="erreur") for l in lignes]):
            with self.assertRaises(ValueError):
                contrastes(invalides, config)

    def creer_artefacts(self, dossier):
        config = dict(self.configuration(dossier), dimensions=[[2, 2]], tailles=[2, 4], graines=[1000])
        x_a = np.arange(8).reshape(4, 2) / 8
        for n in config["tailles"]:
            racine = dossier / "lots" / f"2x2_n{n}_g1000" / "instances/2x2/graine_1000"
            racine.mkdir(parents=True)
            (racine / "modele_a.yml").write_text("modele_a_fixe")
            np.savez_compressed(racine / "donnees.npz", x_a=x_a[:n], y_a=np.zeros(n, dtype=int),
                                x_test=np.full((10, 2), .5), y_test=np.zeros(10, dtype=int),
                                x_diagnostic=np.full((10, 2), .6), y_diagnostic_a=np.zeros(10, dtype=int))
            for h in config["hackers"]:
                for r in (.5, 1.):
                    cas = racine / f"taille_{n}" / f"ratio_{r:g}" / identifiant(h)
                    cas.mkdir(parents=True)
                    nombre = round(n * r)
                    np.savez_compressed(cas / "injection.npz", x_h=x_a[:nombre], y_h=np.ones(nombre, dtype=int))
                    if h == "mrsort_aleatoire":
                        (cas / "modele_h.yml").write_text("modele_h_fixe")
        return config

    def test_a_et_test_doivent_rester_apparies_entre_tailles(self):
        with tempfile.TemporaryDirectory() as dossier:
            dossier = Path(dossier)
            config = self.creer_artefacts(dossier)
            rapport = verifier_appariement(dossier, config)
            self.assertEqual(rapport["jeux_a_test_diagnostic_verifies"], 2)
            self.assertEqual(rapport["injections_emboitees_verifiees"], 8)
            petit = dossier / "lots/2x2_n2_g1000/instances/2x2/graine_1000/donnees.npz"
            with np.load(petit) as archive:
                donnees = {k: archive[k] for k in archive.files}
            donnees["x_test"][0, 0] = .9
            np.savez_compressed(petit, **donnees)
            with self.assertRaises(AssertionError):
                verifier_appariement(dossier, config)

    def test_h_ne_change_pas_son_modele_avec_le_budget(self):
        with tempfile.TemporaryDirectory() as dossier:
            dossier = Path(dossier)
            config = self.creer_artefacts(dossier)
            petit = dossier / "lots/2x2_n2_g1000/instances/2x2/graine_1000/taille_2/ratio_0.5" / identifiant("mrsort_aleatoire") / "modele_h.yml"
            petit.write_text("modele_h_different")
            with self.assertRaisesRegex(ValueError, "modèle H"):
                verifier_appariement(dossier, config)


if __name__ == "__main__":
    unittest.main()
