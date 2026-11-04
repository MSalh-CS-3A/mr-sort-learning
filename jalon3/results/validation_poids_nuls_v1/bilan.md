# Bilan de la campagne

6 parties ; 6 réussies ; 0 en erreur.

Les graines sont les répétitions indépendantes. Les tailles et ratios d'une même graine sont appariés.
Les dispersions sont des écarts-types entre graines ; elles ne sont pas des intervalles de confiance.

| Taille A | Ratio H/A | Attaque | Défense | n / échecs | Fidélité (%) | Écart-type (points) | Perte appariée (points) | Fidélité équilibrée (%) |
|---:|---:|---|---|---:|---:|---:|---:|---:|
| 300 | 0 | aucun | inv2_mieux_explique | 1 / 0 | 94.04 | — | 0.00 | 92.33 |
| 300 | 0 | aucun | inv2_plus_grand | 1 / 0 | 94.04 | — | 0.00 | 92.33 |
| 300 | 0 | aucun | naif | 1 / 0 | 94.71 | — | 0.00 | 94.41 |
| 300 | 1 | classe_basse | inv2_mieux_explique | 1 / 0 | 18.20 | — | 75.84 | 33.33 |
| 300 | 1 | classe_basse | inv2_plus_grand | 1 / 0 | 18.20 | — | 75.84 | 33.33 |
| 300 | 1 | classe_basse | naif | 1 / 0 | 18.20 | — | 76.51 | 33.33 |

## Figures


## Limites d'interprétation

- Sans défense (`naif`), un seul modèle est appris : aucune mesure de séparation des deux règles.
- À parts égales, le rôle A/H est indiscernable sous les lois symétriques du protocole.
- Le désaccord est un diagnostic du simulateur, caché à A, H et B. Il ne sélectionne pas les modèles.
- Le filtre des catégories rares est estimé sur 2 000 points distincts ; il conditionne la population étudiée.
- Les rappels par catégorie peuvent être imprécis pour les classes rares. La fidélité équilibrée est vide si une classe manque au test.
- L'apprentissage naïf utilise l'arrêt du jalon 2 (seuil de temps interne nominal de 4 s, ou arrêt anticipé). Ce seuil ne plafonne pas strictement la durée totale observée. Les données sont reproductibles ; les modèles appris peuvent varier avec la charge machine.
- Une augmentation de la perte avec le ratio n'est pas imposée. Une perte négative signifie une amélioration sur cette répétition.
- Le nuage désaccord/perte répète les mêmes modèles pour plusieurs tailles et ratios : il ne représente pas autant de répétitions indépendantes.

## Calcul, sélection et diagnostics

Le temps attribuable à une défense inclut toute sa préparation. Lorsque deux sélections partagent Inv-2, le temps de préparation est inclus dans chacune ; le calcul réellement exécuté n'est compté qu'une fois dans `temps_calcul_effectif`.

Le gain face à naif est calculé sur le même mélange et la même graine. Il ne prouve pas un avantage à budget égal : naif et Inv-2 gardent leurs arrêts propres. `naif_multi` est un contrôle de redémarrages, à budget demandé explicite.

Les fidélités oracle et reconstructions à permutation près utilisent les vérités cachées uniquement après la décision de B. Elles ne servent jamais à choisir son groupe. La perte de sélection sépare l'absence d'un bon candidat d'un mauvais choix parmi les candidats.

| Critères × catégories | Taille A | Ratio H/A | Attaque | Défense | Temps attribuable moyen (s) | Gain face à naif (points) | Perte de sélection (points) |
|---|---:|---:|---|---|---:|---:|---:|
| 6 × 3 | 300 | 0 | aucun | inv2_mieux_explique | 27.822 | -0.67 | 0.00 |
| 6 × 3 | 300 | 0 | aucun | inv2_plus_grand | 27.822 | -0.67 | 0.00 |
| 6 × 3 | 300 | 0 | aucun | naif | 4.162 | 0.00 | — |
| 6 × 3 | 300 | 1 | classe_basse | inv2_mieux_explique | 11.211 | 0.00 | 62.51 |
| 6 × 3 | 300 | 1 | classe_basse | inv2_plus_grand | 11.211 | 0.00 | 62.51 |
| 6 × 3 | 300 | 1 | classe_basse | naif | 4.014 | 0.00 | — |
