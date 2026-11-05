"""Partie 4, phase 3 : la S3 informée (jalon3_informed_s3.py) contre les défenses de la phase 1 de la partie 3
(D0, D2, D1, D3) ; le résultat contre l'hybride est dans results_jalon3_informed_s3.csv.

Usage : python jalon3_final.py [modèles par case]
Chaque case (défense, proportion) a ses propres modèles A, tirés indépendamment."""
import csv
import sys
import time
from pathlib import Path

import numpy as np

from jalon3_attacks import M_TRAIN, confidence, draw_problem, learn_lincs
from jalon3_defenses import DEFENSES, POISON_SHARES
from jalon3_informed_s3 import optimized_extreme

# ------------------------------------------------------------------ réglages
N_MODELS = 10
OUTPUT = Path("results_jalon3_final.csv")
SEED = 17                     # graine différente de toutes les autres parties

if __name__ == "__main__":
    n_models = int(sys.argv[1]) if len(sys.argv) > 1 else N_MODELS
    cells = [(d, s) for d in DEFENSES for s in POISON_SHARES]
    fields = ["model", "n", "p", "defense", "poison_share", "best_center_mean", "best_half_width", "best_category",
              "agreement", "time_s"]
    done = {}
    if OUTPUT.exists():   # reprise : une case n'est complétée que des modèles qui lui manquent
        with open(OUTPUT, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                done.setdefault((row["defense"], row["poison_share"]), []).append(float(row["agreement"]))
    model_id = sum(len(s) for s in done.values())
    rng = np.random.default_rng([SEED, model_id])   # à chaque reprise, de nouveaux modèles A
    with open(OUTPUT, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not done:
            writer.writeheader()
        for defense, share in cells:
            scores = done.get((defense, f"{share:.3f}"), [])
            if len(scores) >= n_models:
                continue
            for _ in range(n_models - len(scores)):
                start = time.time()
                n, p, X_a, y_a, X_test, y_test = draw_problem(rng)
                a_hat = learn_lincs(X_a, y_a, n, p, int(rng.integers(1 << 30)))   # C infère Â
                count = round(M_TRAIN * share / (1 - share))
                X_c, y_c, (c, r, worst) = optimized_extreme(count, a_hat, X_a, y_a, n, p, rng)
                X, y = np.vstack([X_a, X_c]), np.concatenate([y_a, y_c])
                order = rng.permutation(len(y))                                # B ne voit pas l'ordre d'arrivée
                model_b = DEFENSES[defense](X[order], y[order], n, p, rng)
                agreement = (model_b.predict(X_test) == y_test).mean()
                writer.writerow({"model": model_id, "n": n, "p": p, "defense": defense,
                                 "poison_share": f"{share:.3f}", "best_center_mean": f"{c.mean():.3f}",
                                 "best_half_width": f"{r:.3f}", "best_category": "worst" if worst else "best",
                                 "agreement": f"{agreement:.4f}", "time_s": f"{time.time() - start:.1f}"})
                f.flush()
                model_id += 1
                scores.append(agreement)
            mean, half_width = confidence(scores)
            print(f"S3 informée {defense:18s} C={share:4.0%} : accord {mean:.1%} ± {half_width:.1%} "
                  f"({len(scores)} modèles)", flush=True)
