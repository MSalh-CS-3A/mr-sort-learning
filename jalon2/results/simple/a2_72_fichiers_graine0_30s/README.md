# Évaluation A2 — 72 fichiers, graine 0

A2-uniforme et A2-GMM, 30 secondes nominales par exécution, 1 seconde par appel WPB.
Deux lots séquentiels : 36 fichiers du type A, puis 36 du type B. 144 exécutions, environ 1 h 12 nominale hors dépassements et exports.

- `type_a/resultats.csv` et `type_b/resultats.csv` : résultats séparés, écrits après chaque exécution terminée.
- Sous-dossiers : modèles lincs, problème, affectations et trace.
- `execution.log` : progression de l'ensemble.
- `statut.txt` : lot actif ou fin de traitement.
- `pid.txt` : PID du lanceur détaché.
- `codes_sortie.txt` : code de sortie de chaque lot (0 = aucun résultat invalide).
- `configuration.json` : réglages, versions et empreintes des données.
- `source/projet` : copie figée du code exécuté pour garder la même version entre les deux lots.
- `lancer.sh` : commandes exactes ; une nouvelle exécution nécessite un autre dossier de sortie.

Le processus est détaché du terminal. La mise en veille suspend les calculs ; l'arrêt ou le redémarrage de la machine termine le processus. Aucune inhibition de la veille n'est activée. Les résultats des exécutions terminées sont conservés, mais il n'y a pas de reprise automatique.

## Résultats et évolution

Les deux lots sont terminés : 72 exécutions valides sur A et 72 sur B, sans échec. Les 144 traces ont été contrôlées : temps croissants, meilleur LG non croissant et dernier meilleur LG égal au score du CSV.

Les trois graphiques comparent A2-uniforme et A2-GMM sur le type A, le type B et les deux types réunis. L'ordonnée est la moyenne du meilleur LG/N enregistré à chaque instant, en pourcentage ; chaque fichier a le même poids. L'abscisse est le temps écoulé d'une exécution, comprenant son initialisation, pas la durée cumulée de la campagne. Une seule graine est utilisée.

| Ensemble | A2-uniforme à 30 s | A2-GMM à 30 s |
| --- | ---: | ---: |
| A, 36 fichiers | 13,10 % | 12,09 % |
| B, 36 fichiers | 15,07 % | 14,73 % |
| A + B, 72 fichiers | 14,09 % | 13,41 % |

- [Les trois graphiques réunis](figures/evolutions_a_b_ensemble.png).
- Graphiques individuels : [type A](figures/evolution_type_a.png), [type B](figures/evolution_type_b.png), [ensemble](figures/evolution_commune.png).
- Chaque figure existe aussi en SVG.
- `figures/courbes.csv` contient les points tracés ; `figures/resume_evolution.csv` contient les scores à 10, 20 et 30 secondes, les scores finaux et les temps moyens réels.

Les courbes commencent une fois qu'un premier état existe pour tous les fichiers et les deux initialisations de l'ensemble concerné : avant cela, la zone est grisée. Elles utilisent le dernier état enregistré à une date inférieure ou égale à l'instant considéré, sans interpolation ni prise en compte d'un résultat futur. La population moyenne reste donc constante. Les scores du graphique à 30 secondes peuvent être légèrement supérieurs aux scores finaux du CSV : un dernier apprentissage coopératif peut se terminer après les 30 secondes nominales. Les catégories observées sont les cibles de reconstruction ; ces courbes ne mesurent pas une performance hors échantillon.

Pour régénérer uniquement les figures depuis la racine du dépôt, sans apprentissage :

```bash
.venv/bin/python results/simple/a2_72_fichiers_graine0_30s/tracer.py
```
