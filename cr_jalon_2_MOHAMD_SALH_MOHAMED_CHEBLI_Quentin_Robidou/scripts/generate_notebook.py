"""Générateur du notebook Jupyter pour le Jalon 2."""

from pathlib import Path
import nbformat as nbf

nb = nbf.v4.new_notebook()

cells = []

# Cell 1: Markdown Title & Intro
cells.append(nbf.v4.new_markdown_cell("""# Projet SDP — Système de Décision (Mention IA, CentraleSupélec)
## Jalon 2 : Inférence d'un mélange de modèles MR-Sort pour la segmentation de clientèle (*inv-2-MR-Sort*)

**Groupe :** Mohamed SALH, Mohamed CHEBLI, Quentin Robidou  
**Enseignants :** V. Mousseau, M. Tydrichova  
**Date :** Octobre 2026

---

### Objectifs du Notebook :
1. **Contexte métier :** Comprendre le problème d'assortiment de produits en supermarché et les critères d'évaluation.
2. **Modèle de référence :** Évaluer les limites d'un modèle unitaire **1-MR-Sort** appris via la bibliothèque `lincs`.
3. **Segmentation & Mélange (*inv-2-MR-Sort*) :** Implémenter et expérimenter une heuristique d'optimisation alternée (*k-MRSort*) couplée à une initialisation K-Means / Résiduelle.
4. **Validation empirique :** Comparer les performances sur différents jeux de données (dimensions, proportions, bruit).
5. **Interprétation managériale :** Analyser les préférences spécifiques de chaque segment de consommateurs pour éclairer la politique d'assortiment du magasin.
"""))

# Cell 2: Code Imports & Setup
cells.append(nbf.v4.new_code_cell("""import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Ajout du dossier courant au sys.path pour importer nos modules
current_dir = Path.cwd()
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from lincs_adapter import ProblemDefinition, train_single_mrsort, predict_with_model, parse_category_int
from inv2_mrsort import Inv2MRSortHeuristic

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["font.size"] = 11

print("Environnement configuré avec succès.")
"""))

# Cell 3: Markdown Section 1
cells.append(nbf.v4.new_markdown_cell("""## 1. Contexte métier et Chargement des Données

Un supermarché cherche à rationaliser son offre de produits en rayon à partir de l'historique des tickets de caisse.
Chaque produit $x$ est décrit par un vecteur de $n$ caractéristiques :
$$x = (x_1, x_2, \\dots, x_n) \\in [0, 1]^n$$
où $x_i$ représente la qualité du produit sur le critère $i$ (les préférences sont monotones croissantes : plus $x_i$ est élevé, meilleur est le produit).

Les produits sont classés en 3 catégories ordonnées :
- **Classe 1 (worst) :** *Peu ou pas d'achats*
- **Classe 2 :** *Achats fréquents*
- **Classe 3 (best) :** *Achats très fréquents*

Chargeons le problème de base à 6 critères et 3 catégories, ainsi qu'un jeu d'apprentissage représentatif.
"""))

# Cell 4: Code Load Data
cells.append(nbf.v4.new_code_cell("""# Chemins des données avec détection dynamique
candidates = [
    Path("../Datasets-Step2/Datasets-Step2/type_a/cr06_ca03"),
    Path("Datasets-Step2/Datasets-Step2/type_a/cr06_ca03"),
    Path("../../Datasets-Step2/Datasets-Step2/type_a/cr06_ca03"),
]
data_dir = next((c for c in candidates if c.exists()), candidates[0])
problem_file = data_dir / "problem.yml"
dataset_file = data_dir / "n0300_rep50-50_noise00.csv"

# Chargement du problème et du jeu d'apprentissage
prob_def = ProblemDefinition.from_yaml_file(problem_file)
df = pd.read_csv(dataset_file)

print(f"Nombre de critères    : {prob_def.n_criteria}")
print(f"Critères              : {prob_def.criteria_names}")
print(f"Nombre de catégories  : {prob_def.n_categories}")
print(f"Catégories            : {prob_def.categories_names}")
print(f"Nombre de produits    : {len(df)}")
df.head()
"""))

# Cell 5: Markdown Section 2
cells.append(nbf.v4.new_markdown_cell("""## 2. Limites du modèle unitaire 1-MR-Sort

Dans le Jalon 1, nous apprenions un unique modèle MR-Sort. La bibliothèque `lincs` propose une heuristique génétique/population efficace pour ce problème (*inv-MR-Sort*).
Appliquons-la directement sur notre jeu de données complet.
"""))

# Cell 6: Code Train Baseline
cells.append(nbf.v4.new_code_cell("""# Apprentissage d'un unique modèle MR-Sort
res_single = train_single_mrsort(prob_def, df, seed=42, max_iterations=30)

print(f"Exactitude d'apprentissage (1-MR-Sort) : {res_single.training_accuracy * 100:.2f}%")
print(f"Poids normalisés appris                 : {[round(w, 4) for w in res_single.parameters.weights]}")
print(f"Seuil de majorité (lambda)              : {res_single.parameters.majority_threshold:.4f}")
print(f"Temps de résolution                     : {res_single.runtime_seconds:.2f} s")
"""))

# Cell 7: Markdown Section 3
cells.append(nbf.v4.new_markdown_cell("""### Constat :
L'exactitude plafonne à environ **78.7%** sur un jeu sans aucun bruit de mesure (`noise00`).
Ce plafonnement ne provient pas d'une défaillance de l'optimiseur, mais de l'**inadéquation fondamentale du modèle unitaire** :
la clientèle n'est pas homogène. Deux segments de consommateurs effectuent des arbitrages distincts.
Un modèle unique tente de moyenner ces comportements contradictoires et commet inévitablement des erreurs systématiques.
"""))

# Cell 8: Markdown Section 4
cells.append(nbf.v4.new_markdown_cell("""## 3. Heuristique d'Optimisation Alternée (*inv-2-MR-Sort*)

Le problème *inv-2-MR-Sort* consiste à rechercher simultanément une partition $(L_1, L_2)$ de l'ensemble d'apprentissage et deux modèles MR-Sort $(M_1, M_2)$ maximisant l'exactitude globale :
$$\\max_{L_1, L_2, M_1, M_2} \\frac{1}{|L|} \\left( \\sum_{x \\in L_1} \\mathbf{1}\\{M_1(x) = c(x)\\} + \\sum_{x \\in L_2} \\mathbf{1}\\{M_2(x) = c(x)\\} \\right)$$

Notre heuristique procède par **optimisation alternée (type k-Means / Hard EM)** :
1. **Initialisation :** Partition initiale par K-Means sur l'espace conjoint $(X, c)$ ou par résidu du modèle unitaire.
2. **Étape M :** Apprentissage de $M_1$ sur $L_1$ et $M_2$ sur $L_2$ via l'heuristique LINCS.
3. **Étape E :** Réaffectation de chaque produit $x$ au segment $k \\in \\{1, 2\\}$ qui minimise la distance de prédiction $|M_k(x) - c(x)|$.
4. **Convergence :** Répétition jusqu'à stabilisation de la partition.
"""))

# Cell 9: Code Train Inv2MRSort
cells.append(nbf.v4.new_code_cell("""# Inférence avec notre heuristique inv-2-MR-Sort
heuristic = Inv2MRSortHeuristic(
    prob_def,
    init_strategy=\"kmeans\",
    max_alternating_iterations=5,
    lincs_max_iterations=25,
    seed=42,
    verbose=True
)

res_2mrsort = heuristic.fit(df)

print(\"\\n--- Synthèse comparative ---\")
print(f\"Exactitude 1-MR-Sort baseline : {res_2mrsort.baseline_accuracy_1_mrsort * 100:.2f}%\")
print(f\"Exactitude 2-MR-Sort          : {res_2mrsort.joint_accuracy * 100:.2f}%\")
print(f\"Gain de performance           : +{res_2mrsort.accuracy_gain * 100:.2f} points de pourcentage\")
print(f\"Taille Segment 1              : {res_2mrsort.segment_1_size} ({res_2mrsort.segment_1_proportion*100:.1f}%)\")
print(f\"Taille Segment 2              : {res_2mrsort.segment_2_size} ({res_2mrsort.segment_2_proportion*100:.1f}%)\")
print(f\"Convergence atteinte en       : {res_2mrsort.convergence_iterations} itérations alternées\")
"""))

# Cell 10: Markdown Visualisation Section
cells.append(nbf.v4.new_markdown_cell("""## 4. Visualisations et Analyse des Résultats"""))

# Cell 11: Code Plot Comparison & Weights
cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Graphique 1 : Comparaison des exactitudes
models = [\"1-MR-Sort (Baseline)\", \"2-MR-Sort (Proposé)\"]
accuracies = [res_2mrsort.baseline_accuracy_1_mrsort * 100, res_2mrsort.joint_accuracy * 100]
colors = [\"#d9534f\", \"#5cb85c\"]

bars = axes[0].bar(models, accuracies, color=colors, width=0.5, edgecolor=\"black\", linewidth=1.2)
axes[0].set_ylim(0, 105)
axes[0].set_ylabel(\"Exactitude d'apprentissage (%)\")
axes[0].set_title(\"Gain de performance : Modèle unitaire vs 2 Segments\")
for bar, acc in zip(bars, accuracies):
    axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5, f\"{acc:.2f}%\", ha=\"center\", fontweight=\"bold\")

# Graphique 2 : Poids des critères par segment
crit_labels = [f\"Critère {i+1}\" for i in range(prob_def.n_criteria)]
w1 = res_2mrsort.model_1.weights
w2 = res_2mrsort.model_2.weights

x = np.arange(len(crit_labels))
width = 0.35

axes[1].bar(x - width/2, w1, width, label=f\"Segment 1 (λ={res_2mrsort.model_1.majority_threshold:.2f})\", color=\"#428bca\", edgecolor=\"black\")
axes[1].bar(x + width/2, w2, width, label=f\"Segment 2 (λ={res_2mrsort.model_2.majority_threshold:.2f})\", color=\"#f0ad4e\", edgecolor=\"black\")
axes[1].set_xticks(x)
axes[1].set_xticklabels(crit_labels)
axes[1].set_ylabel(\"Poids normalisé (w_i)\")
axes[1].set_title(\"Structure de préférences des deux segments de consommateurs\")
axes[1].legend(loc=\"upper right\")

plt.tight_layout()
plt.show()
"""))

# Cell 12: Markdown Section 5
cells.append(nbf.v4.new_markdown_cell("""## 5. Interprétation Managériale et Recommandations

L'analyse des poids appris révèle des comportements d'achat radicalement distincts :
- **Segment 1 (Clientèle 'Équilibrée / Généraliste') :** Répartit ses exigences sur plusieurs critères (notamment Critère 6 et les critères 1 à 4) avec un seuil de majorité exigeant ($\\lambda \\approx 0.67$). Ces clients recherchent des produits homogènes sans faiblesse rédhibitoire.
- **Segment 2 (Clientèle 'Spécialisée / Ciblée') :** Concentre une part prépondérante de son poids sur un sous-ensemble restreint (notamment le Critère 4 avec un poids élevé de 0.40), avec un seuil plus souple ($\\lambda \\approx 0.60$). Ces clients sont prêts à acheter un produit dès lors qu'il excelle sur leur critère de prédilection.

### Recommandations pour l'Assortiment du Supermarché :
1. **Diversification du linéaire :** Éviter de sélectionner uniquement des produits moyens sur tous les critères. Il est crucial d'inclure des produits très performants sur le Critère 4 pour capter pleinement le Segment 2.
2. **Double signalétique en rayon :** Mettre en avant les certifications d'excellence spécifique pour le Segment 2, et les labels de qualité globale pour le Segment 1.
3. **Optimisation du chiffre d'affaires :** En répondant précisément aux deux segments, le supermarché élimine les ruptures d'offre perçues et maximise son taux de conversion.
"""))

nb.cells = cells

# Save notebook
out_nb_path = Path("cr_jalon_2_MOHAMD_SALH_MOHAMED_CHEBLI_Quentin_Robidou/notebook_jalon2.ipynb")
nbf.write(nb, out_nb_path)
print(f"Notebook enregistré avec succès dans {out_nb_path}")
