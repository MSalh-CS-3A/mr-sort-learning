import csv
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier, export_text

from jalon3_attacks import ATTACKS, M_TRAIN, confidence, draw_problem, learn_lincs
from jalon3_defenses import DEFENSES, POISON_SHARES

# ------------------------------------------------------------------ réglages
N_MODELS = 60                 # modèles A tirés indépendamment pour chaque case d'évaluation
N_TRAIN = 30                  # jeux simulés par B pour chaque (attaque, proportion) ; 2 * N_TRAIN sans attaque
TREE_DEPTH = 5                # 13 classes (type d'attaque et proportion)
TREE_MIN_LEAF = 5
TRAIN_OUTPUT = Path("results_jalon3_detector_train.csv")
OUTPUT = Path("results_jalon3_hybrid.csv")
TRAIN_SEED = 3                # graine des simulations de B (apprentissage de l'arbre)
SEED = 5                      # graine de l'évaluation, différente de toutes les autres parties (et de la v1)
PHASE1 = Path("results_jalon3_defenses.csv")

FEATURES = ["n", "p", "conflict_share", "max_conflict_degree", "top_category_share", "extreme_category_share",
            "center_ratio", "single_criterion_accuracy", "lincs_fit"]


# ------------------------------------------------------------------ indicateurs calculés sur le jeu reçu
def single_criterion_accuracy(X, y, p):
    """Meilleure précision d'un classement à seuils sur un seul critère (catégorie croissante avec ce critère)."""
    best = 0.0
    for j in range(X.shape[1]):
        f = np.zeros(p)       # f[c] : bien classés au mieux, le dernier point étant mis dans la catégorie c
        for label in y[np.argsort(X[:, j])]:
            f = np.maximum.accumulate(f)
            f[label] += 1
        best = max(best, f.max())
    return best / len(y)


def features(X, y, n, p, model0):
    """Indicateurs du jeu reçu ; model0 est le MR-Sort appris par lincs sur tout le jeu."""
    dominates = (X[None, :, :] >= X[:, None, :]).all(axis=2)
    conflict = dominates & (y[None, :] < y[:, None])
    degree = (conflict | conflict.T).sum(axis=1)
    counts = np.bincount(y, minlength=p) / len(y)
    center = ((X >= 0.25) & (X <= 0.75)).all(axis=1).mean()
    return [n, p,
            (degree > 0).mean(),                    # part des points impliqués dans une violation de monotonie
            degree.max() / len(y),                  # concentration des violations sur un même point
            counts.max(),                           # part de la catégorie la plus fréquente
            max(counts[0], counts[p - 1]),          # part de la catégorie extrême la plus fréquente
            center / 0.5 ** n,                      # 1 si les points sont uniformes
            single_criterion_accuracy(X, y, p),
            (model0.predict(X) == y).mean()]        # ajustement d'un seul MR-Sort


def received_dataset(attack, share, rng):
    """Un problème tiré au hasard et le jeu que reçoit B (données de A et de C remélangées)."""
    n, p, X_a, y_a, X_test, y_test = draw_problem(rng)
    count = round(M_TRAIN * share / (1 - share))
    if attack == "none":
        X_c, y_c = np.empty((0, n)), np.empty(0, dtype=int)
    else:
        X_c, y_c = ATTACKS[attack](count, n, p, rng)
    X, y = np.vstack([X_a, X_c]), np.concatenate([y_a, y_c])
    order = rng.permutation(len(y))                    # B ne voit pas l'ordre d'arrivée
    return n, p, X[order], y[order], X_test, y_test


def cell_label(attack, share):
    """Classe prédite par l'arbre : le type d'attaque et la proportion."""
    return f"{attack}|{float(share):.3f}"


def best_defenses():
    """Redirection : pour chaque case (attaque, proportion), la défense de la phase 1 au meilleur accord moyen."""
    scores = {}
    with open(PHASE1, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (cell_label(row["attack"], row["poison_share"]), row["defense"])
            scores.setdefault(key, []).append(float(row["agreement"]))
    best = {}
    for (cell, defense), values in scores.items():
        if cell not in best or np.mean(values) > best[cell][1]:
            best[cell] = (defense, np.mean(values))
    return {cell: defense for cell, (defense, _) in best.items()}


# ------------------------------------------------------------------ apprentissage du détecteur (une seule fois)
def train_detector(n_train):
    """B simule lui-même le jeu (A tiré au hasard, chaque attaque connue) et apprend un arbre de décision qui
    prédit le type d'attaque à partir des indicateurs. Les simulations sont gardées dans TRAIN_OUTPUT."""
    rows = []
    if TRAIN_OUTPUT.exists():
        with open(TRAIN_OUTPUT, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    cells = [("none", 0.0)] * 2 + [(a, s) for a in ATTACKS for s in POISON_SHARES]
    if len(rows) < len(cells) * n_train:
        rng = np.random.default_rng(TRAIN_SEED)
        rows = []
        with open(TRAIN_OUTPUT, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FEATURES + ["attack", "poison_share"])
            writer.writeheader()
            for attack, share in cells:
                for _ in range(n_train):
                    n, p, X, y, _, _ = received_dataset(attack, share, rng)
                    model0 = learn_lincs(X, y, n, p, int(rng.integers(1 << 30)))
                    row = dict(zip(FEATURES, features(X, y, n, p, model0)))
                    row.update(attack=attack, poison_share=f"{share:.3f}")
                    writer.writerow(row)
                    rows.append(row)
                print(f"simulations : {attack} C={share:.0%} faites", flush=True)
    X_train = np.array([[float(r[k]) for k in FEATURES] for r in rows])
    y_train = np.array([cell_label(r["attack"], r["poison_share"]) for r in rows])
    tree = DecisionTreeClassifier(max_depth=TREE_DEPTH, min_samples_leaf=TREE_MIN_LEAF, random_state=0)
    cv = cross_val_score(tree, X_train, y_train, cv=5).mean()
    tree.fit(X_train, y_train)
    print(export_text(tree, feature_names=FEATURES, decimals=3))
    print(f"arbre : précision sur les simulations {tree.score(X_train, y_train):.1%}, "
          f"en validation croisée {cv:.1%}", flush=True)
    return tree


# ------------------------------------------------------------------ défense hybride
def hybrid(X, y, n, p, tree, redirect, rng):
    """Détecte le type d'attaque et la proportion, puis applique la défense correspondante.
    Renvoie (modèle, classe prédite)."""
    model0 = learn_lincs(X, y, n, p, int(rng.integers(1 << 30)))
    predicted = tree.predict(np.array([features(X, y, n, p, model0)]))[0]
    defense = redirect[predicted]
    model = model0 if defense == "none" else DEFENSES[defense](X, y, n, p, rng)   # D0 : model0 déjà appris
    return model, predicted


if __name__ == "__main__":
    n_models = int(sys.argv[1]) if len(sys.argv) > 1 else N_MODELS
    n_train = int(sys.argv[2]) if len(sys.argv) > 2 else N_TRAIN
    tree = train_detector(n_train)
    redirect = best_defenses()
    for cell, defense in redirect.items():
        print(f"redirection : {cell:22s} -> {defense}", flush=True)
    cells = [("none", 0.0)] + [(a, s) for a in ATTACKS for s in POISON_SHARES]
    fields = ["model", "n", "p", "attack", "poison_share", "predicted", "defense", "agreement", "time_s"]
    done = {}             # lignes déjà obtenues pour chaque case
    if OUTPUT.exists():   # reprise : une case n'est complétée que des modèles qui lui manquent
        with open(OUTPUT, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                done.setdefault((row["attack"], row["poison_share"]), []).append(row)
    model_id = sum(len(r) for r in done.values())
    rng = np.random.default_rng([SEED, model_id])   # à chaque reprise, de nouveaux modèles A (pas ceux déjà tirés)
    with open(OUTPUT, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not done:
            writer.writeheader()
        for attack, share in cells:
            previous = done.get((attack, f"{share:.3f}"), [])
            if len(previous) >= n_models:
                continue
            scores = [float(r["agreement"]) for r in previous]
            predictions = [r["predicted"] for r in previous]
            for _ in range(n_models - len(previous)):
                start = time.time()
                n, p, X, y, X_test, y_test = received_dataset(attack, share, rng)
                model_b, predicted = hybrid(X, y, n, p, tree, redirect, rng)
                agreement = (model_b.predict(X_test) == y_test).mean()
                writer.writerow({"model": model_id, "n": n, "p": p, "attack": attack,
                                 "poison_share": f"{share:.3f}", "predicted": predicted,
                                 "defense": redirect[predicted], "agreement": f"{agreement:.4f}",
                                 "time_s": f"{time.time() - start:.1f}"})
                f.flush()
                model_id += 1
                scores.append(agreement)
                predictions.append(predicted)
            type_detected = sum(pr.split("|")[0] == attack for pr in predictions)
            cell_detected = sum(pr == cell_label(attack, share) for pr in predictions)
            mean, half_width = confidence(scores)
            print(f"hybride {attack:15s} C={share:4.0%} : accord {mean:.1%} ± {half_width:.1%}, "
                  f"type détecté {type_detected}/{len(scores)}, type et proportion {cell_detected}/{len(scores)}", flush=True)
