# Rendu du jalon 1 - Projet SDP

## Rendu conservé

L'[archive préparée](rendu_jalon1_mrsort.zip) et le [PDF](rapport_jalon1_modele_retenu.pdf) sont conservés tels quels, avec leurs noms et leur organisation d'origine. Les instructions ci-dessous décrivent le contenu de cette archive et s'appliquent après extraction.

Dans le dépôt réorganisé, la version Markdown se trouve dans [jalon1/README.md](../README.md). Pour travailler dans le dépôt, utiliser les chemins et commandes du [README du jalon 1](../README.md).

## Instructions de l'archive

Le rapport `rapport_jalon1_modele_retenu.pdf` explique uniquement le modèle MR-Sort retenu : programme linéaire mixte, rôle des contraintes, application à plusieurs catégories, utilisation du code et analyse des résultats. Sa version modifiable est fournie en Markdown.

Le code fourni est une copie exacte des fichiers existants ; aucun changement de code n'a été effectué pour préparer ce rendu.

## Contenu

- `mrsort.py` : lecture des données, apprentissage avec GUROBI et prédiction.
- `benchmark.py` : vingt apprentissages et évaluations sur des objets indépendants.
- `test_mrsort.py` : neuf tests fonctionnels existants.
- `requirements.txt` : dépendance `gurobipy==13.0.3`.
- `dataset0.txt` : jeu du cours, 60 objets, 5 critères, 3 catégories.
- `resultat_dataset0.json` : paramètres appris et diagnostics (60/60 classes restituées).
- `resultat_benchmark.json` : configuration et détail des vingt essais (93,025 % de précision moyenne de test).
- `modele_dataset0.lp` : formulation exportée du modèle construit pour dataset0.

## Installation

Depuis le dossier obtenu après extraction, avec Python 3 et une licence GUROBI utilisable :

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Exécution

```bash
.venv/bin/python mrsort.py dataset0.txt --log \
  --output resultat_dataset0.json --export-lp modele_dataset0.lp
.venv/bin/python -m unittest -v test_mrsort
.venv/bin/python benchmark.py --runs 20 --criteria 3 \
  --categories 2 --train-size 30 --test-size 200 \
  --seed 42 --time-limit 10 --output resultat_benchmark.json
```

Ces commandes réécrivent les résultats dans le dossier extrait. Les temps peuvent varier selon la machine ; les paramètres de solutions optimales peuvent aussi varier selon l'environnement du solveur.

Le programme déduit le nombre de critères de l'en-tête et le nombre de catégories de la classe maximale (avec un minimum de deux). L'option `--categories p` fixe explicitement le nombre total de catégories, notamment si certaines sont absentes de l'apprentissage. Les performances doivent être comprises dans les bornes choisies (0 à 100 par défaut).

Les tests, dataset0 et les vingt essais ont été réexécutés lors de la préparation du rapport. Les résultats déjà présents ont été conservés dans l'archive ; la vérification a reproduit les paramètres de dataset0 et les précisions du benchmark.

Échéance indiquée dans le sujet : mardi 6 octobre 2026 à 23 h 59, heure de Paris. L'archive est préparée pour le dépôt ; elle n'a pas été déposée sur Edunao.
