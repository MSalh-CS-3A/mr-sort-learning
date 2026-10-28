# Lire et utiliser la version simple

## Organisation

La branche `jalon2/simplifie` remplace l'ancien paquet par trois fichiers principaux :

| Fichier | Contenu |
| --- | --- |
| `jalon2/apprentissage.py` | Données, appels à lincs, garde-fou. |
| `jalon2/algorithmes.py` | Initialisation uniforme ou GMM, état de solution, A0-A4. |
| `jalon2/experiences.py` | Sélection des fichiers, boucles du benchmark, export CSV. |

Les deux petits fichiers `__init__.py` et `__main__.py` lancent simplement le programme. Il n'y a ni configuration TOML, ni registre de graines, ni empreinte de code, ni mécanisme de reprise. Le MILP conjoint et l'ancienne suite de tests sont conservés sur `jalon2/salhmed` ; ils ne font pas partie de cette version pédagogique des heuristiques.

Les sorties sous `jalon2/results/version_complete/` décrivent l'ancienne version. Les nouvelles exécutions écrivent sous le dossier que tu choisis, par exemple `jalon2/results/simple/essai_a1`. Le [premier essai de la version simple](../results/simple/essai_5_type_a_graine0/README.md) couvre cinq fichiers du type A et les huit variantes A1-A4.

## Ordre de lecture

Dans `apprentissage.py`, lire `charger`, `predire`, puis `apprendre`. Lincs modifie les catégories d'un objet `Alternatives` lorsqu'il prédit : la fonction `alternatives` crée donc une copie de travail. Les tableaux de performances et de catégories observées sont en lecture seule.

`apprendre` lance WPB puis compare le candidat à l'ancien modèle sur les indices du nouveau groupe. L'ancien modèle est conservé à égalité, s'il est meilleur, si le budget est épuisé ou si le nouvel apprentissage échoue. Sans ancien modèle, une erreur d'apprentissage est propagée ; elle sera visible dans le benchmark.

Dans `algorithmes.py`, commencer par `resoudre` :

1. Fixer une graine et une échéance globale.
2. Initialiser une partition.
3. Apprendre les deux modèles et calculer LG.
4. Appliquer la recherche choisie.
5. Conserver le meilleur état et recommencer tant qu'il reste du temps.

**A0 correspond aux étapes 1 à 3 répétées sans recherche de partition.** Les fonctions `a1`, `a2`, `a3` et `a4` décrivent chacune une trajectoire de recherche.

## Conventions à retenir

- Deux groupes, codés 0 et 1, obligatoirement non vides.
- Catégories internes indexées de 0 à C−1 suivant l'ordre du `problem.yml` ; C ne désigne pas le nombre de modèles.
- `LG` est le nombre d'erreurs du modèle affecté à chaque observation. La perte est 0/1, sans distance ordinale.
- Un déplacement ne change que l'affectation, jamais la performance ou la catégorie observée.
- Les modèles lincs ne sont pas modifiés par nos fonctions : chaque appel WPB construit une nouvelle population.
- Le score d'un candidat rejeté ne remplace ni les modèles ni la partition courants.

Cette version cible les critères réels monotones des données fournies. Le champ `kind` absent des six problèmes est ajouté en mémoire. Les fichiers originaux restent inchangés. Les catégories absentes d'un groupe restent déclarées dans le problème.

## Initialisations et méthodes

L'initialisation uniforme affecte indépendamment chaque ligne à l'un des groupes avec probabilité 1/2, et recommence si un groupe est vide. Elle n'impose pas une répartition exacte.

Le GMM est ajusté séparément dans chaque catégorie sur une copie normalisée selon les bornes publiques et orientée dans le sens de préférence. Les composantes sont raccordées selon la moyenne de leurs centres. L'ordre lexicographique des centres puis leur indice départagent une égalité. Une égalité de probabilités est affectée au centre le plus bas. Les cas trop petits, constants ou non convergents utilisent un recours uniforme, signalé par un avertissement.

| Méthode | Règle |
| --- | --- |
| A0 | Essais indépendants de partitions et de modèles. |
| A1 | Déplacements faux-vers-vrai, puis réentraînement protégé. Une vérification impose `LG_nouveau <= LG_ancien - nombre_de_transferts`. |
| A2 | A1 avec affectation des cas ambigus par distance à la décision MR-Sort : maximiser la robustesse si les deux sont justes, minimiser la distance à la catégorie observée si les deux sont faux. |
| A3 | Évaluer des voisins après réentraînement et accepter la meilleure amélioration trouvée. |
| A4 | Alterner descentes A3 et perturbations ; l'état courant peut se dégrader, le meilleur est conservé. |

Les réglages fixes sont écrits au lieu d'être cachés dans des configurations :

- WPB : neuf modèles, renouvellement des quatre moins précis, GLOP, profils améliorés sur CPU.
- GMM : deux composantes, covariance diagonale, cinq démarrages, régularisation `1e-6`, 200 itérations au plus.
- A2 : tous les cas ambigus sont examinés, sans tirage aléatoire des transferts. Arrêt sur affectation inchangée, cycle neutre ou vingt propositions sans amélioration stricte.
- A3 : au plus huit déplacements et huit échanges, moitié guidés par les erreurs et moitié aléatoires. Des doublons ou voisins inadmissibles peuvent réduire ce nombre.
- A4 : dix perturbations au plus par trajectoire ; taille de 1 % doublée après stagnation, plafonnée à 10 %, remise à 1 % après amélioration.

Les trajectoires terminées redémarrent dans le budget global. L'arrêt d'A3 ne certifie pas un optimum sur l'ensemble du voisinage : seuls les candidats effectivement évalués ont été comparés.

### A2 : distance à la décision MR-Sort

`distances_categorie`, dans `apprentissage.py`, calcule les distances avec les modèles courants, avant tout transfert. Les performances sont normalisées selon les bornes publiques et orientées dans le sens de préférence, sur une copie. La distance retenue est la norme maximale : `d(x, x') = max_j |x_normalise[j] - x'_normalise[j]|`. Une distance de 0,02 autorise donc une modification d'au plus 2 % de l'étendue de chaque critère, éventuellement sur plusieurs critères à la fois. Les observations restent inchangées : les modifications sont seulement hypothétiques.

- Si les deux modèles prédisent la catégorie observée, choisir celui dont la **distance minimale pour sortir de cette catégorie** est la plus grande. La sortie peut se faire vers le bas ou vers le haut ; on retient la plus proche.
- Si les deux modèles se trompent, choisir celui dont la **distance minimale pour atteindre exactement la catégorie observée** est la plus petite. Quitter la mauvaise catégorie vers une autre catégorie encore incorrecte ne suffit pas.
- À égalité, à `1e-12` près sur la distance normalisée, conserver le groupe actuel. Les modèles peuvent prédire deux catégories incorrectes différentes : cela reste un cas ambigu traité par la deuxième règle.

Ce calcul tient compte de la majorité MR-Sort, fixée à 1 dans lincs, et des poids appris, sans normaliser leur somme. Il énumère les coalitions gagnantes minimales et perdantes maximales parmi les `2**m` coalitions possibles. Une coalition gagnante impose d'atteindre certains seuils ; une coalition perdante impose d'en rejeter certains. Atteindre une catégorie intermédiaire exige simultanément de franchir son profil inférieur et de rejeter son profil supérieur. On écarte les combinaisons incompatibles, notamment lorsque des profils confondus rendent une catégorie inaccessible. L'énumération convient aux 6 à 10 critères du projet ; son coût croît exponentiellement avec le nombre de critères.

Les performances hypothétiques restent dans les bornes publiques. Un seuil `None` n'est jamais satisfait ; un critère constant ne peut pas être déplacé. Une région inaccessible a une distance infinie. Les distances sont des **infimums** : sortir par rejet d'un seuil exige une inégalité stricte, mais une observation située exactement sur ce seuil peut avoir une robustesse nulle.

Les choix sont simultanés, à partir du même état. Si un groupe allait se vider, on annule le transfert ambigu de plus petit indice dans ce groupe, en conservant les transferts évidents. On réapprend ensuite avec le garde-fou et on accepte seulement un LG non dégradé. La mémoire identifie aussi les partitions à permutation globale des groupes près. L'aléatoire reste utilisé pour les initialisations et WPB ; **l'affectation par distance d'A2 est déterministe pour un état donné**. L'ancien A2 aléatoire à 1 % est remplacé ; ses éventuels résultats historiques ne décrivent pas cette variante.

## Exécuter soi-même

Installation avec Python 3.14 : `uv sync --locked`. Les commandes sont lancées depuis la racine du dépôt.

```bash
# Une méthode sur un fichier (redémarrages inclus dans les dix secondes).
.venv/bin/jalon2 jalon2/data/type_a/cr06_ca03/n0300_rep50-50_noise00.csv --methodes A1-gmm --graines 0 --temps 10 --temps-appel 0.25 --sortie jalon2/results/simple/essai_a1

# A2 avec affectations par distance MR-Sort, sans tirage des transferts.
.venv/bin/jalon2 jalon2/data/type_a/cr06_ca03/n0300_rep50-50_noise00.csv --methodes A2-gmm --graines 0 --temps 10 --temps-appel 0.25 --sortie jalon2/results/simple/essai_a2_distance

# Prévisualiser le pilote minimal, sans calcul ni création de résultats.
.venv/bin/jalon2 jalon2/data --pilote --graines 0 1 --temps 10 --temps-appel 0.25 --lister

# Comparer deux méthodes sur tous les CSV d'une configuration.
.venv/bin/jalon2 jalon2/data/type_a/cr06_ca03 --methodes A1-uniforme A1-gmm --graines 0 1 2 --temps 30 --temps-appel 1 --sortie jalon2/results/simple/comparaison_a1

# Prévoir les neuf combinaisons A0-A4 sur le pilote.
.venv/bin/jalon2 jalon2/data --pilote --toutes --graines 0 1 --temps 10 --temps-appel 0.25 --lister
```

Les cinq méthodes par défaut sont A0-uniforme, A1-uniforme, A1-GMM, A3-uniforme et A3-GMM. `--toutes` ajoute A2 et A4 avec les deux initialisations. `--methodes` permet de choisir explicitement les combinaisons. Le pilote sélectionne les deux noms `n0300_rep50-50_noise00.csv` et `n1200_rep75-25_noise10.csv` dans chaque configuration.

Le temps global inclut initialisation, apprentissages et redémarrages. La lecture commune des données et l'export sont hors budget. Les arrêts lincs et GMM sont coopératifs : une opération peut dépasser le temps demandé. Le CSV indique le temps réel et le dépassement. Si le premier apprentissage épuise le budget avant le second, le statut sera `sans_solution`.

Une graine unique pilote les tirages de chaque exécution. Pour une même graine et une même initialisation, les méthodes commencent avec les mêmes tirages de partition et d'apprentissage ; leurs tirages divergent ensuite avec leurs opérations. Les résultats sous budget temporel peuvent varier avec la machine et la charge. Les bibliothèques du programme de benchmark sont limitées à un thread.

## Lire les sorties

Le dossier de sortie doit être nouveau pour éviter d'écraser ou mélanger deux expériences. Relancer une expérience nécessite un autre `--sortie` ; il n'y a pas de reprise automatique.

`resultats.csv` contient une ligne par exécution : fichier, méthode, initialisation, graine, dimensions, budgets, temps réel, dépassement, LG, taux d'erreur, tailles des groupes, statut et dossier de détails.

Chaque sous-dossier contient :

- `trace.csv` : temps écoulé, LG courant et meilleur LG rencontré.
- `modele_0.yml` et `modele_1.yml` : les modèles du meilleur état.
- `problem.yml` : le problème dans le format natif de lincs.
- `affectations.csv` : nom, groupe et catégories observée et prédites, avec leurs libellés d'origine.

Un LG vide signifie qu'aucun résultat valide n'est disponible. Les erreurs sont écrites dans la colonne `motif` et affichées. Les lignes terminées sont conservées si tu interromps le programme. Les avertissements de recours GMM ou WPB apparaissent dans le terminal.

Pour choisir une méthode, comparer les mêmes fichiers et budgets sur plusieurs graines, ainsi que les temps réels et les échecs. Les types A/B de même nom partagent leurs performances ; le pilote fait varier plusieurs facteurs ensemble. L'[audit](audit.md) donne les limites d'interprétation. Une fois ton choix fait, la fonction de la méthode retenue pourra servir au code final, avec les mêmes fonctions d'apprentissage et de score. Aucun gagnant n'est fixé dans le programme.

La simplification a d'abord fait l'objet d'une lecture du code et d'une vérification de syntaxe. Le premier essai demandé ensuite compte 40 exécutions valides (cinq fichiers du type A, huit variantes, graine 0, dix secondes nominales), 40 scores confirmés après rechargement et 11 contrôles ciblés de distance A2. Les [lots complets A2 uniforme/GMM sur A et B](../results/simple/a2_72_fichiers_graine0_30s/README.md) sont également terminés : 144 exécutions valides, graine 0, trente secondes nominales. Les évolutions de l'erreur à budget fixé sont enregistrées pour A, B et leur ensemble. Le bilan historique de 38 tests et 120 exécutions appartient à la version de référence. La suite complète des tests unitaires n'a pas été exécutée sur cette branche.

Le budget de dix secondes ne laisse ici aucune perturbation à A4 : ses dix traces ne contiennent que l'initialisation et une amélioration de la première descente A3. Les scores identiques d'A3 et d'A4 sur cet essai ne permettent donc pas de conclure sur l'intérêt des perturbations. Les figures et les limites figurent dans le bilan de l'essai.
