"""Tournoi reproductible : mêmes données pour chaque couple attaque/défense.

Une tâche par dimension/graine, éventuellement dans des processus indépendants.
Chaque bibliothèque numérique utilise un thread. Voir docs/protocole.md.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
from dataclasses import replace
from datetime import datetime
import hashlib
import importlib.metadata
import io
import json
import math
import multiprocessing
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from zoneinfo import ZoneInfo

for nom in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[nom] = "1"
os.environ.setdefault("MPLCONFIGDIR", "/tmp/projet-jalon3-matplotlib")

import numpy as np
from threadpoolctl import threadpool_limits

from .analyse import analyser, identifiant
from .interface import charger_strategies, classer, donnees, objets_uniformes
from .simulation import Comparaison, brouiller, evaluer, generer_instance, graine_derivee, recevoir

COLONNES = ["criteres", "categories", "taille", "graine", "ratio", "hacker", "nombre_h", "defense",
            "fidelite", "fidelite_equilibree", "fidelites_categories", "effectifs_test",
            "reference_majoritaire", "desaccord", "detection_h", "rejet_a", "temps",
            "partition_appariee", "fidelite_oracle_a", "perte_selection", "reconstruction_paire", "inversion_modeles",
            "preparation_id", "temps_preparation", "temps_selection", "temps_calcul_effectif",
            "groupe_choisi", "decision_details", "statut", "motif"]


def dimensions(texte):
    criteres, _, categories = texte.partition("x")
    if not (criteres.isdigit() and categories.isdigit()) or int(criteres) < 1 or int(categories) < 2:
        raise argparse.ArgumentTypeError("format attendu : CRITERESxCATEGORIES, par exemple 6x3")
    return int(criteres), int(categories)


def ecrire_ligne(sortie, fichier, ligne):
    sortie.writerow({c: json.dumps(v) if isinstance(v, (list, dict)) else v for c, v in ligne.items()})
    fichier.flush()


def texte_modele(probleme, modele):
    fichier = io.StringIO()
    modele.dump(probleme, fichier)
    return fichier.getvalue()


def archiver_modele(modele, probleme, chemin):
    if all(hasattr(modele, attribut) for attribut in ("b", "w", "lam")):
        np.savez_compressed(chemin.with_suffix(".npz"), b=modele.b, w=modele.w, lam=modele.lam)
    elif hasattr(modele, "dump"):
        chemin.with_suffix(".yml").write_text(texte_modele(probleme, modele), encoding="utf-8")


def archiver_decision(decision, probleme, dossier, nom):
    """Sauver le modèle retenu, et les deux candidats s'il y a segmentation."""
    chemin = dossier / identifiant(nom)
    archiver_modele(decision.modele, probleme, chemin)
    if decision.suspects is not None:
        np.save(chemin.with_suffix(".suspects.npy"), np.asarray(decision.suspects, dtype=bool))
    if decision.segmentation is not None:
        np.save(chemin.with_suffix(".segment.npy"), decision.segmentation.segment)
        for i, modele in enumerate(decision.segmentation.modeles):
            archiver_modele(modele, probleme, Path(str(chemin) + f"_modele_{i}"))
    if decision.groupe is not None or decision.details is not None:
        chemin.with_suffix(".details.json").write_text(json.dumps(dict(groupe=decision.groupe, details=decision.details),
                                                                 ensure_ascii=False, indent=2), encoding="utf-8")


def jouer_instance(configuration, dimension, graine):
    """Tout ce qui est privé reste dans ce worker ; les stratégies reçoivent leurs seules vues."""
    with threadpool_limits(limits=1):
        return _jouer_instance(configuration, dimension, graine)


def _jouer_instance(configuration, dimension, graine):
    hackers, defenses = charger_strategies()
    criteres, categories = dimension
    dossier = Path(configuration["sortie"]) / "instances" / f"{criteres}x{categories}" / f"graine_{graine:03d}"
    dossier.mkdir(parents=True)
    parties = [(0., "aucun")] + [(r, h) for r in configuration["ratios"] if r > 0
                                 for h in configuration["hackers"]]
    base = dict(criteres=criteres, categories=categories, graine=graine)
    erreur_instance = None
    try:
        instance_max = generer_instance(criteres, categories, max(configuration["tailles"]),
                                       graine, configuration["taille_test"])
        with (dossier / "probleme.yml").open("w", encoding="utf-8") as fichier:
            instance_max.probleme.dump(fichier)
        (dossier / "modele_a.yml").write_text(texte_modele(instance_max.probleme, instance_max.modele_a), encoding="utf-8")
        rng = np.random.default_rng(graine_derivee(graine, "diagnostic", criteres, categories))
        diagnostic = objets_uniformes(instance_max.probleme, configuration["taille_test"], rng)
        diagnostic_a = classer(instance_max.probleme, instance_max.modele_a, diagnostic)
        np.savez_compressed(dossier / "donnees.npz", x_a=instance_max.donnees_a.x, y_a=instance_max.donnees_a.y,
                            x_test=instance_max.test.x, y_test=instance_max.test.y,
                            x_diagnostic=diagnostic, y_diagnostic_a=diagnostic_a)
    except Exception as erreur:
        erreur_instance = f"{type(erreur).__name__}: {erreur}"
    lignes, diagnostics = [], {}
    with (dossier / "parties.csv").open("w", newline="", encoding="utf-8") as fichier:
        sortie = csv.DictWriter(fichier, fieldnames=COLONNES)
        sortie.writeheader()
        for taille in configuration["tailles"]:
            if erreur_instance is None:
                instance = replace(instance_max, donnees_a=donnees(instance_max.probleme,
                                   instance_max.donnees_a.x[:taille], instance_max.donnees_a.y[:taille]))
            for ratio, nom_h in parties:
                partie = dict(base, taille=taille, ratio=ratio, hacker=nom_h)
                echec = erreur_instance
                cas = dossier / f"taille_{taille}" / f"ratio_{ratio:g}" / identifiant(nom_h)
                if echec is None:
                    try:
                        injection = brouiller(instance, hackers.get(nom_h), ratio, graine)
                        recu, source_h = recevoir(instance, *injection, graine)
                        partie["nombre_h"] = len(injection.y)
                        cas.mkdir(parents=True)
                        np.savez_compressed(cas / "injection.npz", x_h=injection.x, y_h=injection.y,
                                            source_h=source_h)
                        if injection.modele is not None:
                            modele = texte_modele(instance.probleme, injection.modele)
                            empreinte = hashlib.sha256(modele.encode()).hexdigest()
                            if empreinte not in diagnostics:
                                prediction_h = classer(instance.probleme, injection.modele, diagnostic)
                                diagnostics[empreinte] = float(np.mean(prediction_h != diagnostic_a))
                            partie["desaccord"] = diagnostics[empreinte]
                            (cas / "modele_h.yml").write_text(modele, encoding="utf-8")
                        comparaison = Comparaison(recu, graine, configuration["temps"])
                    except Exception as erreur:
                        echec = f"{type(erreur).__name__}: {erreur}"
                for nom_d in configuration["defenses"]:
                    ligne = dict(partie, defense=nom_d)
                    try:
                        if echec:
                            raise RuntimeError(echec)
                        decision, duree, calcul = comparaison.decider(defenses[nom_d])
                        ligne.update(calcul, groupe_choisi=decision.groupe, decision_details=decision.details)
                        ligne.update(evaluer(instance, decision, source_h, injection.modele), temps=duree, statut="ok")
                        archiver_decision(decision, instance.probleme, cas, nom_d)
                    except Exception as erreur:
                        ligne.update(statut="erreur", motif=echec or f"{type(erreur).__name__}: {erreur}")
                    lignes.append(ligne)
                    ecrire_ligne(sortie, fichier, ligne)
                    print(f"{criteres}x{categories} graine={graine} N_A={taille} ρ={ratio:g} "
                          f"{nom_h}/{nom_d} : {ligne['statut']}, "
                          f"fidélité={ligne.get('fidelite', float('nan')):.3f}", flush=True)
    return lignes


def archiver_configuration(configuration):
    racine = Path(__file__).resolve().parent.parent
    dossier = Path(configuration["sortie"])
    sources = sorted((racine / "jalon3").rglob("*.py")) + sorted((racine / "jalon3").rglob("*.md"))
    # Inclure les imports locaux des stratégies : l'archive doit être exécutable.
    sources += sorted((racine / "jalon2").rglob("*.py"))
    sources += [racine / "pyproject.toml", racine / "uv.lock"]
    sources = [p for p in sources if "results" not in p.relative_to(racine).parts]
    empreintes = {}
    for source in sources:
        relatif = source.relative_to(racine)
        cible = dossier / "sources" / relatif
        cible.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, cible)
        empreintes[str(relatif)] = hashlib.sha256(source.read_bytes()).hexdigest()
    def git(*arguments):
        return subprocess.run(["git", *arguments], cwd=racine, capture_output=True, text=True, check=False).stdout.strip()
    hackers, defenses = charger_strategies()
    contenu = dict(protocole="uniforme-v1", extension="strategies-v1", configuration=configuration,
                   date_debut=datetime.now(ZoneInfo("Europe/Paris")).isoformat(),
                   python=sys.version, plateforme=platform.platform(), git_head=git("rev-parse", "HEAD"),
                   git_etat=git("status", "--short"), sources_sha256=empreintes,
                   versions={p: importlib.metadata.version(p) for p in ("lincs", "numpy", "scikit-learn", "matplotlib", "threadpoolctl")},
                   apprentissage_naif=dict(modeles_population=9, iterations_sans_progres=10, secondes_max=4),
                   controle_modele=dict(taille=2000, part_minimale=.005, essais_max=100),
                   nouvelles_strategies=dict(filtrage_iteratif=dict(retrait_max=.2, tours_max=2),
                                            naif_multi=dict(redemarrages_max=32, selection="erreur sur le mélange"),
                                            mrsort_concentre=dict(part_centrale=.8, bornes_normalisees=[.4, .6])),
                   strategies_h={h: dict(voit_donnees_a=hackers[h].voit_donnees_a,
                                          groupe_alea=hackers[h].groupe_alea or h) for h in configuration["hackers"]},
                   preparations_partagees={d: (defenses[d].preparer.__module__ + "." + defenses[d].preparer.__qualname__
                                               if defenses[d].preparer else None) for d in configuration["defenses"]},
                   informations_h="problème public, budget N_H, aléa ; aucune donnée A",
                   informations_b="mélange anonymisé, problème public, graine, budget calcul ; borne H<=A connue, ratio exact non fourni")
    (dossier / "configuration.json").write_text(json.dumps(contenu, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv=None):
    hackers, defenses = charger_strategies()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hackers", nargs="+", choices=sorted(hackers))
    parser.add_argument("--defenses", nargs="+", choices=sorted(defenses))
    parser.add_argument("--ratios", nargs="+", type=float, default=[0, .25, .5, 1], help="H/A ; la référence 0 est toujours ajoutée.")
    parser.add_argument("--dimensions", nargs="+", type=dimensions, default=[(6, 3)])
    parser.add_argument("--tailles", "--taille", dest="tailles", nargs="+", type=int, default=[300])
    parser.add_argument("--taille-test", type=int, default=10000)
    parser.add_argument("--graines", nargs="+", type=int, default=[0])
    parser.add_argument("--temps", type=float, default=10, help="Budget demandé aux stratégies ; naif et inv2_* gardent leur arrêt propre.")
    parser.add_argument("--processus", type=int, default=1, help="Répétitions indépendantes en parallèle, un thread numérique par processus.")
    parser.add_argument("--sortie", type=Path, default=Path("jalon3/results/essai"))
    parser.add_argument("--lister", action="store_true")
    parser.add_argument("--sans-figures", action="store_true", help="Produire les tableaux sans tracer les figures (lots d'une campagne).")
    args = parser.parse_args(argv)
    if not all(math.isfinite(r) and 0 <= r <= 1 for r in args.ratios):
        parser.error("Les ratios H/A doivent être entre 0 et 1.")
    if not (math.isfinite(args.temps) and args.temps > 0) or min(*args.tailles, args.taille_test) < 2:
        parser.error("Temps positif et tailles d'au moins deux objets requis.")
    if min(args.graines) < 0 or len(set(args.graines)) != len(args.graines):
        parser.error("Graines positives ou nulles, sans doublon.")
    if len(set(args.dimensions)) != len(args.dimensions) or args.processus < 1:
        parser.error("Dimensions sans doublon et nombre de processus positif requis.")
    if any(min(args.tailles) < categories for _, categories in args.dimensions):
        parser.error("Chaque taille A doit être au moins égale au nombre de catégories.")
    configuration = vars(args).copy()
    configuration.update(hackers=sorted(set(args.hackers or hackers)), defenses=sorted(set(args.defenses or defenses)),
                         ratios=sorted(set([0., *args.ratios])), tailles=sorted(set(args.tailles)),
                         sortie=str(args.sortie))
    for h in configuration["hackers"]:
        print(f"hacker  {h:<28} {hackers[h].fichier}.py (voit A : {hackers[h].voit_donnees_a})")
    for d in configuration["defenses"]:
        print(f"défense {d:<28} {defenses[d].fichier}.py")
    nombre = (len(args.dimensions) * len(args.graines) * len(configuration["tailles"]) *
              (1 + sum(r > 0 for r in configuration["ratios"]) * len(configuration["hackers"])) *
              len(configuration["defenses"]))
    print(f"{nombre} parties ; tailles A={configuration['tailles']}, ratios H/A={configuration['ratios']}.", flush=True)
    print("Les arrêts de naif et inv2_* restent ceux du jalon 2 ; --temps n'est pas une limite globale.", flush=True)
    if args.lister:
        return 0
    if args.sortie.exists():
        parser.error(f"Le dossier {args.sortie} existe déjà ; choisir une nouvelle --sortie.")
    args.sortie.mkdir(parents=True)
    archiver_configuration(configuration)
    taches = [(configuration, dimension, graine) for dimension in args.dimensions for graine in args.graines]
    lignes = []
    with (args.sortie / "resultats.csv").open("w", newline="", encoding="utf-8") as fichier:
        sortie = csv.DictWriter(fichier, fieldnames=COLONNES)
        sortie.writeheader()
        if args.processus == 1:
            for tache in taches:
                for ligne in jouer_instance(*tache):
                    lignes.append(ligne)
                    ecrire_ligne(sortie, fichier, ligne)
        else:
            with ProcessPoolExecutor(max_workers=args.processus, mp_context=multiprocessing.get_context("spawn")) as pool:
                futures = [pool.submit(jouer_instance, *tache) for tache in taches]
                for future in as_completed(futures):
                    for ligne in future.result():
                        lignes.append(ligne)
                        ecrire_ligne(sortie, fichier, ligne)
    analyser(args.sortie, figures=not args.sans_figures)
    echecs = sum(ligne["statut"] != "ok" for ligne in lignes)
    print(f"Résultats, bilan et figures : {args.sortie} ; {echecs} erreurs.", flush=True)
    return int(echecs > 0)


if __name__ == "__main__":
    raise SystemExit(main())
