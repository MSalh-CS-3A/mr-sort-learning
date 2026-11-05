"""Partie 4, phase 1 : les attaques informées de la partie 2 (C a accès aux données de A) contre la défense
hybride de B (détecteur appris une seule fois, puis redirection ; voir jalon3_hybrid.py).
S10 est inchangé : C simule B avec lincs seul pour évaluer ses individus.

Usage : python jalon3_informed_hybrid.py [modèles par case] [modèles par case pour S10]
Chaque case (stratégie, proportion) a ses propres modèles A, tirés indépendamment."""
import csv
import sys
import time
from pathlib import Path

import numpy as np

from jalon3_attacks import M_TRAIN, confidence, draw_problem, learn_lincs
from jalon3_defenses import POISON_SHARES
from jalon3_hybrid import best_defenses, hybrid, train_detector
from jalon3_informed import GA_EVAL_SIZE, INFORMED, shift_direction

# ------------------------------------------------------------------ réglages
N_MODELS = 60
N_GA_MODELS = 10              # S10, plus coûteuse
OUTPUT = Path("results_jalon3_informed_hybrid.csv")
SEED = 11                     # graine différente de toutes les autres parties

if __name__ == "__main__":
    n_models = int(sys.argv[1]) if len(sys.argv) > 1 else N_MODELS
    n_ga_models = int(sys.argv[2]) if len(sys.argv) > 2 else N_GA_MODELS
    tree = train_detector(0)                     # arbre de la phase 2 de la partie 3 (simulations déjà calculées)
    redirect = best_defenses()
    cells = [(s, share) for s in INFORMED for share in POISON_SHARES]
    fields = ["model", "n", "p", "a_hat_agreement", "strategy", "poison_share", "predicted", "defense",
              "agreement", "time_s"]
    done = {}
    if OUTPUT.exists():   # reprise : une case n'est complétée que des modèles qui lui manquent
        with open(OUTPUT, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                done.setdefault((row["strategy"], row["poison_share"]), []).append(row)
    model_id = sum(len(r) for r in done.values())
    rng = np.random.default_rng([SEED, model_id])   # à chaque reprise, de nouveaux modèles A
    with open(OUTPUT, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not done:
            writer.writeheader()
        for strategy, share in cells:
            target = n_ga_models if strategy == "optimized" else n_models
            previous = done.get((strategy, f"{share:.3f}"), [])
            if len(previous) >= target:
                continue
            scores = [float(r["agreement"]) for r in previous]
            defenses = [r["defense"] for r in previous]
            for _ in range(target - len(previous)):
                start = time.time()
                n, p, X_a, y_a, X_test, y_test = draw_problem(rng)
                a_hat = learn_lincs(X_a, y_a, n, p, int(rng.integers(1 << 30)))   # C infère Â
                a_hat_agreement = (a_hat.predict(X_test) == y_test).mean()
                delta = shift_direction(a_hat.predict(rng.random((GA_EVAL_SIZE, n))), p)
                count = round(M_TRAIN * share / (1 - share))
                X_c, y_c = INFORMED[strategy](count, a_hat, delta, X_a, y_a, n, p, rng)
                X, y = np.vstack([X_a, X_c]), np.concatenate([y_a, y_c])
                order = rng.permutation(len(y))                                # B ne voit pas l'ordre d'arrivée
                model_b, predicted = hybrid(X[order], y[order], n, p, tree, redirect, rng)
                agreement = (model_b.predict(X_test) == y_test).mean()
                writer.writerow({"model": model_id, "n": n, "p": p, "a_hat_agreement": f"{a_hat_agreement:.4f}",
                                 "strategy": strategy, "poison_share": f"{share:.3f}", "predicted": predicted,
                                 "defense": redirect[predicted], "agreement": f"{agreement:.4f}",
                                 "time_s": f"{time.time() - start:.1f}"})
                f.flush()
                model_id += 1
                scores.append(agreement)
                defenses.append(redirect[predicted])
            mean, half_width = confidence(scores)
            used = ", ".join(f"{d} {defenses.count(d)}" for d in sorted(set(defenses)))
            print(f"hybride {strategy:15s} C={share:4.0%} : accord {mean:.1%} ± {half_width:.1%} "
                  f"({len(scores)} modèles ; redirections : {used})", flush=True)
