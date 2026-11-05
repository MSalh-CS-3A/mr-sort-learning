# Jalon 3 — Apprendre MR-Sort malgré un brouillage

B reçoit toutes les données hors ligne. A transmet des objets classés par un modèle MR-Sort caché M_A ; H ajoute au plus autant d'objets que A ; B reçoit le mélange sans provenance et cherche à reproduire les décisions de M_A.

Échéance : 05/11/2026 à 23 h 59 ; soutenance : 06/11/2026. Énoncé : page 5 de [docs/sujet.pdf](../docs/sujet.pdf).

Le [rapport complet du jalon 3](../output/pdf/rapport_jalon3.pdf) présente la
confirmation, les mécanismes des attaques, les coûts et l'extension hybride
exploratoire. Sa [source LaTeX](../output/pdf/rapport_jalon3.tex) et le
[guide de compilation](../output/pdf/README.md) sont conservés avec les figures
et les tableaux issus des résultats audités.

## Protocole de référence

Lire [le protocole détaillé uniforme-v1](docs/protocole.md) avant d'ajouter une stratégie ou d'interpréter les figures. Il fixe les distributions, les informations accessibles, l'appariement, les ressources et les limites d'identification.

L'[extension des comparaisons](docs/comparaisons.md) définit les attaques à classe constante et concentrée, le filtrage, les redémarrages naïfs et le partage des préparations Inv-2.

Le [guide des campagnes locales](docs/campagnes_locales.md) décrit les lots audités,
la reprise après interruption, le calibrage des 25 couples (400 évaluations) et
les plans à 2 400 puis 9 600 évaluations. Le lanceur `python -m jalon3.campagne`
exécute une copie figée du code et conserve les tentatives interrompues.

Le calibrage initial `calibrage_local_v1` a révélé une division par zéro lors de
la conversion des modèles LINCS à poids tous nuls. Le cas est corrigé et couvert
par les tests de régression ; la relance utilise `calibrage_local_v2`, avec le
même plan de 400 évaluations et une nouvelle archive du code. Les contrôles
stricts de finitude des modèles sont conservés.

La [confirmation ciblée des quatre couples](docs/confirmation_quatre_couples.md)
fixe les deux attaques et deux défenses sur vingt nouvelles graines, avec
N_A=300, 500 et 1 000 : **840 évaluations**, témoins inclus. La phase
`confirmation` du lanceur produit les comparaisons appariées et vérifie les
préfixes effectivement sauvegardés entre tailles.

Premier couple : **`mrsort_aleatoire` / `naif`**. M_A et M_H sont des tirages indépendants du même générateur LINCS 2.0.2, filtrés symétriquement pour éviter les catégories presque vides. Les performances sont uniformes, les classes calculées exactement par chaque modèle. H ne voit aucune donnée de A. B apprend un seul MR-Sort sur tout le mélange.

Les classes ne sont pas équilibrées artificiellement. **Ce protocole remplace la génération équilibrée historique** : les anciens résultats ne sont pas directement comparables. Les modèles, le test et les observations partagées restent fixes lorsqu'on change la quantité de données, pour les hackers de référence.

## Organisation

| Fichier | Rôle |
|---|---|
| [interface.py](interface.py) | Contrats `Vue`, `Donnees`, `Decision`, `Brouillage` ; génération et classification |
| [simulation.py](simulation.py) | Génération de A, contrôle de H, mélange anonymisé, décision et évaluation |
| [hackers/](hackers/) | Attaques chargées automatiquement |
| [defenses/](defenses/) | Défenses chargées automatiquement |
| [experiences.py](experiences.py) | Grilles de tailles et ratios, répétitions, archives et exécution |
| [campagne.py](campagne.py) | Campagnes locales par lots audités, reprise, regroupement et estimation |
| [analyse.py](analyse.py) | Dégradations appariées, résumés et figures par couple |
| [validation_resultats.py](validation_resultats.py) | Audit du premier couple depuis les modèles et données sauvegardés |
| [validation_comparaisons.py](validation_comparaisons.py) | Audit des comparaisons, du partage des modèles et des temps |
| [tests/](tests/) | Contrats et invariants scientifiques |

## Exécuter

Depuis la racine, environnement installé par `uv sync --locked` :

```bash
.venv/bin/python -m unittest discover -v -s jalon3/tests

# Essai court. Choisir un dossier de sortie nouveau.
.venv/bin/python -m jalon3 --hackers mrsort_aleatoire --defenses naif --tailles 100 300 --ratios 0 0.5 1 --graines 0 1 --taille-test 10000 --processus 2 --sortie jalon3/results/mon_essai

# Campagne complète : 480 apprentissages.
.venv/bin/python -m jalon3 --hackers mrsort_aleatoire --defenses naif --dimensions 6x3 --tailles 100 300 500 1000 --ratios 0 0.25 0.5 1 --graines {0..29} --taille-test 10000 --processus 3 --sortie jalon3/results/mrsort_naif_uniforme_v1

# Refaire uniquement l'analyse et les figures.
.venv/bin/python -m jalon3.analyse jalon3/results/mrsort_naif_uniforme_v1

# Vérifier les mesures depuis les modèles et données sauvegardés.
.venv/bin/python -m jalon3.validation_resultats jalon3/results/mrsort_naif_uniforme_v1
```

`--lister` affiche les stratégies et le nombre de parties sans calcul. `--tailles` (alias compatible `--taille`) accepte plusieurs N_A. `--ratios` désigne H/A ; 1 signifie 50 % de données malveillantes dans le mélange. La référence 0 est toujours ajoutée. `--dimensions` accepte par exemple `6x3 10x5`. Un thread numérique est utilisé par processus.

Les défenses `naif` et `inv2_*` utilisent leurs arrêts du jalon 2, **indépendamment de `--temps`** : seuil de temps interne nominal de 4 s par appel lincs, au plus huit itérations externes pour `inv2_*`. Le temps total observé peut dépasser ce seuil. Les défenses `variante_*` utilisent le budget demandé. Les temps réels sont enregistrés ; l'arrêt en temps réel limite la reproductibilité des modèles appris sous des charges machine différentes.

`naif_multi` et `filtrage_iteratif` utilisent `--temps` comme budget souple et réalisent au moins un appel. Les deux règles `inv2_*` partagent désormais une seule préparation par mélange ; leurs temps attribuables incluent chacun la préparation complète. `temps_calcul_effectif` compte cette préparation une seule fois dans le coût physique de l'expérience.

## Lire les résultats

La [discussion des résultats et le plan d'analyse](docs/discussion_analyse_resultats.md)
conservent les conclusions vérifiées de la confirmation, l'origine de l'oracle
à 85,5 %, les hypothèses sur l'attaque classe haute, les diagnostics des groupes
et la proposition d'analyse des compromis entre fidélité et temps de calcul.

L'[analyse approfondie réalisée](results/analyse_approfondie_confirmation_v1/analyse.md)
présente les confusions par catégorie, les compositions réelles des groupes,
la défaillance de sélection, les sélecteurs exploratoires et les dominances en
deux et trois critères. Le module `python -m jalon3.analyse_approfondie SOURCE SORTIE`
recalcule ces diagnostics depuis les archives, sans nouvel apprentissage.

La [recherche d'un sélecteur hybride](results/recherche_selection_v1/proposition.md)
combine accord sur le mélange et diversité publique. Le coefficient est réglé
sur les anciennes graines ; les résultats sur les vingt graines déjà connues
restent exploratoires. `inv2_hybride_experimental` conserve la préparation Inv2
et est disponible pour une future confirmation indépendante.

La [première campagne exécutée](results/mrsort_naif_uniforme_v1/compte_rendu.md) contient 480 apprentissages sur 30 graines, sans erreur, et un audit des modèles sauvegardés. Le [pilote de validation](results/validation_uniforme_v1/bilan.md) ne comprend que deux graines et sert à vérifier la pipeline.

Le [pilote des comparaisons](results/pilote_comparaisons_v1/compte_rendu.md) contient 75 décisions sur cinq graines, avec 25 préparations Inv-2 partagées. L'[essai des nouvelles stratégies](results/essai_nouvelles_strategies_v1/compte_rendu.md) contient 21 décisions sur une seule graine. Ces deux exécutions ont été auditées, et les 20 tests passent. Elles n'ont pas le même périmètre statistique que la campagne initiale à trente graines.

- `configuration.json`, `sources/`, `instances/` : configuration, code et données utilisés ;
- `resultats.csv` : résultats bruts ; `resultats_apparies.csv` : ajout des pertes par rapport à sans attaque ;
- `resume.csv` : moyennes, écarts-types, nombres de valeurs et erreurs **par taille** ;
- `figures/` : une figure PNG et SVG par couple attaque/défense et par dimension ;
- `bilan.md` : tableau récapitulatif, figures et limites d'interprétation.

La mesure principale est `fidelite` au modèle A sur 10 000 nouveaux objets uniformes. `fidelite_equilibree` est la moyenne des rappels par catégorie ; elle reste vide si une catégorie manque au test. `delta_attaque` est la perte de fidélité calculée par graine, taille et défense avant moyenne. `desaccord` compare les modèles A et H sur un diagnostic indépendant, caché aux stratégies. `detection_h` et `rejet_a` restent vides si B ne désigne pas de suspects.

`gain_defense` compare une défense au naïf sur le même mélange. Lorsqu'une défense renvoie deux candidats, `fidelite_oracle_a`, `perte_selection`, `reconstruction_paire` et `inversion_modeles` décrivent leur qualité et le choix du groupe, sans fournir la vérité à B. L'[extension du protocole](docs/comparaisons.md) définit précisément ces diagnostics.

À parts égales, les rôles A/H sont symétriques : retrouver les deux règles n'identifie pas automatiquement leur provenance. La séparation de deux modèles est non applicable à `naif`, qui n'en apprend qu'un.

## Stratégies disponibles

| Attaque | Définition |
|---|---|
| `aucun` | Référence rho=0, sans injection |
| `etiquettes_aleatoires` | Performances uniformes et classes au hasard |
| `mrsort_aleatoire` | Unique MR-Sort indépendant ; toutes les classes H sont cohérentes |
| `classe_basse`, `classe_haute` | Performances uniformes identiques entre les deux variantes, classe fixée respectivement à 0 et C-1 |
| `mrsort_concentre` | Même modèle H que la référence cohérente ; 80 % des performances dans une boîte centrale |

| Défense | Définition |
|---|---|
| `naif` | Un modèle appris sur toutes les lignes |
| `inv2_plus_grand` | Inv-2 officiel du jalon 2, puis modèle du plus grand groupe |
| `inv2_mieux_explique` | Inv-2 officiel, puis modèle au plus faible taux d'erreur sur son groupe |
| `inv2_hybride_experimental` | Même Inv-2, puis accord sur le mélange entier + 0,2 fois l'entropie des prédictions publiques ; validation indépendante à faire |
| `variante_plus_grand`, `variante_mieux_explique` | Même sélection avec A2 et départ GMM de la variante du jalon 2 |
| `naif_multi` | Contrôle : redémarrages sur tout le mélange, sélection par erreur d'apprentissage |
| `filtrage_iteratif` | Retrait d'au plus 20 % des lignes mal classées, au plus deux réentraînements |

## Ajouter une stratégie

Créer son fichier dans `hackers/` ou `defenses/`, avec des noms de stratégies préfixés par son prénom. Les fichiers commençant par `_` ne sont pas importés. Les noms en double sont refusés.

```python
from jalon3.interface import hacker, objets_uniformes

@hacker("prenom_aleatoire")
def attaquer(vue, rng):
    x = objets_uniformes(vue.probleme, vue.nombre, rng)
    y = rng.integers(len(vue.probleme.ordered_categories), size=len(x))
    return x, y
```

H renvoie au plus `vue.nombre` lignes, dans les bornes, avec des classes entières de 0 à C-1. Tous les tirages passent par `rng`. Un hacker cohérent peut renvoyer `Brouillage(x, y, modele)` : le simulateur vérifie la cohérence et mesure le désaccord. **Le modèle déclaré n'est jamais envoyé à B.** Une attaque sans modèle peut continuer à renvoyer `(x, y)` ; le diagnostic de désaccord reste alors vide.

```python
from jalon3.interface import Decision, defense
from jalon2.jalon2_deux_mrsort import learn

@defense("prenom_naif")
def apprendre(recu, graine, temps):
    return Decision(learn(recu.probleme, recu.x, recu.y, graine))
```

B renvoie un modèle LINCS ou doté de `predict(x)` et, facultativement, `suspects` (un booléen par ligne). Il ne reçoit ni les sources, ni le test, ni le ratio exact. `@hacker(..., voit_donnees_a=True)` active une hypothèse différente à déclarer dans le rapport.

Avant partage : tests de contrat, invariants du protocole, puis petit tournoi contre les références. Les changements de la pipeline commune doivent rester compatibles avec les stratégies des autres membres du groupe.
