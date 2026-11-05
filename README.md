# Projet SDP - Apprentissage de modèles MR-Sort

Projet SDP, CentraleSupélec, mention IA, 2026-2027. Groupe : Mohamed SALH, Mohamed Chebli, Quentin Robidou.

Chaque jalon a son dossier, avec son code, ses données, ses résultats et son compte rendu. Les jalons 1 et 2 sont indépendants ; le jalon 3 réutilise le code du jalon 2.

| Dossier | Problème | Outil | Point d'entrée |
| --- | --- | --- | --- |
| [jalon1/](jalon1/) | Inv-MR-Sort exact : un modèle appris par programme linéaire mixte | Gurobi | [compte rendu](jalon1/README.md) |
| [jalon2/](jalon2/) | Inv-2-MR-Sort : deux segments, une partition et un modèle par segment | lincs (WPB) | [README](jalon2/README.md) (version officielle) |
| [jalon3/](jalon3/) | Retrouver le modèle de A malgré les données ajoutées par un agent malveillant | jalon 2 et lincs | [README](jalon3/README.md) |
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
├── jalon2/          paquet Python `jalon2`, version officielle (Quentin)
│   ├── jalon2_deux_mrsort.py, validation_jalon2.py
│   ├── data/        72 CSV : type_a/, type_b/
│   ├── results/     résultats sur les 72 CSV et validation synthétique
│   └── variante_a0_a4/   autre version (heuristiques A0-A4), avec ses docs et résultats
└── jalon3/          paquet Python `jalon3`
    ├── interface.py, simulation.py, experiences.py, analyse.py
    ├── docs/        protocole expérimental uniforme-v1
    ├── results/     campagnes, modèles, données et figures
    ├── hackers/     stratégies de H, un fichier par personne
    ├── defenses/    stratégies de B, un fichier par personne
    └── tests/       contrats et invariants scientifiques
```

## Installation

Python 3.14, depuis la racine du dépôt :

```bash
uv sync --locked
```

Les paquets `jalon2` et `jalon3` sont installés en mode éditable : `from jalon2.jalon2_deux_mrsort import inv_two_mrsort_misclassified` fonctionne depuis n'importe quel dossier. Toutes les commandes des README se lancent depuis la racine.

## Commandes principales

```bash
# Jalon 1 : apprentissage sur dataset0 et tests (licence Gurobi requise).
.venv/bin/python jalon1/mrsort.py jalon1/data/dataset0.txt
.venv/bin/python -m unittest discover -v -s jalon1

# Jalon 2 (version officielle) : un fichier, avec le détail des itérations.
.venv/bin/python jalon2/jalon2_deux_mrsort.py jalon2/data/type_a/cr06_ca03/n0300_rep50-50_noise00.csv

# Jalon 3 : contrats, puis premier couple (H cohérent, B sans défense).
.venv/bin/python -m unittest discover -v -s jalon3/tests
.venv/bin/jalon3 --hackers mrsort_aleatoire --defenses naif --tailles 100 300 --graines 0 1 --sortie jalon3/results/essai
```

Le [protocole du jalon 3](jalon3/docs/protocole.md) fixe les distributions et les informations accessibles à H et B. Chaque campagne produit les données et modèles archivés, les résultats appariés et une figure par couple attaque/défense.

## Échéances

- Jalon 3 : dépôt sur Edunao au plus tard le 05/11/2026 à 23 h 59.
- Soutenance : 06/11/2026.
