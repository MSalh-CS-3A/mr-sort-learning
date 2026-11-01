# Essai des huit variantes sur cinq fichiers du type A

Exécution du 19 octobre 2026 sur la branche `jalon2/simplifie`, incluant le nouvel A2 par distance. Les modifications A2 ne sont pas encore commitées au moment de l'essai.

40 exécutions séquentielles, graine 0, budget global nominal de 10 secondes et 0,25 seconde par appel WPB. Un thread par bibliothèque. Les appels sont coopératifs : le temps réel cumulé des solveurs est 415.45 secondes (6.92 minutes), hors démarrage, lecture et exports. Le plus grand dépassement d'une exécution est 1.13 seconde(s).

## Fichiers

- `data/type_a/cr06_ca03/n0300_rep50-50_noise00.csv`
- `data/type_a/cr06_ca03/n0600_rep75-25_noise10.csv`
- `data/type_a/cr08_ca04/n0300_rep50-50_noise10.csv`
- `data/type_a/cr08_ca04/n1200_rep75-25_noise00.csv`
- `data/type_a/cr10_ca05/n0600_rep75-25_noise10.csv`

## Résultats

Moyenne des taux d'erreur LG/N, en donnant le même poids à chacun des cinq fichiers ; plus petit est meilleur. Il s'agit de reconstruction des CSV, sans évaluation hors échantillon.

| Méthode | Uniforme | GMM |
| --- | ---: | ---: |
| A1 | 16.17 % | 14.43 % |
| A2 | 14.57 % | 13.27 % |
| A3 | 26.25 % | 21.07 % |
| A4 | 26.25 % | 21.07 % |

A2-GMM obtient le meilleur taux moyen sur ce petit échantillon avec une seule graine. Ce constat ne suffit pas à désigner une méthode gagnante pour tous les fichiers.

Les dix traces A4 ne contiennent que l'initialisation et une amélioration de la première descente A3 : aucune perturbation A4 n'est enregistrée avant épuisement du budget. A3 et A4 ont ici exactement les mêmes scores finaux. Cet essai vérifie le fonctionnement des commandes et exports ; il ne permet pas de mesurer l'apport des perturbations A4. Prévoir un budget plus long et vérifier les traces avant d'interpréter leur comparaison.

## Contrôles

- 40 résultats valides ; aucun échec ou résultat absent.
- Rechargement des 80 modèles lincs : mêmes prédictions exportées et mêmes LG pour les 40 exécutions.
- Vérification des partitions non vides, catégories observées, tailles des groupes, traces temporelles et immuabilité des données lors des prédictions.
- 11 contrôles ciblés de distance A2 : coalitions pondérées, entrée dans la catégorie observée à travers plusieurs profils, sortie supérieure et inférieure, égalité, catégorie vide, seuil None et décision constante.
- La suite complète des tests unitaires n'a pas été exécutée.

`verification.json` détaille les contrôles. Pour les reproduire depuis la racine : `.venv/bin/python results/simple/essai_5_type_a_graine0/verifier.py`.

## Sorties

- `resultats.csv` : résultats par fichier et variante, temps réels et dépassements.
- `comparaison.csv` : moyennes par variante.
- `comparaison.png` et `comparaison.svg` : scores finaux et progression.
- Sous-dossiers : modèles, problème lincs, affectations et trace de chaque exécution.

La courbe moyenne commence seulement lorsque les cinq fichiers disposent d'un premier état. A3/A4 enregistrent les améliorations à la fin des passes ; la courbe ne décrit donc pas l'instant de découverte de chaque candidat intermédiaire. Les états terminés légèrement après les dix secondes nominales apparaissent après cette limite sur la figure.

Les lots complets de type A et de type B ne sont pas inclus dans cet essai.
