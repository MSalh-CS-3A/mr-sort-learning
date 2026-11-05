"""Partie 3, phase 3 : meilleure réponse de C (à l'aveugle) face aux défenses de B, en partant de S3.

Chaque variante place des points étiquetés tous dans une catégorie extrême e (tirée au hasard, comme S3), mais
dans une boîte choisie en fonction de e : pour e = pire catégorie, la boîte [lo, hi]^n ; pour e = meilleure,
la boîte symétrique [1 - hi, 1 - lo]^n (les points contredisent alors A là où il les classe le plus haut, ou le
plus bas). S3 correspond à [0, 1] et S6 à [0,25 ; 0,75].

Usage : python jalon3_counter.py [modèles par case] [défenses séparées par des virgules] [variantes]
Chaque case (variante, défense, proportion) a ses propres modèles A, tirés indépendamment."""
import csv
import sys
import time
from pathlib import Path

import numpy as np

from jalon3_attacks import M_TRAIN, confidence, draw_problem
from jalon3_defenses import DEFENSES, POISON_SHARES
from jalon3_hybrid import best_defenses, hybrid, train_detector

# ------------------------------------------------------------------ réglages
N_MODELS = 20
OUTPUT = Path("results_jalon3_counter.csv")
SEED = 7                      # graine différente de toutes les autres parties


def extreme_box(lo, hi, mix_uniform=0.0):
    """Variante de S3 : catégorie extrême, points dans la boîte orientée ; une part mix_uniform des points
    reste uniforme sur [0, 1]^n."""
    def attack(count, n, p, rng):
        e = rng.choice([0, p - 1])
        a, b = (lo, hi) if e == 0 else (1 - hi, 1 - lo)
        X = rng.uniform(a, b, (count, n))
        uniform = rng.random(count) < mix_uniform
        X[uniform] = rng.random((uniform.sum(), n))
        return X, np.full(count, e)
    return attack


def upper_unanimous(lo=0.5, corner=0.85, corner_share=0.1):
    """Variante haute « non dictatoriale » : comme extreme_box(lo, 1), mais une part corner_share des points est
    placée dans le coin [corner, 1]^n et étiquetée à l'autre extrême. Les données de C sont alors celles d'un
    MR-Sort unanime (tous les critères au-dessus de corner), et plus celles d'un modèle constant, que l'heuristique
    à deux modèles apprend sous une forme dictatoriale que D3 rejette."""
    def attack(count, n, p, rng):
        e = rng.choice([0, p - 1])
        special = rng.random(count) < corner_share
        if e == 0:   # boîte haute étiquetée pire, sauf le coin [corner, 1]^n (meilleure) : unanimité au seuil corner
            X = rng.uniform(lo, 1, (count, n))
            X[special] = rng.uniform(corner, 1, (special.sum(), n))
            y = np.where((X >= corner).all(axis=1), p - 1, 0)
        else:        # boîte basse étiquetée meilleure, sauf si un critère est sous 1 - corner (pire) : unanimité
            X = rng.uniform(1 - corner, 1 - lo, (count, n))     # [0,15 ; 0,5]^n : tous étiquetés meilleure
            idx = np.flatnonzero(special)
            X[idx, rng.integers(n, size=len(idx))] = rng.uniform(0, 1 - corner, len(idx))
            y = np.where((X >= 1 - corner).all(axis=1), p - 1, 0)
        return X, y
    return attack


VARIANTS = {
    "extreme": extreme_box(0.0, 1.0),                         # S3, référence
    "extreme_shifted": extreme_box(0.25, 1.0),                # contredire A là où il classe haut (ou bas)
    "extreme_upper": extreme_box(0.5, 1.0),
    "extreme_center_shifted": extreme_box(0.4, 0.9),          # S6 décalé vers la zone contredite
    "extreme_mix": extreme_box(0.25, 0.75, mix_uniform=0.5),  # moitié S3, moitié S6
    "upper_unanimous": upper_unanimous(),                     # haute, mais non dictatoriale (contre D3)
}


def received(variant, share, rng):
    n, p, X_a, y_a, X_test, y_test = draw_problem(rng)
    count = round(M_TRAIN * share / (1 - share))
    X_c, y_c = VARIANTS[variant](count, n, p, rng)
    X, y = np.vstack([X_a, X_c]), np.concatenate([y_a, y_c])
    order = rng.permutation(len(y))                    # B ne voit pas l'ordre d'arrivée
    return n, p, X[order], y[order], X_test, y_test


if __name__ == "__main__":
    n_models = int(sys.argv[1]) if len(sys.argv) > 1 else N_MODELS
    defenses = sys.argv[2].split(",") if len(sys.argv) > 2 else ["none", "monotone_cleaning", "hybrid"]
    variants = sys.argv[3].split(",") if len(sys.argv) > 3 else list(VARIANTS)
    tree = train_detector(0) if "hybrid" in defenses else None      # arbre de la phase 2 (CSV déjà calculé)
    redirect = best_defenses()
    cells = [(v, d, s) for v in variants for d in defenses for s in POISON_SHARES]
    fields = ["model", "n", "p", "variant", "defense", "poison_share", "redirected", "agreement", "time_s"]
    done = {}
    if OUTPUT.exists():   # reprise : une case n'est complétée que des modèles qui lui manquent
        with open(OUTPUT, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                done.setdefault((row["variant"], row["defense"], row["poison_share"]), []).append(float(row["agreement"]))
    model_id = sum(len(s) for s in done.values())
    rng = np.random.default_rng([SEED, model_id])   # à chaque reprise, de nouveaux modèles A
    with open(OUTPUT, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not done:
            writer.writeheader()
        for variant, defense, share in cells:
            scores = done.get((variant, defense, f"{share:.3f}"), [])
            if len(scores) >= n_models:
                continue
            for _ in range(n_models - len(scores)):
                start = time.time()
                n, p, X, y, X_test, y_test = received(variant, share, rng)
                if defense == "hybrid":
                    model_b, predicted = hybrid(X, y, n, p, tree, redirect, rng)
                    redirected = redirect[predicted]
                else:
                    model_b, redirected = DEFENSES[defense](X, y, n, p, rng), ""
                agreement = (model_b.predict(X_test) == y_test).mean()
                writer.writerow({"model": model_id, "n": n, "p": p, "variant": variant, "defense": defense,
                                 "poison_share": f"{share:.3f}", "redirected": redirected,
                                 "agreement": f"{agreement:.4f}", "time_s": f"{time.time() - start:.1f}"})
                f.flush()
                model_id += 1
                scores.append(agreement)
            mean, half_width = confidence(scores)
            print(f"{variant:24s} {defense:18s} C={share:4.0%} : accord {mean:.1%} ± {half_width:.1%} "
                  f"({len(scores)} modèles)", flush=True)
