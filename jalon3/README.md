# Jalon 3 - Apprendre MR-Sort malgré un brouillage

> **Brouillon du plan expérimental, à discuter dans le groupe.** Aucun code n'est encore écrit.
> Jalon optionnel. Dépôt sur Edunao au plus tard le 05/11/2026 à 23 h 59 ; soutenance le 06/11/2026.
> Énoncé : page 5 de [docs/sujet.pdf](../docs/sujet.pdf).

## Le problème

- **A** observe des objets classés par un modèle MR-Sort inconnu, noté $M_A$. A n'a presque pas de puissance de calcul : il transmet ses données à B sans les traiter.
- **H**, un agent malveillant, ajoute de fausses données : un vecteur de performances et une catégorie. Il peut en ajouter **au plus une par donnée de A**, donc jusqu'à la moitié de ce que B reçoit.
- **B** reçoit le mélange sans savoir qui a envoyé chaque ligne. Il a de la puissance de calcul et cherche à retrouver $M_A$.

L'énoncé demande deux choses :

1. **Partie 1.** H est « basique » : il tire un MR-Sort au hasard, $M_H$, et s'en sert pour classer ses objets. Utiliser le jalon 2 pour aider B, sur des données que nous construisons.
2. **Partie 2.** Se mettre à la place de H : trouver une stratégie de brouillage efficace et montrer, sur une instance, à quel point elle gêne B.

## Lien avec le jalon 2

Quand H classe ses objets avec un MR-Sort, B reçoit un mélange de deux segments MR-Sort : c'est exactement le problème Inv-2-MR-Sort du jalon 2. `jalon2.algorithmes.resoudre` renvoie une partition en deux groupes et un modèle par groupe ; si tout se passe bien, un groupe contient les données de A et son modèle approche $M_A$.

Les CSV du jalon 2 avaient déjà cette forme (`rep50-50`, `rep75-25`), mais sans la source de chaque ligne ni les modèles d'origine. Pour évaluer B, il faut les connaître : on génère donc nos instances avec lincs (`generate_problem`, `generate_mrsort_model`, `generate_alternatives`). Écrire chaque instance au format CSV et `problem.yml` du jalon 2 permet de réutiliser `jalon2.apprentissage.charger` tel quel.

## Modèle de base

- H ne voit pas les données de A. Il connaît seulement le problème : critères, bornes et catégories.
- B n'a pas de défense spécifique contre H : il apprend sur tout ce qu'il reçoit. On compare deux B :
  - **B naïf** : un seul MR-Sort appris par lincs sur le mélange ;
  - **B jalon 2** : Inv-2-MR-Sort, puis choix d'un des deux modèles.
- Hors ligne : B reçoit tout le learning set en une fois.

## Expériences de la partie 1

| Expérience | Données ajoutées par H | Rôle |
| --- | --- | --- |
| E0 | aucune | Référence : ce que B obtient sans brouillage. |
| E1 | objets classés au hasard, sans MR-Sort | Bruit pur. |
| E2 | objets classés par un autre MR-Sort tiré au hasard, $M_H$ | Agent basique de l'énoncé. |

Paramètres à faire varier, avec peu de valeurs vu le délai :

- proportion de données de H par donnée de A : 0,25, 0,5 et 1 (le maximum autorisé) ;
- taille du learning set de A : 300 objets, puis 600 si le temps le permet ;
- dimensions : 6 critères et 3 catégories, puis 10 critères et 5 catégories ;
- au moins cinq graines par configuration.

À titre d'ordre de grandeur, 90 exécutions d'Inv-2-MR-Sort à 30 secondes chacune prennent environ 45 minutes.

## Mesures

- **Fidélité à $M_A$** : proportion d'objets d'un jeu de test indépendant que $M_A$ et le modèle retenu par B classent dans la même catégorie. C'est le protocole du jalon 1 et la mesure principale.
- **Détection du brouillage** : proportion de lignes bien rangées dans le groupe de A ou dans celui de H, à permutation des groupes près.
- **LG** de la partition, pour comparer avec les résultats du jalon 2.

## Questions à trancher avant de coder

1. **Quel groupe appartient à A ?** Inv-2-MR-Sort renvoie deux modèles sans dire lequel est celui de A. Avec une donnée de H par donnée de A et $M_H$ tiré comme $M_A$, les deux groupes sont symétriques : B n'a aucune raison de préférer l'un à l'autre. Règles possibles :
   - garder le plus grand groupe, ce qui marche seulement si H envoie moins de données que A ;
   - garder le groupe le mieux expliqué par son modèle, ce qui suffit contre E1 où les étiquettes de H ne suivent aucun MR-Sort ;
   - supposer que B connaît quelques exemples authentifiés envoyés par A.
2. Comment H tire-t-il ses vecteurs de performances : même loi que A, ou une autre loi ?
3. Que vaut « B ne se défend pas » quand B utilise le jalon 2 : la règle de choix du groupe fait-elle partie de la défense ?

## Pistes pour la partie 2

- **Rendre les deux segments indiscernables** : H choisit un $M_H$ aussi plausible que $M_A$ et envoie autant de données que A. La partition peut être parfaite ; B garde pourtant le mauvais modèle une fois sur deux.
- **Faire varier la distance entre $M_H$ et $M_A$** : si $M_H$ est proche de $M_A$, le brouillage change peu le modèle appris ; s'il en est loin, Inv-2-MR-Sort sépare facilement les deux groupes. Le cas le plus gênant est peut-être entre les deux.
- **Hypothèse plus forte, si H voit les données de A** : renvoyer les mêmes vecteurs avec une catégorie décalée d'un cran. Chaque objet apparaît alors deux fois, avec deux classes différentes.
