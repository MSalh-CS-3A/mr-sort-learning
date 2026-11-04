# Comparaisons des stratégies — extension strategies-v1

Cette extension conserve la génération de A et les tests du [protocole uniforme-v1](protocole.md). Elle ajoute des stratégies aveugles, le partage des préparations Inv-2 et des diagnostics de sélection. Les résultats historiques du premier couple restent conservés dans leur dossier original ; aucune campagne existante n'est écrasée.

## Attaques

| Nom | Performances | Classes | Modèle déclaré |
|---|---|---|---|
| `mrsort_aleatoire` | Uniformes sur tout le domaine | M_H(x), unique modèle indépendant | Oui, LINCS |
| `etiquettes_aleatoires` | Uniformes sur tout le domaine | Uniformes indépendantes de x | Non |
| `classe_basse` | Uniformes sur tout le domaine | Toujours 0 | Non |
| `classe_haute` | Uniformes sur tout le domaine | Toujours C-1 | Non |
| `mrsort_concentre` | Mélange : 80 % uniformes dans la boîte centrale [0,4 ; 0,6]^d, 20 % uniformes sur tout le domaine | M_H(x), unique modèle indépendant | Oui, LINCS |

Tous les hackers reçoivent uniquement le problème public, leur plafond d'injection et leur flux aléatoire. Ils ne reçoivent ni données A, ni modèle A, ni test. Les catégories cibles des attaques constantes et les paramètres de concentration sont fixés avant les résultats et ne sont pas choisis selon M_A.

Les observations constantes ne sont pas annoncées comme intrinsèquement impossibles à expliquer par un MR-Sort : aucun modèle n'est déclaré par ces attaques, et elles ne sont pas contraintes par le filtre de catégories rares appliqué aux modèles aléatoires.

### Appariement des variantes

`groupe_alea` permet de coupler deux variantes sans changer les flux historiques :

- les attaques constante basse/haute ont exactement les mêmes performances ; seules leurs étiquettes changent ;
- `mrsort_concentre` partage le tirage du modèle M_H de `mrsort_aleatoire` pour une même graine et dimension ; ses performances suivent un nouveau flux pour le mélange des deux lois ;
- les modèles restent fixes et les observations H emboîtées lorsque les quantités changent ;
- le désaccord A/H est mesuré sous la loi uniforme du diagnostic, même pour l'attaque concentrée. Il ne mesure donc pas directement le désaccord pondéré par la distribution particulière des observations injectées.

Une attaque ayant une distribution des performances différente est une expérience identifiée séparément. Elle ne remplace pas la comparaison initiale à distributions uniformes communes.

## Défenses et contrôle d'optimisation

### Références

- `naif` : un appel à `learn` sur toutes les observations.
- `inv2_plus_grand` : partition et deux modèles du jalon 2 officiel ; conserver le plus grand groupe. Une égalité est tranchée par le plus petit indice de groupe.
- `inv2_mieux_explique` : même apprentissage partagé ; conserver le groupe au plus faible taux d'erreur interne. Une égalité est tranchée par le plus petit indice.
- `variante_plus_grand` / `variante_mieux_explique` : même principe de partage pour l'algorithme A2/GMM.

Le plus grand groupe appris n'est pas nécessairement la véritable source majoritaire. Le groupe le mieux expliqué peut être celui du hacker. À parts égales, aucune de ces règles ne résout la symétrie A/H du cas cohérent.

### `naif_multi` : contrôle du calcul disponible

Effectuer des redémarrages sur le mélange complet. Le premier appel utilise la même graine que `naif` ; les suivants utilisent un flux dérivé. Conserver le modèle minimisant d'abord le nombre d'erreurs sur les données reçues, puis la somme des écarts de catégories. Les égalités conservent le premier modèle.

Arrêt si toutes les observations sont expliquées, s'il reste moins de quatre secondes nominales avant le prochain appel, ou après au plus 32 appels. Le premier apprentissage est toujours réalisé : le budget est souple et n'interrompt jamais un appel commencé. Les détails de décision archivent le nombre effectif d'appels et le budget demandé.

Il s'agit d'un contrôle de redémarrages, pas d'une défense supposée robuste. La sélection s'effectue sur le mélange contaminé ; améliorer son ajustement peut aussi renforcer l'attaque. Comparer plusieurs budgets et les durées mesurées est nécessaire avant de conclure à un avantage de robustesse d'Inv-2.

### `filtrage_iteratif`

Réglages fixés avant les essais : retrait maximal de 20 % des lignes reçues, au plus deux réentraînements après l'apprentissage initial.

1. Apprendre sur tout le mélange.
2. Parmi les lignes mal classées, classer les incompatibilités par écart absolu de catégorie décroissant, puis marge de concordance croissante, puis indice dans le mélange pour trancher les égalités.
3. Exclure au plus floor(0,2 N) lignes, puis réapprendre sur les restantes.
4. Recalculer les exclusions sur le jeu complet avec le nouveau modèle, sans cumuler mécaniquement les retraits, et recommencer au plus une fois.

Ne pas retirer une ligne déjà compatible uniquement pour atteindre 20 %. Arrêter si la sélection ne change plus, s'il n'y a plus d'erreurs, si le sous-jeu ne contient plus deux catégories ou si le budget restant ne permet pas de commencer un nouvel appel nominal. `suspects` correspond uniquement aux lignes effectivement exclues lors du dernier apprentissage réalisé. Aucun taux d'injection véritable ni origine n'est utilisé.

Le filtrage peut supprimer des observations authentiques, particulièrement celles de catégories rares, et renforcer un mauvais modèle. Il ne possède pas ici de garantie théorique. Le taux de 20 % est un point de départ fixé, non un réglage optimisé sur la campagne. Toute optimisation future doit utiliser des simulations de développement distinctes des graines d'évaluation.

## Préparation partagée et comptabilité du calcul

Les défenses enregistrées avec le même `preparer` utilisent une seule préparation par condition (même mélange, même graine, même budget). Le cache est local à cette condition, sans réutilisation entre données différentes. Une erreur de préparation est conservée et rapportée pour les sélections concernées.

La préparation ne reçoit que `recu`, `graine`, `temps`. Les vérités privées ne lui sont pas accessibles. Les fonctions des défenses restent utilisables seules avec leurs trois arguments historiques ; dans ce cas, elles réalisent leur propre préparation.

Une sélection personnalisée peut s'enregistrer avec `@defense("prenom_regle", preparer=preparer_inv2)` et accepter l'argument facultatif `preparation=None`. Elle utilise cet objet s'il est fourni et le construit elle-même sinon. Elle ne doit pas modifier les candidats ou la partition partagés.

Les deux règles Inv-2 prennent leur décision sur **exactement les mêmes modèles et la même partition**. Les modèles candidats, la partition et le groupe choisi sont sauvegardés pour chaque décision. Le CSV contient :

- `preparation_id` : identifiant du calcul partagé ;
- `temps_preparation` et `temps_selection` ;
- `temps` : temps attribuable = préparation complète + sélection, pour chacune des règles ;
- `temps_calcul_effectif` : coût réellement exécuté, avec la préparation comptée une seule fois ;
- `groupe_choisi` et `decision_details` : décisions et nombre d'appels des nouvelles stratégies.

Additionner les temps attribuables des deux règles surestime le coût physique de la campagne ; inversement, présenter la seconde règle comme instantanée sous-estimerait son coût d'utilisation autonome.

## Mesures supplémentaires, réservées au simulateur

- `gain_defense` : fidélité de la défense moins celle de `naif`, sur le même mélange et la même graine. Calculer ces différences avant la moyenne.
- `partition_appariee` : fraction de provenances correctes après la meilleure permutation des deux groupes. La provenance reste ambiguë sur les observations compatibles avec les deux règles ; cette métrique n'est pas une garantie d'identifiabilité.
- `fidelite_oracle_a` : meilleure fidélité à A parmi les deux modèles appris. C'est un diagnostic inaccessible à B.
- `perte_selection` : fidélité oracle moins fidélité effectivement obtenue par le choix de B. Elle sépare la qualité des candidats du choix du groupe.
- `reconstruction_paire` : meilleure moyenne des fidélités aux règles A et H, après permutation, sur les mêmes performances de test. Disponible seulement si H déclare un modèle.
- `inversion_modeles` : 1 si B choisit le groupe opposé à l'alignement conjoint A/H le plus fidèle ; vide si cet alignement est à égalité ou si H ne déclare pas de modèle.

Les vérités A/H sont utilisées après la décision de B. Elles ne corrigent jamais son choix. La présence d'une bonne solution oracle ne constitue pas une défense réalisable.

Les figures par couple sont conservées. Des figures transversales comparent les défenses et leurs gains face à `naif`. Les bandes sont ± un écart-type entre graines. Les temps moyens figurent dans le bilan : un gain sous un budget différent ne prouve pas une supériorité à calcul égal.

## Exécutions prévues avant extension des répétitions

### Pilote de référence : 75 évaluations

Deux attaques historiques, trois défenses, cinq graines, N_A=300, ratios 0 / 0,5 / 1, test de 10 000 objets. La référence sans attaque est partagée entre les attaques. Il y a 25 mélanges : 25 apprentissages Inv-2 partagés et 25 apprentissages naïfs, donnant 75 décisions. Les appels lincs internes d'Inv-2 sont plus nombreux.

```bash
.venv/bin/python -m unittest discover -v -s jalon3/tests
.venv/bin/python -m jalon3 --hackers mrsort_aleatoire etiquettes_aleatoires --defenses naif inv2_plus_grand inv2_mieux_explique --tailles 300 --ratios 0 0.5 1 --graines 0 1 2 3 4 --taille-test 10000 --processus 3 --sortie jalon3/results/pilote_comparaisons_v1
```

### Essai des stratégies ajoutées

Une graine, N_A=100, ratios 0 / 0,5 / 1, attaques constante basse/haute et cohérente concentrée, défenses `naif`, `naif_multi`, `filtrage_iteratif`. Le budget demandé aux nouvelles stratégies est 12 secondes. Cela donne 7 mélanges et 21 décisions. Cet essai vérifie le fonctionnement et les diagnostics ; une graine ne permet pas d'inférence statistique.

```bash
.venv/bin/python -m jalon3 --hackers classe_basse classe_haute mrsort_concentre --defenses naif naif_multi filtrage_iteratif --tailles 100 --ratios 0 0.5 1 --graines 0 --temps 12 --taille-test 10000 --processus 1 --sortie jalon3/results/essai_nouvelles_strategies_v1
```

Les 30 graines et les quatre tailles ne seront étendues à ces nouvelles comparaisons qu'après examen du pilote, des temps et des échecs. Les résultats du pilote ne doivent pas servir à sélectionner une variante puis être présentés comme son évaluation indépendante finale.

### Audit des fichiers sauvegardés

```bash
.venv/bin/python -m jalon3.validation_comparaisons jalon3/results/pilote_comparaisons_v1
.venv/bin/python -m jalon3.validation_comparaisons jalon3/results/essai_nouvelles_strategies_v1
```

Ce vérificateur cible les modèles NumPy MR-Sort du jalon 2 officiel, utilisés par ces deux exécutions. Il vérifie le plan, les vérités A/H, les modèles B rechargés, les gains et pertes appariés, les sélections, l'identité des candidats partagés et la comptabilité du calcul. Les modèles LINCS de la variante sont sauvegardés en YAML par la pipeline ; leur audit ou celui d'un objet `predict()` personnalisé nécessiterait un adaptateur de chargement approprié.
