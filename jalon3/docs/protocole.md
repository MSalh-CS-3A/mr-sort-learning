# Protocole expérimental commun — uniforme-v1

## Objectif et périmètre

Mesurer la capacité de B à reproduire les décisions du modèle MR-Sort authentique M_A lorsque H injecte des observations cohérentes avec un second modèle M_H. Le premier couple est `mrsort_aleatoire` / `naif`. B travaille hors ligne et apprend un unique MR-Sort sur tout le mélange. Ce document fixe les choix de cette campagne avant son exécution. Une modification de la distribution de A ou du test, ou du générateur de modèles, constitue une autre version du protocole. Les lois propres aux nouvelles attaques et les défenses supplémentaires sont définies séparément dans l'[extension strategies-v1](comparaisons.md), en conservant les données A et tests de référence.

L'unité de répétition indépendante est la graine. Les observations de test ne sont pas des répétitions indépendantes de l'expérience d'apprentissage. Les tailles et ratios associés à une même graine sont appariés.

## Informations accessibles aux acteurs

| Acteur | Informations reçues | Informations cachées |
|---|---|---|
| A | Ses observations authentiques, qu'il transmet sans traitement | Données et modèle de H |
| H | Problème public (critères, directions, bornes, catégories), plafond N_H, générateur aléatoire | M_A, performances et classes de A, test et diagnostic |
| B | Mélange anonymisé, problème public, graine d'apprentissage et budget de calcul | Provenance des lignes, M_A, M_H, test, diagnostic, N_A et N_H séparément, ratio exact |
| Simulateur | Toutes les vérités de référence | Aucune ; ses informations privées ne sont pas transmises aux stratégies |

B connaît la contrainte publique N_H <= N_A. H utilise le plafond qui lui est communiqué sans recevoir les données de A. Le contrat `Vue.donnees_a` vaut `None` pour cette attaque. Le mécanisme optionnel `voit_donnees_a=True` est réservé à une autre hypothèse, à déclarer explicitement ; il n'est pas utilisé dans cette campagne.

Ce contrat sépare les arguments des fonctions ; il ne constitue pas une sandbox de sécurité contre un code qui lirait volontairement les fichiers du simulateur. Les stratégies doivent respecter les informations autorisées et ne pas exploiter les graines pour reconstruire les vérités cachées.

## 1. Problème public et génération des modèles

La campagne initiale utilise 6 critères réels croissants sur [0,1] et 3 catégories ordonnées (indices 0, 1, 2). Le nombre de catégories est distinct du nombre de sources, toujours deux en présence de H.

M_A et M_H sont deux tirages indépendants du même générateur `lc.generate_mrsort_model` de LINCS **2.0.2**, avec des flux pseudo-aléatoires distincts. Nous ne postulons ni une loi uniforme sur tous les MR-Sort, ni une loi Dirichlet sur les poids. La version et les réglages du générateur font partie de la définition expérimentale de la population étudiée.

LINCS représente la majorité par un seuil fixé à 1 et des poids de somme S >= 1. La représentation normalisée équivalente est w'_j = w_j/S et lambda' = 1/S. Elle conserve les décisions ; elle ne signifie pas que lambda' est uniforme dans [0,5 ; 1]. Les seuils des profils sont ordonnés pour chaque critère.

Source : [génération des modèles LINCS](https://mics-lab.github.io/lincs/user-guide.html#generating-a-model).

### Filtre symétrique des catégories rares

Pour chaque modèle candidat, les proportions des catégories sont estimées sur 2 000 performances uniformes de contrôle. Chaque catégorie doit représenter au moins 0,5 % de ce contrôle (au moins 10 objets). Sinon, un autre modèle est tiré, avec au maximum 100 essais. Le même mécanisme s'applique à A et H, indépendamment.

Les points de contrôle sont indépendants des données d'apprentissage, du test et du diagnostic. Ils sont communs aux candidats successifs d'un même tirage de modèle, afin de conserver le mécanisme déjà utilisé. Ce filtre définit une population conditionnée et demeure estimatif : il ne garantit pas une probabilité réelle supérieure à 0,5 %, ni la présence de toutes les catégories dans un petit apprentissage. Nous ne rééquilibrons pas ensuite les données.

H ne sélectionne jamais son modèle selon son désaccord avec M_A. Aucune répétition n'est retirée selon la fidélité obtenue.

## 2. Distribution des performances et attribution des classes

Pour A, H, le test et le diagnostic, les composantes des performances sont indépendantes et uniformes sur les bornes publiques : X_j ~ U([0,1]). Les flux de ces quatre jeux sont distincts.

Les classes ne sont pas tirées au hasard :

- A : Y_A = M_A(X_A) ;
- H : Y_H = M_H(X_H) ;
- test : Y_test = M_A(X_test).

**Cohérent** signifie qu'un unique M_H valide explique exactement toutes les étiquettes injectées pendant une répétition : aucun bruit de classe, aucun changement de modèle entre ratios ou tailles. Cela n'impose pas l'équilibre des classes, l'accord avec A ou une attaque efficace. Le simulateur vérifie les étiquettes lorsqu'un modèle H est déclaré.

Le générateur équilibré historique (`max_imbalance=0.2`) n'est plus utilisé pour ces observations. Il contraignait chaque effectif à ±20 % de l'équilibre parfait et modifiait la distribution marginale des performances. Cette différence rend les anciennes expériences non directement comparables aux nouvelles.

Source : [génération des observations LINCS](https://mics-lab.github.io/lincs/user-guide.html#generating-alternatives).

## 3. Plan factoriel et appariement

| Paramètre | Campagne initiale |
|---|---|
| Dimension | 6 critères, 3 catégories |
| N_A | 100, 300, 500, 1 000 |
| rho = N_H / N_A demandé | 0, 0.25, 0.5, 1 |
| Graines | 0 à 29 : 30 répétitions indépendantes |
| Test uniforme | 10 000 objets par graine |
| Diagnostic uniforme | 10 000 autres objets par graine |
| Attaque | `mrsort_aleatoire`, aveugle |
| Défense | `naif`, apprentissage sur tout le mélange |

Le plan représente 4 x 4 x 30 = **480 apprentissages**, dont 120 sans attaque. N_H = round(rho * N_A), avec l'arrondi Python au pair en cas de demi-entier. Les valeurs de cette campagne sont toutes entières avant arrondi. Pour les futures attaques pouvant utiliser moins que leur plafond, `nombre_h` donne l'effectif réellement injecté ; le ratio demandé doit être distingué du ratio réalisé.

rho est le rapport H/A, pas la fraction de H dans le mélange. La fraction malveillante vaut rho/(1+rho) lorsque tout le budget est utilisé : rho=1 correspond à 50 % des lignes reçues.

Pour chaque graine :

1. Générer une fois M_A, le test, le diagnostic et le plus grand jeu A.
2. Tirer le même M_H pour tous les budgets du hacker de référence.
3. Utiliser les préfixes des jeux A et H pour construire les petites tailles. Deux conditions avec le même N_H ont exactement les mêmes observations H.
4. Mélanger A et H ; supprimer la provenance et attribuer des noms neutres avant de présenter les données à B.
5. Présenter exactement le même mélange à toutes les défenses sélectionnées.
6. Évaluer B sur le test caché et enregistrer le résultat.

Les graines dérivées utilisent les identifiants de rôle, dimensions et stratégie, et CRC32 (pas `hash()` de Python). Les flux A, H, test et diagnostic sont séparés. Le ratio et N_A ne participent pas à la graine du modèle H. Changer la taille du test ne change pas M_A ni l'apprentissage.

La garantie d'emboîtement des injections vaut pour les deux hackers de référence. Une stratégie future peut adapter sa construction au budget : elle doit documenter si ses données sont emboîtées et si son modèle reste fixe. La pipeline ne tronque pas arbitrairement une attaque adaptative.

La référence rho=0 est calculée une seule fois par graine, taille et défense, puis réutilisée dans les figures des différentes attaques. Elle est toujours incluse, même si `--ratios` ne mentionne que des ratios positifs.

## 4. Apprentissage sans défense et ressources

`naif` appelle directement `learn` du jalon 2 officiel. Il apprend un seul MR-Sort sans filtrage, segmentation, sélection à partir du test, ni connaissance de la provenance.

Réglages conservés : population de 9 modèles WPB, optimisation des poids GLOP, amélioration des profils sur CPU, arrêt lorsque tous les objets sont expliqués, après 10 itérations sans progrès ou au seuil de temps interne nominal de 4 secondes. Ce seuil ne plafonne pas strictement la durée totale observée : les temps réels de la campagne sont conservés dans les CSV. Un thread numérique par processus ; la campagne peut répartir les graines entre plusieurs processus indépendants. Le nombre de processus est enregistré.

Le paramètre `--temps` est communiqué aux stratégies, mais `naif` et les défenses officielles `inv2_*` conservent leurs arrêts propres. Il ne faut pas présenter `--temps` comme un plafond effectivement imposé à ces stratégies.

La graine et les données sont reproductibles. Un arrêt en temps réel peut modifier le nombre d'itérations et le modèle appris selon la charge machine. Les durées réelles et l'environnement sont donc archivés. À budget fixe, augmenter N_A augmente aussi le travail d'apprentissage : une baisse de fidélité peut provenir du calcul disponible autant que des données. Une étude ultérieure de sensibilité au budget serait nécessaire pour isoler cet effet.

## 5. Mesures et règles d'analyse

### Fidélité principale

Acc_A = moyenne sur le test uniforme de 1{M_B(X) = M_A(X)}. On mesure une fidélité de prédiction, pas l'égalité des poids ou frontières : plusieurs paramétrages peuvent produire les mêmes décisions.

### Dégradation appariée

Delta_attaque(s, N_A, rho, H, B) = Acc_A(s, N_A, 0, B) - Acc_A(s, N_A, rho, H, B).

Les différences sont calculées **avant** de moyenner les graines, avec la même taille et la même défense. Une valeur positive indique une perte ; une valeur négative indique une amélioration. Si la référence a échoué, la différence reste vide. On ne remplace pas une erreur par zéro.

### Fidélité équilibrée et catégories rares

Calculer le rappel de chaque catégorie de M_A, puis leur moyenne non pondérée. Sauvegarder les effectifs du test et chaque rappel dans les CSV. Si une catégorie manque au test, la fidélité équilibrée reste vide ; elle n'est pas calculée en supprimant silencieusement cette catégorie. Les nombres de valeurs disponibles figurent dans le résumé.

Sauvegarder aussi la fréquence de la catégorie majoritaire de M_A sur le test, pour contextualiser une fidélité globale élevée. Avec une classe de probabilité 0,5 %, 10 000 objets n'en donnent qu'environ 50 en moyenne. Le protocole initial ne contient pas de test stratifié complémentaire : celui-ci sera une analyse séparée, explicitement étiquetée, si nécessaire.

### Désaccord des modèles, caché aux stratégies

D = moyenne sur le diagnostic uniforme indépendant de 1{M_A(X) != M_H(X)}.

Le désaccord est mesuré après les tirages ; il ne guide ni H ni le filtrage. Il est commun aux tailles et ratios d'une graine pour le hacker cohérent. Les valeurs peuvent être associées aux dégradations de façon descriptive ; les multiples points de la même graine restent dépendants.

### Détection et séparation

`detection_h` est le rappel des lignes de H signalées comme suspectes. `rejet_a` est la fraction de lignes de A signalées à tort. Elles restent vides pour `naif`, qui ne désigne aucun suspect.

`naif` ne renvoie qu'un modèle : la reconstruction de deux règles et l'évaluation à permutation près sont **non applicables** au premier couple. Une future défense à deux modèles devra renvoyer les éléments nécessaires à ce diagnostic. Un alignement utilisant la vérité du simulateur ne devra jamais servir au choix effectué par B.

### Symétrie à parts égales

À rho=1, même loi de modèles et même loi de performances, les rôles A/H sont symétriques. Retrouver les deux règles ne suffit pas à identifier laquelle appartient à A. De plus, une observation sur laquelle les deux règles sont d'accord ne révèle pas sa provenance, même si les règles sont parfaitement connues.

Cela ne signifie pas une fidélité plafonnée à 50 %. Dans le cas idéal où les deux règles sont connues sans provenance, choisir l'une au hasard donne en moyenne 1-D/2 de fidélité à A. Pour rho<1, la majorité des sources est un indice potentiel, sans garantie que la partition apprise reconstruise les sources.

## 6. Graphiques et statistiques

Une figure par couple (attaque, défense) et par dimension, exportée en PNG et SVG :

1. Fidélité au test en fonction de rho ; une courbe par N_A.
2. Dégradation appariée en fonction de rho ; une courbe par N_A.
3. Fidélité équilibrée en fonction de rho.
4. Nuage descriptif désaccord / dégradation, coloré par ratio.

Courbes : moyenne sur les graines réussies ; bandes : ± un écart-type échantillonnal (ddof=1), limité à [0,100] pour les fidélités. Ce ne sont ni des intervalles de confiance, ni une incertitude liée seulement au nombre d'objets de test. Une seule graine donne un point sans bande. Les échecs et les effectifs disponibles sont explicités dans le CSV de synthèse et le bilan.

Aucune monotonie n'est imposée, aucun modèle n'est sélectionné après examen des courbes et aucun test de significativité n'est calculé en traitant les 480 cellules comme indépendantes.

## 7. Validation et artefacts

Avant la campagne : contrats des stratégies, emboîtement A/H, invariance des modèles et du test, cohérence de toutes les étiquettes H, restriction de la vue H, calcul manuel des métriques et appariement avec échecs. Puis essai réel de bout en bout sur deux graines, deux tailles et trois ratios, génération des figures et inspection visuelle.

Chaque exécution crée un nouveau dossier :

- `configuration.json` : plan, version du protocole, environnement, réglages, commit et empreintes SHA256 des sources ;
- `sources/` : copie du code, documentation et verrou de dépendances utilisés ;
- `instances/6x3/graine_NNN/` : problème, modèle A, données A maximales, test, diagnostic et journal progressif des parties ;
- sous chaque condition : injection H, provenance du mélange pour audit, modèle H et modèle B sérialisables ;
- `resultats.csv` : résultats bruts, par lots de graines terminées ; les journaux `parties.csv` sont écrits après chaque apprentissage ;
- `resultats_apparies.csv` : résultats et dégradations calculées par graine ;
- `resume.csv` : effectifs, erreurs, moyennes et écarts-types par dimension, taille, ratio, attaque et défense ;
- `figures/` et `bilan.md` : figures et bilan descriptif.

La copie des modèles B est prise en charge pour les MR-Sort du jalon 2 et les modèles LINCS. Une stratégie à objet `predict()` personnalisé reste évaluable, mais doit fournir son propre mécanisme de sauvegarde si nécessaire.

## Commandes de reproduction

Depuis la racine du dépôt :

```bash
# Vérifications scientifiques et contrats.
.venv/bin/python -m unittest discover -v -s jalon3/tests

# Vérification du plan sans exécution.
.venv/bin/python -m jalon3 --hackers mrsort_aleatoire --defenses naif --dimensions 6x3 --tailles 100 300 500 1000 --ratios 0 0.25 0.5 1 --graines {0..29} --lister

# Campagne initiale : 480 apprentissages, trois processus.
.venv/bin/python -m jalon3 --hackers mrsort_aleatoire --defenses naif --dimensions 6x3 --tailles 100 300 500 1000 --ratios 0 0.25 0.5 1 --graines {0..29} --taille-test 10000 --processus 3 --sortie jalon3/results/mrsort_naif_uniforme_v1

# Recalculer les graphiques et le bilan depuis les résultats, sans apprentissage.
.venv/bin/python -m jalon3.analyse jalon3/results/mrsort_naif_uniforme_v1

# Audit du premier couple : recharge les modèles A/H/B et recalcule les mesures.
.venv/bin/python -m jalon3.validation_resultats jalon3/results/mrsort_naif_uniforme_v1
```

Le dossier de sortie doit être nouveau pour une campagne. Pour reproduire un résultat après des modifications, utiliser la copie `sources/` et ses dépendances verrouillées. Le partage de jeux de données exige la même version de protocole et les mêmes graines ; les résultats historiques équilibrés ne doivent pas être agrégés avec `uniforme-v1`.
