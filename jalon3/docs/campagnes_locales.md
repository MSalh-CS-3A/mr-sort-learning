# Campagnes locales, lots et reprise

Ce lanceur utilise les stratégies et les distributions déjà définies dans le
[protocole](protocole.md) et les [comparaisons](comparaisons.md). Il organise le
calcul ; il ne change ni les informations de H/B ni l'apprentissage du jalon 2.

## Plans prévus

Les cinq attaques sont `mrsort_aleatoire`, `etiquettes_aleatoires`, `classe_basse`,
`classe_haute` et `mrsort_concentre`. Les cinq défenses sont `naif`,
`inv2_plus_grand`, `inv2_mieux_explique`, `naif_multi` et `filtrage_iteratif`.
Chaque lot utilise les 25 couples, six critères, trois catégories, les ratios
H/A 0, 0,25, 0,5 et 1, un test de 10 000 objets et un diagnostic distinct de
10 000 objets. H reste aveugle aux données de A. Le témoin sans attaque est
exécuté une fois par défense, sans être dupliqué pour les cinq attaques.

| Phase | Graines | Tailles A | Lots | Évaluations |
|---|---|---|---:|---:|
| `calibrage` | 100 à 104 | 300 | 5 | 400 |
| `principale` | 1000 à 1029 | 300 | 30 | 2 400 |
| `complete` | 1000 à 1029 | 100, 300, 500, 1000 | 120 | 9 600 |

Un lot correspond à une dimension, une graine et une taille. Il comporte
`5 × (1 + 5 × 3) = 80` décisions. Le partage des préparations Inv-2 est conservé
à l'intérieur du lot. Les flux de génération préservent les mêmes modèles et
tests, ainsi que les préfixes des données lorsque la taille change.

Les graines du calibrage sont distinctes des campagnes historiques 0 à 29 et
de l'évaluation finale. Le calibrage sert à contrôler le fonctionnement et les
durées. Les choix de stratégies et d'hyperparamètres doivent être figés avant
d'examiner les résultats des graines 1000 à 1029. Les deux phases finales
partagent volontairement ces graines : l'extension étudie les tailles sur les
mêmes instances, elle n'ajoute pas des répétitions indépendantes.

Le budget demandé vaut 12 s par défaut. **Ce n'est pas une comparaison à temps
égal** : `naif` et `inv2_*` conservent les arrêts du jalon 2 ; les deux autres
méthodes utilisent ce budget souple. Les durées réelles restent enregistrées.
Cette campagne mesure les stratégies sous ces réglages. Une étude des budgets
comparables et des intervalles de confiance reste nécessaire avant de revendiquer
une supériorité à calcul égal. Les graphiques actuels montrent ± un écart-type,
pas des intervalles de confiance.

## Lancer et suivre

Depuis la racine du dépôt, avec l'environnement `.venv` déjà installé :

```bash
# Vérifier le plan et les ressources sans lancer de calcul.
.venv/bin/python -m jalon3.campagne --phase calibrage --sortie jalon3/results/calibrage_local_v2 --plan

# Lancer le calibrage, deux processus indépendants et un thread numérique chacun.
.venv/bin/python -u -m jalon3.campagne --phase calibrage --processus 2 --sortie jalon3/results/calibrage_local_v2

# Lire la progression sans interrompre le calcul.
.venv/bin/python -m jalon3.campagne --sortie jalon3/results/calibrage_local_v2 --etat

# Reprendre une campagne interrompue.
.venv/bin/python -u -m jalon3.campagne --sortie jalon3/results/calibrage_local_v2 --reprendre --processus 2
```

Sans `--processus`, le choix automatique est conservateur : au plus deux
processus, en laissant si possible deux processeurs logiques libres et en tenant
compte de la mémoire disponible. C'est une estimation, pas une réservation RAM
ou une limite stricte de consommation. Le nombre peut être changé à la reprise ;
la charge influence l'arrêt en temps réel des apprentissages et doit donc être
consignée dans l'interprétation. Ne pas lancer une autre campagne lourde en même
temps. La machine doit rester allumée et ne pas être mise en veille.

`Ctrl-C` ou SIGTERM arrête le lanceur et ses sous-processus. Pour arrêter
proprement **après les lots en cours**, créer le fichier `ARRETER` dans le dossier
de campagne. Retirer ou renommer ce fichier avant la reprise. Un verrou empêche
deux lanceurs d'écrire dans la même campagne. Après un arrêt brutal du parent,
la reprise refuse de déplacer un lot dont le sous-processus détient encore le
verrou de calcul. Les verrous fonctionnent aussi entre espaces de PID distincts.

Les calculs longs peuvent être démarrés dans une session persistante (`tmux`,
`screen`, ou un lancement détaché avec journal). Le lanceur lui-même ne modifie
pas les réglages de veille ni les services du système.

## Garanties de reprise et limites

À la création, `configuration.json` archive les versions, le plan et les
empreintes des sources. `sources/` contient une copie exécutable de `jalon3` et
de ses imports locaux du jalon 2. Chaque sous-processus exécute cette copie,
même si le code de travail est modifié pendant la campagne.

Un lot est réutilisable uniquement lorsque :

1. son plan est couvert exactement, sans doublon et sans échec ;
2. l'audit scientifique a rechargé ses données, modèles, partitions et métriques ;
3. `termine.json` est présent, avec des empreintes intactes de ses artefacts ;
4. sa configuration et les versions Python/bibliothèques restent compatibles.

Un lot incomplet ou échoué n'est jamais agrégé. À la reprise, sa tentative est
déplacée dans `tentatives_interrompues/`, puis **le lot entier est recalculé**.
La reprise n'est pas à la décision individuelle : cela préserve le partage des
préparations et évite de mélanger plusieurs optimisations interrompues. Les
échecs ne sont pas relancés silencieusement jusqu'à obtenir un succès ; ils sont
consignés et nécessitent une reprise explicite après examen.

Le système ne garantit pas des modèles appris identiques à une autre exécution :
l'apprentissage dépend aussi de l'arrêt temporel. Les entrées, paramètres,
versions, tentatives et résultats effectifs sont conservés.

## Résultats et estimation

- `lots/IDENTIFIANT/` : archives normales d'une expérience, audit et marqueur de fin ;
- `journaux/` : sorties et erreurs des sous-processus, une tentative par journal ;
- `progression.json` : PID du lanceur, lots actifs, terminés et échecs ;
- `resultats.csv`, `resultats_apparies.csv`, `resume.csv`, `bilan.md` : regroupement des lots audités ;
- `audit_campagne.json` : couverture attendue/réalisée, références aux audits des lots ;
- `figures/` : PNG/SVG par couple et comparaisons, produits à la fin du lancement ;
- `estimation.md` et `estimation.json` : extrapolation des durées des lots déjà audités.

Un regroupement partiel porte explicitement la mention **INCOMPLÈTE**. L'audit
global est `ok` uniquement lorsque tous les lots attendus sont présents et
validés. Ne pas appliquer directement `validation_comparaisons` au regroupement :
les données sont dans les sous-dossiers `lots/`. Les audits scientifiques
s'appliquent individuellement à ceux-ci, et l'audit de campagne vérifie leur
couverture. Ils restent limités aux modèles NumPy MR-Sort officiels utilisés ici.

Après le calibrage, l'estimation extrapole le coût moyen d'un lot aux 30 ou
120 lots finaux et indique la durée idéale avec le parallélisme demandé. La
variation avec la taille, l'attaque et le modèle empêche de garantir cette durée.
Les heures cumulées de sous-processus ne sont pas des heures CPU mesurées.

Pour reconstruire le regroupement et les figures sans nouvel apprentissage :

```bash
.venv/bin/python -m jalon3.campagne --sortie jalon3/results/calibrage_local_v2 --analyser
```

## Campagnes finales et extension

Ces commandes sont prévues pour la suite, après examen du calibrage :

```bash
.venv/bin/python -u -m jalon3.campagne --phase principale --processus 2 --sortie jalon3/results/principale_locale_v1

# Importer les 30 lots à taille 300 déjà audités, puis calculer les 90 autres.
.venv/bin/python -u -m jalon3.campagne --phase complete --processus 2 --sortie jalon3/results/complete_locale_v1 --depuis jalon3/results/principale_locale_v1
```

L'import exige les mêmes sources archivées, versions, stratégies, distributions,
budgets et paramètres de génération. Il copie les lots complets sans modifier
leurs archives et enregistre leur origine dans `provenance_lots.json`. Le chemin
de sortie d'origine reste dans leur configuration : c'est une information
opérationnelle, sans effet sur l'expérience. Un code différent impose une nouvelle
campagne cohérente ; on ne fusionne pas automatiquement des résultats historiques.

Les phases à 2 400 et 9 600 évaluations ne sont pas déclenchées automatiquement par
le calibrage. Les conclusions finales concernent les cinq attaques, cinq défenses,
six critères, trois catégories et distributions fixées dans ce protocole.

## Correction du calibrage initial : poids tous nuls

Le 2 novembre 2026, `calibrage_local_v1` a calculé les 400 décisions, mais quatre
lots ont échoué à l'audit : la conversion du modèle LINCS normalisait des poids
tous nuls par leur somme, créant `NaN` et un seuil infini. Ce cas est apparu dans
Inv-2 face à `classe_basse`. Un seul lot de 80 décisions a été audité. Cette
campagne incomplète et ses sources sont conservées comme trace du diagnostic.

La conversion corrigée conserve `w=0` et `lambda=1` lorsque la somme des poids est
nulle. Dans la représentation LINCS, le seuil vaut 1 : aucune coalition de poids
nuls ne peut franchir de profil, donc toutes les prédictions sont en classe 0.
La représentation corrigée conserve exactement ce comportement et produit des
marges finies. Pour les poids non nuls, la normalisation habituelle reste la même.
Ce modèle constant est une exception explicite à la convention de somme des poids
égale à 1 ; aucune classe n'est choisie à partir du test ou de l'origine A/H.

Les nouveaux tests comparent les prédictions à celles du modèle LINCS natif,
contrôlent les marges et la sauvegarde/relecture, et exercent un apprentissage
réel à classe basse constante. Le simulateur refuse immédiatement tout modèle
NumPy non fini, y compris un candidat Inv-2 non retenu. L'audit conserve ses
contrôles stricts : aucun paramètre non fini n'est accepté.

`calibrage_local_v2` reprend le même plan de données et de graines avec le code
corrigé et recalcule tous les lots. Les `NaN` pouvant aussi fausser les marges et
réaffectations intermédiaires d'Inv-2, il ne suffit pas de retoucher les archives
finales ni de réutiliser automatiquement le lot qui avait passé l'ancien audit.
