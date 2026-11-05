# Jalon 3 — version de Quentin : attaques par injection de données et défenses

Rapport : [rapport/sdp_jalon_3_ROBIDOU_SALH_CHEBLI.pdf](rapport/sdp_jalon_3_ROBIDOU_SALH_CHEBLI.pdf) (source : [rapport/rapport_jalon3.tex](rapport/rapport_jalon3.tex)).

A envoie à B des données classées par un MR-Sort ; B apprend un MR-Sort (lincs) ; C ajoute ses propres données pour
éloigner le modèle appris de celui de A. Le score d'une attaque est l'accord moyen entre A et B sur 10 000 points de
test (plus il est bas, meilleure est l'attaque). Chaque case (stratégie ou défense, proportion) a ses propres modèles A,
tirés indépendamment ; les tableaux donnent la moyenne et l'intervalle de confiance à 95 %.

Ces scripts sont autonomes : ils n'utilisent pas `interface.py` ni le tournoi de `jalon3/`, et ne sont pas chargés par
celui-ci. Ils réutilisent l'heuristique à deux modèles de [jalon2/jalon2_deux_mrsort.py](../../jalon2/jalon2_deux_mrsort.py)
(version avec budget de temps `TIME_LIMIT`, fixé ici à 30 s).

## Scripts et résultats

| Partie du rapport | Script | Résultats |
| --- | --- | --- |
| 1. Attaques à l'aveugle S1–S6 contre lincs (60 modèles) | `jalon3_attacks.py` | `results_jalon3_attacks.csv` |
| 1. Choix de l'algorithme de B (lincs ou Gurobi) | `jalon3_noise_test.py` | `results_jalon3_noise.csv`, `results_jalon3_mrsort.csv` |
| 2. Attaques informées S7–S10 (60 modèles, 10 pour S10) | `jalon3_informed.py` | `results_jalon3_informed.csv` |
| 3, phase 1. Défenses D0–D3 contre S0–S6 (20 modèles) | `jalon3_defenses.py` | `results_jalon3_defenses.csv` |
| 3, phase 2. Défense hybride : détecteur (arbre) puis redirection (60 modèles) | `jalon3_hybrid.py` | `results_jalon3_detector_train.csv`, `results_jalon3_hybrid.csv` |
| 3, phase 3. Variantes de S3 contre les défenses (20 modèles) | `jalon3_counter.py` | `results_jalon3_counter.csv` |
| 4, phase 1. Attaques informées contre l'hybride | `jalon3_informed_hybrid.py` | `results_jalon3_informed_hybrid.csv` |
| 4, phase 2. S3 informée (algorithme génétique) contre l'hybride | `jalon3_informed_s3.py` | `results_jalon3_informed_s3.csv` |
| 4, phase 3. S3 informée contre toutes les défenses | `jalon3_final.py` | `results_jalon3_final.csv` |

Chaque script écrit aussi un journal `journal_jalon3_*.txt` (sortie console des campagnes). Les scripts se lancent depuis
ce dossier, car ils lisent et écrivent leurs CSV dans le dossier courant :

```bash
cd jalon3/quentin
../../.venv/bin/python jalon3_attacks.py            # nombre de modèles par case en argument (60 par défaut)
../../.venv/bin/python jalon3_defenses.py 20
../../.venv/bin/python jalon3_hybrid.py 60 30       # modèles par case, simulations par situation pour l'arbre
```

Les scripts des défenses, de l'hybride et de la partie 4 reprennent là où ils s'étaient arrêtés : une case n'est
complétée que des modèles qui lui manquent, avec de nouveaux modèles A. Pour tout recalculer, supprimer d'abord le CSV
correspondant. Le détecteur de l'hybride réutilise `results_jalon3_detector_train.csv` s'il existe.

Durées indicatives : environ 1 h pour la partie 1, 1 h 30 pour la partie 2 (dont S10), 5 h pour la phase 1 de la
partie 3 (les défenses à deux modèles prennent 30 s par jeu), 2 h pour l'hybride, 1 à 3 h pour chaque phase de la
partie 4.

## Point technique : évaluer le modèle exactement comme lincs

lincs calcule en simple précision (float32) et déclare une coalition suffisante si la somme des poids atteint 1.
Recalculer la concordance en double précision change la décision de certains modèles (par exemple trois poids de
0,33333299). `LincsMRSort` (dans `jalon3_attacks.py`) et `ExactMRSort` (dans `jalon3_defenses.py`, qui remplace la classe
MR-Sort du jalon 2 sans modifier son fichier) reproduisent exactement le calcul de lincs : aucun désaccord sur
400 000 points de test.

## Dépendances

Celles du dépôt (`lincs==2.0.2`, `numpy`, `scikit-learn` pour l'arbre de décision de l'hybride). `jalon3_noise_test.py`
compare aussi à Gurobi et demande une licence ; aucun identifiant n'est stocké dans le code.
