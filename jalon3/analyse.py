"""Analyse appariée et figures scientifiques, sans relancer d'apprentissage.

Usage : python -m jalon3.analyse DOSSIER_EXPERIENCE
Les bandes représentent ± un écart-type entre graines, pas un intervalle de confiance.
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path
import re
import hashlib
import statistics


CLE = ("criteres", "categories", "taille", "ratio", "hacker", "defense")
MESURES = ("fidelite", "fidelite_equilibree", "delta_attaque", "desaccord", "temps",
           "detection_h", "rejet_a", "reference_majoritaire", "gain_defense",
           "partition_appariee", "fidelite_oracle_a", "perte_selection", "reconstruction_paire", "inversion_modeles",
           "temps_preparation", "temps_selection", "temps_calcul_effectif")


def identifiant(nom):
    """Nom de fichier stable, sans chemins et sans collisions après nettoyage."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", nom) + "_" + hashlib.sha256(nom.encode()).hexdigest()[:8]


def lire_resultats(chemin):
    with Path(chemin).open(newline="", encoding="utf-8") as fichier:
        lignes = list(csv.DictReader(fichier))
    for ligne in lignes:
        for cle in ("criteres", "categories", "taille", "graine", "nombre_h"):
            ligne[cle] = int(ligne[cle]) if ligne.get(cle) else None
        for cle in ("ratio", *MESURES):
            ligne[cle] = float(ligne[cle]) if ligne.get(cle) not in (None, "") else None
    return lignes


def apparier(lignes):
    """Delta par graine, taille et défense ; aucune moyenne non appariée."""
    cle = lambda l: (l["criteres"], l["categories"], l["taille"], l["graine"], l["defense"])
    references = {cle(l): l["fidelite"] for l in lignes if l["ratio"] == 0 and l["statut"] == "ok"}
    cle_naif = lambda l: (l["criteres"], l["categories"], l["taille"], l["graine"], l["ratio"], l["hacker"])
    naifs = {cle_naif(l): l["fidelite"] for l in lignes if l["defense"] == "naif" and l["statut"] == "ok"}
    for ligne in lignes:
        reference = references.get(cle(ligne))
        ligne["delta_attaque"] = (reference - ligne["fidelite"]
                                  if reference is not None and ligne["statut"] == "ok" else None)
        reference_naive = naifs.get(cle_naif(ligne))
        ligne["gain_defense"] = (ligne["fidelite"] - reference_naive
                                  if reference_naive is not None and ligne["statut"] == "ok" else None)
    return lignes


def resumer(lignes):
    groupes = defaultdict(list)
    for ligne in lignes:
        groupes[tuple(ligne[c] for c in CLE)].append(ligne)
    resume = []
    for cle, groupe in sorted(groupes.items()):
        reussis = [l for l in groupe if l["statut"] == "ok"]
        ligne = dict(zip(CLE, cle), parties=len(reussis), echecs=len(groupe) - len(reussis))
        for mesure in MESURES:
            valeurs = [l[mesure] for l in reussis if l.get(mesure) is not None]
            ligne[mesure + "_n"] = len(valeurs)
            ligne[mesure + "_moyenne"] = statistics.mean(valeurs) if valeurs else None
            ligne[mesure + "_ecart_type"] = statistics.stdev(valeurs) if len(valeurs) > 1 else None
        resume.append(ligne)
    return resume


def tracer(lignes, resume, dossier):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    couples = sorted({(l["criteres"], l["categories"], l["hacker"], l["defense"])
                      for l in lignes if l["ratio"] > 0})
    fichiers = []
    for criteres, categories, hacker, defense in couples:
        selection = [r for r in resume if (r["criteres"], r["categories"], r["defense"]) ==
                     (criteres, categories, defense) and (r["hacker"] == hacker or r["ratio"] == 0)]
        tailles = sorted({r["taille"] for r in selection})
        fig, axes = plt.subplots(2, 2, figsize=(13, 9), layout="constrained")
        couleurs = plt.get_cmap("tab10")
        for i, taille in enumerate(tailles):
            groupe = sorted((r for r in selection if r["taille"] == taille), key=lambda r: r["ratio"])
            x = np.array([r["ratio"] for r in groupe])
            for ax, mesure in ((axes[0, 0], "fidelite"), (axes[0, 1], "delta_attaque"),
                               (axes[1, 0], "fidelite_equilibree")):
                y = np.array([r[mesure + "_moyenne"] if r[mesure + "_moyenne"] is not None
                              else np.nan for r in groupe]) * 100
                std = np.array([r[mesure + "_ecart_type"] if r[mesure + "_ecart_type"] is not None
                                else np.nan for r in groupe]) * 100
                ax.plot(x, y, "o-", color=couleurs(i), label=f"N_A = {taille}")
                bas, haut = y - std, y + std
                if mesure != "delta_attaque":
                    bas, haut = np.maximum(0, bas), np.minimum(100, haut)
                ax.fill_between(x, bas, haut, color=couleurs(i), alpha=.12)
        for ax in (axes[0, 0], axes[0, 1], axes[1, 0]):
            ax.set_xlabel("Ratio d'injection ρ = N_H / N_A")
            ax.set_xticks(sorted({r["ratio"] for r in selection}))
            ax.grid(alpha=.2)
        axes[0, 0].set(ylabel="Fidélité à A (%)", ylim=(0, 100), title="Décisions sur le test uniforme")
        axes[0, 0].legend(ncol=2, fontsize=9)
        axes[0, 1].set(ylabel="Perte par rapport à sans attaque (points)", title="Dégradation appariée par graine")
        axes[0, 1].axhline(0, color="black", lw=.8)
        axes[1, 0].set(ylabel="Fidélité moyenne par catégorie (%)", ylim=(0, 100),
                       title="Moyenne non pondérée des rappels")
        points = [l for l in lignes if l["statut"] == "ok" and
                  (l["criteres"], l["categories"], l["hacker"], l["defense"]) ==
                  (criteres, categories, hacker, defense) and l.get("desaccord") is not None
                  and l.get("delta_attaque") is not None]
        if points:
            scatter = axes[1, 1].scatter([100 * l["desaccord"] for l in points],
                                         [100 * l["delta_attaque"] for l in points],
                                         c=[l["ratio"] for l in points], cmap="viridis", vmin=0, vmax=1,
                                         alpha=.55, s=22, edgecolors="none")
            fig.colorbar(scatter, ax=axes[1, 1], label="ρ = N_H / N_A")
        else:
            axes[1, 1].text(.5, .5, "Pas de modèle H déclaré pour ce diagnostic",
                            ha="center", va="center", transform=axes[1, 1].transAxes)
        axes[1, 1].set(xlabel="Désaccord entre M_A et M_H (%)",
                       ylabel="Dégradation appariée (points)", title="Diagnostic descriptif : tailles et ratios répétés")
        axes[1, 1].axhline(0, color="black", lw=.8)
        axes[1, 1].grid(alpha=.2)
        effectifs = sorted({r["parties"] for r in selection})
        echecs = sum(r["echecs"] for r in selection)
        fig.suptitle(f"Attaque : {hacker}  |  Défense : {defense}\n"
                     f"{criteres} critères, {categories} catégories — n par point : {effectifs}, échecs : {echecs}\n"
                     "Bandes : moyenne ± 1 écart-type entre graines (pas un IC)", fontsize=12)
        nom = f"{criteres}x{categories}__{identifiant(hacker)}__{identifiant(defense)}"
        for extension in ("png", "svg"):
            chemin = dossier / f"{nom}.{extension}"
            fig.savefig(chemin, dpi=160)
            fichiers.append(chemin)
        plt.close(fig)
    return fichiers


def tracer_comparaisons(resume, dossier):
    """Comparaisons entre défenses sur les mêmes attaques et les mêmes graines."""
    import matplotlib.pyplot as plt
    import numpy as np

    fichiers = []
    attaques = sorted({(r["criteres"], r["categories"], r["hacker"]) for r in resume if r["ratio"] > 0})
    for criteres, categories, hacker in attaques:
        selection = [r for r in resume if (r["criteres"], r["categories"]) == (criteres, categories)
                     and (r["hacker"] == hacker or r["ratio"] == 0)]
        tailles = sorted({r["taille"] for r in selection})
        defenses = sorted({r["defense"] for r in selection})
        if len(defenses) < 2:
            continue
        fig, axes = plt.subplots(len(tailles), 2, figsize=(12, 4.3 * len(tailles)), squeeze=False, layout="constrained")
        for i, taille in enumerate(tailles):
            for defense in defenses:
                groupe = sorted((r for r in selection if r["taille"] == taille and r["defense"] == defense),
                                key=lambda r: r["ratio"])
                x = np.array([r["ratio"] for r in groupe])
                for j, mesure in enumerate(("fidelite", "gain_defense")):
                    y = np.array([r[mesure + "_moyenne"] if r[mesure + "_moyenne"] is not None else np.nan for r in groupe]) * 100
                    std = np.array([r[mesure + "_ecart_type"] if r[mesure + "_ecart_type"] is not None else np.nan for r in groupe]) * 100
                    ligne, = axes[i, j].plot(x, y, "o-", label=defense)
                    bas, haut = y - std, y + std
                    if j == 0:
                        bas, haut = np.maximum(0, bas), np.minimum(100, haut)
                    axes[i, j].fill_between(x, bas, haut, color=ligne.get_color(), alpha=.1)
            for j in (0, 1):
                axes[i, j].set_xlabel("Ratio d'injection ρ = N_H / N_A")
                axes[i, j].set_xticks(sorted({r["ratio"] for r in selection}))
                axes[i, j].grid(alpha=.2)
            axes[i, 0].set(ylabel="Fidélité à A (%)", ylim=(0, 100), title=f"N_A = {taille} — comparaison des défenses")
            axes[i, 1].set(ylabel="Gain face à naif (points)", title="Différences appariées par graine")
            axes[i, 1].axhline(0, color="black", lw=.8)
            axes[i, 0].legend(fontsize=8)
        effectifs = sorted({r["parties"] for r in selection})
        fig.suptitle(f"{hacker} — {criteres} critères, {categories} catégories ; n par point : {effectifs}\n"
                     "Bandes ± un écart-type uniquement si n ≥ 2 ; budgets différents, consulter les temps", fontsize=11)
        nom = f"comparaison_{criteres}x{categories}__{identifiant(hacker)}"
        for extension in ("png", "svg"):
            chemin = Path(dossier) / f"{nom}.{extension}"
            fig.savefig(chemin, dpi=160)
            fichiers.append(chemin)
        plt.close(fig)
    return fichiers


def bilan(lignes, resume, figures, dossier):
    echecs = [l for l in lignes if l["statut"] != "ok"]
    texte = ["# Bilan de la campagne", "",
             f"{len(lignes)} parties ; {len(lignes) - len(echecs)} réussies ; {len(echecs)} en erreur.", "",
             "Les graines sont les répétitions indépendantes. Les tailles et ratios d'une même graine sont appariés.",
             "Les dispersions sont des écarts-types entre graines ; elles ne sont pas des intervalles de confiance.", "",
             "| Taille A | Ratio H/A | Attaque | Défense | n / échecs | Fidélité (%) | Écart-type (points) | Perte appariée (points) | Fidélité équilibrée (%) |",
             "|---:|---:|---|---|---:|---:|---:|---:|---:|"]
    def nombre(v):
        return f"{100 * v:.2f}" if v is not None else "—"
    for r in resume:
        texte.append(f"| {r['taille']} | {r['ratio']:g} | {r['hacker']} | {r['defense']} | "
                     f"{r['parties']} / {r['echecs']} | {nombre(r['fidelite_moyenne'])} | "
                     f"{nombre(r['fidelite_ecart_type'])} | {nombre(r['delta_attaque_moyenne'])} | "
                     f"{nombre(r['fidelite_equilibree_moyenne'])} |")
    texte += ["", "## Figures", ""]
    texte += [f"![{p.stem}]({p.relative_to(dossier).as_posix()})" for p in figures if p.suffix == ".png"]
    texte += ["", "## Limites d'interprétation", "",
              "- Sans défense (`naif`), un seul modèle est appris : aucune mesure de séparation des deux règles.",
              "- À parts égales, le rôle A/H est indiscernable sous les lois symétriques du protocole.",
              "- Le désaccord est un diagnostic du simulateur, caché à A, H et B. Il ne sélectionne pas les modèles.",
              "- Le filtre des catégories rares est estimé sur 2 000 points distincts ; il conditionne la population étudiée.",
              "- Les rappels par catégorie peuvent être imprécis pour les classes rares. La fidélité équilibrée est vide si une classe manque au test.",
              "- L'apprentissage naïf utilise l'arrêt du jalon 2 (seuil de temps interne nominal de 4 s, ou arrêt anticipé). Ce seuil ne plafonne pas strictement la durée totale observée. Les données sont reproductibles ; les modèles appris peuvent varier avec la charge machine.",
              "- Une augmentation de la perte avec le ratio n'est pas imposée. Une perte négative signifie une amélioration sur cette répétition.",
              "- Le nuage désaccord/perte répète les mêmes modèles pour plusieurs tailles et ratios : il ne représente pas autant de répétitions indépendantes."]
    texte += ["", "## Calcul, sélection et diagnostics", "",
              "Le temps attribuable à une défense inclut toute sa préparation. Lorsque deux sélections partagent Inv-2, le temps de préparation est inclus dans chacune ; le calcul réellement exécuté n'est compté qu'une fois dans `temps_calcul_effectif`.", "",
              "Le gain face à naif est calculé sur le même mélange et la même graine. Il ne prouve pas un avantage à budget égal : naif et Inv-2 gardent leurs arrêts propres. `naif_multi` est un contrôle de redémarrages, à budget demandé explicite.", "",
              "Les fidélités oracle et reconstructions à permutation près utilisent les vérités cachées uniquement après la décision de B. Elles ne servent jamais à choisir son groupe. La perte de sélection sépare l'absence d'un bon candidat d'un mauvais choix parmi les candidats.", "",
              "| Critères × catégories | Taille A | Ratio H/A | Attaque | Défense | Temps attribuable moyen (s) | Gain face à naif (points) | Perte de sélection (points) |",
              "|---|---:|---:|---|---|---:|---:|---:|"]
    for r in resume:
        temps = r["temps_moyenne"]
        texte.append(f"| {r['criteres']} × {r['categories']} | {r['taille']} | {r['ratio']:g} | {r['hacker']} | {r['defense']} | "
                     f"{temps:.3f}" + f" | {nombre(r['gain_defense_moyenne'])} | {nombre(r['perte_selection_moyenne'])} |"
                     if temps is not None else f"| {r['criteres']} × {r['categories']} | {r['taille']} | {r['ratio']:g} | {r['hacker']} | {r['defense']} | — | — | — |")
    if echecs:
        texte += ["", "## Erreurs", ""] + [f"- {l['graine']}, {l['taille']}, {l['ratio']}, {l['defense']} : {l['motif']}" for l in echecs]
    (Path(dossier) / "bilan.md").write_text("\n".join(texte) + "\n", encoding="utf-8")


def analyser(dossier, figures=True):
    dossier = Path(dossier)
    lignes = apparier(lire_resultats(dossier / "resultats.csv"))
    resume = resumer(lignes)
    with (dossier / "resume.csv").open("w", newline="", encoding="utf-8") as fichier:
        sortie = csv.DictWriter(fichier, fieldnames=[*CLE, "parties", "echecs",
                                                    *(m + s for m in MESURES for s in ("_n", "_moyenne", "_ecart_type"))])
        sortie.writeheader()
        sortie.writerows(resume)
    # Fichier séparé : le journal brut reste intact, y compris après une réanalyse.
    with (dossier / "resultats_apparies.csv").open("w", newline="", encoding="utf-8") as fichier:
        sortie = csv.DictWriter(fichier, fieldnames=list(lignes[0]) if lignes else [])
        sortie.writeheader()
        sortie.writerows(lignes)
    fichiers = []
    if figures:
        fichiers = tracer(lignes, resume, dossier / "figures")
        fichiers += tracer_comparaisons(resume, dossier / "figures")
    bilan(lignes, resume, fichiers, dossier)
    return resume


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dossier", type=Path)
    analyser(parser.parse_args().dossier)
