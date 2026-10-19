# Guide Explicatif du Répertoire des Datasets (Jalon 2 - SDP)

**Projet Système de Décision (SDP) — Mention IA, CentraleSupélec**  
**Auteurs :** Mohamed SALH, Mohamed CHEBLI, Quentin Robidou  

---

## 1. Contexte métier : Le problème du Supermarché

Le problème posé dans le Jalon 2 modélise l'assortiment des rayons d'un supermarché à partir de l'historique des tickets de caisse :

* **Alternatives ($x$) :** Chaque ligne du fichier CSV correspond à un **produit** vendu dans le supermarché (ex. *Alternative 1*, *Alternative 2*, ...).
* **Critères ($x_1, \dots, x_n$) :** Les colonnes `Criterion 1` à `Criterion n` décrivent les caractéristiques quantitatives et qualitatives du produit (ex. rapport qualité/prix, fraîcheur, éco-responsabilité, notoriété de la marque, attractivité du packaging). Les scores sont normalisés dans l'intervalle $[0, 1]$ : **plus la valeur est élevée, meilleure est la qualité du produit sur ce critère**.
* **Catégorie d'affectation (`category`) :** Classe ordonnée attribuée au produit selon son succès commercial sur les tickets de caisse des 2 mois passés :
  * `1 (worst)` : *Peu ou pas d'achats* (produit délaissé ou peu performant).
  * `2` : *Achats fréquents* (ventes stables et régulières).
  * `3 (best)` : *Achats très fréquents* (best-sellers / produits phares).
  *(Pour les configurations à 4 ou 5 catégories, l'échelle s'étend de `1 (worst)` jusqu'à `4 (best)` ou `5 (best)`).*

---

## 2. Pourquoi deux segments de clients (inv-2-MR-Sort) ?

Dans la réalité, **les clients n'ont pas tous le même comportement d'achat** :
* Un **Segment 1** privilégie fortement le prix et les caractéristiques de base (poids forts sur `Criterion 1` et `Criterion 4`).
* Un **Segment 2** est prêt à payer plus cher pour des critères d'éco-responsabilité ou de marque (poids forts sur `Criterion 6` et `Criterion 3`).

Puisque les données observées résultent du mélange de ces deux populations, un modèle unique (**1-MR-Sort**) est incapable d'expliquer correctement les achats (son exactitude plafonne autour de 73% à 78%). 
L'objectif du **Jalon 2 (inv-2-MR-Sort)** est de :
1. **Partitionner les produits** entre les 2 segments de clientèle.
2. **Apprendre conjointement les 2 modèles MR-Sort** sous-jacents ($M_1$ et $M_2$).

---

## 3. Déchiffrage de la nomenclature des fichiers CSV

Prenons comme exemple le fichier :
```text
Datasets-Step2/Datasets-Step2/type_a/cr06_ca03/n0300_rep50-50_noise00.csv
```

La nomenclature suit la structure :
`n[TAILLE]_rep[RÉPARTITION]_noise[BRUIT].csv`

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    n0300     │  _  │  rep50-50    │  _  │   noise00    │  .csv
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │                    │                    └─► Niveau de Bruit (0% vs 10%)
       │                    └──────────────────────► Répartition des Segments (50/50 vs 75/25)
       └───────────────────────────────────────────► Taille du Dataset (n = 300, 600, 1200)
```

### A. La taille d'échantillon : `n0300`, `n0600`, `n1200`
* **`n0300`** : Le dataset contient **$n = 300$ produits**.
* **`n0600`** : Le dataset contient **$n = 600$ produits**.
* **`n1200`** : Le dataset contient **$n = 1200$ produits**.
* *Objectif pédagogique :* Évaluer la **scalabilité** et la vitesse de convergence de l'heuristique lorsque le volume de données augmente.

### B. La répartition des segments : `rep50-50` vs `rep75-25`
* **`rep50-50` (Équilibré - 50% / 50%) :**
  * 50% des produits ont été classés par le comportement du **Segment 1**, et 50% par le **Segment 2**.
  * Les deux groupes ont un poids démographique égal dans la clientèle.
* **`rep75-25` (Déséquilibré - 75% / 25%) :**
  * 75% des produits sont dictés par un **segment majoritaire** (la grande masse des consommateurs).
  * 25% des produits sont dictés par un **segment minoritaire** (clientèle de niche ou spécialisée).
  * *Objectif pédagogique :* Vérifier si l'algorithme arrive à isoler le segment minoritaire (25%) sans que ses règles de décision ne soient étouffées ou ignorées par le segment majoritaire.

### C. Le niveau de bruit d'étiquetage : `noise00` vs `noise10`
* **`noise00` (Bruit nul - 0%) :**
  * Les catégories observées correspondent **exactement** aux règles théoriques des deux modèles MR-Sort. Il n'y a aucune incohérence ni erreur de saisie.
  * Dans ce cas, une bonne heuristique 2-MR-Sort peut atteindre **98% à 100% d'exactitude**.
* **`noise10` (Bruit de 10%) :**
  * **10% des produits ont vu leur catégorie modifiée aléatoirement** (simulant des erreurs de caisse, des clients distraits, des achats impulsifs atypiques ou des ruptures de stock ponctuelles).
  * Dans ce cas, le plafond théorique atteignable est d'environ **90% d'exactitude** (car 10% des données sont fausses par construction).
  * *Objectif pédagogique :* Tester la **robustesse** du modèle au surapprentissage (*overfitting*).

---

## 4. Organisation des répertoires et dimensions

### A. Dimensions : `cr06_ca03`, `cr08_ca04`, `cr10_ca05`
* **`cr06_ca03`** : 6 critères ($m = 6$), 3 catégories ($p = 3$). Deux profils frontières $b^1, b^2$ à estimer par modèle.
* **`cr08_ca04`** : 8 critères ($m = 8$), 4 catégories ($p = 4$). Trois profils frontières $b^1, b^2, b^3$ à estimer.
* **`cr10_ca05`** : 10 critères ($m = 10$), 5 catégories ($p = 5$). Quatre profils frontières $b^1, b^2, b^3, b^4$ à estimer.

### B. Types de préférences : `type_a` vs `type_b`
* **`type_a`** : Premier jeu de modèles synthétiques sous-jacents (divergence modérée entre les deux segments de clientèle).
* **`type_b`** : Second jeu de modèles synthétiques sous-jacents (structure de préférences différente, divergence plus marquée entre les segments).

### C. Fichier de définition : `problem.yml`
Chaque sous-dossier contient un fichier `problem.yml` qui formalise le problème pour la bibliothèque LINCS :
* Nom et type de chaque critère (`real`, direction de préférence `increasing`).
* Liste ordonnée des catégories cibles (`1 (worst)`, `2`, ..., `k (best)`).

---

## 5. Tableau récapitulatif des 24 configurations de test

| Dossier | Fichier CSV | Produits ($n$) | Répartition | Bruit | Critères ($m$) | Catégories ($p$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `type_a/cr06_ca03` | `n0300_rep50-50_noise00.csv` | 300 | 50% / 50% | 0% | 6 | 3 |
| `type_a/cr06_ca03` | `n0300_rep50-50_noise10.csv` | 300 | 50% / 50% | 10% | 6 | 3 |
| `type_a/cr06_ca03` | `n0300_rep75-25_noise00.csv` | 300 | 75% / 25% | 0% | 6 | 3 |
| `type_a/cr06_ca03` | `n0300_rep75-25_noise10.csv` | 300 | 75% / 25% | 10% | 6 | 3 |
| `type_a/cr06_ca03` | `n0600_rep50-50_noise00.csv` | 600 | 50% / 50% | 0% | 6 | 3 |
| `type_a/cr06_ca03` | `n0600_rep50-50_noise10.csv` | 600 | 50% / 50% | 10% | 6 | 3 |
| `type_a/cr06_ca03` | `n1200_rep50-50_noise00.csv` | 1200 | 50% / 50% | 0% | 6 | 3 |
| `type_a/cr08_ca04` | `n0300_rep50-50_noise00.csv` | 300 | 50% / 50% | 0% | 8 | 4 |
| `...` | `...` | ... | ... | ... | ... | ... |

---

## 6. Synthèse des résultats obtenus par notre heuristique

Sur ces benchmarks :
* **1-MR-Sort (modèle unique)** obtient en moyenne **73.9%** d'exactitude (il est incapable de concilier les deux groupes de clients).
* **2-MR-Sort (notre algorithme)** obtient en moyenne **92.6%** d'exactitude :
  * Sur les jeux sans bruit (`noise00`) : exactitude entre **92.7% et 100%**.
  * Sur les jeux avec bruit (`noise10`) : exactitude entre **85.5% et 91.0%** (ce qui est optimal compte tenu des 10% de bruit injecté).
