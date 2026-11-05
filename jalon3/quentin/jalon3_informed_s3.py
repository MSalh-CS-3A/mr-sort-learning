"""Partie 4, phase 2 : S3 informée. C a accès aux données de A ; il place des points tous étiquetés dans une
catégorie extrême (comme S3) dans une boîte [c - r, c + r], et un algorithme génétique choisit le centre c, la
demi-largeur r et la catégorie (pire ou meilleure). Chaque individu est évalué en simulant B par lincs seul (pas par
la défense hybride) et en mesurant l'accord entre le modèle appris et Â, avec de nouveaux points, une nouvelle
graine et de nouveaux points d'évaluation à chaque fois (comme S10).
La population de départ contient S3, S6 et la variante « haute » de la partie 3 (dans les deux sens).
L'attaque est évaluée contre la défense hybride.

Usage : python jalon3_informed_s3.py [modèles par proportion]"""
import csv
import sys
import time
from pathlib import Path

import numpy as np

from jalon3_attacks import M_TRAIN, confidence, draw_problem, learn_lincs
from jalon3_defenses import POISON_SHARES
from jalon3_hybrid import best_defenses, hybrid, train_detector
from jalon3_informed import GA_EVAL_SIZE, GA_GENERATIONS, GA_LINCS_SECONDS, GA_POPULATION

# ------------------------------------------------------------------ réglages
N_MODELS = 10
OUTPUT = Path("results_jalon3_informed_s3.csv")
SEED = 13                     # graine différente de toutes les autres parties


def box_points(individual, count, n, p, rng):
    """Points d'un individu : uniformes dans [c - r, c + r] (dans [0, 1]^n), tous dans la catégorie extrême choisie
    (worst = True : pire catégorie, sinon meilleure)."""
    c, r, worst = individual
    X = np.clip(rng.uniform(c - r, c + r, (count, n)), 0, 1)
    return X, np.full(count, 0 if worst else p - 1)


def optimized_extreme(count, a_hat, X_a, y_a, n, p, rng):
    """Algorithme génétique sur (c, r, catégorie) ; mêmes réglages que S10."""
    X_eval = rng.random((GA_EVAL_SIZE, n))
    y_eval = a_hat.predict(X_eval)

    def fitness(individual):
        X_c, y_c = box_points(individual, count, n, p, rng)
        model_b = learn_lincs(np.vstack([X_a, X_c]), np.concatenate([y_a, y_c]), n, p, int(rng.integers(1 << 30)),
                              seconds=GA_LINCS_SECONDS)
        return (model_b.predict(X_eval) == y_eval).mean()

    def mutate(individual):
        c, r, worst = individual
        c = np.clip(c + rng.normal(0, 0.1, n), 0, 1)
        r = float(np.clip(r + rng.normal(0, 0.05), 0.05, 0.5))
        return (c, r, (not worst) if rng.random() < 0.1 else worst)

    def crossover(a, b):
        mask = rng.random(n) < 0.5
        return (np.where(mask, a[0], b[0]), a[1] if rng.random() < 0.5 else b[1], a[2] if rng.random() < 0.5 else b[2])

    half = lambda v: np.full(n, v)
    population = [(half(0.5), 0.5, True), (half(0.5), 0.5, False),       # S3, dans les deux sens
                  (half(0.75), 0.25, True), (half(0.25), 0.25, False),   # variante « haute » et son symétrique
                  (half(0.5), 0.25, True), (half(0.5), 0.25, False)]     # S6, dans les deux sens
    population += [(rng.random(n), rng.uniform(0.05, 0.5), bool(rng.random() < 0.5))
                   for _ in range(GA_POPULATION - len(population))]
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
    X_c, y_c = box_points(best, count, n, p, rng)
    return X_c, y_c, best


if __name__ == "__main__":
    n_models = int(sys.argv[1]) if len(sys.argv) > 1 else N_MODELS
    tree = train_detector(0)                     # arbre de la partie 3 (simulations déjà calculées)
    redirect = best_defenses()
    fields = ["model", "n", "p", "a_hat_agreement", "poison_share", "best_center_mean", "best_half_width",
              "best_category", "predicted", "defense", "agreement", "time_s"]
    done = {}
    if OUTPUT.exists():   # reprise : une proportion n'est complétée que des modèles qui lui manquent
        with open(OUTPUT, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                done.setdefault(row["poison_share"], []).append(float(row["agreement"]))
    model_id = sum(len(s) for s in done.values())
    rng = np.random.default_rng([SEED, model_id])   # à chaque reprise, de nouveaux modèles A
    with open(OUTPUT, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not done:
            writer.writeheader()
        for share in POISON_SHARES:
            scores = done.get(f"{share:.3f}", [])
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
                model_b, predicted = hybrid(X[order], y[order], n, p, tree, redirect, rng)
                agreement = (model_b.predict(X_test) == y_test).mean()
                writer.writerow({"model": model_id, "n": n, "p": p,
                                 "a_hat_agreement": f"{(a_hat.predict(X_test) == y_test).mean():.4f}",
                                 "poison_share": f"{share:.3f}", "best_center_mean": f"{c.mean():.3f}",
                                 "best_half_width": f"{r:.3f}", "best_category": "worst" if worst else "best",
                                 "predicted": predicted, "defense": redirect[predicted],
                                 "agreement": f"{agreement:.4f}", "time_s": f"{time.time() - start:.1f}"})
                f.flush()
                model_id += 1
                scores.append(agreement)
            mean, half_width = confidence(scores)
            print(f"hybride S3 informée C={share:4.0%} : accord {mean:.1%} ± {half_width:.1%} "
                  f"({len(scores)} modèles)", flush=True)
