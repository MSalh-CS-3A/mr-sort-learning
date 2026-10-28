# Jalon 3 - Apprendre MR-Sort malgré un brouillage

> Jalon optionnel. Dépôt sur Edunao au plus tard le 05/11/2026 à 23 h 59 ; soutenance le 06/11/2026.
> Énoncé : page 5 de [docs/sujet.pdf](../docs/sujet.pdf).
> **Décision :** B reçoit tout hors ligne, en une seule fois.

## Le problème

- **A** observe des objets classés par un modèle MR-Sort inconnu, noté $M_A$. A n'a presque pas de puissance de calcul : il transmet ses données à B sans les traiter.
- **H**, un agent malveillant, ajoute de fausses données : un vecteur de performances et une catégorie. Il peut en ajouter **au plus une par donnée de A**, donc jusqu'à la moitié de ce que B reçoit.
- **B** reçoit le mélange sans savoir qui a envoyé chaque ligne. Il a de la puissance de calcul et cherche à retrouver $M_A$.

L'énoncé demande deux choses :

1. **Partie 1.** H est « basique » : il tire un MR-Sort au hasard, $M_H$, et s'en sert pour classer ses objets. Utiliser le jalon 2 pour aider B, sur des données que nous construisons.
2. **Partie 2.** Se mettre à la place de H : trouver une stratégie de brouillage efficace et montrer, sur une instance, à quel point elle gêne B.

Quand H classe ses objets avec un MR-Sort, B reçoit un mélange de deux segments MR-Sort : c'est le problème Inv-2-MR-Sort du jalon 2. Les défenses de référence l'utilisent directement.

## Organisation du code

Une partie se déroule toujours de la même façon. On génère une instance, H brouille, B reçoit le mélange et décide, puis on évalue B sur des objets neufs. Chacun n'écrit que des stratégies, dans `hackers/` ou `defenses/` ; le reste est commun.

| Fichier | Rôle |
| --- | --- |
| [interface.py](interface.py) | **À lire en premier.** Ce qu'une stratégie reçoit et renvoie, et les outils pour en écrire une. |
| [hackers/](hackers/) | Stratégies de H. Chaque fichier est chargé automatiquement. |
| [defenses/](defenses/) | Stratégies de B. Chaque fichier est chargé automatiquement. |
| [simulation.py](simulation.py) | Une partie : instance, brouillage vérifié, mélange, décision, évaluation. |
| [experiences.py](experiences.py) | Le tournoi : toutes les défenses contre tous les hackers, sur les mêmes instances. |
| [tests/test_contrats.py](tests/test_contrats.py) | Vérifie que chaque stratégie enregistrée respecte son contrat. |

Stratégies déjà présentes, dans les fichiers `reference.py` :

| Hacker | Rôle |
| --- | --- |
| *aucun* (ratio 0) | E0 : référence sans brouillage. |
| `etiquettes_aleatoires` | E1 : objets uniformes, catégories au hasard, aucun MR-Sort derrière. |
| `mrsort_aleatoire` | E2 : agent basique de l'énoncé, $M_H$ tiré exactement comme $M_A$. |

| Défense | Rôle |
| --- | --- |
| `naif` | Un seul MR-Sort appris par lincs sur tout ce que B reçoit. |
| `inv2_plus_grand` | Inv-2-MR-Sort du jalon 2 (A2, GMM), puis le modèle du plus grand groupe. |
| `inv2_mieux_explique` | Inv-2-MR-Sort, puis le groupe dont le modèle fait le moins d'erreurs sur ses propres lignes. |

### Comment les instances sont construites

Pour une graine donnée, le problème, $M_A$ et le jeu de test sont fixés. Ils ne dépendent ni de la taille du learning set de A, ni du hacker, ni de la défense. Les données de H sont les mêmes pour toutes les défenses : les comparaisons sont appariées.

Un MR-Sort tiré au hasard par lincs classe des objets uniformes de façon très déséquilibrée : jusqu'à 87 % dans une catégorie, parfois une catégorie vide. Une fidélité de 87 % ne voudrait alors rien dire. Les données de A et le jeu de test viennent donc du générateur équilibré de lincs : chaque catégorie est à ±20 % de l'équilibre. Les modèles dont une catégorie couvre moins de 0,5 % de l'espace sont écartés, car ce générateur pourrait chercher leurs objets pendant des dizaines de secondes.

B reçoit les lignes dans un ordre aléatoire, avec des noms neutres (`objet 1`, `objet 2`…) : rien ne trahit la source.

## Ajouter une stratégie

Créer un fichier à son nom, par exemple `hackers/quentin.py` ou `defenses/quentin.py`. Préfixer le nom de chaque stratégie par son prénom, pour éviter les collisions : deux stratégies du même nom déclenchent une erreur.

```python
"""Hackers de Quentin."""

from jalon3.interface import hacker, objets_uniformes


@hacker("quentin_frontieres")
def frontieres(vue, rng):
    """Une phrase : ce que fait H et pourquoi cela gênerait B."""
    x = objets_uniformes(vue.probleme, vue.nombre, rng)
    y = rng.integers(len(vue.probleme.ordered_categories), size=len(x))
    return x, y
```

- H reçoit `vue.probleme` (critères, bornes, catégories) et `vue.nombre`, le nombre maximal de données qu'il peut envoyer. Il ne voit pas les données de A. `@hacker(nom, voit_donnees_a=True)` lui donne `vue.donnees_a` : c'est une hypothèse plus forte, à signaler dans le rapport.
- H renvoie `x`, de forme `(au plus vue.nombre, nombre de critères)` et dans les bornes, et `y`, des entiers de 0 à C-1. Tout tirage passe par `rng`, pour que les résultats soient reproductibles.

```python
"""Défenses de Quentin."""

import numpy as np

from jalon3.defenses.reference import inv2
from jalon3.interface import Decision, defense


@defense("quentin_vote")
def vote(recu, graine, temps):
    """Une phrase : comment B choisit le modèle qu'il attribue à A."""
    etat = inv2(recu, graine, temps)
    groupe = int(np.argmax(np.bincount(etat.z, minlength=2)))
    return Decision(etat.modeles[groupe], suspects=etat.z != groupe)
```

- B reçoit `recu` au format du jalon 2 (`recu.x`, `recu.y`, `recu.probleme`), une graine et un budget `temps` en secondes, qu'il doit respecter.
- B renvoie `Decision(modele, suspects)` : le modèle lincs qu'il attribue à A et, s'il veut être évalué sur la détection, un booléen par ligne reçue (`True` = vient de H selon lui).

`interface.py` fournit aussi `tirer_modele`, `tirer_objets`, `objets_uniformes`, `classer` et `donnees`. Un fichier dont le nom commence par `_` n'est pas chargé : pratique pour un brouillon.

## Lancer les tests et le tournoi

Depuis la racine du dépôt :

```bash
# Contrats de toutes les stratégies enregistrées (environ 20 secondes).
.venv/bin/python -m unittest discover -v -s jalon3/tests

# Voir les stratégies chargées et le nombre de parties, sans calcul.
.venv/bin/jalon3 --lister

# Tester sa stratégie contre les références seulement.
.venv/bin/jalon3 --hackers quentin_frontieres --defenses naif inv2_plus_grand --graines 0 1 --temps 5 --sortie jalon3/results/quentin_essai

# Tournoi complet : toutes les stratégies, plusieurs dimensions et graines.
.venv/bin/jalon3 --dimensions 6x3 10x5 --ratios 0 0.25 0.5 1 --graines 0 1 2 3 4 --temps 10 --sortie jalon3/results/tournoi
```

Options : `--taille` (données de A, 300 par défaut), `--taille-test` (1 000), `--ratios` (données de H par donnée de A, entre 0 et 1 ; 0 est la référence sans brouillage), `--dimensions` (critères x catégories), `--graines`, `--temps` (secondes par défense). Le dossier `--sortie` doit être nouveau.

Le tournoi écrit :

- `resultats.csv` : une ligne par partie, écrite au fil de l'eau ;
- `resume.csv` : moyennes par dimension, ratio, hacker et défense ;
- dans le terminal, une matrice hacker × défense de la fidélité moyenne pour chaque ratio.

## Mesures

- **`fidelite`** : proportion d'objets du jeu de test que $M_A$ et le modèle de B classent dans la même catégorie. C'est la mesure principale : H veut la faire baisser, B la faire monter.
- **`detection_h`** : proportion des lignes de H que B désigne comme suspectes.
- **`rejet_a`** : proportion des lignes de A que B désigne à tort comme suspectes.
- **`temps`** : temps réel de la défense.

Les deux mesures de détection restent vides pour une défense qui ne désigne pas de suspects.

## Travailler à plusieurs

1. Partir de la branche commune et créer la sienne : `git switch -c jalon3/<prenom>`.
2. N'ajouter que ses propres fichiers dans `hackers/` ou `defenses/`. Le reste du code étant commun, une modification de `interface.py` ou de `simulation.py` se discute dans le groupe.
3. Avant de partager : tests de contrat, puis un petit tournoi contre les références.
4. Fusionner dans la branche commune. Le tournoi complet charge automatiquement les stratégies de tout le monde : c'est l'évaluation finale.

## Questions ouvertes

1. **Quel groupe appartient à A ?** Inv-2-MR-Sort renvoie deux modèles sans dire lequel est celui de A. Avec une donnée de H par donnée de A et $M_H$ tiré comme $M_A$, les deux groupes sont symétriques. `inv2_plus_grand` et `inv2_mieux_explique` sont deux réponses à comparer ; une autre piste est de supposer que B connaît quelques exemples authentifiés envoyés par A.
2. **Faut-il découper quand il n'y a pas d'attaque ?** Inv-2 coupe toujours en deux groupes, même quand toutes les données viennent de A. B apprend alors sur moitié moins de données.
3. **Comment H tire-t-il ses performances ?** `mrsort_aleatoire` utilise le même générateur que A ; `etiquettes_aleatoires` tire des objets uniformes, dont la loi diffère de celle de A.

## Pistes pour la partie 2

- **Rendre les deux segments indiscernables** : H choisit un $M_H$ aussi plausible que $M_A$ et envoie autant de données que A. La partition peut être parfaite ; B garde pourtant le mauvais modèle une fois sur deux.
- **Faire varier la distance entre $M_H$ et $M_A$** : si $M_H$ est proche de $M_A$, le brouillage change peu le modèle appris ; s'il en est loin, Inv-2-MR-Sort sépare facilement les deux groupes. Le cas le plus gênant est peut-être entre les deux.
- **Hypothèse plus forte, si H voit les données de A** : renvoyer les mêmes vecteurs avec une catégorie décalée d'un cran. Chaque objet apparaît alors deux fois, avec deux classes différentes.
