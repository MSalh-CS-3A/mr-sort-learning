# Apprentissage de MR-Sort avec GUROBI

Le programme apprend les poids, le seuil de majorité et les frontières d'un modèle MR-Sort. Il minimise le nombre d'objets dont les contraintes de classe sont relâchées. Il accepte deux catégories ou davantage, ordonnées de **1 (la plus basse) à p (la plus haute)**. Tous les critères sont à maximiser.

## Quel algorithme résout le problème ?

Notre choix porte sur le **modèle MILP** et son objectif. GUROBI fournit le moteur de résolution : une recherche **branch-and-cut**, qui combine séparation et évaluation, coupes et heuristiques.

1. Le solveur simplifie le modèle par prétraitement.
2. Il résout une relaxation linéaire : les variables binaires peuvent provisoirement prendre une valeur entre 0 et 1. Son objectif fournit une borne inférieure du nombre de violations possible.
3. Des heuristiques cherchent des solutions admissibles avec des variables binaires. La meilleure fournit une borne supérieure.
4. Le solveur ajoute des coupes valides et, si nécessaire, sépare le problème en branches, par exemple en imposant une variable binaire à 0 ou à 1. Les branches irréalisables ou incapables d'améliorer la meilleure solution sont éliminées.
5. L'optimalité est prouvée lorsque les bornes permettent d'exclure une meilleure solution, sous les tolérances du solveur. Une limite de temps peut arrêter la recherche avant cette preuve.

Le simplexe et la méthode de points intérieurs (barrière) servent à résoudre les relaxations continues ; ils ne remplacent pas la recherche nécessaire pour les variables binaires. Nous laissons GUROBI sélectionner automatiquement ces méthodes, les coupes et les heuristiques. Sources : [journal de résolution MIP](https://docs.gurobi.com/projects/optimizer/en/current/concepts/logging/mip.html) et [algorithmes des relaxations continues](https://docs.gurobi.com/projects/optimizer/en/current/concepts/numericguide/numeric_parameters.html).

## Installation

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Avec `uv`, on peut installer les dépendances avec `uv pip install --python .venv/bin/python -r requirements.txt`.

La version vérifiée est GUROBI 13.0.3. L'installation de `gurobipy` inclut une licence limitée à 2 000 variables et 2 000 contraintes pour les modèles linéaires ; les exemples et `dataset0.txt` ont été exécutés avec cette licence. Une licence académique complète permet de traiter des modèles plus grands. Source : [licence fournie avec gurobipy](https://support.gurobi.com/hc/en-us/articles/29682074018833-What-does-Restricted-license-for-non-production-use-only-mean).

## Exécuter le jeu du cours

```bash
.venv/bin/python mrsort.py dataset0.txt --log --output resultat_dataset0.json --export-lp modele_dataset0.lp
```

Le fichier contient 60 objets, 5 critères et 3 catégories. Les performances sont dans `[0, 100]`, les bornes par défaut du programme. Les blancs et tabulations supplémentaires à la fin des lignes sont acceptés. Le nombre de critères est déduit de l'en-tête et `p` de la classe maximale ; `--categories` permet de fixer `p` si certaines catégories sont absentes des données.

Pour des notes sur 20, ajouter `--upper-bound 20`. Un tableau à deux catégories utilise **1 pour refusé** et **2 pour accepté**. Format attendu :

```text
    M   P   L   H   categ.
Alice   11  12  13  12  2
Bob     13  12  15  10  1
```

Les paramètres de calcul disponibles comprennent `--time-limit`, `--threads` et `--seed`. Par défaut : 60 secondes, un thread, graine 0. Les tolérances `MIPGap` et `MIPGapAbs` valent zéro pour demander une preuve d'optimalité ; elles n'annulent pas la limite de temps. Les réglages des méthodes de résolution restent automatiques.

Le JSON conserve le modèle appris, les classes observées et prédites, le nombre de contraintes de classe relâchées, la précision effectivement obtenue, le statut, la borne de l'objectif et l'écart d'optimalité. `optimal: false` signifie qu'aucune preuve d'optimalité n'est annoncée, même si une solution exploitable a été trouvée.

## Correspondance avec la modélisation

Le code reprend les indicateurs de v, la linéarisation de vi et l'objectif de vii. Pour une catégorie intermédiaire c, l'objet doit franchir la frontière inférieure `b^(c-1)` et ne pas franchir la frontière supérieure `b^c`. Les frontières sont ordonnées sur chaque critère et partagent les mêmes poids et le même seuil. Une seule variable d'erreur est utilisée par objet, même lorsque deux contraintes de classe lui sont associées.

Les comparaisons aux frontières qui ne sont pas adjacentes à la classe observée sont inutiles pour imposer cette classe : les autres conditions suivent de l'ordre des frontières. De plus, deux objets de même performance sur un critère partagent leur indicateur et leur contribution à une frontière donnée. Ces deux réductions préservent exactement le problème d'apprentissage.

Pour `dataset0.txt`, cela donne 742 variables et 1 756 contraintes. La solution vérifiée reproduit les 60 classes, avec un objectif nul et le statut `OPTIMAL`. Le fichier LP exporté permet d'inspecter les équations réellement transmises au solveur.

Les marges `--performance-margin` (sur les performances) et `--score-margin` (sur le score) valent `1e-4` par défaut. Elles remplacent les côtés stricts des comparaisons, comme expliqué dans le rapport. Le compte des violations de marge et le nombre réel de mauvaises prédictions sont enregistrés séparément. Une tolérance numérique de `1e-7`, inférieure aux marges, est utilisée pour prédire avec les paramètres extraits ; la fixer à zéro dans `MRSortModel` applique littéralement les comparaisons mathématiques.

## Tests et évaluation du jalon 1

```bash
.venv/bin/python -m unittest -v test_mrsort
.venv/bin/python benchmark.py --runs 20 --output resultat_benchmark.json
```

Les tests vérifient notamment les égalités aux seuils, les catégories ordonnées, la restitution d'un modèle compatible et le meilleur compte d'erreurs pour des objets identiques aux classes contradictoires. Ils utilisent de vrais appels à GUROBI.

Le benchmark suit le protocole du sujet : modèle aléatoire de référence, objets d'apprentissage classés par ce modèle, apprentissage par GUROBI, puis objets de test indépendants comparés aux classes du modèle de référence. Il conserve les paramètres des deux modèles et calcule la précision moyenne sur les répétitions. Par défaut : 20 répétitions, 3 critères, 2 catégories, 30 objets d'apprentissage et 200 objets de test par répétition. Ces tailles peuvent être changées avec les options du script.

Une restitution parfaite du jeu d'apprentissage ne prouve pas une généralisation parfaite : c'est précisément ce que mesure le test indépendant. Le benchmark ne suppose pas que les poids appris sont identiques aux poids de référence.

## Utiliser le modèle enregistré

```python
import json
from mrsort import MRSortModel

with open("resultat_dataset0.json", encoding="utf-8") as file:
    result = json.load(file)
model = MRSortModel(**result["model"])
category = model.predict([50, 60, 70, 40, 80])
```
