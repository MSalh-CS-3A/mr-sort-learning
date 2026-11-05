"""Protection des longues campagnes contre les reprises et agrégations invalides."""

import csv
import fcntl
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from jalon3 import campagne as c
from jalon3.experiences import COLONNES


class Campagne(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.racine = Path(self.temp.name)
        self.config = dict(c.plan("calibrage", self.racine), hackers=["mrsort_aleatoire"],
                           defenses=["naif"], ratios=[0., 1.], graines=[100])
        self.lot = c.lots(self.config)[0]
        self.dossier = self.racine / "lots" / self.lot["id"]
        self.lot_config = c.configuration_lot(self.config, self.lot, self.dossier)

    def creer_lot(self):
        self.dossier.mkdir(parents=True)
        lignes = []
        for cle in sorted(c.cles_attendues(self.lot_config)):
            ligne = dict(zip(c.CLE, cle), statut="ok", nombre_h=0 if cle[4] == 0 else 300,
                         fidelite=.9 if cle[4] == 0 else .7, temps=1)
            lignes.append(ligne)
        with (self.dossier / "resultats.csv").open("w", newline="") as fichier:
            sortie = csv.DictWriter(fichier, fieldnames=COLONNES)
            sortie.writeheader()
            sortie.writerows(lignes)
        c.ecrire_json(self.dossier / "audit.json", dict(statut="ok", decisions_verifiees=2))
        c.ecrire_json(self.dossier / "configuration.json", dict(configuration=self.lot_config))
        return lignes

    def test_plans_et_separation_developpement_evaluation(self):
        calibrage = c.plan("calibrage", self.racine)
        principale = c.plan("principale", self.racine)
        complete = c.plan("complete", self.racine)
        self.assertEqual(len(c.cles_attendues(calibrage)), 400)
        self.assertEqual(len(c.cles_attendues(principale)), 2400)
        self.assertEqual(len(c.cles_attendues(complete)), 9600)
        self.assertFalse(set(calibrage["graines"]) & set(principale["graines"]))
        self.assertTrue(c.cles_attendues(principale) < c.cles_attendues(complete))

    def test_confirmation_quatre_couples_trois_tailles_et_nouvelles_graines(self):
        config = c.plan("confirmation", self.racine)
        self.assertEqual(len(c.lots(config)), 60)
        self.assertEqual(len(c.cles_attendues(config)), 840)
        self.assertEqual(set(config["hackers"]), {"classe_haute", "mrsort_aleatoire"})
        self.assertEqual(set(config["defenses"]), {"inv2_plus_grand", "naif"})
        self.assertEqual(config["tailles"], [300, 500, 1000])
        self.assertEqual(config["graines"], list(range(1000, 1020)))
        self.assertFalse(set(config["graines"]) & set(c.plan("calibrage", self.racine)["graines"]))

    def test_refuse_cles_manquantes_dupliquees_et_erreurs(self):
        lignes = self.creer_lot()
        c.verifier_couverture(lignes, self.lot_config)
        for invalides in (lignes[:1], lignes + lignes[:1], [dict(l, statut="erreur") for l in lignes]):
            with self.assertRaises(ValueError):
                c.verifier_couverture(invalides, self.lot_config)

    def test_aucune_reprise_silencieuse_dun_lot_modifie(self):
        self.creer_lot()
        self.assertFalse(c.lot_valide(self.dossier, self.lot_config))
        c.terminer_lot(self.dossier, self.lot_config, 10)
        self.assertTrue(c.lot_valide(self.dossier, self.lot_config))
        with self.assertRaises(ValueError):
            c.lot_valide(self.dossier, dict(self.lot_config, temps=99))
        with (self.dossier / "resultats.csv").open("a") as fichier:
            fichier.write("corruption\n")
        with self.assertRaisesRegex(ValueError, "Artefact modifié"):
            c.lot_valide(self.dossier, self.lot_config)

    def test_marqueur_interdit_si_audit_incomplet(self):
        self.creer_lot()
        c.ecrire_json(self.dossier / "audit.json", dict(statut="ok", decisions_verifiees=1))
        with self.assertRaises(ValueError):
            c.terminer_lot(self.dossier, self.lot_config, 10)
        self.assertFalse((self.dossier / "termine.json").exists())

    def test_agregation_recalcule_les_differences_et_annonce_incomplet(self):
        self.creer_lot()
        config = dict(self.config, graines=[100, 101])
        rapport = c.agreger(self.racine, dict(configuration=config), [self.lot])
        self.assertEqual(rapport["statut"], "incomplet")
        self.assertEqual(rapport["decisions_verifiees"], 2)
        from jalon3.analyse import lire_resultats
        lignes = lire_resultats(self.racine / "resultats_apparies.csv")
        self.assertAlmostEqual(lignes[1]["delta_attaque"], .2)
        self.assertIn("INCOMPLÈTE", (self.racine / "bilan.md").read_text())
        self.assertEqual(len(list((self.racine / "figures").glob("*"))), 0)

    def test_reprise_ne_relance_pas_les_lots_valides(self):
        self.creer_lot()
        c.terminer_lot(self.dossier, self.lot_config, 10)
        with patch.object(c.subprocess, "Popen", side_effect=AssertionError("Ne doit pas apprendre")), \
             patch.object(c, "agreger") as agreger:
            self.assertEqual(c.lancer(self.racine, dict(configuration=self.config), 1, [self.lot]), 0)
        self.assertTrue(agreger.called)

    def test_arret_ne_demarre_aucun_lot(self):
        (self.racine / "ARRETER").touch()
        with patch.object(c.subprocess, "Popen", side_effect=AssertionError("Ne doit pas apprendre")):
            self.assertEqual(c.lancer(self.racine, dict(configuration=self.config), 1, []), 1)
        self.assertEqual(c.lire_json(self.racine / "progression.json")["statut"], "arrete")

    def test_extension_importe_sans_modifier_les_archives(self):
        self.creer_lot()
        c.terminer_lot(self.dossier, self.lot_config, 10)
        c.ecrire_json(self.racine / "configuration.json", dict(configuration=self.config, sources_sha256={}))
        cible = self.racine / "extension"
        cible.mkdir()
        with patch.object(c, "verifier_archive"):
            c.importer_lots(cible, dict(configuration=self.config, sources_sha256={}), self.racine)
        nouveau = cible / "lots" / self.lot["id"]
        self.assertTrue(c.lot_valide(nouveau, dict(self.lot_config, sortie=str(nouveau))))
        self.assertEqual((nouveau / "termine.json").read_bytes(), (self.dossier / "termine.json").read_bytes())

    def test_refus_environnement_ou_sources_modifies(self):
        source = self.racine / "sources" / "code.py"
        source.parent.mkdir()
        source.write_text("x = 1\n")
        manifeste = dict(sources_sha256={"code.py": c.empreinte(source)}, versions={}, python="ancien")
        with self.assertRaisesRegex(ValueError, "environnement"):
            c.verifier_archive(self.racine, manifeste)
        source.write_text("x = 2\n")
        with self.assertRaisesRegex(ValueError, "Source archivée"):
            c.verifier_archive(self.racine, manifeste)

    def test_verrou_detecte_un_lanceur_ou_worker_actif(self):
        verrou = self.racine / "verrou"
        self.assertFalse(c.verrou_actif(verrou))
        with verrou.open("a") as fichier:
            fcntl.flock(fichier, fcntl.LOCK_EX)
            self.assertTrue(c.verrou_actif(verrou))
        self.assertFalse(c.verrou_actif(verrou))


if __name__ == "__main__":
    unittest.main()
