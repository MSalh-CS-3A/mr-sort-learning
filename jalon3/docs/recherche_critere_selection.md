# Recherche d'un critère de sélection pour Inv2

4 novembre 2026. Travail de développement, après examen des vingt graines de
confirmation. Aucune amélioration sur ces vingt graines ne sera présentée comme
une nouvelle confirmation indépendante. Les stratégies existantes sont conservées.

## Motivations et recherches

La taille d'un groupe dépend de l'affectation des observations compatibles avec
les deux modèles. La diversité seule échoue quand le hacker MR-Sort possède une
distribution de catégories plus équilibrée que celle de A.

Une première exploration des archives indique que l'erreur sur le mélange ENTIER
(différente de l'erreur sur le groupe propre) aide notamment aux ratios
intermédiaires. Elle ne suffit pas à rejeter un candidat presque constant à
parts égales. Les seuils de quasi-constance simples ne donnent pas de règle
uniformément satisfaisante et ne sont pas retenus comme résultat validé.

Les travaux sur la décontamination soulignent le rôle des hypothèses
d'identifiabilité ; ils ne garantissent pas le fonctionnement de notre heuristique :
[Scott et al., 2013](https://proceedings.mlr.press/v30/Scott13.html),
[Katz-Samuels et al., 2019](https://jmlr.org/papers/v20/17-576.html).
Un petit échantillon authentifié peut lever une ambiguïté de provenance, mais
constitue un protocole différent :
[Charikar et al., 2017](https://arxiv.org/abs/1611.02315).

## Critère proposé : accord sur le mélange + diversité faiblement pondérée

Pour les candidats M_0,M_1 :

    A_k = moyenne_i 1{M_k(x_i)=y_i} sur le mélange reçu,
    H_k = - somme_c q_k,c log(q_k,c) / log(C),
    S_k = A_k + lambda H_k ; choix = argmax_k S_k.

q_k,c est estimé sur 10 000 points publics uniformes nouvellement générés,
sans catégorie authentique. La diversité est un indice faiblement pondéré,
pas une preuve d'authenticité. À égalité de scores, conserver le plus grand groupe.

Les différences A_0-A_1 proviennent uniquement des observations sur lesquelles
les deux modèles divergent : les accords s'annulent. Pour des modèles exacts,
des performances de même loi et une proportion authentique alpha>1/2 :

    E[A_A-A_H] = (2 alpha - 1) * D,

où D est leur désaccord. C'est une justification de population. Pour des modèles
appris sur les mêmes données, les accords d'apprentissage sont optimistes et ne
donnent pas des garanties ni des IC binomiaux valides de provenance.

## Règle de développement fixée avant d'examiner les scores hybrides

Développement numérique : cinq graines 100..104 du calibrage corrigé v2,
N_A=300, attaques classe haute et MR aléatoire, ratios 0,25/0,5/1, plus le témoin
partagé. Trente-cinq paires de candidats archivés, sans réapprentissage.

- Grille lambda fixée : 0 ; 0,02 ; 0,05 ; 0,1 ; 0,2.
- Exclure une valeur si son gain moyen de fidélité par rapport au plus grand
  groupe est inférieur à -1 point dans l'une des conditions témoin, MR aléatoire
  à 0,25 ou MR aléatoire à 0,5. C'est une contrainte de développement, pas une garantie.
- Parmi les valeurs admissibles, maximiser la fidélité moyenne en pondérant
  également les sept conditions ; en cas d'égalité, choisir le plus petit lambda.
- Si aucune valeur n'est admissible, ne pas déclarer de règle retenue.
- Figer cette valeur, puis examiner les vingt graines 1000..1019 uniquement
  comme une étude rétrospective de transfert. Ces graines sont déjà connues.
- Présenter toutes les conditions, les cas défavorables et les incertitudes,
  sans retoucher lambda après consultation.

La fidélité au test de A peut être utilisée par l'expérimentateur pour régler
lambda sur le développement. Une fois lambda fixé, le critère B ne reçoit ni
ces catégories, ni le test, ni le ratio, ni le nom de l'attaque.

## Validation nécessaire avant de parler d'amélioration confirmée

Les candidats actuels ont été appris sur le mélange complet. L'exploration
réutilise ces candidats et ne mesure pas le temps d'apprentissage d'une nouvelle
défense. Une validation future doit fixer la règle puis employer de nouvelles
graines jamais consultées, sur les deux attaques et le témoin, avec temps réels.
Une validation sur un sous-échantillon du mélange doit séparer celui-ci AVANT
l'apprentissage des candidats ; découper après apprentissage ne suffit pas.

À rho=1 et mêmes lois pour A et H aléatoire, aucune règle fondée seulement sur
le mélange ne peut garantir d'identifier A. L'ajout de quelques exemples vérifiés
ou d'une requête authentifiée à A est une autre piste, explicitement hors du
protocole actuel. En leur absence, une décision peut être accompagnée d'un signal
d'ambiguïté plutôt que d'une certitude artificielle.

## Résultat du développement et état de l'implémentation

La règle de réglage ci-dessus a retenu lambda=0,2 parmi les cinq valeurs
admissibles. La grille n'a pas été élargie après le transfert. Le prototype puis
la défense exécutable `inv2_hybride_experimental` ont été évalués par rejeu des
candidats existants, sans modifier les stratégies de référence.

Sur les vingt graines déjà analysées, les moyennes s'améliorent dans 17 des
21 conditions, sont identiques dans deux et diminuent légèrement dans deux.
Pour N_A=1000 : classe haute/rho=1 passe de 32,20 à 67,99 % ; MR aléatoire/rho=0,5
reste à 88,22 %. L'oracle n'est pas atteint partout, le coût sans attaque à
N_A=300 n'est pas supprimé, et le transfert reste rétrospectif.

[Proposition complète, tous les résultats et limites](../results/recherche_selection_v1/proposition.md).
Les 44 tests passent. Le rejeu de la défense sur 420 paires retrouve tous les
choix et fidélités du prototype. Le nouveau choix seul prend environ 2,6 ms en
moyenne sur ces candidats chargés ; ce n'est pas un chronométrage de nouvel
apprentissage complet. Aucune nouvelle campagne indépendante n'a été lancée.
