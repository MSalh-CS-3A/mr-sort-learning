import csv
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt

METHODS = {"random": ("Départ aléatoire", "#2a78d6"),
           "single_model": ("Départ modèle unique", "#eb6834")}
TEXT, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
GRID_TIMES = np.arange(0, 90.5, 0.5)


def error_curves(history_path):
    """Pour chaque (dataset, méthode), taux d'erreur (1 - meilleure précision) sur la grille de temps,
    NaN tant que la première itération n'est pas terminée."""
    steps = defaultdict(list)
    with open(history_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            steps[(row["file"], row["method"])].append((float(row["time_s"]), float(row["best_accuracy"])))
    curves = {}
    for key, points in steps.items():
        times, best = np.array(points).T
        idx = np.searchsorted(times, GRID_TIMES, side="right") - 1   # dernière itération terminée à chaque instant
        curves[key] = np.where(idx >= 0, 100 * (1 - best[np.clip(idx, 0, None)]), np.nan)
    return curves


def draw(ax, curves, files, title):
    """Taux d'erreur moyen et intervalle interquartile par méthode, à partir du moment où tous les datasets
    du groupe ont une valeur (sinon la moyenne changerait de population au cours du temps)."""
    for method, (label, color) in METHODS.items():
        values = np.array([curves[(f, method)] for f in files])
        complete = ~np.isnan(values).any(axis=0)
        t, v = GRID_TIMES[complete], values[:, complete]
        mean = v.mean(axis=0)
        ax.fill_between(t, np.percentile(v, 25, axis=0), np.percentile(v, 75, axis=0), color=color, alpha=0.12,
                        linewidth=0)
        ax.plot(t, mean, color=color, linewidth=2, label=label)
        ax.annotate(f"{mean[-1]:.1f} %", (t[-1], mean[-1]), xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=9, color=TEXT)
    ax.set_title(title, loc="left", fontsize=11, color=TEXT)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Temps (s)", color=MUTED)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.tick_params(colors=MUTED, length=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)


if __name__ == "__main__":
    curves = error_curves("history_step2.csv")
    files = sorted({f for f, _ in curves})
    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb"})

    # Graphe 1 : tous les datasets
    fig, ax = plt.subplots(figsize=(8, 4.8))
    draw(ax, curves, files, f"Taux d'erreur moyen sur les {len(files)} datasets (meilleure partition atteinte)")
    ax.set_ylabel("Objets mal classés (%)", color=MUTED)
    ax.legend(frameon=False, loc="upper right")
    fig.text(0.01, 0.01, "Zone colorée : intervalle interquartile entre datasets. Courbes tracées à partir du moment "
             "où tous les datasets ont fini leur première itération.", fontsize=7.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig("convergence_erreur_moyenne.png", dpi=200)

    # Graphe 2 : un panneau par taille de learning set
    sizes = {"300": "300 objets", "600": "600 objets", "1200": "1 200 objets"}
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.4), sharey=True)
    for ax, (m, title) in zip(axes, sizes.items()):
        group = [f for f in files if f"/n{int(m):04d}_" in f]
        draw(ax, curves, group, f"{title} ({len(group)} datasets)")
    axes[0].set_ylabel("Objets mal classés (%)", color=MUTED)
    axes[0].legend(frameon=False, loc="upper right")
    fig.suptitle("Taux d'erreur moyen selon la taille du learning set", x=0.01, ha="left", fontsize=12, color=TEXT)
    fig.tight_layout()
    fig.savefig("convergence_par_taille.png", dpi=200)

    # Graphes 3 et 4 : moyenne sur les datasets de type A, puis de type B (même échelle pour les comparer)
    for dataset_type in ("type_a", "type_b"):
        group = [f for f in files if f.startswith(dataset_type + "/")]
        fig, ax = plt.subplots(figsize=(8, 4.8))
        draw(ax, curves, group, f"Taux d'erreur moyen sur les {len(group)} datasets de type "
                                f"{dataset_type[-1].upper()}")
        ax.set_ylim(0, 35)
        ax.set_ylabel("Objets mal classés (%)", color=MUTED)
        ax.legend(frameon=False, loc="upper right")
        fig.text(0.01, 0.01, "Zone colorée : intervalle interquartile entre datasets. Courbes tracées à partir du "
                 "moment où tous les datasets ont fini leur première itération.", fontsize=7.5, color=MUTED)
        fig.tight_layout(rect=(0, 0.03, 1, 1))
        fig.savefig(f"convergence_{dataset_type}.png", dpi=200)
    print("Graphes écrits : convergence_erreur_moyenne.png, convergence_par_taille.png, "
          "convergence_type_a.png, convergence_type_b.png")
