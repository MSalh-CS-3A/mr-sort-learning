"""Audit des artefacts du premier couple, sans aucun nouvel apprentissage.

Recharge les données, modèles A/H/B et prédictions ; vérifie les 480 cellules
attendues, les injections emboîtées et les dégradations appariées.
Usage : python -m jalon3.validation_resultats DOSSIER
"""

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from lincs import classification as lc
from threadpoolctl import threadpool_limits

from .analyse import identifiant, lire_resultats
from .interface import classer
from jalon2.jalon2_deux_mrsort import MRSort


def verifier(dossier):
    dossier = Path(dossier)
    manifeste = json.loads((dossier / "configuration.json").read_text())
    config = manifeste["configuration"]
    if config["hackers"] != ["mrsort_aleatoire"] or config["defenses"] != ["naif"]:
        raise ValueError("Cet audit complet est réservé au premier couple mrsort_aleatoire / naif.")
    lignes = lire_resultats(dossier / "resultats.csv")
    appariees = lire_resultats(dossier / "resultats_apparies.csv")
    cle = lambda l: (l["criteres"], l["categories"], l["graine"], l["taille"], l["ratio"])
    index = {cle(l): l for l in lignes}
    index_apparie = {cle(l): l for l in appariees}
    attendu = {(d, c, s, n, r) for d, c in config["dimensions"] for s in config["graines"]
               for n in config["tailles"] for r in config["ratios"]}
    assert set(index) == attendu and len(index) == len(lignes), "Plan incomplet ou cellules dupliquées"
    assert set(index_apparie) == attendu and len(index_apparie) == len(appariees), "Appariement incomplet"
    assert all(l["statut"] == "ok" for l in lignes), "Au moins une partie en erreur"
    for relatif, empreinte in manifeste["sources_sha256"].items():
        assert hashlib.sha256((dossier / "sources" / relatif).read_bytes()).hexdigest() == empreinte, relatif
    compte = 0
    donnees_sha256 = {}
    for d, c in config["dimensions"]:
        for graine in config["graines"]:
            racine = dossier / "instances" / f"{d}x{c}" / f"graine_{graine:03d}"
            probleme = lc.Problem.load(io.StringIO((racine / "probleme.yml").read_text()))
            modele_a = lc.Model.load(probleme, io.StringIO((racine / "modele_a.yml").read_text()))
            with np.load(racine / "donnees.npz") as archive:
                jeux = {k: archive[k] for k in archive.files}
            for x, y in (("x_a", "y_a"), ("x_test", "y_test"), ("x_diagnostic", "y_diagnostic_a")):
                np.testing.assert_array_equal(classer(probleme, modele_a, jeux[x]), jeux[y])
                assert np.isfinite(jeux[x]).all() and (jeux[x] >= 0).all() and (jeux[x] <= 1).all()
            donnees_sha256[str(racine.relative_to(dossier))] = hashlib.sha256((racine / "donnees.npz").read_bytes()).hexdigest()
            assert len(jeux["x_test"]) == config["taille_test"]
            assert not np.array_equal(jeux["x_test"], jeux["x_diagnostic"])
            injections = []
            modele_h_texte = None
            modele_h = None
            desaccord = None
            for taille in config["tailles"]:
                reference = index[d, c, graine, taille, 0]["fidelite"]
                for ratio in config["ratios"]:
                    ligne = index[d, c, graine, taille, ratio]
                    nom_h = "aucun" if ratio == 0 else "mrsort_aleatoire"
                    assert ligne["hacker"] == nom_h and ligne["defense"] == "naif"
                    cas = racine / f"taille_{taille}" / f"ratio_{ratio:g}" / identifiant(nom_h)
                    with np.load(cas / "injection.npz") as injection:
                        x_h, y_h, source_h = injection["x_h"], injection["y_h"], injection["source_h"]
                    nombre = round(taille * ratio)
                    assert len(y_h) == nombre == ligne["nombre_h"]
                    assert len(source_h) == taille + nombre and source_h.sum() == nombre
                    if ratio > 0:
                        texte_h = (cas / "modele_h.yml").read_text()
                        if modele_h_texte is None:
                            modele_h_texte = texte_h
                            modele_h = lc.Model.load(probleme, io.StringIO(texte_h))
                            desaccord = np.mean(classer(probleme, modele_h, jeux["x_diagnostic"]) != jeux["y_diagnostic_a"])
                        assert texte_h == modele_h_texte, "M_H a changé entre conditions"
                        np.testing.assert_array_equal(classer(probleme, modele_h, x_h), y_h)
                        np.testing.assert_allclose(ligne["desaccord"], desaccord, atol=1e-12)
                        injections.append((x_h, y_h))
                    with np.load(cas / (identifiant("naif") + ".npz")) as modele:
                        assert all(np.isfinite(modele[k]).all() for k in modele.files), "Modèle B non fini"
                        modele_b = MRSort(modele["b"], modele["w"], float(modele["lam"]))
                    correct = modele_b.predict(jeux["x_test"]) == jeux["y_test"]
                    np.testing.assert_allclose(ligne["fidelite"], correct.mean(), atol=1e-12)
                    effectifs = np.bincount(jeux["y_test"], minlength=c)
                    assert json.loads(ligne["effectifs_test"]) == effectifs.tolist()
                    rappels = [correct[jeux["y_test"] == categorie].mean() if effectifs[categorie] else None
                               for categorie in range(c)]
                    for calcule, conserve in zip(rappels, json.loads(ligne["fidelites_categories"])):
                        if calcule is None:
                            assert conserve is None
                        else:
                            np.testing.assert_allclose(calcule, conserve, atol=1e-12)
                    if effectifs.all():
                        np.testing.assert_allclose(ligne["fidelite_equilibree"], np.mean(rappels), atol=1e-12)
                    else:
                        assert ligne["fidelite_equilibree"] is None
                    np.testing.assert_allclose(index_apparie[d, c, graine, taille, ratio]["delta_attaque"],
                                               reference - correct.mean(), atol=1e-12)
                    compte += 1
            if injections:
                grand_x, grand_y = max(injections, key=lambda xy: len(xy[1]))
                for x, y in injections:
                    np.testing.assert_array_equal(x, grand_x[:len(y)])
                    np.testing.assert_array_equal(y, grand_y[:len(y)])
            print(f"Graine {graine} ({d}x{c}) : données, injections et modèles B vérifiés.", flush=True)
    with (dossier / "resume.csv").open(newline="", encoding="utf-8") as fichier:
        resume = list(csv.DictReader(fichier))
    for r in resume:
        groupe = [l for l in lignes if (l["criteres"], l["categories"], l["taille"], l["ratio"], l["hacker"], l["defense"]) ==
                  (int(r["criteres"]), int(r["categories"]), int(r["taille"]), float(r["ratio"]), r["hacker"], r["defense"])]
        assert int(r["parties"]) == len(config["graines"]) == len(groupe) and int(r["echecs"]) == 0
        np.testing.assert_allclose(float(r["fidelite_moyenne"]), np.mean([l["fidelite"] for l in groupe]), atol=1e-12)
        if len(groupe) > 1:
            np.testing.assert_allclose(float(r["fidelite_ecart_type"]), np.std([l["fidelite"] for l in groupe], ddof=1), atol=1e-12)
    rapport = dict(statut="ok", parties_verifiees=compte, graines=len(config["graines"]),
                   controles=["plan complet sans doublons", "sources archivées intactes", "étiquettes A/test/diagnostic",
                              "M_H fixe et cohérent", "injections H emboîtées", "plafonds et sources",
                              "modèles B rechargés et fidélités recalculées", "rappels et effectifs par catégorie",
                              "dégradations appariées", "effectifs et statistiques de synthèse"],
                   donnees_sha256=donnees_sha256,
                   script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (dossier / "audit.json").write_text(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Audit réussi : {compte} parties, {len(config['graines'])} graines, aucun nouvel apprentissage.")
    return rapport


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dossier", type=Path)
    with threadpool_limits(limits=1):
        verifier(parser.parse_args().dossier)
