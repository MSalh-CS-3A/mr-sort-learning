"""Contrastes prédéfinis et contrôle d'appariement de la confirmation.

Ce module ne participe jamais aux décisions de H ou B. Il relit les artefacts
une fois les lots audités, sans réapprentissage ni sélection d'une stratégie.
"""

import csv
import json
from pathlib import Path

import numpy as np

from .analyse import identifiant, lire_resultats

BOOTSTRAPS = 10000
GRAINE_BOOTSTRAP = 20261103


def intervalle(valeurs, rng):
    """Bootstrap des différences déjà appariées, unité = graine indépendante."""
    valeurs = np.asarray(valeurs, dtype=float)
    if len(valeurs) < 2 or not np.isfinite(valeurs).all():
        raise ValueError("Au moins deux répétitions finies sont requises")
    indices = rng.integers(len(valeurs), size=(BOOTSTRAPS, len(valeurs)))
    moyennes = valeurs[indices].mean(axis=1)
    bas, haut = np.quantile(moyennes, [.025, .975])
    return dict(n=len(valeurs), moyenne_points=float(100 * valeurs.mean()),
                ecart_type_points=float(100 * valeurs.std(ddof=1)),
                ic95_bas_points=float(100 * bas), ic95_haut_points=float(100 * haut))


def contrastes(lignes, configuration):
    """Comparer quatre couples, sans retirer de répétition ni changer de cible."""
    from .campagne import verifier_couverture
    verifier_couverture(lignes, configuration)
    if len(configuration["dimensions"]) != 1:
        raise ValueError("La confirmation utilise une seule dimension")
    if set(configuration["hackers"]) != {"mrsort_aleatoire", "classe_haute"} or set(configuration["defenses"]) != {"naif", "inv2_plus_grand"}:
        raise ValueError("Deux attaques et deux défenses fixées sont requises")
    index = {(l["taille"], l["graine"], l["ratio"], l["hacker"], l["defense"]): l for l in lignes}
    rng = np.random.default_rng(GRAINE_BOOTSTRAP)
    resultat = []
    for taille in sorted(configuration["tailles"]):
        def valeurs(ratio, hacker, defense):
            return np.array([index[taille, s, ratio, hacker, defense]["fidelite"]
                             for s in sorted(configuration["graines"])])

        sans_naif = valeurs(0., "aucun", "naif")
        sans_inv2 = valeurs(0., "aucun", "inv2_plus_grand")
        resultat.append(dict(taille=taille, ratio=0., effet="cout_defense_sans_attaque", principal=False,
                             **intervalle(sans_naif - sans_inv2, rng)))
        for ratio in sorted(r for r in configuration["ratios"] if r > 0):
            naif_base = valeurs(ratio, "mrsort_aleatoire", "naif")
            inv2_base = valeurs(ratio, "mrsort_aleatoire", "inv2_plus_grand")
            naif_haut = valeurs(ratio, "classe_haute", "naif")
            inv2_haut = valeurs(ratio, "classe_haute", "inv2_plus_grand")
            effets = dict(gain_inv2_hacker_basique=inv2_base - naif_base,
                          effet_classe_haute_sur_inv2=inv2_base - inv2_haut,
                          effet_classe_haute_sur_naif=naif_base - naif_haut,
                          interaction_attaque_defense=(inv2_base - inv2_haut) - (naif_base - naif_haut))
            for effet, differences in effets.items():
                principal = taille == 300 and ratio == .5 and effet in (
                    "gain_inv2_hacker_basique", "effet_classe_haute_sur_inv2")
                resultat.append(dict(taille=taille, ratio=ratio, effet=effet, principal=principal,
                                     **intervalle(differences, rng)))
    return resultat


def verifier_appariement(racine, configuration):
    """Contrôler les préfixes réellement sauvegardés, pas seulement le générateur."""
    d, c = configuration["dimensions"][0]
    tailles = sorted(configuration["tailles"])
    controle_jeux = controle_injections = 0
    for graine in configuration["graines"]:
        def dossier(taille):
            return racine / "lots" / f"{d}x{c}_n{taille}_g{graine:04d}" / "instances" / f"{d}x{c}" / f"graine_{graine:03d}"

        grand = dossier(max(tailles))
        with np.load(grand / "donnees.npz") as archive:
            reference = {k: archive[k] for k in archive.files}
        modele_a = (grand / "modele_a.yml").read_bytes()
        for taille in tailles:
            courant = dossier(taille)
            if (courant / "modele_a.yml").read_bytes() != modele_a:
                raise ValueError("Le modèle A a changé entre les tailles")
            with np.load(courant / "donnees.npz") as archive:
                np.testing.assert_array_equal(archive["x_a"], reference["x_a"][:taille])
                np.testing.assert_array_equal(archive["y_a"], reference["y_a"][:taille])
                for k in ("x_test", "y_test", "x_diagnostic", "y_diagnostic_a"):
                    np.testing.assert_array_equal(archive[k], reference[k])
            controle_jeux += 1
        for hacker in configuration["hackers"]:
            plus_grand = grand / f"taille_{max(tailles)}" / f"ratio_{max(configuration['ratios']):g}" / identifiant(hacker)
            with np.load(plus_grand / "injection.npz") as archive:
                grand_x, grand_y = archive["x_h"], archive["y_h"]
            texte_h = (plus_grand / "modele_h.yml").read_bytes() if hacker == "mrsort_aleatoire" else None
            for taille in tailles:
                for ratio in (r for r in configuration["ratios"] if r > 0):
                    cas = dossier(taille) / f"taille_{taille}" / f"ratio_{ratio:g}" / identifiant(hacker)
                    with np.load(cas / "injection.npz") as archive:
                        nombre = len(archive["y_h"])
                        if nombre != round(taille * ratio):
                            raise ValueError("L'attaque n'a pas utilisé le budget prévu")
                        np.testing.assert_array_equal(archive["x_h"], grand_x[:nombre])
                        np.testing.assert_array_equal(archive["y_h"], grand_y[:nombre])
                    if texte_h is not None and (cas / "modele_h.yml").read_bytes() != texte_h:
                        raise ValueError("Le modèle H a changé entre les tailles ou ratios")
                    controle_injections += 1
    rapport = dict(statut="ok", jeux_a_test_diagnostic_verifies=controle_jeux,
                   injections_emboitees_verifiees=controle_injections,
                   controles=["modèle A fixe", "préfixes A", "test et diagnostic fixes",
                              "modèle H basique fixe", "préfixes H et budgets"])
    (racine / "audit_appariement_tailles.json").write_text(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return rapport


def analyser_confirmation(racine, configuration):
    racine = Path(racine)
    # Un défaut d'appariement interdit de présenter les contrastes comme appariés.
    rapport = verifier_appariement(racine, configuration)
    resultats = contrastes(lire_resultats(racine / "resultats.csv"), configuration)
    with (racine / "comparaisons_confirmation.csv").open("w", newline="", encoding="utf-8") as fichier:
        sortie = csv.DictWriter(fichier, fieldnames=list(resultats[0]))
        sortie.writeheader()
        sortie.writerows(resultats)
    texte = ["# Comparaisons des quatre expériences", "",
             f"{len(configuration['graines'])} graines ; tailles A={configuration['tailles']} ; "
             "les différences sont calculées par graine avant toute moyenne.", "",
             "Deux contrastes principaux fixés avant le calcul, pour N_A=300 et H/A=0,5 : "
             "gain d'Inv2 sur le hacker basique ; perte supplémentaire d'Inv2 face à classe haute. "
             "Les autres tailles et ratios sont des analyses complémentaires.", "",
             "Une valeur positive signifie : gain pour Inv2 (`gain_inv2_hacker_basique`), "
             "attaque classe haute plus dommageable (`effet_classe_haute_sur_*`), "
             "surcroît de dommage plus important sur Inv2 que sur le naïf (`interaction_attaque_defense`), "
             "ou coût d'Inv2 sans attaque (`cout_defense_sans_attaque`).", "",
             f"IC à 95 % : bootstrap percentile de {BOOTSTRAPS} rééchantillonnages des graines "
             f"(graine d'analyse {GRAINE_BOOTSTRAP}). Les différences sont rééchantillonnées après appariement. "
             "Intervalles approximatifs et individuels, sans ajustement pour comparaisons multiples. "
             "Ils n'établissent pas à eux seuls une supériorité générale. "
             "Les bandes des graphiques historiques restent ± un écart-type, pas ces IC.", "",
             "Les temps réels figurent dans `resume.csv` et `bilan.md` : cette confirmation "
             "compare les méthodes avec leurs arrêts propres, pas à budget de calcul égal. "
             "Le cas H/A=1 est à discuter séparément pour le hacker MR-Sort symétrique.", "",
             "| Taille A | H/A | Contraste | Principal | n | Moyenne (points) | IC 95 % (points) |",
             "|---:|---:|---|---|---:|---:|---|" ]
    for r in resultats:
        texte.append(f"| {r['taille']} | {r['ratio']:g} | {r['effet']} | {'oui' if r['principal'] else ''} | "
                     f"{r['n']} | {r['moyenne_points']:.2f} | [{r['ic95_bas_points']:.2f} ; {r['ic95_haut_points']:.2f}] |")
    texte += ["", "## Artefacts", "", "- [Bilan et graphiques](bilan.md)",
              "- [Contrastes CSV](comparaisons_confirmation.csv)",
              "- [Contrôle des préfixes entre tailles](audit_appariement_tailles.json)", "",
              "Les résultats de signe contraire à l'hypothèse sont conservés. "
              "L'attaque et la défense n'ont pas été remplacées après examen de ces graines."]
    (racine / "comparaisons_confirmation.md").write_text("\n".join(texte) + "\n", encoding="utf-8")
    return rapport
