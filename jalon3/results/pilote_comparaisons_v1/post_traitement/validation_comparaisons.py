"""Recharger les artefacts des comparaisons, sans nouvel apprentissage.

Usage : python -m jalon3.validation_comparaisons DOSSIER
Vérifie le plan, les fidélités, les deltas/gains appariés et l'identité des
partitions/modèles réellement partagés par les deux sélections Inv-2.
"""

import argparse
from collections import defaultdict
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from lincs import classification as lc
from threadpoolctl import threadpool_limits

from jalon2.jalon2_deux_mrsort import MRSort
from .analyse import identifiant, lire_resultats
from .interface import classer
from .simulation import graine_derivee


def charger_modele(chemin):
    with np.load(chemin) as archive:
        assert all(np.isfinite(archive[k]).all() for k in archive.files), str(chemin)
        return MRSort(archive["b"], archive["w"], float(archive["lam"]))


def verifier(dossier):
    dossier = Path(dossier)
    manifeste = json.loads((dossier / "configuration.json").read_text())
    config = manifeste["configuration"]
    lignes = lire_resultats(dossier / "resultats_apparies.csv")
    cle = lambda l: (l["criteres"], l["categories"], l["graine"], l["taille"], l["ratio"], l["hacker"], l["defense"])
    index = {cle(l): l for l in lignes}
    attendu = {(d, c, s, n, r, h, b) for d, c in config["dimensions"] for s in config["graines"]
               for n in config["tailles"] for r in config["ratios"]
               for h in (["aucun"] if r == 0 else config["hackers"]) for b in config["defenses"]}
    assert set(index) == attendu and len(index) == len(lignes), "Plan incomplet ou doublons"
    assert all(l["statut"] == "ok" for l in lignes), "Au moins une partie a échoué"
    for relatif, empreinte in manifeste["sources_sha256"].items():
        assert hashlib.sha256((dossier / "sources" / relatif).read_bytes()).hexdigest() == empreinte
    jeux, cas_charges, partages = {}, {}, defaultdict(list)
    for ligne in lignes:
        d, c, graine, taille, ratio, hacker, defense = cle(ligne)
        racine = dossier / "instances" / f"{d}x{c}" / f"graine_{graine:03d}"
        if (d, c, graine) not in jeux:
            with np.load(racine / "donnees.npz") as archive:
                donnees = {k: archive[k] for k in archive.files}
            probleme = lc.Problem.load(io.StringIO((racine / "probleme.yml").read_text()))
            modele_a = lc.Model.load(probleme, io.StringIO((racine / "modele_a.yml").read_text()))
            for x, y in (("x_a", "y_a"), ("x_test", "y_test"), ("x_diagnostic", "y_diagnostic_a")):
                np.testing.assert_array_equal(classer(probleme, modele_a, donnees[x]), donnees[y])
            jeux[d, c, graine] = donnees, probleme
        donnees, probleme = jeux[d, c, graine]
        cle_cas = (d, c, graine, taille, ratio, hacker)
        cas = racine / f"taille_{taille}" / f"ratio_{ratio:g}" / identifiant(hacker)
        if cle_cas not in cas_charges:
            with np.load(cas / "injection.npz") as archive:
                x_h, y_h, source_h = archive["x_h"], archive["y_h"], archive["source_h"]
            assert len(y_h) <= round(taille * ratio)
            x = np.vstack((donnees["x_a"][:taille], x_h))
            y = np.concatenate((donnees["y_a"][:taille], y_h))
            ordre = np.random.default_rng(graine_derivee(graine, "melange")).permutation(len(y))
            source = np.concatenate((np.zeros(taille, dtype=bool), np.ones(len(y_h), dtype=bool)))[ordre]
            np.testing.assert_array_equal(source_h, source)
            verite_h = None
            if (cas / "modele_h.yml").exists():
                modele_h = lc.Model.load(probleme, io.StringIO((cas / "modele_h.yml").read_text()))
                np.testing.assert_array_equal(classer(probleme, modele_h, x_h), y_h)
                verite_h = classer(probleme, modele_h, donnees["x_test"])
                desaccord = float(np.mean(classer(probleme, modele_h, donnees["x_diagnostic"]) != donnees["y_diagnostic_a"]))
            else:
                desaccord = None
            cas_charges[cle_cas] = x[ordre], y[ordre], source_h, verite_h, desaccord, len(y_h)
        x, y, source_h, verite_h, desaccord, nombre_h = cas_charges[cle_cas]
        assert ligne["nombre_h"] == nombre_h
        if desaccord is None:
            assert ligne["desaccord"] is None
        else:
            np.testing.assert_allclose(ligne["desaccord"], desaccord, atol=1e-12)
        nom = identifiant(defense)
        modele_b = charger_modele(cas / (nom + ".npz"))
        prediction = modele_b.predict(donnees["x_test"])
        correct = prediction == donnees["y_test"]
        np.testing.assert_allclose(ligne["fidelite"], correct.mean(), atol=1e-12)
        effectifs = np.bincount(donnees["y_test"], minlength=c)
        assert json.loads(ligne["effectifs_test"]) == effectifs.tolist()
        if effectifs.all():
            rappels = [correct[donnees["y_test"] == i].mean() for i in range(c)]
            np.testing.assert_allclose(ligne["fidelite_equilibree"], np.mean(rappels), atol=1e-12)
        reference = index[d, c, graine, taille, 0, "aucun", defense]
        np.testing.assert_allclose(ligne["delta_attaque"], reference["fidelite"] - ligne["fidelite"], atol=1e-12)
        reference_naive = index.get((d, c, graine, taille, ratio, hacker, "naif"))
        if reference_naive is not None:
            np.testing.assert_allclose(ligne["gain_defense"], ligne["fidelite"] - reference_naive["fidelite"], atol=1e-12)
        if (cas / (nom + ".suspects.npy")).exists():
            suspects = np.load(cas / (nom + ".suspects.npy"))
            np.testing.assert_allclose(ligne["rejet_a"], suspects[~source_h].mean(), atol=1e-12)
            if source_h.any():
                np.testing.assert_allclose(ligne["detection_h"], suspects[source_h].mean(), atol=1e-12)
        if ligne.get("preparation_id"):
            segment = np.load(cas / (nom + ".segment.npy"))
            candidats = [charger_modele(cas / (nom + f"_modele_{k}.npz")) for k in (0, 1)]
            groupe = int(ligne["groupe_choisi"])
            np.testing.assert_array_equal(candidats[groupe].predict(donnees["x_test"]), prediction)
            np.testing.assert_array_equal(np.load(cas / (nom + ".suspects.npy")), segment != groupe)
            if defense.endswith("plus_grand"):
                assert groupe == int(np.argmax(np.bincount(segment, minlength=2)))
            elif defense.endswith("mieux_explique"):
                erreurs = [np.mean(candidats[k].predict(x[segment == k]) != y[segment == k]) for k in (0, 1)]
                assert groupe == int(np.argmin(erreurs))
            preds = [m.predict(donnees["x_test"]) for m in candidats]
            fidelites_a = [np.mean(p == donnees["y_test"]) for p in preds]
            np.testing.assert_allclose(ligne["fidelite_oracle_a"], max(fidelites_a), atol=1e-12)
            np.testing.assert_allclose(ligne["perte_selection"], max(fidelites_a) - ligne["fidelite"], atol=1e-12)
            accord = np.mean(segment == source_h.astype(int))
            np.testing.assert_allclose(ligne["partition_appariee"], max(accord, 1 - accord), atol=1e-12)
            if verite_h is not None:
                fidelites_h = [np.mean(p == verite_h) for p in preds]
                alignements = [(fidelites_a[0] + fidelites_h[1]) / 2, (fidelites_a[1] + fidelites_h[0]) / 2]
                np.testing.assert_allclose(ligne["reconstruction_paire"], max(alignements), atol=1e-12)
                if not np.isclose(alignements[0], alignements[1], rtol=0, atol=1e-12):
                    assert ligne["inversion_modeles"] == int(groupe != int(np.argmax(alignements)))
                else:
                    assert ligne["inversion_modeles"] is None
            partages[ligne["preparation_id"]].append((ligne, segment, candidats))
    for groupe in partages.values():
        reference, segment, modeles = groupe[0]
        cout = 0
        for ligne, autre_segment, autres_modeles in groupe:
            np.testing.assert_array_equal(segment, autre_segment)
            for a, b in zip(modeles, autres_modeles):
                for attribut in ("b", "w", "lam"):
                    np.testing.assert_array_equal(getattr(a, attribut), getattr(b, attribut))
            np.testing.assert_allclose(ligne["temps_preparation"], reference["temps_preparation"], atol=1e-12)
            np.testing.assert_allclose(ligne["temps"], ligne["temps_preparation"] + ligne["temps_selection"], atol=1e-10)
            cout += ligne["temps_calcul_effectif"]
        np.testing.assert_allclose(cout, reference["temps_preparation"] + sum(l[0]["temps_selection"] for l in groupe), atol=1e-9)
    rapport = dict(statut="ok", decisions_verifiees=len(lignes), melanges=len(cas_charges),
                   preparations_inv2=len(partages), selections_partagees=sum(len(g) for g in partages.values()),
                   controles=["plan et sources", "données et classes A/H", "modèles B rechargés", "fidélités et rappels",
                              "deltas et gains appariés", "détection", "règles de sélection", "identité des modèles et partitions",
                              "diagnostics oracle", "comptabilité des temps partagés"],
                   script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (dossier / "audit.json").write_text(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Audit réussi : {len(lignes)} décisions, {len(cas_charges)} mélanges, {len(partages)} préparations partagées.")
    return rapport


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dossier", type=Path)
    with threadpool_limits(limits=1):
        verifier(parser.parse_args().dossier)
