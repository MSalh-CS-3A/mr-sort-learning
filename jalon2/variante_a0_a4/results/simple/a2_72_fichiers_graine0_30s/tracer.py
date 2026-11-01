"""Tracer les évolutions A2 à partir des résultats, sans relancer l'apprentissage."""

import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/projet-matplotlib')
for nom in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[nom] = '1'

import csv
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


RACINE = Path(__file__).resolve().parent
SORTIE = RACINE / 'figures'
INITIALISATIONS = ('uniforme', 'gmm')
TITRES = {'type_a': 'Type A', 'type_b': 'Type B', 'commune': 'Types A + B'}


def lire():
    executions = []
    for lot in ('type_a', 'type_b'):
        with (RACINE / lot / 'resultats.csv').open() as fichier:
            lignes = list(csv.DictReader(fichier))
        assert len(lignes) == 72 and all(l['statut'] == 'ok' for l in lignes)
        for ligne in lignes:
            with (RACINE / lot / ligne['details'] / 'trace.csv').open() as fichier:
                trace = list(csv.DictReader(fichier))
            temps = np.array([float(t['temps']) for t in trace])
            lg = np.array([int(t['meilleur_LG']) for t in trace])
            assert len(temps) and np.all(np.diff(temps) >= 0)
            assert np.all(np.diff(lg) <= 0) and lg[-1] == int(ligne['LG'])
            executions.append(dict(lot=lot, initialisation=ligne['initialisation'],
                                   fichier=ligne['fichier'], temps=temps,
                                   erreurs=100 * lg / int(ligne['N']),
                                   erreur_finale=100 * float(ligne['taux_erreur']),
                                   temps_total=float(ligne['temps_total'])))
    return executions


def construire(executions):
    groupes, resume, points = {}, [], []
    for lot in TITRES:
        selection = [e for e in executions if lot == 'commune' or e['lot'] == lot]
        ensembles = [{e['fichier'] for e in selection if e['initialisation'] == init}
                     for init in INITIALISATIONS]
        assert ensembles[0] == ensembles[1]
        nombre = len(ensembles[0])
        # Même ensemble de fichiers à chaque instant : ne pas moyenner une
        # population qui change au gré de l'arrivée des premiers modèles.
        debut = max(e['temps'][0] for e in selection)
        grille = np.unique(np.concatenate([
            np.linspace(0, 30, 301), [debut],
            *[e['temps'][e['temps'] <= 30] for e in selection],
        ]))
        courbes = {}
        for init in INITIALISATIONS:
            lignes = [e for e in selection if e['initialisation'] == init]
            valeurs = []
            for e in lignes:
                positions = np.searchsorted(e['temps'], grille, side='right') - 1
                valeurs.append(np.where(positions >= 0,
                                        e['erreurs'][np.maximum(positions, 0)], np.nan))
            moyenne = np.mean(valeurs, axis=0)
            moyenne[grille < debut] = np.nan
            courbes[init] = moyenne
            mesures = {f'erreur_{t}s_pct': float(moyenne[np.searchsorted(grille, t)])
                       for t in (10, 20, 30)}
            resume.append(dict(ensemble=lot, initialisation=init, fichiers=nombre,
                               debut_comparaison_s=float(debut), **mesures,
                               erreur_finale_pct=float(np.mean([e['erreur_finale'] for e in lignes])),
                               temps_moyen_s=float(np.mean([e['temps_total'] for e in lignes]))))
        groupes[lot] = dict(grille=grille, debut=debut, courbes=courbes, nombre=nombre)
        for i, temps in enumerate(grille):
            points.append(dict(ensemble=lot, temps_s=float(temps), fichiers=nombre,
                               **{f'A2_{init}_erreur_pct': float(courbes[init][i])
                                  if np.isfinite(courbes[init][i]) else ''
                                  for init in INITIALISATIONS}))
    return groupes, resume, points


def dessiner(ax, lot, groupe, plafond):
    ax.axvspan(0, groupe['debut'], color='#dddddd', alpha=.45, linewidth=0)
    ax.text(groupe['debut']/2, plafond*.5, 'Premiers modèles\nen cours',
            ha='center', va='center', fontsize=9, color='#666666')
    for init, couleur in zip(INITIALISATIONS, ('#377eb8', '#e98921')):
        valeurs = groupe['courbes'][init]
        ax.step(groupe['grille'], valeurs, where='post', linewidth=2, color=couleur,
                label=f"A2-{init} : {valeurs[-1]:.2f} % à 30 s")
    ax.set(title=f"{TITRES[lot]} — {groupe['nombre']} fichiers", xlim=(0, 30),
           ylim=(0, plafond), xlabel='Temps écoulé par exécution (s)',
           ylabel="Meilleur taux d'erreur moyen (%)")
    ax.set_xticks(np.arange(0, 31, 5))
    ax.grid(alpha=.2)
    ax.set_axisbelow(True)
    ax.legend(loc='upper right', fontsize=9, frameon=False)


def main():
    SORTIE.mkdir(exist_ok=True)
    groupes, resume, points = construire(lire())
    plafond = 5*np.ceil(max(np.nanmax(c) for g in groupes.values()
                           for c in g['courbes'].values()) / 5)
    for lot, groupe in groupes.items():
        fig, ax = plt.subplots(figsize=(8.5, 5), layout='constrained')
        dessiner(ax, lot, groupe, plafond)
        fig.suptitle('A2 · évolution de la reconstruction · graine 0', fontsize=12)
        for extension in ('png', 'svg'):
            fig.savefig(SORTIE / f'evolution_{lot}.{extension}', dpi=160)
        plt.close(fig)
    fig, axes = plt.subplots(1, 3, figsize=(17, 5), layout='constrained')
    for ax, (lot, groupe) in zip(axes, groupes.items()):
        dessiner(ax, lot, groupe, plafond)
    fig.suptitle('A2 — meilleure erreur de reconstruction au cours du temps · graine 0', fontsize=14)
    for extension in ('png', 'svg'):
        fig.savefig(SORTIE / f'evolutions_a_b_ensemble.{extension}', dpi=160)
    plt.close(fig)
    for nom, lignes in (('resume_evolution.csv', resume), ('courbes.csv', points)):
        with (SORTIE / nom).open('w', newline='', encoding='utf-8') as fichier:
            sortie = csv.DictWriter(fichier, fieldnames=list(lignes[0]))
            sortie.writeheader()
            sortie.writerows(lignes)
    for ligne in resume:
        print(ligne)
    print('Figures enregistrées :', SORTIE)


if __name__ == '__main__':
    main()
