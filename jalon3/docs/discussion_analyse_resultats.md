# Discussion et plan d'analyse des résultats du jalon 3

Date : 4 novembre 2026. Cette note conserve la discussion avec l'utilisateur,
les résultats vérifiés, les hypothèses et les prochaines analyses proposées.
Elle ne modifie ni les stratégies ni la campagne de confirmation. Les nouvelles
analyses proposées ci-dessous sont exploratoires, après consultation des résultats.

## 1. Périmètre et état du travail

Campagne : `jalon3/results/confirmation_quatre_couples_v1`.

- Six critères croissants, trois catégories ordonnées ; performances uniformes.
- N_A = 300, 500, 1000 ; rho = N_H/N_A = 0, 0,25, 0,5, 1.
- Vingt graines nouvelles, de 1000 à 1019 ; 10 000 objets de test par graine.
- Attaques : MR-Sort aléatoire et classe haute ; témoin sans attaque partagé.
- Décisions de B : naïf et Inv2 avec sélection du plus grand groupe.
- 840 évaluations terminées et auditées, réparties en 60 lots.
- Modèles et tests fixes par graine ; préfixes emboîtés entre tailles/ratios.
- H ne voit ni les observations ni le modèle de A. B ne voit ni les origines,
  ni le test, ni le modèle de A, ni les effectifs séparés A/H.

Les calculs de confirmation sont terminés. Il reste à expliquer les mécanismes
avec les archives, et à présenter des exemples commentés. Aucune nouvelle grande
campagne n'est nécessaire pour formuler les conclusions actuellement défendables.

## 2. Discussion déjà menée et corrections à préserver

L'utilisateur observe une forte efficacité de classe haute, une faiblesse
d'Inv2 face à cette attaque, et des gains modestes d'Inv2 face au hacker aléatoire.
Il souhaite comprendre ces comportements avant de finaliser le rapport.

- Les valeurs 95,9 % de fidélité et 91,2 % de fidélité équilibrée sans attaque
  concernent le naïf avec N_A=300 ; elles ne sont pas universelles.
- Une référence sans attaque n'est pas un plafond théorique : une amélioration
  ponctuelle sous injection n'établit pas une erreur de protocole.
- Les différences de fidélité s'expriment en points de pourcentage ; une baisse
  relative en pour cent est une autre mesure.
- Le ratio 0,75 n'a pas été testé. La dimension étudiée est 6 critères, pas 5.
- rho=1 signifie 50 % de lignes H dans le mélange, pas 100 %.
- Le naïf apprend un seul modèle sur le mélange ; il ne sépare pas A et H.
- Classe haute concentre les étiquettes, pas les performances : X_H reste uniforme.
- Le hacker MR-Sort est tiré au hasard ; ce n'est pas une recherche du modèle
  maximisant le dommage. Sa faiblesse relative ne condamne pas toutes les attaques
  fondées sur un modèle MR-Sort.
- La fidélité ne mesure pas un « biais statistique ». Le naïf n'est pas toujours
  supérieur et Inv2 n'est pas toujours utile : il faut préciser la condition.
- Les figures présentent des bandes +/- un écart-type entre graines ; les IC des
  contrastes sont des bootstrap appariés distincts. Les tailles ne constituent
  pas des répétitions indépendantes supplémentaires.

## 3. Résultats numériques vérifiés

### Sans attaque, naïf

| N_A | Fidélité (%) | Fidélité équilibrée (%) |
|---:|---:|---:|
| 300 | 95,896 | 91,178 |
| 500 | 92,697 | 87,262 |
| 1000 | 93,763 | 87,821 |

### Fidélité globale à rho=1

| N_A | Classe haute / naïf | Classe haute / Inv2 | MR aléatoire / naïf | MR aléatoire / Inv2 |
|---:|---:|---:|---:|---:|
| 300 | 52,312 % | 44,689 % | 68,141 % | 66,393 % |
| 500 | 45,349 % | 35,890 % | 70,418 % | 66,999 % |
| 1000 | 42,923 % | 32,200 % | 64,812 % | 65,075 % |

Le résultat « classe haute est meilleure » signifie ici : plus dommageable,
parmi ces deux attaques, sur ces configurations à forte injection. Il ne désigne
ni une attaque optimale en général, ni un classement établi à tous les ratios.

### Gain Inv2 moins naïf, hacker MR-Sort aléatoire, rho=0,5

| N_A | Gain (points) | IC bootstrap apparié à 95 % |
|---:|---:|---:|
| 300 | +4,44 | [0,65 ; 9,00] |
| 500 | +3,29 | [-0,46 ; 7,32] |
| 1000 | +3,53 | [-0,19 ; 7,42] |

Le premier contraste était principal et fixé avant la confirmation. Les autres
tailles sont complémentaires ; les IC sont individuels, sans correction multiple.

## 4. Origine exacte des 85,5 % : l'oracle des candidats

Pour une graine s, Inv2 produit deux modèles M_0,s et M_1,s. On définit leur
fidélité au test indépendant de A :

    F_s(M) = (1 / n_test) somme_i 1[M(x_i) = M_A(x_i)].

La règle réelle choisit k_s = argmax_k |G_k,s|, puis utilise M_k_s,s.
L'oracle d'évaluation, interdit à B, vaut :

    O_s = max(F_s(M_0,s), F_s(M_1,s)).
    L_s = O_s - F_s(M_k_s,s).
    O_moyen = (1 / 20) somme_s O_s.

C'est le maximum PAR GRAINE, puis la moyenne ; ce n'est ni le maximum des
moyennes des indices 0/1, ni un choix différent pour chaque observation de test.
Les indices 0/1 n'ont pas de signification A/H fixe.

Pour classe haute, N_A=1000, rho=1 : O_moyen=0,855, fidélité réelle=0,321995,
perte moyenne de sélection=0,533005. À la graine 1000, ces valeurs sont
respectivement 0,9474, 0,219 et 0,7284.

Sources : `resultats.csv`, colonnes `fidelite_oracle_a`, `fidelite`,
`perte_selection` ; calcul dans `jalon3/simulation.py`, fonction `evaluer`.
La moyenne des vingt lignes correspondantes a été recalculée directement.

Interprétation : un meilleur candidat existe souvent déjà, mais il est écarté.
L'oracle ne constitue pas une défense déployable, une estimation indépendante
d'un nouveau sélecteur, ou la preuve d'une partition exacte des provenances.

## 5. Question 1 : pourquoi une étiquette haute sur des performances uniformes ?

L'utilisateur demande une explication des fidélités par classe ET du mécanisme
par lequel y_H=2 pour tout X_H uniforme déstabilise l'apprentissage.

### Identités pour lire les métriques

Pour c=0,1,2, p_c est la fréquence réelle de la classe c au test, et R_c son rappel :

    F_globale = somme_c p_c R_c.
    F_equilibree = (R_0 + R_1 + R_2) / 3.

Si un modèle prédit toujours la classe haute, sa fidélité globale vaut p_2 et sa
fidélité équilibrée vaut 1/3, lorsque les trois classes sont présentes.
Ce repère ne prouve pas que les modèles appris sont tous constants.

### Effet sur le problème d'apprentissage : raisonnement de population

Sous les hypothèses actuelles (mêmes performances uniformes pour A et H,
étiquettes A déterministes, mélange au ratio rho), pour une performance x :

    P(Y=c | X=x) = [1{M_A(x)=c} + rho * 1{c=2}] / (1+rho).

Dans les régions où M_A(x) n'est pas 2, les étiquettes authentique et haute
entrent en compétition. Dans la région où M_A(x)=2, les deux sources concordent.
L'attaque introduit ainsi des étiquettes hautes aussi pour des performances que A
classe bas ou au milieu. Elle peut favoriser des frontières/profils plus permissifs
pour la classe haute. Ce déplacement doit être vérifié sur les modèles sauvegardés.

Important : pour rho<1, l'étiquette A reste la plus probable à chaque x. Ainsi,
à la population, minimiser exactement l'erreur de classification ne contraint pas
à dégrader A. Pour les deux règles particulières A et « toujours haut », les
erreurs sur le mélange valent respectivement :

    risque(A) = rho * (1-p_2) / (1+rho),
    risque(toujours haut) = (1-p_2) / (1+rho).

Elles sont égales à rho=1. Pour rho<1, A est préférable à cette règle constante.
Les échecs observés avant rho=1 doivent donc aussi être reliés à l'échantillonnage,
à l'optimisation et/ou à la segmentation et à la sélection. L'attaque seule ne
prouve pas une impossibilité théorique de retrouver A à tous les ratios.

### Analyses prévues

1. Rappels R_0,R_1,R_2 et fréquences p_c par graine, défense, taille et ratio.
2. Matrices de confusion normalisées par vraie catégorie et fréquence prédite
   de la classe haute, calculées depuis les modèles et tests archivés.
3. Comparaison appariée avec le témoin, puis avec le MR-Sort aléatoire.
4. Lecture des profils/poids/seuils et des prédictions sur un même diagnostic.
   Ne pas attribuer tout changement à un seuil unique : les paramètres peuvent
   varier conjointement et plusieurs paramètres peuvent représenter la même règle.

Livrable : figures des rappels, matrices de confusion et explication séparant
observations et hypothèses. Pas de réentraînement de la campagne.

## 6. Question 2 : groupes, ambiguïté et futur critère de sélection

Il faut distinguer les catégories basse/moyenne/haute des deux groupes appris.
On nommera ces derniers G_0,G_1, ou G_grand,G_petit selon leur taille ; aucun
indice ne représente automatiquement A, H, une classe haute ou une classe basse.

Pour chaque groupe :

    |G_k| = n_A,k + n_H,k.

Cette égalité emploie la provenance connue de l'évaluateur, pas de B. Même si
N_A >= N_H, on ne peut pas en déduire que le groupe le plus grand représente A.

### Construction illustrative à vérifier dans les archives

Un modèle constant haut peut expliquer toutes les lignes H et les n_A,2 lignes
de A déjà classées haut. Une partition cohérente possible est alors :

    |G_haut| = N_H + n_A,2,
    |G_autre| = N_A - n_A,2.

Le groupe haut est plus grand si :

    rho + 2 * (n_A,2 / N_A) > 1.

Par exemple, à rho=0,5, cela se produit si plus de 25 % des lignes A sont hautes.
À rho=1, il suffit d'une proportion strictement positive. C'est une construction
possible avec des modèles compatibles, pas une description déjà vérifiée des
partitions apprises. Les contraintes de taille minimale et l'heuristique peuvent
produire d'autres partitions ; des lignes H compatibles avec A peuvent aussi
rejoindre l'autre groupe.

### Diagnostics puis pistes, sans fuite d'information

- Mesurer, par groupe, les effectifs A/H, les étiquettes, la qualité des candidats,
  les erreurs d'ajustement et le choix réel ; tracer O_s, F_s et L_s.
- Distinguer échec des candidats, échec de sélection et combinaison des deux.
- Examiner des quantités calculables par B : taille, diversité des étiquettes,
  stabilité du candidat, couverture des catégories sur des performances publiques
  générées indépendamment. Une faible diversité ne suffit pas à déclarer un groupe
  malveillant : des préférences authentiques peuvent aussi produire une classe fréquente.
- Tenir compte du fait que le générateur de A exclut les modèles quasi constants :
  une couverture des catégories peut fournir un indice sous CE prior public,
  pas une règle universelle d'authenticité. Le contrôle doit employer de nouveaux
  points publics, jamais le test privé de A.
- Un nouveau sélecteur conçu sur ces résultats devra être développé sur des
  données de développement puis évalué sur de nouvelles graines réservées.
  Réutiliser les graines 1000..1019 pour prétendre confirmer ce sélecteur serait
  une sélection après observation. Aucun nouveau sélecteur n'est validé à ce stade.

## 7. Question 3 : temps, espace des critères et dominance

Les temps sont déjà sauvegardés dans `resultats.csv` et agrégés dans `resume.csv` :
`temps`, `temps_preparation`, `temps_selection`, `temps_calcul_effectif`.
`temps` est une durée murale de décision mesurée, pas un temps CPU ni le temps
de toute la campagne. L'évaluation et l'archivage sont hors du chronomètre de
décision ; les méthodes conservent leurs propres arrêts. Si une préparation est
partagée, chaque défense est créditée de son coût complet pour la comparaison ;
`temps_calcul_effectif` sert à éviter le double comptage du travail exécuté.

Proposition principale : espace 2D (temps à minimiser, fidélité globale à maximiser).
Complément : espace 3D (temps à minimiser, fidélité globale et équilibrée à maximiser).
Ce sont des espaces de critères, pas une PCA ni une projection des six critères
des alternatives MR-Sort. L'espace 2D est à privilégier pour la lecture ; la 3D
ne sera utile que si elle révèle un compromis absent des deux vues 2D.

Pour une attaque, un N_A et un rho fixés, D_1 domine D_2 si :

    temps(D_1) <= temps(D_2),
    F(D_1) >= F(D_2),
    et au moins une inégalité est stricte.

En 3D, ajouter F_equilibree(D_1) >= F_equilibree(D_2).
Une dominance calculée sur les moyennes est descriptive : compléter par les
différences appariées, leur incertitude et les fréquences de dominance par graine.
Avec seulement deux défenses, la frontière contiendra un ou deux points par
condition. Les ratios peuvent être reliés pour montrer des trajectoires.

Ne pas calculer une frontière globale mélangeant toutes les attaques et tailles :
les méthodes seraient comparées sur des difficultés différentes. Ne pas comparer
attaque et défense comme si elles optimisaient le même objectif. Pour comparer
les attaques, fixer la défense, le ratio et N_A ; minimiser la fidélité de B ou
maximiser sa perte. Le temps mesuré ici est celui de B, pas le coût de création
de l'attaque, et ne permet pas d'affirmer la dominance en coût du hacker.

Exemples vérifiés dans `resume.csv`, pour N_A=300 (moyennes sur vingt graines) :

| Condition | Décision | Temps (s) | Fidélité (%) | Fidélité équilibrée (%) |
|---|---|---:|---:|---:|
| Sans attaque | Naïf | 3,69 | 95,90 | 91,18 |
| Sans attaque | Inv2 | 20,90 | 91,32 | 86,37 |
| MR aléatoire, rho=0,5 | Naïf | 4,79 | 86,22 | 81,21 |
| MR aléatoire, rho=0,5 | Inv2 | 55,73 | 90,66 | 82,49 |
| Classe haute, rho=1 | Naïf | 4,70 | 52,31 | 52,02 |
| Classe haute, rho=1 | Inv2 | 56,98 | 44,69 | 48,70 |

Sur ces moyennes, le naïf domine Inv2 en 2D et en 3D dans le témoin et dans
le dernier scénario. Face au MR aléatoire à rho=0,5, les deux sont non dominés :
Inv2 offre une meilleure fidélité mais demande davantage de temps. Il faut
conserver l'incertitude et l'appariement dans la présentation finale.

## 8. Ordre de travail retenu pour la suite

1. Conserver cette discussion et la provenance des nombres : présente note.
2. Post-traiter les rappels et confusions pour comprendre classe haute et le naïf.
3. Analyser les groupes/candidats pour expliquer Inv2 et vérifier la construction.
4. Mettre les fidélités en regard des temps, par condition comparable, et étudier
   les dominances descriptives ainsi que les incertitudes.
5. Choisir des exemples illustratifs explicitement présentés comme tels ; finaliser
   le rapport en distinguant résultats confirmatoires, diagnostics exploratoires
   et éventuelles pistes de nouveaux sélecteurs.

Le protocole de génération et d'évaluation reste conservé. L'objectif immédiat
est l'explication des résultats existants, pas l'ajout systématique d'attaques,
de dimensions, de ratios ou d'une nouvelle grande campagne.

## 9. Sources locales

- `jalon3/results/confirmation_quatre_couples_v1/resultats.csv`
- `jalon3/results/confirmation_quatre_couples_v1/resume.csv`
- `jalon3/results/confirmation_quatre_couples_v1/comparaisons_confirmation.md`
- `jalon3/results/confirmation_quatre_couples_v1/audit_campagne.json`
- `jalon3/results/confirmation_quatre_couples_v1/lots/` : modèles, données, partitions.
- `jalon3/simulation.py` : évaluation et chronométrage des décisions.
- `jalon3/defenses/reference.py` : règle de sélection du plus grand groupe.
- `jalon3/docs/confirmation_quatre_couples.md` : plan fixé avant confirmation.
- `jalon3/docs/reevaluation_methodologique.md` : lien à l'énoncé du jalon.

## 10. Analyses réalisées le 4 novembre après accord de l'utilisateur

Les trois axes ont maintenant été post-traités, sans nouvel apprentissage :
[analyse complète](../results/analyse_approfondie_confirmation_v1/analyse.md).
Le module reproductible est `jalon3/analyse_approfondie.py`.

- 840 décisions recalculées, 840 candidats rechargés pour 420 paires ; confusions,
  rappels, composition des groupes et comptabilité des temps vérifiés.
- Neuf figures PNG/SVG et neuf tableaux CSV ; la campagne source est conservée.
- Classe haute, N_A=1000, rho=1 : rappels bas/moyen/haut d'Inv2 =
  4,50 / 4,94 / 99,80 %, avec 96,36 % de prédictions hautes.
- Le modèle prédisant le plus souvent haut est choisi dans 19 graines sur 20 ;
  son groupe contient en moyenne 93,71 % des H et 86,92 % des A déjà hauts.
  La construction explicative est donc compatible avec les partitions observées.
- L'exemple de la graine 1007 rend visibles des groupes de 1057 et 943 lignes,
  avec des fidélités respectives de 6,26 et 94,49 % ; le mauvais groupe est choisi.
- Deux critères publics ont été examinés rétrospectivement sur les candidats
  existants : couverture minimale des trois catégories et entropie maximale.
  L'entropie corrige les choix dans les vingt cas classe haute/N_A=1000/rho=1
  (85,50 %), mais fait perdre 22,18 points sur MR aléatoire/N_A=1000/rho=0,5.
  Aucun nouveau sélecteur n'est donc déclaré validé ou supérieur en général.
- Sur les moyennes des 21 conditions, le naïf domine dans 13 conditions en 2D
  et en 3D ; les huit autres présentent des compromis. Ces comptes décrivent
  la grille et ne sont pas des probabilités universelles de supériorité.
- Le temps est celui de la construction du modèle de B, pas la latence de
  classification, le coût du hacker, ou le temps de calcul de toute la campagne.

Les IC et sélecteurs additionnels sont exploratoires. Les contrastes principaux
restent ceux du plan confirmatoire. Les hypothèses et pistes de la note initiale
ci-dessus sont conservées pour tracer la progression de la discussion ; pour
les conclusions actualisées, consulter l'analyse complète.

## 11. Recherche d'un compromis de sélection après cette analyse

L'utilisateur demande de chercher un critère améliorant le compromis entre les
deux attaques. Une [recherche documentée](recherche_critere_selection.md) propose
le score accord sur le mélange entier + lambda fois l'entropie publique.
Le réglage sur cinq anciennes graines retient lambda=0,2 ; le transfert sur les
vingt graines déjà connues est prometteur (17 moyennes améliorées, deux égales,
deux légèrement dégradées), mais ne constitue pas une confirmation indépendante.

La défense `inv2_hybride_experimental` est ajoutée sans remplacer les références.
44 tests passent et ses 420 décisions rejouées concordent avec le prototype.
Les [résultats et la proposition de validation](../results/recherche_selection_v1/proposition.md)
sont conservés. La prochaine confirmation indépendante reste à exécuter avec
coefficient fixé et objectifs de succès annoncés ; aucune nouvelle campagne
longue n'a été lancée dans ce travail de recherche.
