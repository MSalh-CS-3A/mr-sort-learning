# Réévaluation du jalon 3 par rapport à l'énoncé

Date : 3 novembre 2026. Référence : [énoncé du projet](../../docs/sujet.pdf),
page 5, relue avec la page 4 pour le lien au jalon 2. Cette note est une analyse
du travail existant et une recommandation. Elle ne lance aucune campagne et ne
modifie aucune stratégie ni résultat enregistré.

## 1. Ce qui est réellement demandé

Le jalon 3 est annoncé comme optionnel dans le document. Sa première partie
demande un hacker basique dont les données suivent un MR-Sort choisi au hasard,
l'utilisation du travail du jalon 2 pour aider B, et un exemple construit de
cette communication. Sa seconde partie demande de concevoir une stratégie de
brouillage efficace et de montrer son effet sur une instance.

| Demande de l'énoncé | Notre réalisation | Évaluation |
|---|---|---|
| A transmet des objets et leurs catégories ; B reçoit un mélange | Simulateur A/H/B, mélange anonymisé, vérités privées réservées à l'évaluation | Adapté ; un réseau réel ou une simulation en ligne ne sont pas explicitement requis |
| H ajoute au plus une observation par observation de A | N_H <= N_A ; ratios H/A de 0 à 1 | Respecté |
| Hacker basique : un MR-Sort tiré au hasard | `mrsort_aleatoire`, un seul modèle H par répétition, classes vérifiées | Réponse directe à la première partie |
| Utiliser le travail du jalon 2 pour aider B | Inv-2 officiel, puis sélection du modèle par B | Présent ; la règle de sélection est un point central à justifier et évaluer |
| Implémenter un exemple construit | Données, modèles, partitions, métriques et archives disponibles | Réalisé techniquement ; il manque une présentation courte et commentée d'un exemple précis |
| Concevoir une stratégie malicieuse efficace et montrer son effet | Candidats à classes constantes et à performances concentrées, comparés dans le pilote | Matériel disponible ; il faut formuler la cible, le mécanisme et une démonstration claire face à B |

L'énoncé ne fixe pas cinq attaques, cinq défenses, quatre tailles, 30 graines,
10 000 objets de test ou un graphique pour chaque couple. Ces choix viennent de
notre protocole et des échanges, et non des exigences explicites du sujet.
Les 9 600 évaluations envisagées ne sont donc pas un minimum à atteindre.

Le caractère aveugle de H est une contrainte ajoutée explicitement par
l'utilisateur. L'énoncé ne détaille pas ses accès. Cette hypothèse est cohérente
avec le problème et doit être conservée et annoncée, plutôt que présentée comme
une phrase imposée par le sujet.

## 2. Bases méthodologiques à conserver

- Une population de modèles A/H annoncée, avec générateur LINCS et filtre de
  catégories rares documentés. Le filtre conditionne la population ; il ne
  définit pas tous les MR-Sort possibles.
- Des performances tirées selon une distribution explicite, puis des classes
  calculées par le modèle correspondant. L'uniforme est une hypothèse simple,
  pas une représentation universelle de données réelles.
- Aucun accès de H aux observations ou au modèle de A, selon notre hypothèse.
- Aucun accès de B au test, aux origines ou au modèle de A.
- Les mêmes données reçues et le même test pour comparer les défenses.
- Un test indépendant mesurant la fidélité à M_A. Retrouver exactement les poids
  n'est pas le critère approprié : des paramètres différents peuvent avoir les
  mêmes décisions.
- Des témoins sans attaque, des répétitions par modèles/jeux de données et des
  diagnostics de sélection séparés de la décision réelle de B.
- Des archives et audits permettant de vérifier les résultats effectivement
  calculés. L'audit réussi assure la cohérence des artefacts, pas la supériorité
  scientifique d'une stratégie.

La cohérence MR-Sort de H est requise pour la première partie. La seconde partie
autorise des fausses observations sans imposer à nouveau cette cohérence. Les
attaques à classes constantes sont donc des candidats permis, sous les autres
contraintes annoncées. Une stratégie simple peut répondre au sujet ; une
optimisation mathématique du hacker n'est pas explicitement exigée.

## 3. Les problèmes prioritaires

### Séparer l'apprentissage de deux règles et le choix de A

Inv-2 cherche deux modèles et une partition expliquant le mélange. Cet objectif
ne dit pas lequel est authentique. La règle du plus grand groupe utilise la
majorité de A comme indice ; la partition apprise n'est toutefois pas la
provenance véritable. Les observations sur lesquelles les règles sont d'accord
peuvent rejoindre l'un ou l'autre groupe. La règle « mieux expliqué » peut
préférer un groupe H très facile à expliquer, notamment avec une classe
constante. Cohérence interne et authenticité sont deux propriétés différentes.

Les diagnostics utiles sont donc : fidélité du modèle effectivement choisi,
meilleure fidélité parmi les deux candidats (oracle d'évaluation), perte due au
choix, puis reconstruction des deux règles lorsque le modèle H est déclaré.
L'oracle ne doit jamais choisir pour B. La provenance n'est pas toujours
identifiable pour les observations compatibles avec les deux règles ; une
partition imparfaite ne suffit pas à établir que la classification de A est
mauvaise.

### Traiter le cas à parts égales comme une limite précise

Pour `mrsort_aleatoire`, si A et H suivent les mêmes lois et N_A=N_H, échanger
leurs rôles conserve la loi des données observables. Même deux modèles connus
exactement, mais sans provenance, ne permettent pas d'identifier toujours A.
Ce cas mérite une discussion spécifique, plutôt que devenir l'unique preuve
qu'une attaque est efficace contre une défense mal conçue.

Cette symétrie ne s'étend pas automatiquement aux autres attaques : classes
constantes et performances concentrées n'ont pas les mêmes lois que A.
Pour analyser les défaillances algorithmiques en présence d'une majorité A,
les ratios 0,25 et 0,5 sont particulièrement informatifs.

### Examiner le coût de la défense sans attaque

Le calibrage corrigé `calibrage_local_v2` contient cinq graines, N_A=300, et
400 décisions auditées. Ses moyennes sont exploratoires :

| Condition | Naïf | Inv-2, plus grand groupe | Inv-2, mieux expliqué |
|---|---:|---:|---:|
| Sans attaque | 96,90 % | 88,72 % | 86,04 % |
| H MR-Sort aléatoire, H/A=0,5 | 83,41 % | 89,05 % | 72,57 % |
| H classe haute, H/A=0,5 | 88,44 % | 77,03 % | 89,58 % |

Source : `jalon3/results/calibrage_local_v2/resume.csv`. Les comparaisons sont
appariées sur les cinq graines ; ces moyennes ne sont pas des garanties.
Elles montrent un compromis réel : la segmentation aide dans certaines
conditions et dégrade d'autres résultats. Le cas sans attaque révèle le coût
d'imposer deux groupes. Il faut expliquer ce comportement, et éventuellement
étudier une sélection entre un et deux modèles fondée uniquement sur les
données reçues. Le sujet n'impose pas que cette amélioration algorithmique soit
réussie ; une limite correctement montrée et analysée est un résultat utile.

### Comparer les performances avec les ressources correspondantes

Sur H MR-Sort aléatoire à H/A=0,5, les temps moyens sont environ 54,6 s pour
Inv-2 et 4,3 s pour le naïf. On peut comparer ces algorithmes tels que configurés,
en annonçant ce coût. On ne peut pas attribuer tout avantage à la défense en
affirmant une supériorité à budget égal. Le contrôle `naif_multi` à 12 secondes
ne résout pas à lui seul cette différence.

Une étude complémentaire à effort comparable ou une courbe qualité/temps
renforcerait une affirmation de robustesse propre à la méthode. Il faut la
dimensionner selon l'affirmation retenue, sans en faire une nouvelle obligation
de milliers de simulations.

### Rendre la seconde partie intentionnelle

Les familles de brouillage actuelles sont des candidats. Le bruit aléatoire
sert de contrôle ; concentrer les performances au centre est une hypothèse
d'attaque ; aucune de ces appellations ne prouve une efficacité particulière.
Il faut choisir une défense cible, énoncer sa faiblesse, décrire ce que H peut
calculer avec les seules informations autorisées et mesurer le dommage.

Par exemple, les classes constantes peuvent viser la sélection d'un groupe
très bien expliqué, ou perturber la relation entre taille du groupe appris et
nombre de lignes authentiques. C'est une hypothèse mécanistique à vérifier sur
les partitions et les modèles, et non une conclusion fournie par les seules
moyennes. L'exemple `classe_haute` ci-dessus montre déjà l'intérêt de cette
question contre la règle du plus grand groupe.

Choisir une stratégie après examen des cinq graines est du développement.
Elle peut ensuite être évaluée sur de nouvelles graines. Si l'on choisit une
instance déjà observée pour illustrer un mécanisme, il faut la présenter comme
une illustration exploratoire, sans en déduire une performance générale.

## 4. Réponse au jalon recommandée

### Première démonstration : aider B face au hacker basique

Garder six critères, trois classes et N_A=300 pour une première démonstration.
Fixer un exemple reproductible avec H MR-Sort aléatoire. Comparer le modèle
unique naïf à Inv-2 et une règle de sélection explicite, sur les mêmes données.
Présenter les cas H/A=0, 0,25 et 0,5 ; discuter séparément le cas 1.
Montrer les modèles estimés, la règle choisie par B, la fidélité à A et le temps.

### Deuxième démonstration : aider le hacker

Choisir et justifier une attaque, éventuellement parmi les candidats existants,
face à la même défense B. À M_A, données A, budget N_H et test identiques,
comparer absence d'attaque, H basique et attaque proposée. Mesurer son effet
sur B et expliquer le mécanisme avec les diagnostics des candidats/partitions.
L'attaque doit être définie sans accéder à M_A ni au test. Le sujet demande une
instance démonstrative ; un ensemble de nouvelles instances soutient une
affirmation plus générale si l'on souhaite la faire.

### Confirmation ciblée, si nécessaire

Un plan possible après choix de l'attaque et de B :

| Élément | Proposition |
|---|---|
| Dimension | 6 critères, 3 classes |
| Taille A | 300 |
| Attaques | H MR-Sort aléatoire + une attaque conçue |
| Défenses | Naïf + Inv-2 avec sélection fixée |
| Ratios H/A | 0, 0,25, 0,5, 1 |
| Graines | 20 nouvelles, par exemple 1000 à 1019 |
| Test | 10 000 objets indépendants par graine |

Avec les témoins partagés : `20 × 2 × (1 + 2 × 3) = 280` décisions.
Vingt graines est une proposition de confirmation, pas un seuil imposé ni une
garantie de précision. Les modèles, données et choix algorithmiques doivent être
figés avant cette évaluation. Des différences appariées entre graines et des
intervalles de confiance explicitement définis sont préférables pour quantifier
l'incertitude d'une moyenne. Les cinq graines actuelles restent du développement.

Une étude de la taille A, des budgets ou des dimensions vient ensuite seulement
si elle répond à une question supplémentaire. Un deuxième axe N_A n'est pas
nécessaire pour satisfaire les deux démonstrations demandées.

## 5. Présentation proposée pour le rendu

1. Une page : acteurs, objectif, contraintes et informations accessibles.
2. Une démonstration du hacker basique et de l'utilisation du jalon 2 par B.
3. Une stratégie de brouillage expliquée et un exemple de son effet sur B.
4. Quelques résultats comparatifs et diagnostics, avec budgets et incertitudes.
5. Les limites : sélection du modèle authentique, cas symétrique, coût sans
   attaque et portée des distributions testées.

Deux ou trois graphiques centraux peuvent suffire : fidélité à A selon le ratio,
comparaison des attaques contre B, puis qualité des candidats et perte de
sélection. La galerie des 25 couples peut rester en annexe. Les résultats
défavorables à une défense doivent être conservés et expliqués.

## Décision recommandée

Conserver l'infrastructure, les données auditées et les choix de génération.
Recentrer l'analyse sur les deux demandes de la page 5 et expliquer les échecs
de sélection observés. Rédiger les deux démonstrations avant d'étendre le calcul.
La priorité actuelle est la qualité de l'argument et du rendu, et non le nombre
d'affrontements exécutés.
