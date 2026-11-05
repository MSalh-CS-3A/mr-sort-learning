import csv
import sys
import time

import numpy as np

from jalon3_attacks import M_TRAIN, POISON_SHARES, confidence, draw_problem, learn_lincs, poisoned_agreement

# ------------------------------------------------------------------ réglages
N_MODELS = 60                 # modèles A par case pour les stratégies sans optimisation
N_GA_MODELS = 10              # modèles A par case pour l'optimisation S10 (plus coûteuse : environ 1 h 10 au total)
FRONTIER_SIGMA = 0.1          # S9 : écart-type des points autour d'un profil
GA_POPULATION = 10
GA_GENERATIONS = 7
GA_EVAL_SIZE = 2000           # points tirés par C pour évaluer un individu (étiquetés par Â)
GA_LINCS_SECONDS = 5.0        # budget de lincs pendant l'optimisation (B garde 30 s pour le score final)
SEED = 0


# ------------------------------------------------------------------ outils
def shift_direction(labels, p):
    """Sens du décalage (+1 ou -1) qui laisse le moins d'étiquettes bloquées à une extrémité."""
    return 1 if (labels < p - 1).sum() >= (labels > 0).sum() else -1


def shift(labels, delta, p):
    """Décale chaque étiquette d'une catégorie dans le sens delta, ou dans l'autre sens si elle est déjà au bout :
    chaque étiquette envoyée par C contredit donc celle de Â."""
    shifted = labels + delta
    out = (shifted < 0) | (shifted > p - 1)
    shifted[out] = labels[out] - delta
    return shifted


# ------------------------------------------------------------------ attaques avec accès aux données de A
def shifted_model(count, a_hat, delta, X_a, y_a, n, p, rng):
    """S7 : points uniformes étiquetés par Â décalé d'une catégorie."""
    X = rng.random((count, n))
    return X, shift(a_hat.predict(X), delta, p)


def shifted_copy(count, a_hat, delta, X_a, y_a, n, p, rng):
    """S8 : les points mêmes de A, avec leur étiquette décalée d'une catégorie."""
    idx = rng.permutation(len(y_a))[:count]
    return X_a[idx].copy(), shift(y_a[idx], delta, p)


def frontier(count, a_hat, delta, X_a, y_a, n, p, rng):
    """S9 : points tirés autour des profils de Â, étiquetés du côté opposé à celui que Â leur donne
    (au-dessus du profil si delta = +1, en dessous si delta = -1)."""
    h = rng.integers(1, p, count)                              # profil visé b^h, entre les catégories h-1 et h
    X = np.clip(a_hat.b[h - 1] + rng.normal(0, FRONTIER_SIGMA, (count, n)), 0, 1)
    return X, np.where(delta > 0, h, h - 1)


def box_points(individual, count, a_hat, n, p, rng):
    """Points d'un individu de S10 : uniformes dans la boîte [c - r, c + r], étiquettes de Â décalées."""
    c, r, delta = individual
    X = np.clip(rng.uniform(c - r, c + r, (count, n)), 0, 1)
    return X, shift(a_hat.predict(X), delta, p)


def optimized(count, a_hat, delta, X_a, y_a, n, p, rng):
    """S10 : algorithme génétique sur (centre c, demi-largeur r, sens du décalage) de la boîte où C place ses
    points. Chaque individu est évalué en simulant B (lincs) et en mesurant l'accord entre le modèle appris et Â,
    avec de nouveaux points, une nouvelle graine lincs et de nouveaux points d'évaluation à chaque fois."""
    X_eval = rng.random((GA_EVAL_SIZE, n))
    y_eval = a_hat.predict(X_eval)

    def fitness(individual):
        X_c, y_c = box_points(individual, count, a_hat, n, p, rng)
        model_b = learn_lincs(np.vstack([X_a, X_c]), np.concatenate([y_a, y_c]), n, p, int(rng.integers(1 << 30)),
                              seconds=GA_LINCS_SECONDS)
        return (model_b.predict(X_eval) == y_eval).mean()

    def random_individual():
        return (rng.random(n), rng.uniform(0.05, 0.5), int(rng.choice([-1, 1])))

    def mutate(individual):
        c, r, d = individual
        c = np.clip(c + rng.normal(0, 0.1, n), 0, 1)
        r = float(np.clip(r + rng.normal(0, 0.05), 0.05, 0.5))
        return (c, r, -d if rng.random() < 0.1 else d)

    def crossover(a, b):
        mask = rng.random(n) < 0.5
        return (np.where(mask, a[0], b[0]), a[1] if rng.random() < 0.5 else b[1], a[2] if rng.random() < 0.5 else b[2])

    # population initiale : S7 (tout l'espace), une boîte centrale (proche de S6), le reste au hasard
    population = [(np.full(n, 0.5), 0.5, delta), (np.full(n, 0.5), 0.25, delta)]
    population += [random_individual() for _ in range(GA_POPULATION - 2)]
    scores = [fitness(ind) for ind in population]
    for _ in range(GA_GENERATIONS):
        order = np.argsort(scores)                              # plus l'accord est bas, meilleur est l'individu
        children = [population[i] for i in order[:2]]          # élitisme : on garde les deux meilleurs
        child_scores = [scores[i] for i in order[:2]]
        while len(children) < GA_POPULATION:
            parents = [min(rng.choice(len(population), 3, replace=False), key=lambda i: scores[i]) for _ in range(2)]
            child = mutate(crossover(population[parents[0]], population[parents[1]]))
            children.append(child)
            child_scores.append(fitness(child))
        population, scores = children, child_scores
    best = population[int(np.argmin(scores))]
    return box_points(best, count, a_hat, n, p, rng)


INFORMED = {"shifted_model": shifted_model, "shifted_copy": shifted_copy, "frontier": frontier,
            "optimized": optimized}


if __name__ == "__main__":
    n_models = int(sys.argv[1]) if len(sys.argv) > 1 else N_MODELS
    n_ga_models = int(sys.argv[2]) if len(sys.argv) > 2 else N_GA_MODELS
    rng = np.random.default_rng(SEED + 1)        # autre graine que la partie 1 : d'autres modèles A
    # une case = une stratégie et une proportion ; chaque case a ses propres modèles A, tirés indépendamment.
    # La référence sans attaque et les stratégies à l'aveugle sont dans results_jalon3_attacks.csv (partie 1).
    fields = ["model", "n", "p", "a_hat_agreement", "strategy", "poison_share", "agreement", "time_s"]
    with open("results_jalon3_informed.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        model_id = 0
        for strategy, attack in INFORMED.items():
            for share in POISON_SHARES:
                scores = []
                for _ in range(n_ga_models if strategy == "optimized" else n_models):
                    start = time.time()
                    n, p, X_a, y_a, X_test, y_test = draw_problem(rng)
                    a_hat = learn_lincs(X_a, y_a, n, p, int(rng.integers(1 << 30)))   # C infère Â
                    a_hat_agreement = (a_hat.predict(X_test) == y_test).mean()
                    delta = shift_direction(a_hat.predict(rng.random((GA_EVAL_SIZE, n))), p)
                    count = round(M_TRAIN * share / (1 - share))
                    X_c, y_c = attack(count, a_hat, delta, X_a, y_a, n, p, rng)
                    agreement = poisoned_agreement(X_a, y_a, X_c, y_c, X_test, y_test, n, p, rng)
                    writer.writerow({"model": model_id, "n": n, "p": p, "a_hat_agreement": f"{a_hat_agreement:.4f}",
                                     "strategy": strategy, "poison_share": f"{share:.3f}",
                                     "agreement": f"{agreement:.4f}", "time_s": f"{time.time() - start:.1f}"})
                    f.flush()
                    model_id += 1
                    scores.append(agreement)
                if scores:
                    mean, half_width = confidence(scores)
                    print(f"{strategy:15s} C={share:4.0%} : accord {mean:.1%} ± {half_width:.1%} "
                          f"({len(scores)} modèles)", flush=True)
