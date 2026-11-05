# Comparaisons des quatre expériences

20 graines ; tailles A=[300, 500, 1000] ; les différences sont calculées par graine avant toute moyenne.

Deux contrastes principaux fixés avant le calcul, pour N_A=300 et H/A=0,5 : gain d'Inv2 sur le hacker basique ; perte supplémentaire d'Inv2 face à classe haute. Les autres tailles et ratios sont des analyses complémentaires.

Une valeur positive signifie : gain pour Inv2 (`gain_inv2_hacker_basique`), attaque classe haute plus dommageable (`effet_classe_haute_sur_*`), surcroît de dommage plus important sur Inv2 que sur le naïf (`interaction_attaque_defense`), ou coût d'Inv2 sans attaque (`cout_defense_sans_attaque`).

IC à 95 % : bootstrap percentile de 10000 rééchantillonnages des graines (graine d'analyse 20261103). Les différences sont rééchantillonnées après appariement. Intervalles approximatifs et individuels, sans ajustement pour comparaisons multiples. Ils n'établissent pas à eux seuls une supériorité générale. Les bandes des graphiques historiques restent ± un écart-type, pas ces IC.

Les temps réels figurent dans `resume.csv` et `bilan.md` : cette confirmation compare les méthodes avec leurs arrêts propres, pas à budget de calcul égal. Le cas H/A=1 est à discuter séparément pour le hacker MR-Sort symétrique.

| Taille A | H/A | Contraste | Principal | n | Moyenne (points) | IC 95 % (points) |
|---:|---:|---|---|---:|---:|---|
| 300 | 0 | cout_defense_sans_attaque |  | 20 | 4.58 | [1.59 ; 7.47] |
| 300 | 0.25 | gain_inv2_hacker_basique |  | 20 | 0.61 | [-3.14 ; 4.73] |
| 300 | 0.25 | effet_classe_haute_sur_inv2 |  | 20 | 5.79 | [-0.52 ; 12.99] |
| 300 | 0.25 | effet_classe_haute_sur_naif |  | 20 | -1.17 | [-4.87 ; 2.21] |
| 300 | 0.25 | interaction_attaque_defense |  | 20 | 6.96 | [-1.07 ; 15.60] |
| 300 | 0.5 | gain_inv2_hacker_basique | oui | 20 | 4.44 | [0.65 ; 9.00] |
| 300 | 0.5 | effet_classe_haute_sur_inv2 | oui | 20 | 9.84 | [1.82 ; 19.84] |
| 300 | 0.5 | effet_classe_haute_sur_naif |  | 20 | 0.45 | [-3.90 ; 4.43] |
| 300 | 0.5 | interaction_attaque_defense |  | 20 | 9.39 | [0.12 ; 20.22] |
| 300 | 1 | gain_inv2_hacker_basique |  | 20 | -1.75 | [-12.48 ; 7.32] |
| 300 | 1 | effet_classe_haute_sur_inv2 |  | 20 | 21.70 | [2.10 ; 42.08] |
| 300 | 1 | effet_classe_haute_sur_naif |  | 20 | 15.83 | [2.41 ; 29.81] |
| 300 | 1 | interaction_attaque_defense |  | 20 | 5.88 | [-9.70 ; 22.17] |
| 500 | 0 | cout_defense_sans_attaque |  | 20 | 0.58 | [-3.83 ; 4.04] |
| 500 | 0.25 | gain_inv2_hacker_basique |  | 20 | -0.37 | [-2.77 ; 1.87] |
| 500 | 0.25 | effet_classe_haute_sur_inv2 |  | 20 | 0.33 | [-5.87 ; 6.58] |
| 500 | 0.25 | effet_classe_haute_sur_naif |  | 20 | -0.28 | [-4.25 ; 3.33] |
| 500 | 0.25 | interaction_attaque_defense |  | 20 | 0.60 | [-4.06 ; 5.76] |
| 500 | 0.5 | gain_inv2_hacker_basique |  | 20 | 3.29 | [-0.46 ; 7.32] |
| 500 | 0.5 | effet_classe_haute_sur_inv2 |  | 20 | 8.58 | [0.21 ; 18.56] |
| 500 | 0.5 | effet_classe_haute_sur_naif |  | 20 | 2.46 | [-1.95 ; 6.93] |
| 500 | 0.5 | interaction_attaque_defense |  | 20 | 6.12 | [-2.86 ; 16.41] |
| 500 | 1 | gain_inv2_hacker_basique |  | 20 | -3.42 | [-11.40 ; 3.52] |
| 500 | 1 | effet_classe_haute_sur_inv2 |  | 20 | 31.11 | [14.44 ; 47.68] |
| 500 | 1 | effet_classe_haute_sur_naif |  | 20 | 25.07 | [13.91 ; 36.41] |
| 500 | 1 | interaction_attaque_defense |  | 20 | 6.04 | [-8.25 ; 20.42] |
| 1000 | 0 | cout_defense_sans_attaque |  | 20 | 1.38 | [-1.74 ; 4.47] |
| 1000 | 0.25 | gain_inv2_hacker_basique |  | 20 | 4.38 | [0.84 ; 7.74] |
| 1000 | 0.25 | effet_classe_haute_sur_inv2 |  | 20 | 2.48 | [-1.56 ; 7.19] |
| 1000 | 0.25 | effet_classe_haute_sur_naif |  | 20 | -0.65 | [-4.27 ; 2.82] |
| 1000 | 0.25 | interaction_attaque_defense |  | 20 | 3.13 | [-2.73 ; 9.59] |
| 1000 | 0.5 | gain_inv2_hacker_basique |  | 20 | 3.53 | [-0.19 ; 7.42] |
| 1000 | 0.5 | effet_classe_haute_sur_inv2 |  | 20 | 4.91 | [-0.01 ; 10.33] |
| 1000 | 0.5 | effet_classe_haute_sur_naif |  | 20 | 3.65 | [0.16 ; 7.37] |
| 1000 | 0.5 | interaction_attaque_defense |  | 20 | 1.25 | [-5.07 ; 7.55] |
| 1000 | 1 | gain_inv2_hacker_basique |  | 20 | 0.26 | [-10.60 ; 10.50] |
| 1000 | 1 | effet_classe_haute_sur_inv2 |  | 20 | 32.88 | [21.59 ; 45.38] |
| 1000 | 1 | effet_classe_haute_sur_naif |  | 20 | 21.89 | [8.66 ; 34.38] |
| 1000 | 1 | interaction_attaque_defense |  | 20 | 10.99 | [1.25 ; 20.75] |

## Artefacts

- [Bilan et graphiques](bilan.md)
- [Contrastes CSV](comparaisons_confirmation.csv)
- [Contrôle des préfixes entre tailles](audit_appariement_tailles.json)

Les résultats de signe contraire à l'hypothèse sont conservés. L'attaque et la défense n'ont pas été remplacées après examen de ces graines.
