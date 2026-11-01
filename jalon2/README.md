# Jalon 2 - Inv-2-MR-Sort (version officielle)

Version de Quentin Robidou, retenue comme version officielle du jalon 2. Une autre version, fondée sur les heuristiques A0 à A4, est conservée dans [variante_a0_a4/](variante_a0_a4/README.md) ; les deux partagent les données de [data/](data/).

## Méthode

On cherche une partition des objets en deux segments et un modèle MR-Sort par segment. L'heuristique alterne deux étapes, au plus huit fois :

1. **Apprendre un MR-Sort par segment** avec l'heuristique de lincs (WPB) : neuf modèles en parallèle, arrêt quand tous les objets sont bien classés, après dix itérations sans progrès ou après quatre secondes.
2. **Réaffecter les objets** au modèle qui les explique le mieux : d'abord l'écart entre catégorie prédite et catégorie observée, puis la marge de concordance. Au plus 10 % des objets changent de segment par itération, et chaque segment garde au moins 15 % des objets.

La meilleure partition rencontrée est conservée : celle qui maximise la proportion d'objets bien classés par le modèle de leur segment, puis la marge totale.

Deux partitions de départ sont comparées :

- **aléatoire** : chaque objet est placé dans un segment à pile ou face ;
- **mal classés** : un seul MR-Sort est appris sur tout le jeu, et les objets qu'il classe mal forment le second segment.

## Fichiers

| Fichier | Contenu |
| --- | --- |
| [jalon2_deux_mrsort.py](jalon2_deux_mrsort.py) | Lecture des données, modèle MR-Sort, heuristique, lancement sur un fichier ou un dossier. |
| [validation_jalon2.py](validation_jalon2.py) | Validation sur des données synthétiques dont les deux modèles et la partition sont connus. |
| [results/](results/) | `results_step2.csv` (les 72 CSV) et `journal_validation_jalon2.txt` (validation synthétique). |
| [requirements.txt](requirements.txt) | Dépendances minimales pour lancer le script hors du dépôt. |

## Lancer

Depuis la racine du dépôt, après `uv sync --locked` :

```bash
# Un fichier, avec le détail des itérations et des modèles appris.
.venv/bin/python jalon2/jalon2_deux_mrsort.py jalon2/data/type_a/cr06_ca03/n0300_rep50-50_noise00.csv

# Les 72 fichiers : complète jalon2/results/results_step2.csv sans refaire les fichiers déjà traités.
.venv/bin/python jalon2/jalon2_deux_mrsort.py

# Validation sur données synthétiques : quatre configurations, trois essais chacune.
.venv/bin/python jalon2/validation_jalon2.py
```

Les graines sont fixées dans les scripts. Comme `results_step2.csv` contient déjà les 72 fichiers, la deuxième commande ne recalcule rien : pour tout relancer, renommer ce fichier d'abord. Compter environ 80 secondes par fichier pour les deux départs, soit près de deux heures pour les 72 ; cela dépend de la machine.

Lors de l'intégration au dépôt, seuls les chemins par défaut ont changé : les données sont lues dans `jalon2/data/` et les résultats écrits dans `jalon2/results/`, quel que soit le dossier courant. L'algorithme et les réglages sont inchangés : la première commande reproduit la première ligne de `results_step2.csv` (79,0 % avec un seul modèle, 94,3 % et 94,0 % avec deux).

## Résultats

Proportion d'objets bien classés par le modèle de leur segment, sur les 72 CSV :

| Données | Un seul MR-Sort | Deux, départ aléatoire | Deux, départ mal classés |
| --- | ---: | ---: | ---: |
| Type A (36 fichiers) | 72,8 % | 89,2 % | 92,5 % |
| Type B (36 fichiers) | 64,4 % | 84,3 % | 89,4 % |
| Ensemble | 68,6 % | 86,8 % | 91,0 % |

Le départ « mal classés » fait au moins aussi bien que le départ aléatoire sur 60 fichiers sur 72. Chaque départ prend en moyenne une quarantaine de secondes par fichier.

La validation synthétique montre que deux modèles expliquent 88 à 99 % des objets, mais que la partition ne retrouve que 58 à 70 % des vrais segments. Entre 39 et 53 % des objets sont classés de la même façon par les deux vrais modèles : ils peuvent aller dans l'un ou l'autre segment sans erreur. Sur les autres objets, la partition est retrouvée à 62 à 86 %.

## Utilisation par le jalon 3

Les défenses de référence du [jalon 3](../jalon3/README.md) appellent `inv_two_mrsort_misclassified` et `learn` de ce fichier.
