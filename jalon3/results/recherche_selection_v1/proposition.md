# Proposition de sélection hybride pour Inv2

4 novembre 2026. Résultat de développement ; ce document ne remplace pas les
conclusions de la confirmation initiale. Les méthodes d'origine sont conservées.

## Proposition concrète

Pour chaque modèle candidat, calculer :

- A_k : proportion de catégories correctement expliquées sur le mélange ENTIER ;
- H_k : entropie normalisée des catégories prédites sur 10 000 nouveaux points
  publics uniformes, sans étiquettes de A.

    Score_k = A_k + 0,2 H_k.

Retenir le score maximal ; en cas d'égalité, garder le plus grand groupe.
L'entropie est comprise entre 0 et 1 : le supplément au score est plafonné à
0,2. Ce n'est pas un indice infaillible d'authenticité ni une probabilité de
confiance. Le coefficient 0,2 n'est pas présenté comme optimal.

La défense `inv2_hybride_experimental` est disponible dans
`jalon3/defenses/hybride.py`. Elle partage la préparation Inv2 avec la règle
initiale. Elle ne reçoit ni le modèle de A, ni les origines, ni le ratio, ni le
nom de l'attaque, ni le test. Elle ne lit aucun fichier de vérité.

## Pourquoi combiner ces deux indices ?

La taille d'un groupe compte les observations attribuées à ce groupe, y compris
celles que les deux modèles pourraient expliquer. L'accord global compare les
modèles directement : les observations où leurs prédictions sont identiques
s'annulent dans la différence de scores. Seules les prédictions différentes
peuvent départager l'accord.

Dans le cas idéal de modèles exacts et de performances de même loi pour A et H,
si alpha est la proportion authentique et D le désaccord :

    E[A_A - A_H] = (2 alpha - 1) D.

Avec une majorité authentique, cet accord favorise donc A à la population.
Pour des modèles appris sur les mêmes données, le score d'apprentissage est
optimiste ; cette identité idéale ne prouve pas la performance du sélecteur.

L'accord seul reste vulnérable à un modèle presque constant haut à ratio 1.
L'entropie apporte un indice contre ce cas, mais sa pondération limitée évite de
préférer systématiquement le candidat le plus équilibré, comme le faisait le
sélecteur d'entropie pure. Cela réduit un risque, sans garantir son élimination.

## Réglage effectué AVANT l'examen des scores hybrides de transfert

Cinq anciennes graines de développement (100..104), N_A=300, deux attaques,
trois ratios et un témoin : 35 paires archivées.

La grille était fixée à 0 / 0,02 / 0,05 / 0,1 / 0,2. On excluait un coefficient
si sa perte moyenne dépassait un point dans le témoin ou face au MR aléatoire
aux ratios 0,25 et 0,5. Parmi les valeurs restantes, on maximisait la fidélité
moyenne en pondérant également les sept conditions ; égalités au plus petit
coefficient. Toutes les valeurs étaient admissibles et 0,2 a été retenu.

Le plan est conservé dans `jalon3/docs/recherche_critere_selection.md`.
La règle et le résultat de ce réglage ont été écrits dans
[regle_figee.json](regle_figee.json) avant lecture des scores hybrides des vingt
graines suivantes. La recherche n'a pas élargi la grille après observation.

## Résultats rétrospectifs sur les vingt graines déjà connues

Les graines 1000..1019 avaient déjà servi à analyser les mécanismes et à motiver
la famille de règles. Ce transfert n'est donc PAS une confirmation indépendante,
même si la valeur numérique du coefficient provient des anciennes graines.
Aucun candidat n'a été réappris.

Les valeurs ci-dessous sont des fidélités globales moyennes, et des différences
appariées au sélecteur du plus grand groupe. Toutes les conditions sont montrées.

| N_A | Attaque | H/A | Plus grand groupe (%) | Hybride (%) | Gain (points) | IC exploratoire 95 % |
|---:|---|---:|---:|---:|---:|---|
| 300 | aucun | 0 | 91.32 | 91.35 | +0.04 | [-0.53 ; 0.55] |
| 300 | mrsort_aleatoire | 0.25 | 91.40 | 91.40 | +0.00 | [0.00 ; 0.00] |
| 300 | mrsort_aleatoire | 0.5 | 90.66 | 90.65 | -0.01 | [-0.04 ; 0.00] |
| 300 | mrsort_aleatoire | 1 | 66.39 | 69.89 | +3.50 | [-9.49 ; 16.27] |
| 300 | classe_haute | 0.25 | 85.61 | 89.86 | +4.26 | [0.00 ; 9.19] |
| 300 | classe_haute | 0.5 | 80.83 | 88.12 | +7.29 | [0.00 ; 16.35] |
| 300 | classe_haute | 1 | 44.69 | 67.00 | +22.31 | [3.97 ; 41.55] |
| 500 | aucun | 0 | 92.12 | 92.84 | +0.72 | [0.01 ; 1.53] |
| 500 | mrsort_aleatoire | 0.25 | 88.69 | 88.44 | -0.26 | [-0.77 ; 0.00] |
| 500 | mrsort_aleatoire | 0.5 | 88.69 | 89.09 | +0.40 | [0.00 ; 1.00] |
| 500 | mrsort_aleatoire | 1 | 67.00 | 74.83 | +7.83 | [-1.12 ; 18.80] |
| 500 | classe_haute | 0.25 | 88.37 | 91.28 | +2.91 | [0.00 ; 7.61] |
| 500 | classe_haute | 0.5 | 80.10 | 85.48 | +5.37 | [0.00 ; 11.69] |
| 500 | classe_haute | 1 | 35.89 | 60.74 | +24.85 | [9.14 ; 42.11] |
| 1000 | aucun | 0 | 92.38 | 94.45 | +2.07 | [0.93 ; 3.41] |
| 1000 | mrsort_aleatoire | 0.25 | 89.45 | 89.57 | +0.12 | [0.00 ; 0.35] |
| 1000 | mrsort_aleatoire | 0.5 | 88.22 | 88.22 | +0.00 | [0.00 ; 0.00] |
| 1000 | mrsort_aleatoire | 1 | 65.08 | 68.16 | +3.09 | [-3.89 ; 11.00] |
| 1000 | classe_haute | 0.25 | 86.98 | 90.47 | +3.49 | [0.00 ; 8.72] |
| 1000 | classe_haute | 0.5 | 83.32 | 87.28 | +3.96 | [0.57 ; 8.00] |
| 1000 | classe_haute | 1 | 32.20 | 67.99 | +35.80 | [19.33 ; 53.34] |

Sur cette grille : 17 gains moyens positifs, deux nuls et deux négatifs. Les deux
pertes sont petites en moyenne (-0,01 et -0,26 point), mais cela ne garantit pas
l'absence de pertes importantes sur une instance individuelle.

En pondérant également les 21 conditions et en regroupant AVANT rééchantillonnage
les conditions de chaque graine, le gain moyen est de 6,08 points, IC exploratoire
[4,15 ; 7,93]. Cet agrégat dépend de notre grille et ne représente pas une
probabilité de supériorité dans un environnement réel.

Les intervalles sont des bootstrap appariés de 10 000 rééchantillonnages,
individuels, sans correction multiple. Ils ne corrigent pas le choix de la
famille de critères après consultation des vingt graines. Les lignes avec un
IC touchant zéro ne sont pas des preuves de supériorité.

L'hybride ne retrouve pas l'oracle de 85,5 % à N_A=1000/classe haute/rho=1 : il
obtient 67,99 %. Il conserve donc une marge d'échec importante. Le simple accord
global y donne 29,60 %, ce qui montre la contribution du terme de diversité.
Face au MR aléatoire au même ratio et à la même taille, l'accord seul donne
74,75 %, contre 68,16 % pour l'hybride : la combinaison paie aussi un compromis.

Il faut également préserver le cas sans attaque : à N_A=300, l'hybride reste
à 91,35 %, contre 95,90 % pour le naïf. Améliorer la sélection des deux candidats
ne supprime pas le coût de la segmentation imposée.

## Vérification et calcul

Les 44 tests de la pipeline passent, dont quatre tests du nouveau sélecteur.
La défense exécutable a aussi été rejouée sur les 420 paires de candidats
archivés : tous les choix et fidélités concordent avec le prototype.
Voir [verification_defense.json](verification_defense.json).

Le rejeu chronomètre seulement le nouveau choix sur candidats déjà chargés.
Il ne fournit pas un nouveau benchmark d'apprentissage de bout en bout. Le
surcoût réel sera mesuré pendant la confirmation future, en partageant une
seule préparation entre les deux sélecteurs. Aucune dominance temps/qualité de
la nouvelle défense n'est déclarée à partir de ces durées de rejeu.

## Validation suivante recommandée, non exécutée ici

Une confirmation ciblée suffit pour commencer : N_A=300, six critères, trois
catégories, vingt nouvelles graines, deux attaques, ratios 0/0,5/1, et trois
méthodes (naïf, Inv2 plus grand groupe, hybride). Cela représente 300 décisions
évaluées pour 100 mélanges ; les deux sélecteurs partagent leurs apprentissages.

Figer avant lancement les deux objectifs : améliorer classe haute à ratio 1,
et ne pas perdre plus de deux points en moyenne sur MR aléatoire à ratio 0,5,
avec analyse appariée et IC. Le témoin documente le coût sans attaque. Cette
marge de deux points est une proposition de critère de succès à annoncer,
pas une conséquence des résultats. Ne pas retoucher le coefficient pendant la
confirmation. Ne pas annoncer la réussite avant analyse des nouvelles graines.

La validation de N_A=500/1000 serait une extension distincte ; une confirmation
à 300 ne doit pas être présentée comme une garantie pour toutes les tailles.

## Autres propositions et limites

- Validation croisée sur le mélange : apprendre les candidats sur une partie,
  comparer leurs accords sur une autre. Cela réduit le biais d'ajustement, mais
  diminue les données d'apprentissage et augmente le coût. Un découpage APRES
  apprentissage ne constitue pas une validation.
- Stabilité par rééchantillonnage : observer si le même comportement est retenu
  après perturbation du mélange. Piste utile pour signaler une ambiguïté ; elle
  ne garantit pas que le comportement stable soit celui de A.
- Quelques observations authentifiées de A permettraient un choix direct entre
  candidats ; c'est un autre protocole, pas une information dont B dispose ici.

Les travaux de [Scott et al.](https://proceedings.mlr.press/v30/Scott13.html) et de
[Katz-Samuels et al.](https://jmlr.org/papers/v20/17-576.html) étudient des conditions
d'identifiabilité de distributions contaminées. Ils ne valident pas notre score
hybride. [Charikar et al.](https://arxiv.org/abs/1611.02315) distinguent notamment
le fait de fournir une liste de candidats et l'apport de petites données fiables.

À parts égales, pour les deux sources MR aléatoires de même loi, l'échange A/H
ne modifie pas les observations : aucun score basé seulement sur ce mélange ne
peut garantir la bonne identité. Le problème ne disparaît pas avec le nouveau score.

## Fichiers

- [Réglage et contraintes sur les cinq graines](reglage_developpement.csv)
- [Caractéristiques du développement](caracteristiques_developpement.csv)
- [Choix par graine sur les archives](transfert_retroactif.csv)
- [Moyennes, métriques équilibrées, changements et IC](resume_transfert.csv)
- [Règle figée](regle_figee.json)
- [Audit de recherche](audit_recherche.json)
- [Rejeu de la défense](verification_defense.json)

Reproduction de la recherche, depuis la racine :

```bash
.venv/bin/python -m jalon3.recherche_selection jalon3/results/calibrage_local_v2 jalon3/results/analyse_approfondie_confirmation_v1 jalon3/results/une_nouvelle_recherche
```
