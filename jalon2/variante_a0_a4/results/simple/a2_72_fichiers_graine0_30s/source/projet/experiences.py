"""Boucle de benchmark et export CSV. Aucun calcul ne démarre à l'import."""

import argparse
import csv
import math
import os
from pathlib import Path

# Un thread pour comparer les méthodes avec les mêmes ressources.
for nom in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[nom] = "1"
os.environ.setdefault("MPLCONFIGDIR", "/tmp/projet-matplotlib")

from threadpoolctl import threadpool_limits

from .apprentissage import charger
from .algorithmes import resoudre


METHODES = ["A0-uniforme"] + [f"{methode}-{init}" for methode in ("A1", "A2", "A3", "A4")
                             for init in ("uniforme", "gmm")]
COMPARAISON_MINIMALE = ["A0-uniforme", "A1-uniforme", "A1-gmm", "A3-uniforme", "A3-gmm"]


def ecrire_csv(chemin, colonnes, lignes):
    with chemin.open("w", newline="", encoding="utf-8") as fichier:
        sortie = csv.writer(fichier)
        sortie.writerow(colonnes)
        sortie.writerows(lignes)


def exporter(dossier, donnees, resultat):
    """Sauver le meilleur état et la trajectoire, sans recopier les données."""
    dossier.mkdir()
    ecrire_csv(dossier / "trace.csv", ["temps", "LG_courant", "meilleur_LG"],
               ((t["temps"], t["LG_courant"], t["meilleur_LG"]) for t in resultat.trace))
    etat = resultat.meilleur
    if etat is None:
        return
    with (dossier / "problem.yml").open("w", encoding="utf-8") as fichier:
        donnees.probleme.dump(fichier)
    for groupe, modele in enumerate(etat.modeles):
        with (dossier / f"modele_{groupe}.yml").open("w", encoding="utf-8") as fichier:
            modele.dump(donnees.probleme, fichier)
    categories = [c.name for c in donnees.probleme.ordered_categories]
    lignes = ((nom, int(etat.z[i]), categories[donnees.y[i]],
               categories[etat.predictions[0, i]], categories[etat.predictions[1, i]])
              for i, nom in enumerate(donnees.noms))
    ecrire_csv(dossier / "affectations.csv",
               ["nom", "groupe", "categorie_observee", "prediction_0", "prediction_1"], lignes)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Comparer les heuristiques Inv-2-MR-Sort.")
    parser.add_argument("donnees", nargs="+", type=Path, help="CSV ou répertoires de données.")
    choix = parser.add_mutually_exclusive_group()
    choix.add_argument("--methodes", nargs="+", choices=METHODES, help="Défaut : comparaison minimale de cinq méthodes.")
    choix.add_argument("--toutes", action="store_true", help="Les neuf combinaisons A0-A4.")
    parser.add_argument("--graines", nargs="+", type=int, default=[0])
    parser.add_argument("--temps", type=float, default=30, help="Secondes par exécution, initialisation comprise.")
    parser.add_argument("--temps-appel", type=float, default=1, help="Secondes nominales par appel WPB.")
    parser.add_argument("--sortie", type=Path, default=Path("results/simple/essai"), help="Nouveau dossier à créer.")
    parser.add_argument("--pilote", action="store_true", help="Sélectionner les douze fichiers du pilote.")
    parser.add_argument("--lister", action="store_true", help="Afficher le programme sans apprentissage ni export.")
    args = parser.parse_args(argv)
    if not all(math.isfinite(t) and t > 0 for t in (args.temps, args.temps_appel)):
        parser.error("Les temps doivent être positifs et finis.")
    if min(args.graines) < 0 or len(set(args.graines)) != len(args.graines):
        parser.error("Les graines doivent être positives ou nulles, sans doublon.")
    fichiers = set()
    for chemin in args.donnees:
        if chemin.is_dir():
            fichiers.update(chemin.rglob("*.csv"))
        elif chemin.is_file() and chemin.suffix == ".csv":
            fichiers.add(chemin)
        else:
            parser.error(f"CSV ou répertoire introuvable : {chemin}")
    if args.pilote:
        fichiers = {p for p in fichiers if p.name in {
            "n0300_rep50-50_noise00.csv", "n1200_rep75-25_noise10.csv"}}
    fichiers = sorted(fichiers)
    methodes = METHODES if args.toutes else (args.methodes or COMPARAISON_MINIMALE)
    if not fichiers or len(set(methodes)) != len(methodes):
        parser.error("Aucun fichier sélectionné ou méthodes dupliquées.")
    nombre = len(fichiers)*len(methodes)*len(args.graines)
    print(f"{len(fichiers)} fichiers × {len(methodes)} méthodes × {len(args.graines)} graines = {nombre} exécutions.")
    print(f"Budget nominal maximal : {nombre*args.temps/60:.1f} minutes, hors dépassements coopératifs.")
    if args.lister:
        return 0
    if args.sortie.exists():
        parser.error(f"Le dossier {args.sortie} existe déjà ; choisir une nouvelle --sortie.")
    args.sortie.mkdir(parents=True)
    colonnes = ["fichier", "methode", "initialisation", "graine", "N", "criteres", "categories",
                "budget", "temps_appel", "temps_total", "depassement", "LG", "taux_erreur",
                "taille_groupe_0", "taille_groupe_1", "statut", "motif", "details"]
    numero, echecs = 0, 0
    with (args.sortie / "resultats.csv").open("w", newline="", encoding="utf-8") as fichier, threadpool_limits(limits=1):
        sortie = csv.DictWriter(fichier, fieldnames=colonnes)
        sortie.writeheader()
        for chemin in fichiers:
            donnees = charger(chemin)  # Lecture commune, hors budget des méthodes.
            for identifiant in methodes:
                methode, initialisation = identifiant.split("-")
                for graine in args.graines:
                    numero += 1
                    details = f"{numero:04d}_{identifiant}_graine_{graine}"
                    ligne = dict(fichier=str(chemin), methode=methode, initialisation=initialisation,
                                 graine=graine, N=len(donnees.y), criteres=donnees.x.shape[1],
                                 categories=len(donnees.probleme.ordered_categories),
                                 budget=args.temps, temps_appel=args.temps_appel, details=details)
                    try:
                        resultat = resoudre(donnees, methode, initialisation, args.temps, args.temps_appel, graine)
                        exporter(args.sortie / details, donnees, resultat)
                        etat = resultat.meilleur
                        ligne.update(temps_total=resultat.temps, depassement=max(0, resultat.temps-args.temps),
                                     statut="ok" if etat else "sans_solution", motif=resultat.arret)
                        if etat is not None:
                            ligne.update(LG=etat.lg, taux_erreur=etat.lg/len(donnees.y),
                                         taille_groupe_0=int((etat.z == 0).sum()),
                                         taille_groupe_1=int((etat.z == 1).sum()))
                        else:
                            echecs += 1
                    except Exception as erreur:
                        ligne.update(statut="erreur", motif=f"{type(erreur).__name__}: {erreur}")
                        echecs += 1
                    sortie.writerow(ligne)
                    fichier.flush()  # Les lignes terminées restent lisibles après une interruption.
                    print(f"[{numero}/{nombre}] {chemin} {identifiant} graine={graine} : "
                          f"{ligne['statut']}, LG={ligne.get('LG', '?')}", flush=True)
                    if ligne["statut"] == "erreur":
                        print(ligne["motif"], flush=True)
    print(f"Résultats : {args.sortie / 'resultats.csv'} ; {echecs} exécutions sans résultat valide.")
    return int(echecs > 0)


if __name__ == "__main__":
    raise SystemExit(main())
