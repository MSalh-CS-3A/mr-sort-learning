# Inv-2-MR-Sort : utilisation et conventions

## Objectif et organisation

On cherche deux groupes non vides et deux modèles MR-Sort minimisant `LG`, le nombre d'observations dont la catégorie observée diffère de la prédiction du modèle de leur groupe. Le nombre de catégories est fixé par le problème et peut dépasser deux. Aucune proportion source ni présence de chaque catégorie dans chaque groupe n'est imposée.

Le code du jalon 2 est dans `src/projet`. Les scripts à la racine et les résultats du jalon 1 restent utilisables. Les variantes A2-distance, raccordements exhaustifs, covariance complète et voisinage MILP ne font pas partie de cette version.

## Installation et vérifications

Python 3.14 est requis. Installation recommandée depuis la racine :

```bash
uv sync --locked
.venv/bin/python -m unittest -v test_mrsort
.venv/bin/python -m unittest discover -s tests -v
```

Autre installation : créer un environnement Python 3.14, installer `requirements.txt`, puis `pip install -e .`. Le fichier de dépendances est exporté de `uv.lock` avec `uv export --locked --no-hashes --no-emit-project --output-file requirements.txt --no-header`.

Les versions lincs 2.0.2 et Gurobi 13.0.3 sont fixées ; les autres versions exactes sont dans le verrou et dans chaque résultat. Le CLI fixe OpenMP, OpenBLAS et MKL à un thread avant les imports natifs ; `threadpoolctl` applique également cette limite pendant les calculs. L'exécution des expériences est séquentielle. Les utilisateurs de l'API Python doivent fixer les variables d'environnement avant d'importer lincs pour reproduire ce démarrage.

## Audit et données

```bash
.venv/bin/projet audit --data data --output results/jalon2/audit.json
```

Le lecteur utilise `Problem.load` et `Alternatives.load` de lincs. Le champ `kind` absent des six fichiers `problem.yml` est ajouté en mémoire uniquement. Les colonnes doivent être exactement le nom, les critères déclarés et la catégorie. Les catégories sont identifiées par leurs libellés, jamais en extrayant un nombre depuis le texte.

Cette version accepte les critères réels ou entiers monotones, croissants ou décroissants. Les critères énumérés et non monotones sont refusés explicitement. Les données originales ne sont ni réorientées ni réécrites pour l'apprentissage ; seule une copie numérique sert au GMM.

L'audit contrôle les dimensions annoncées, domaines, valeurs non finies, données manquantes, identifiants, catégories absentes et doublons. Il conserve les performances identiques portant des catégories contradictoires. Les recouvrements sont comparés sur les performances chargées par lincs, pas sur les noms `Alternative i` réutilisés entre fichiers. Les empreintes portent sur les octets des CSV et problèmes originaux.

Les 72 CSV actuels ne contiennent aucune source cachée ni catégorie avant bruit. Aucun modèle source n'est fourni. Type B signifie difficulté annoncée supérieure à type A, d'après l'information utilisateur ; le mécanisme du bruit reste inconnu. Les fichiers `noise00` et `noise10` ne sont pas des versions appariées ligne à ligne. Ces limitations empêchent d'annoncer une récupération des vraies sources.

Les 36 paires A/B de même nom partagent les mêmes performances, dans le même ordre, avec des catégories différentes. Elles ne sont donc pas indépendantes. Voir [le rapport d'audit](audit_jalon2.md) pour les relations et effectifs vérifiés.

## Méthodes et réglages

Chaque instance conserve des tuples de performances et de catégories observées. Les groupes sont codés `0/1` et les catégories `0..C-1`, conformément à lincs. Les libellés d'origine sont sauvegardés. Chaque prédiction utilise un objet `Alternatives` temporaire, car le classifieur lincs modifie les catégories de cet objet.

Un état contient la partition, les deux modèles, leurs prédictions sur tout le jeu et le score correspondant. Les modèles sont des snapshots YAML immuables. Un candidat rejeté ne modifie pas l'état courant.

`fit_guarded` entraîne avec WPB puis compare le candidat à l'ancien modèle sur le nouveau groupe. Il conserve l'ancien à égalité ou en cas d'échec du candidat. Sans ancien modèle valide, l'échec est journalisé et la trajectoire est abandonnée. Ce mécanisme n'est pas une initialisation interne de WPB avec l'ancien modèle.

| Méthode | Comportement |
| --- | --- |
| A0 | Partitions et apprentissages indépendants ; meilleur état conservé. |
| A1 | Transferts simultanés faux-vers-vrai ; réentraînement protégé ; vérification de `LG_nouveau <= LG_ancien - transferts`. |
| A2 | Transferts A1 et transferts aléatoires sur les cas ambigus ; acceptation des plateaux sans cycle, stagnation bornée. |
| A3 | Meilleure amélioration après réentraînement, sur seize voisins au plus : huit déplacements et huit échanges, moitié guidés et moitié aléatoires. |
| A4 | Descentes A3 et perturbations éventuellement dégradantes de l'état courant ; meilleur état conservé séparément. |

Les trajectoires terminées redémarrent dans le budget global. Les arrêts incluent zéro erreur, budget et bornes optionnelles de travail. L'absence d'amélioration d'A3 concerne seulement les voisins effectivement évalués. A1 et A2 gardent la première observation transférable dans un groupe si tous ses membres devaient le quitter.

L'initialisation uniforme utilise des Bernoulli indépendantes de paramètre 1/2 et rejette les groupes vides. Elle n'impose pas un équilibre exact. Le GMM utilise deux composantes par catégorie, des covariances diagonales, cinq démarrages, une régularisation de `1e-6` et 200 itérations au plus. La transformation utilise les bornes publiques et le sens des critères. Les composantes sont raccordées selon la moyenne des centres transformés, puis leur ordre lexicographique et leur indice en cas d'égalité. Une égalité de responsabilités est affectée au groupe du centre le plus bas. Les catégories trop petites, constantes et les échecs d'EM déclenchent un recours uniforme journalisé ; un résultat global vide déclenche un recours uniforme global.

WPB utilise GLOP, l'amélioration des profils sur CPU, neuf modèles internes et le renouvellement des quatre moins précis. Les sous-graines de partition, GMM, propositions, perturbations et apprentissages sont dérivées par SHA-256 de la graine racine et d'un compteur propre à chaque flux. La chaîne entière est enregistrée. Une limite en nombre d'appels peut compléter la limite de temps pour les tests.

## Exécution et budgets

```bash
# Essai court : dix secondes au total, 0,25 seconde par appel WPB
.venv/bin/projet run data/type_a/cr06_ca03/n0300_rep50-50_noise00.csv --method A1 --seed 0

# GMM et recherche locale
.venv/bin/projet run data/type_b/cr08_ca04/n0300_rep50-50_noise00.csv --method A3 --initializer gmm --seconds 30 --wpb-seconds 1

# Diagnostic distinct à un modèle
.venv/bin/projet run data/type_a/cr06_ca03/n0300_rep50-50_noise00.csv --method single --seconds 10

# Inventorier le coût sans lancer les expériences
.venv/bin/projet pilot --config configs/pilot.toml --dry-run
.venv/bin/projet campaign --config configs/campaign.toml --dry-run

# Pilote : 12 CSV × 5 méthodes × 2 graines = 120 exécutions
.venv/bin/projet pilot --config configs/pilot.toml

# Campagne minimale : 72 CSV × 5 méthodes × 5 graines = 1 800 exécutions
.venv/bin/projet campaign --config configs/campaign.toml

# Extensions : 9 combinaisons, 3 240 exécutions
.venv/bin/projet campaign --config configs/campaign.toml --profile extended --output results/jalon2/extended
```

Les cinq méthodes minimales sont A0-uniform, A1-uniform, A1-gmm, A3-uniform et A3-gmm. Le pilote prend les fichiers `n0300_rep50-50_noise00` et `n1200_rep75-25_noise10` dans chacune des six configurations. Il utilise les graines 0 et 1, dix secondes par exécution et 0,25 seconde par appel WPB, soit vingt minutes avant surcoûts.

Les campagnes utilisent les graines 0 à 4, trente secondes par exécution et une seconde par appel WPB : quinze heures pour la campagne minimale, vingt-sept pour les neuf combinaisons. Ces durées sont des plafonds nominaux avant surcoûts ; un arrêt à zéro peut raccourcir les calculs. `--seeds 0,1`, `--limit 5`, `--seconds` et `--wpb-seconds` permettent de réduire explicitement le protocole. La campagne n'est jamais lancée automatiquement.

Les fichiers TOML séparent budgets, WPB, initialisation, recherche et MILP. Les options de ligne de commande prennent le pas sur le TOML ; les valeurs absentes utilisent les défauts de la commande. Les clés inconnues et dupliquées sont refusées.

Le temps global utilise une horloge monotone et inclut initialisation, recherche, réentraînements et redémarrages. La lecture commune des données est séparée et mesurée dans le manifeste. Le démarrage du processus, les imports communs, le contrôle des threads, l'écriture finale des artefacts et leur validation de rechargement sont hors du budget algorithmique. L'import spécifique de scikit-learn lors du premier GMM est inclus dans son initialisation. Les arrêts de WPB sont coopératifs : les préparations et l'itération en cours peuvent dépasser la limite ; chaque dépassement est enregistré.

## MILP conjoint à marge

```bash
.venv/bin/projet run data/type_a/cr06_ca03/n0300_rep50-50_noise00.csv --method MILP --milp-seconds 30

# Facultatif : point de départ issu d'un résultat sauvegardé
.venv/bin/projet run data/type_a/cr06_ca03/n0300_rep50-50_noise00.csv --method MILP --warm-start results/jalon2/run/IDENTIFIANT/result.json
```

Le MILP optimise conjointement affectations et modèles. Le point de départ ne fixe pas les variables d'affectation. Les deux groupes sont non vides et seule la symétrie globale est supprimée en affectant la première ligne au groupe 0.

La concordance utilise un seuil fixé à 1 et des poids indépendants non négatifs communs aux frontières d'un modèle. Leur somme n'est pas normalisée. On borne chaque poids à 1 : écrêter un poids supérieur à 1 préserve toutes les coalitions gagnantes pour un seuil 1. Les poids tous nuls et les modèles constants sont admis.

Pour chaque critère et frontière, les indicateurs d'acceptation sont monotones sur les valeurs distinctes, ordonnées dans le sens de préférence. Ils sont également ordonnés entre frontières. Les indicateurs et contributions sont partagés pour les valeurs ex æquo. Les configurations tout accepté et tout refusé sont incluses ; cette dernière se reconstruit avec `None`. Les produits poids–indicateur utilisent la linéarisation binaire–continue avec borne 1.

Les contraintes de catégorie inférieure exigent un score d'au moins 1 ; le refus de la frontière supérieure exige au plus `1 - score_margin`. La marge vaut `1e-4` et les tolérances `1e-8`. Les constantes de désactivation découlent des bornes `0 <= score <= m`. Un démarrage est omis avec motif enregistré s'il ne respecte pas cette famille ou la marge.

La construction, la validation du démarrage et la résolution partagent les trente secondes. Une vérification lincs suit la reconstruction. Une observation dont l'erreur MILP est nulle mais dont la prédiction est fausse entraîne le statut `invalid_numerical`. L'objectif du solveur, le vrai `LG` reconstruit, la borne, le gap et les statuts sont séparés. `optimal_for_margin_formulation` n'affirme aucune exactitude du problème continu sans marge : une marge positive peut en restreindre les solutions.

Les tests utilisent des instances minuscules compatibles avec la licence limitée incluse dans gurobipy. Avec cette licence, les CSV n0300 déclenchent le statut sauvegardé `license_limit`. Une licence complète permet de les résoudre ; le bilan contient aussi un essai n0300 de trente secondes avec une licence liée à la machine. Cette dernière nécessite l'accès à l'identifiant matériel : dans le bac à sable de la session, Gurobi renvoie `HostID mismatch`, alors que les mêmes tests passent hors de ce bac à sable. `--include-milp` ajoute les n0300 à une campagne et `--include-diagnostic` ajoute le diagnostic à un modèle, chacun pour les graines sélectionnées. Ces options ne sont pas activées par défaut.

## Sorties, reprise et analyse

Chaque exécution possède un sous-dossier identifié par les données, problème, configuration, graine, versions, plateforme et empreinte du code. Un point de départ MILP entre également dans cette identité.

- `result.json` : métadonnées, état complet, catégories, scores, graines, événements, compteurs, dépassements et informations de threads.
- `model1.yml`, `model2.yml` et `assignments.json` : meilleur état à deux groupes ; `single_model.yml` pour le diagnostic séparé.
- `trace.json` : temps, objectif courant et meilleur objectif. Les incumbents MILP antérieurs à la validation lincs sont signalés explicitement.
- `manifest.json` : plan et suivi du lot, temps de lecture commune et motifs d'échec.

Relancer la même commande réutilise seulement les résultats terminés ayant une identité identique. Les modèles et prédictions sont revalidés par lincs lors de cette reprise. Une interruption laisse une exécution non terminée, qui sera recalculée. Changer le code, les données, les dépendances, les paramètres ou la graine crée une autre identité. `--no-resume` force le recalcul. Le manifeste est reconstruit pour les jobs de la commande courante ; les autres sous-dossiers sont conservés.

```bash
.venv/bin/projet analyze results/jalon2/pilot
```

L'analyse produit les résultats individuels, les synthèses globales et par instance, les strates type/configuration/bruit/répartition, toutes les différences appariées de méthodes sur un même CSV et une même graine, les temps pour atteindre 0 %, 5 % et 10 % d'erreurs, et les figures `final_quality.png`, `quality_time.png` et `factors.png`. Les médianes, quartiles, meilleurs résultats et fréquences de zéro sont fournis. La figure temporelle affiche une médiane sur la cohorte finale constante une fois celle-ci entièrement disponible ; un panneau séparé montre la proportion de toutes les tentatives ayant déjà une solution. `anytime.csv` conserve les effectifs, la médiane partielle et la médiane de cohorte constante.

Les résumés distinguent le nombre de tentatives et de solutions valides ; `failures.csv` répertorie les exécutions sans solution ou invalides. La fréquence de zéro utilise toutes les tentatives comme dénominateur, tandis que les taux d'erreur et quartiles portent sur les solutions disponibles. Une méthode sans solution conserve une ligne de résumé avec qualité indéfinie, jamais une erreur inventée égale à zéro.

Les méthodes et budgets sont distingués ; analyser séparément des campagnes de réglages différents qui produiraient plusieurs résultats pour un même appariement. Les résultats sans solution ou invalides sont comptés par statut mais exclus des statistiques de qualité. Les répétitions mesurent l'aléa algorithmique sur les fichiers fournis, sans démontrer une généralisation à de nouvelles instances.

Le pilote fait varier simultanément taille, bruit et répartition entre ses deux fichiers par configuration : il ne permet pas d'isoler l'effet de ces facteurs. De même, nombres de critères et de catégories varient ensemble. Les figures par facteur sont descriptives et ne permettent pas d'attribuer un effet causal individuel.

Le [bilan du pilote](comptes_rendus/compte_rendu_jalon2.md) et son archive de code précisent l'empreinte utilisée pour les résultats livrés. Les corrections finales relatives aux entiers, instances synthétiques, interruptions MILP et statistiques d'échec changent l'empreinte du code courant ; une nouvelle exécution courante n'est donc pas confondue avec ces résultats archivés. La commande de reprise de la version exacte est fournie dans le bilan.

## API Python

Les points d'entrée sont `projet.data.load_instance`, `projet.initializers.initialize`, `projet.core.predict`, `fit_guarded`, `evaluate`, `projet.search.solve` et `projet.milp.solve_joint_milp`. `projet.runner.load_run` recharge et vérifie un résultat sauvegardé contre l'instance originale.

```python
from projet.core import Config
from projet.data import load_instance
from projet.search import solve

data = load_instance("data/type_a/cr06_ca03/n0300_rep50-50_noise00.csv")
result = solve(data, Config(heuristic="A1", seconds=10, wpb_seconds=0.25), seed=0)
if result.best is not None:
    print(result.best.loss, result.best.assignments)
```
