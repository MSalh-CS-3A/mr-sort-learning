# Confirmation des quatre couples - plan fixé avant exécution

Décision du 3 novembre 2026, après examen du calibrage de développement et accord
de l'utilisateur. Génération, test indépendant et informations accessibles à
A/H/B : [protocole uniforme-v1](protocole.md), conservé. L'utilisateur a demandé
trois tailles A : 300, 500 et 1 000.

## Comparaisons fixées

| Couple | Attaque H | Apprentissage B |
|---|---|---|
| E1 | `mrsort_aleatoire` : un MR-Sort indépendant, classes cohérentes | `naif` |
| E2 | `mrsort_aleatoire` | `inv2_plus_grand` |
| E3 | `classe_haute` : performances uniformes, classe toujours C-1 | `naif` |
| E4 | `classe_haute` | `inv2_plus_grand` |

Inv2 et classe haute sont fixés avant les nouvelles graines. Le choix a été
guidé par l'hypothèse de majorité et le calibrage, pas par un résultat final.
Classe haute reste un candidat : son efficacité supplémentaire est à mesurer.
Les témoins sans H sont partagés entre les attaques, une fois par défense,
taille et graine. Ils mesurent aussi le coût de la défense sans attaque.

## Paramètres

| Paramètre | Valeur |
|---|---|
| Critères / catégories | 6 / 3 |
| Tailles A | 300, 500, 1 000 |
| Ratios H/A | 0 ; 0,25 ; 0,5 ; 1 |
| Graines | 1000 à 1019 : vingt répétitions indépendantes |
| Test | 10 000 objets uniformes par graine, cachés à H/B |
| Diagnostic | 10 000 autres objets par graine, cachés à H/B |
| Exécution locale | Deux sous-processus, un thread numérique chacun |
| Apprentissage | Réglages existants et correction des poids nuls conservés |

Les configurations déjà enregistrées ont été vérifiées avant lancement : aucune
graine de 1000 à 1019 n'y figurait. Les graines 100 à 104 restent du développement.
Un lot correspond à une taille et une graine, avec 14 décisions : deux témoins et
douze sous attaque. Il y a 60 lots, donc **840 évaluations : 720 sous attaque et
120 témoins**.

| N_A | N_H à ratio 0 | N_H à 0,25 | N_H à 0,5 | N_H à 1 |
|---:|---:|---:|---:|---:|
| 300 | 0 | 75 | 150 | 300 |
| 500 | 0 | 125 | 250 | 500 |
| 1 000 | 0 | 250 | 500 | 1 000 |

Une même graine conserve M_A, M_H basique, le test et le diagnostic entre tailles
et ratios. Les petits jeux A et H sont les préfixes des grands. Les défenses
reçoivent exactement le même mélange. À ratio fixé, augmenter A augmente aussi H :
c'est une étude de la taille à contamination proportionnelle. Le nombre de
répétitions indépendantes reste vingt, pas soixante.

Les arrêts du jalon 2 restent inchangés. Le budget demandé de 12 s ne plafonne
ni `naif` ni Inv2. Les temps mesurés sont présentés avec les fidélités. Ce plan
ne compare pas les défenses à calcul égal et n'isole pas tous les effets
d'optimisation liés à la taille sous arrêt temporel.

## Analyse arrêtée avant consultation des résultats

Mesure principale : fidélité à M_A sur le test indépendant. Deux contrastes
principaux sont fixés pour N_A=300 et H/A=0,5 :

1. **E2-E1** : gain d'Inv2 contre le hacker basique. Positif = meilleure fidélité
   d'Inv2 dans ces réglages.
2. **E2-E4** : dommage supplémentaire de classe haute contre Inv2. Positif =
   classe haute plus dommageable que le hacker basique au même budget.

Les autres tailles et ratios sont des analyses complémentaires. Sont aussi
calculés E1-E3 (effet sur le naïf), (E2-E4)-(E1-E3) (différence d'effet entre
défenses) et le coût d'Inv2 face au naïf sans attaque. Tous les signes sont
conservés, sans remplacement de stratégie ni retrait d'une graine défavorable.

Les différences sont calculées par graine avant la moyenne. IC à 95 % : bootstrap
percentile de 10 000 rééchantillonnages des graines après appariement (graine
d'analyse 20261103). Intervalles approximatifs, individuels et sans correction
de multiplicité. Les bandes des graphiques usuels restent ± un écart-type,
distinctes de ces IC.

La meilleure fidélité parmi les candidats Inv2, la perte de sélection et la
partition servent à l'explication après décision. Aucun oracle ne choisit pour
B. À H/A=1, la symétrie A/H concerne le hacker MR-Sort de mêmes lois ; elle ne
s'applique pas automatiquement à classe haute.

## Exécution

```bash
.venv/bin/python -m jalon3.campagne --phase confirmation --sortie jalon3/results/confirmation_quatre_couples_v1 --processus 2 --plan
.venv/bin/python -u -m jalon3.campagne --phase confirmation --sortie jalon3/results/confirmation_quatre_couples_v1 --processus 2
.venv/bin/python -m jalon3.campagne --sortie jalon3/results/confirmation_quatre_couples_v1 --etat
.venv/bin/python -u -m jalon3.campagne --sortie jalon3/results/confirmation_quatre_couples_v1 --reprendre --processus 2
```

Chaque lot est audité avant agrégation et exécuté depuis le code figé. À la fin,
un contrôle vérifie les modèles fixes et préfixes réellement sauvegardés entre
tailles et ratios. Sorties : `bilan.md`, `resume.csv`, `figures/`,
`comparaisons_confirmation.md` et `.csv`, `audit_campagne.json`,
`audit_appariement_tailles.json`, configuration, sources, journaux et progression.

Le résultat scientifique sera lu après le calcul : un audit réussi ne garantit
ni la supériorité d'Inv2 ni celle de classe haute. Nous analyserons ensemble les
effets observés, leurs dispersions et leurs limites.
