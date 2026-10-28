# Projet SDP - Apprentissage de modèles MR-Sort

Projet SDP, CentraleSupélec, mention IA, 2026-2027. Groupe : Mohamed SALH, Mohamed Chebli, Quentin Robidou.

Chaque jalon a son dossier, avec son code, ses données, ses résultats et son compte rendu. Les jalons 1 et 2 sont indépendants ; le jalon 3 réutilise le code du jalon 2.

| Dossier | Problème | Outil | Point d'entrée |
| --- | --- | --- | --- |
| [jalon1/](jalon1/) | Inv-MR-Sort exact : un modèle appris par programme linéaire mixte | Gurobi | [compte rendu](jalon1/README.md) |
| [jalon2/](jalon2/) | Inv-2-MR-Sort : deux segments, une partition et un modèle par segment | lincs (WPB) | [README](jalon2/README.md) |
| [jalon3/](jalon3/) | Retrouver le modèle de A malgré les données ajoutées par un agent malveillant | jalon 2 et lincs | [plan expérimental](jalon3/README.md) |
| [docs/](docs/) | Énoncé, réponses aux préliminaires, suivi des jalons | | [suivi](docs/suivi_projet.md) |

## Arborescence

```text
.
├── docs/            sujet.pdf, suivi_projet.md
├── jalon1/          scripts autonomes, sans paquet Python
│   ├── mrsort.py, benchmark.py, test_mrsort.py
│   ├── data/        dataset0.txt
│   ├── results/     résultats de dataset0 et du benchmark
│   └── rendu/       archive, PDF et LIRE_MOI du rendu
├── jalon2/          paquet Python `jalon2`
│   ├── apprentissage.py, algorithmes.py, experiences.py
│   ├── data/        72 CSV : type_a/, type_b/
│   ├── docs/        guide, audit, compte rendu de la version complète
│   ├── results/     simple/ (version actuelle), version_complete/ (branche jalon2/salhmed)
│   └── tests/       fixtures
└── jalon3/          plan expérimental, code à venir
```

## Installation

Python 3.14, depuis la racine du dépôt :

```bash
uv sync --locked
```

Le paquet `jalon2` est installé en mode éditable : `from jalon2.algorithmes import resoudre` fonctionne depuis n'importe quel dossier. Le jalon 3 suivra le même principe. Toutes les commandes des README se lancent depuis la racine.

## Commandes principales

```bash
# Jalon 1 : apprentissage sur dataset0 et tests (licence Gurobi requise).
.venv/bin/python jalon1/mrsort.py jalon1/data/dataset0.txt
.venv/bin/python -m unittest discover -v -s jalon1

# Jalon 2 : afficher le programme du pilote, sans aucun calcul.
.venv/bin/jalon2 jalon2/data --pilote --graines 0 1 --temps 10 --temps-appel 0.25 --lister
```

## Échéances

- Jalon 3 : dépôt sur Edunao au plus tard le 05/11/2026 à 23 h 59.
- Soutenance : 06/11/2026.
