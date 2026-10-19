import statistics

import numpy as np
import lincs.classification as lc

from jalon2_deux_mrsort import MRSort, inv_two_mrsort_misclassified, inv_two_mrsort_random

CONFIGS = [(6, 3, 300, 0.5), (6, 3, 600, 0.5), (6, 3, 600, 0.75), (8, 4, 600, 0.5)]   # (n, p, m, part du segment 1)
TRIALS = 3
TEST_SIZE = 10000
SEED = 1
METHODS = (("random", inv_two_mrsort_random), ("misclassified", inv_two_mrsort_misclassified))


def random_model(n, p, rng):
    """Modèle MR-Sort tiré comme dans Leroy, Mousseau et Pirlot (2011)."""
    w = rng.random(n)
    w /= w.sum()
    lam = rng.uniform(0.5, 1)
    b, low = [], np.zeros(n)
    for h in range(1, p):
        low = rng.uniform(low, (h + 1) / p)
        b.append(low)
    return MRSort(np.array(b), w, lam)


def trial(n, p, m, share, rng):
    """Génère deux modèles M1', M2' et un learning set mélangé, lance les deux heuristiques sur les mêmes
    données et compare chacune aux vrais segments et aux vrais modèles."""
    problem = lc.generate_problem(n, p, int(rng.integers(1 << 30)))
    true_models = [random_model(n, p, rng), random_model(n, p, rng)]
    X = rng.random((m, n))
    true_segment = (rng.random(m) >= share).astype(int)
    y = np.where(true_segment == 0, true_models[0].predict(X), true_models[1].predict(X))
    T = rng.random((TEST_SIZE, n))
    # Objets discriminants : M1' et M2' leur donnent des catégories différentes. Seuls ceux-là permettent
    # de savoir de quel segment vient l'objet ; les autres sont expliqués aussi bien par les deux modèles.
    discriminant = true_models[0].predict(X) != true_models[1].predict(X)

    rows = {}
    for name, method in METHODS:
        result = method(problem, X, y, rng)
        segment = result["segment"]
        if (segment == true_segment).mean() < 0.5:     # numérotation des segments inversée
            segment, learned = 1 - segment, result["models"][::-1]
        else:
            learned = result["models"]
        agreements = [(true_models[j].predict(T) == learned[j].predict(T)).mean() for j in (0, 1)]
        discriminant_recovery = (segment[discriminant] == true_segment[discriminant]).mean()
        rows[name] = ((segment == true_segment).mean(), agreements, result["accuracy"],
                      discriminant_recovery, discriminant.mean())
    return rows


if __name__ == "__main__":
    rng = np.random.default_rng(SEED)
    print("n  p     m  seg1   départ          2 modèles  partition  partition (discr.)  part discr.  "
          "accord M1'/M1*  accord M2'/M2*")
    for n, p, m, share in CONFIGS:
        trials = [trial(n, p, m, share, rng) for _ in range(TRIALS)]
        for name, _ in METHODS:
            rows = [t[name] for t in trials]
            recovery = statistics.mean(r[0] for r in rows)
            agreement_1 = statistics.mean(r[1][0] for r in rows)
            agreement_2 = statistics.mean(r[1][1] for r in rows)
            two = statistics.mean(r[2] for r in rows)
            discr_recovery = statistics.mean(r[3] for r in rows)
            discr_share = statistics.mean(r[4] for r in rows)
            print(f"{n:<2d} {p:<2d} {m:5d}  {share:.0%}   {name:13s}   {two:8.1%}   {recovery:8.1%}   "
                  f"{discr_recovery:17.1%}   {discr_share:10.1%}   {agreement_1:13.1%}   {agreement_2:13.1%}",
                  flush=True)
