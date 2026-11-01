# Audit des données Inv-2-MR-Sort

Audit réalisé le 18 octobre 2026 avec `projet audit`. La sortie structurée et les empreintes des fichiers sont dans `jalon2/variante_a0_a4/results/version_complete/audit.json`.

## Inventaire vérifié

Les 72 CSV se chargent correctement. Chaque configuration contient douze fichiers : trois tailles (300, 600, 1 200), deux répartitions annoncées (50-50, 75-25) et deux niveaux de bruit annoncés (00, 10).

| Type | Configuration | Critères | Catégories | CSV | Plus petit effectif de catégorie dans un CSV |
| --- | --- | ---: | ---: | ---: | ---: |
| A | cr06_ca03 | 6 | 3 | 12 | 28 |
| A | cr08_ca04 | 8 | 4 | 12 | 18 |
| A | cr10_ca05 | 10 | 5 | 12 | 17 |
| B | cr06_ca03 | 6 | 3 | 12 | 49 |
| B | cr08_ca04 | 8 | 4 | 12 | 40 |
| B | cr10_ca05 | 10 | 5 | 12 | 12 |

Les critères sont tous réels, croissants et bornés par `[0,1]`. Les nombres de lignes correspondent aux noms. Toutes les catégories du problème figurent dans chaque CSV complet. Les identifiants sont uniques dans chaque fichier. Aucun vecteur de performances dupliqué, aucune valeur manquante, non finie ou hors domaine n'a été détecté. Les données ne contiennent que `name`, les critères et `category` ; aucune source cachée ou catégorie avant bruit n'est fournie.

Les six problèmes ont un `format_version` valide mais omettent `kind`. Le chargeur ajoute `kind: classification-problem` en mémoire avant validation native lincs ; les fichiers originaux restent inchangés.

## Dépendances entre fichiers

Les 36 paires A/B de même configuration et même nom partagent **exactement les mêmes performances, dans le même ordre**. Leurs catégories diffèrent pour environ 56,0 % à 74,4 % des lignes selon la paire. Les 72 fichiers ont néanmoins des empreintes distinctes. Ces paires ne constituent pas des échantillons indépendants de performances ; les comparaisons de difficulté A/B doivent tenir compte de leur appariement et des étiquettes différentes.

Les 36 paires nominales `noise00`/`noise10` d'un même type, taille et répartition ne partagent pas les mêmes performances : elles ne permettent pas de mesurer directement un taux de catégories modifiées par comparaison ligne à ligne. Les ensembles des tailles 300, 600 et 1 200 ne sont pas imbriqués dans une même combinaison type/configuration/répartition/bruit. Aucun autre recouvrement de vecteurs complets n'a été détecté entre les fichiers de même dimension.

La sortie d'audit comporte 144 relations : 36 paires nominales de bruit, 72 comparaisons nominales de tailles et 36 paires A/B partageant leurs performances. Un même nom `Alternative i` réapparaît dans plusieurs fichiers et n'est pas, à lui seul, un identifiant inter-fichiers.

## Limites d'interprétation

- Type B désigne une difficulté annoncée supérieure au type A, selon l'information utilisateur. L'audit ne déduit pas un mécanisme de génération de cette désignation.
- La définition exacte du bruit et la manière de construire les deux sources ne sont pas disponibles.
- Les répartitions et niveaux de bruit des noms restent des métadonnées annoncées ; les proportions ne sont pas imposées à l'apprentissage.
- Les modèles sources ne sont pas fournis. L'évaluation principale mesure la compatibilité avec les catégories observées, pas la récupération de ces modèles ou de leurs sources.
- `dataset0.txt` appartient au jalon 1 : 60 objets, cinq critères, trois catégories, performances sur `[0,100]`. Il est conservé dans la suite de régression historique.
