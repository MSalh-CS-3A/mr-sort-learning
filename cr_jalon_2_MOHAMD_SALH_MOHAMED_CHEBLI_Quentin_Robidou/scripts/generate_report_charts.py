"""Génère les graphiques pour le rapport PDF du Jalon 2."""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10

out_dir = Path("cr_jalon_2_MOHAMD_SALH_MOHAMED_CHEBLI_Quentin_Robidou/figures")
out_dir.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# Graphique 1 : Comparaison des exactitudes 1-MR-Sort vs 2-MR-Sort
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 3.8), dpi=300)

configs = [
    "cr06 / n300 (50-50, bruit 0%)",
    "cr06 / n300 (50-50, bruit 10%)",
    "cr06 / n300 (75-25, bruit 0%)",
    "cr06 / n300 (75-25, bruit 10%)",
    "cr06 / n600 (50-50, bruit 0%)",
    "cr08 / n300 (75-25, bruit 0%)",
]
acc_1 = [78.67, 68.67, 86.33, 75.67, 75.50, 85.00]
acc_2 = [98.67, 91.67, 100.00, 92.67, 97.67, 98.33]

y = np.arange(len(configs))
height = 0.35

rects1 = ax.barh(y - height/2, acc_1, height, label="1-MR-Sort (Baseline LINCS)", color="#D9534F", edgecolor="black", linewidth=0.8)
rects2 = ax.barh(y + height/2, acc_2, height, label="2-MR-Sort (Heuristique proposée)", color="#2E7D32", edgecolor="black", linewidth=0.8)

ax.set_xlabel("Exactitude de classification (%)", fontweight="bold", fontsize=10)
ax.set_title("Comparaison des exactitudes : Modèle unitaire vs Mélange 2-MR-Sort", fontweight="bold", fontsize=11, pad=12)
ax.set_yticks(y)
ax.set_yticklabels(configs, fontsize=9)
ax.set_xlim(50, 105)
ax.legend(loc="lower right", frameon=True, fontsize=9)

# Annotations des gains
for i in range(len(configs)):
    gain = acc_2[i] - acc_1[i]
    ax.text(acc_2[i] + 1.0, y[i] + height/2 - 0.08, f"+{gain:.1f}%", va="center", fontweight="bold", color="#1B5E20", fontsize=8.5)

plt.tight_layout()
fig_path1 = out_dir / "figure1_comparaison_exactitudes.png"
fig.savefig(fig_path1, bbox_inches="tight")
plt.close(fig)
print(f"Graphique 1 enregistré : {fig_path1}")

# -------------------------------------------------------------
# Graphique 2 : Poids des critères des deux segments (Profils de préférences)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6.5, 3.6), dpi=300)

criteria = [f"Critère {i}" for i in range(1, 7)]
w1 = [0.1667, 0.1667, 0.1667, 0.1667, 0.0000, 0.3333]
w2 = [0.2000, 0.0000, 0.2000, 0.4000, 0.0000, 0.2000]

x = np.arange(len(criteria))
width = 0.35

ax.bar(x - width/2, w1, width, label="Segment 1 (λ = 0.67)", color="#1F77B4", edgecolor="black", linewidth=0.8)
ax.bar(x + width/2, w2, width, label="Segment 2 (λ = 0.60)", color="#FF7F0E", edgecolor="black", linewidth=0.8)

ax.set_ylabel("Poids normalisé (wi)", fontweight="bold", fontsize=10)
ax.set_title("Poids des critères appris pour les deux segments de clientèle", fontweight="bold", fontsize=11, pad=12)
ax.set_xticks(x)
ax.set_xticklabels(criteria, fontsize=9.5)
ax.set_ylim(0, 0.48)
ax.legend(loc="upper right", frameon=True, fontsize=9)

for i in range(len(criteria)):
    if w1[i] > 0.01:
        ax.text(x[i] - width/2, w1[i] + 0.015, f"{w1[i]:.2f}", ha="center", fontsize=8, color="#0D47A1", fontweight="bold")
    if w2[i] > 0.01:
        ax.text(x[i] + width/2, w2[i] + 0.015, f"{w2[i]:.2f}", ha="center", fontsize=8, color="#E65100", fontweight="bold")

plt.tight_layout()
fig_path2 = out_dir / "figure2_poids_segments.png"
fig.savefig(fig_path2, bbox_inches="tight")
plt.close(fig)
print(f"Graphique 2 enregistré : {fig_path2}")
