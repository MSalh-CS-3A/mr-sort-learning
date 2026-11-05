"""Tournoi : chaque défense contre chaque hacker, sur les mêmes instances et graines."""

import argparse
import csv
import math
import os
from pathlib import Path
import statistics

# Un thread pour comparer les défenses avec les mêmes ressources.
for nom in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[nom] = "1"

from threadpoolctl import threadpool_limits

from .interface import charger_strategies
from .simulation import brouiller, decider, evaluer, generer_instance, recevoir

COLONNES = ["criteres", "categories", "taille", "graine", "ratio", "hacker", "nombre_h", "defense",
            "fidelite", "detection_h", "rejet_a", "temps", "statut", "motif"]
CLE = ["criteres", "categories", "ratio", "hacker", "defense"]


def dimensions(texte):
    criteres, _, categories = texte.partition("x")
    if not (criteres.isdigit() and categories.isdigit()) or int(criteres) < 1 or int(categories) < 2:
        raise argparse.ArgumentTypeError("format attendu : CRITERESxCATEGORIES, par exemple 6x3")
    return int(criteres), int(categories)


def moyenne(valeurs):
    valeurs = [v for v in valeurs if v is not None]
    return statistics.mean(valeurs) if valeurs else None


def resumer(lignes):
    """Une ligne par configuration, hacker et défense, sur les parties réussies."""
    groupes = {}
    for ligne in lignes:
        if ligne["statut"] == "ok":
            groupes.setdefault(tuple(ligne[c] for c in CLE), []).append(ligne)
    return [dict(zip(CLE, cle), parties=len(groupe),
                 fidelite_moyenne=moyenne(l["fidelite"] for l in groupe),
                 fidelite_min=min(l["fidelite"] for l in groupe),
                 detection_h_moyenne=moyenne(l.get("detection_h") for l in groupe),
                 rejet_a_moyen=moyenne(l.get("rejet_a") for l in groupe))
            for cle, groupe in sorted(groupes.items())]


def afficher(resume, defenses):
    """Matrice hacker × défense de la fidélité moyenne, une par dimension et ratio."""
    blocs = {}
    for r in resume:
        blocs.setdefault((r["criteres"], r["categories"], r["ratio"]), {})[r["hacker"], r["defense"]] = r
    for (criteres, categories, ratio), cellules in blocs.items():
        print(f"\nFidélité moyenne à M_A : {criteres} critères, {categories} catégories, ratio {ratio:g}")
        hackers = sorted({h for h, _ in cellules})
        largeur = max(map(len, hackers + ["hacker"]))
        print(f"{'hacker':<{largeur}}" + "".join(f"  {d:>20}" for d in defenses))
        for h in hackers:
            valeurs = [cellules.get((h, d)) for d in defenses]
            print(f"{h:<{largeur}}" + "".join(
                f"  {r['fidelite_moyenne']:>20.3f}" if r else f"  {'-':>20}" for r in valeurs))


def main(argv=None):
    hackers, defenses = charger_strategies()
    parser = argparse.ArgumentParser(description="Faire jouer les défenses de B contre les hackers.")
    parser.add_argument("--hackers", nargs="+", choices=sorted(hackers), help="Défaut : tous les hackers enregistrés.")
    parser.add_argument("--defenses", nargs="+", choices=sorted(defenses), help="Défaut : toutes les défenses enregistrées.")
    parser.add_argument("--ratios", nargs="+", type=float, default=[0, .5, 1],
                        help="Données de H par donnée de A, entre 0 et 1. 0 : référence sans brouillage.")
    parser.add_argument("--dimensions", nargs="+", type=dimensions, default=[(6, 3)], help="Par exemple 6x3 10x5.")
    parser.add_argument("--taille", type=int, default=300, help="Nombre de données envoyées par A.")
    parser.add_argument("--taille-test", type=int, default=1000, help="Objets neufs pour mesurer la fidélité.")
    parser.add_argument("--graines", nargs="+", type=int, default=[0])
    parser.add_argument("--temps", type=float, default=10, help="Secondes accordées à chaque défense.")
    parser.add_argument("--sortie", type=Path, default=Path("jalon3/results/essai"), help="Nouveau dossier à créer.")
    parser.add_argument("--lister", action="store_true", help="Afficher stratégies et programme, sans calcul.")
    args = parser.parse_args(argv)
    if not all(0 <= r <= 1 for r in args.ratios):
        parser.error("Les ratios doivent être entre 0 et 1 : H envoie au plus une donnée par donnée de A.")
    if not (math.isfinite(args.temps) and args.temps > 0) or min(args.taille, args.taille_test) < 2:
        parser.error("Temps positif et tailles d'au moins deux objets requis.")
    if min(args.graines) < 0 or len(set(args.graines)) != len(args.graines):
        parser.error("Les graines doivent être positives ou nulles, sans doublon.")
    noms_h = args.hackers or sorted(hackers)
    noms_d = args.defenses or sorted(defenses)
    ratios = sorted(set(args.ratios))
    parties = [(r, None) for r in ratios if r == 0] + [(r, h) for r in ratios if r > 0 for h in noms_h]

    for nom in noms_h:
        print(f"hacker  {nom:<28} {hackers[nom].fichier}.py")
    for nom in noms_d:
        print(f"défense {nom:<28} {defenses[nom].fichier}.py")
    nombre = len(args.dimensions) * len(args.graines) * len(parties) * len(noms_d)
    print(f"{len(args.dimensions) * len(args.graines)} instances × {len(parties)} brouillages × "
          f"{len(noms_d)} défenses = {nombre} parties.")
    print(f"Budget nominal : {nombre * args.temps / 60:.1f} minutes si chaque défense respecte --temps, "
          "hors génération ; les défenses inv2_* ont leur propre arrêt.")
    if args.lister:
        return 0
    if args.sortie.exists():
        parser.error(f"Le dossier {args.sortie} existe déjà ; choisir une nouvelle --sortie.")
    args.sortie.mkdir(parents=True)

    lignes, numero = [], 0
    with (args.sortie / "resultats.csv").open("w", newline="", encoding="utf-8") as fichier, threadpool_limits(limits=1):
        sortie = csv.DictWriter(fichier, fieldnames=COLONNES)
        sortie.writeheader()
        for criteres, categories in args.dimensions:
            for graine in args.graines:
                base = dict(criteres=criteres, categories=categories, taille=args.taille, graine=graine)
                try:
                    instance = generer_instance(criteres, categories, args.taille, graine, args.taille_test)
                except Exception as erreur:
                    instance, echec_instance = None, f"{type(erreur).__name__}: {erreur}"
                for ratio, nom_h in parties:
                    partie = dict(base, ratio=ratio, hacker=nom_h or "aucun")
                    echec = None if instance else echec_instance
                    if instance:
                        try:
                            x_h, y_h = brouiller(instance, hackers.get(nom_h), ratio, graine)
                            recu, source_h = recevoir(instance, x_h, y_h, graine)
                            partie["nombre_h"] = len(y_h)
                        except Exception as erreur:
                            echec = f"{type(erreur).__name__}: {erreur}"
                    for nom_d in noms_d:
                        numero += 1
                        ligne = dict(partie, defense=nom_d)
                        try:
                            if echec:
                                raise RuntimeError(echec)
                            decision, duree = decider(defenses[nom_d], recu, graine, args.temps)
                            ligne.update(evaluer(instance, decision, source_h), temps=duree, statut="ok")
                        except Exception as erreur:
                            ligne.update(statut="erreur", motif=echec or f"{type(erreur).__name__}: {erreur}")
                        lignes.append(ligne)
                        sortie.writerow(ligne)
                        fichier.flush()  # Les parties terminées restent lisibles après une interruption.
                        print(f"[{numero}/{nombre}] {criteres}x{categories} graine={graine} ratio={ratio:g} "
                              f"{ligne['hacker']} contre {nom_d} : {ligne['statut']}, "
                              f"fidélité={ligne.get('fidelite', float('nan')):.3f}", flush=True)
                        if ligne["statut"] == "erreur":
                            print(ligne["motif"], flush=True)

    resume = resumer(lignes)
    with (args.sortie / "resume.csv").open("w", newline="", encoding="utf-8") as fichier:
        sortie = csv.DictWriter(fichier, fieldnames=CLE + ["parties", "fidelite_moyenne", "fidelite_min",
                                                           "detection_h_moyenne", "rejet_a_moyen"])
        sortie.writeheader()
        sortie.writerows(resume)
    afficher(resume, noms_d)
    echecs = sum(ligne["statut"] != "ok" for ligne in lignes)
    print(f"\nRésultats : {args.sortie / 'resultats.csv'} et {args.sortie / 'resume.csv'} ; {echecs} parties en erreur.")
    return int(echecs > 0)


if __name__ == "__main__":
    raise SystemExit(main())
