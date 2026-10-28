# Jalon 2 - Inv-2-MR-Sort : version simple

Ce dossier reprend la branche `jalon2/simplifie` : une implémentation pédagogique des heuristiques. L'objectif est de lire les algorithmes, les comparer sur les CSV existants, puis choisir la méthode à présenter.

La version complète précédente, son MILP conjoint et son infrastructure restent disponibles sur la branche `jalon2/salhmed` au commit `2872c47`. Les données et résultats historiques sont conservés. **Aucun benchmark n'a été exécuté avec cette nouvelle version.**

## Trois fichiers à lire

1. [apprentissage.py](apprentissage.py) : lecture des données, prédiction et apprentissage lincs/WPB avec garde-fou.
2. [algorithmes.py](algorithmes.py) : initialisations, A0 à A4 et calcul de LG. Commencer par `resoudre`, puis lire la fonction de la méthode choisie.
3. [experiences.py](experiences.py) : boucles sur les fichiers, méthodes et graines ; export des résultats.

Le [guide court](docs/guide.md) décrit les algorithmes, les paramètres et les sorties. Le code est autonome vis-à-vis de l'ancienne architecture : aucun import de ses modules n'est nécessaire.

## Installation

Python 3.14 et les dépendances du verrou existant :

```bash
uv sync --locked
```

Le point d'entrée est `.venv/bin/jalon2`. On peut aussi utiliser `.venv/bin/python -m jalon2`.

## Lire le programme d'expériences avant de le lancer

```bash
.venv/bin/jalon2 jalon2/data --pilote --graines 0 1 --temps 10 --temps-appel 0.25 --lister
```

`--lister` affiche le nombre d'exécutions et leur budget nominal, sans apprentissage ni création de résultats. Sans précision de méthode, la comparaison utilise A0-uniforme, A1-uniforme, A1-GMM, A3-uniforme et A3-GMM.

## Essayer une seule méthode

```bash
.venv/bin/jalon2 jalon2/data/type_a/cr06_ca03/n0300_rep50-50_noise00.csv --methodes A1-gmm --graines 0 --temps 10 --temps-appel 0.25 --sortie jalon2/results/simple/essai_a1
```

Le dossier de sortie doit être nouveau. La commande crée un `resultats.csv` et, pour chaque exécution, les deux modèles, les affectations et la trace temporelle. Une exécution sans solution garde un LG vide dans le CSV.

## Comparer les méthodes

```bash
# Pilote : 12 fichiers × 5 méthodes × 2 graines = 120 exécutions.
.venv/bin/jalon2 jalon2/data --pilote --graines 0 1 --temps 10 --temps-appel 0.25 --sortie jalon2/results/simple/pilote

# Ajouter A2 et A4 : neuf combinaisons au total.
.venv/bin/jalon2 jalon2/data --pilote --toutes --graines 0 1 --temps 10 --temps-appel 0.25 --sortie jalon2/results/simple/pilote_complet --lister
```

Le pilote minimal représente environ vingt minutes nominales. Pour les 72 CSV, enlever `--pilote`. Aucun calcul n'est lancé automatiquement et aucune méthode gagnante n'est prédéfinie. Tu peux analyser les CSV avec les outils de ton choix et reprendre ensuite la fonction de la méthode retenue.

## Travail antérieur

- [Énoncé](../docs/sujet.pdf).
- [Audit des 72 CSV](docs/audit.md).
- [Bilan du benchmark de la version précédente](docs/compte_rendu.md) : résultats historiques, pas des mesures de cette simplification.
- [Jalon 1](../jalon1/README.md) : les scripts `mrsort.py`, `benchmark.py` et `test_mrsort.py` restent inchangés.

La suite de tests précédente du jalon 2 appartient à la branche de référence. Sur cette branche, la vérification effectuée lors de la simplification est limitée à la syntaxe Python ; les apprentissages, expériences et analyses sont laissés à ta lecture et à ton exécution.
