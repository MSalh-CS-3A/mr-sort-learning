import csv
import sys
import time

import numpy as np
import lincs.classification as lc

# ------------------------------------------------------------------ réglages
N_MODELS = 60                          # nombre de modèles A tirés
M_TRAIN = 300                          # données envoyées par A
M_TEST = 10000
POISON_SHARES = [0.10, 0.25, 1 / 3, 0.50]   # part des données de C dans le dataset reçu par B
N_RANGE = (3, 6)                       # nombre de critères, tiré à chaque modèle et connu de C
P_RANGE = (2, 4)                       # nombre de catégories, tiré à chaque modèle et connu de C
LINCS_MODELS = 9
LINCS_NO_PROGRESS = 20
LINCS_SECONDS = 30.0
SEED = 0


# ------------------------------------------------------------------ modèle MR-Sort
class MRSort:
    """Modèle MR-Sort : profils b (p-1, n), poids w de somme 1, seuil lam."""

    def __init__(self, b, w, lam):
        self.b, self.w, self.lam = b, w, lam

    def predict(self, X):
        return (np.stack([(X >= profile) @ self.w for profile in self.b], axis=1) >= self.lam - 1e-9).sum(axis=1)


class LincsMRSort(MRSort):
    """MR-Sort appris par lincs, évalué exactement comme lincs : lincs travaille en simple précision (float32),
    compare les performances aux profils et additionne les poids critère par critère en float32, et déclare la
    coalition suffisante si la somme atteint 1. En double précision, une somme comme 3 x 0.33333299 vaut
    0.99999997 < 1 alors que lincs l'arrondit à 1 : le modèle évalué ne serait plus celui appris.
    w et lam (poids de somme 1, seuil 1 / somme) ne servent qu'à lire le modèle."""

    def __init__(self, b, raw_weights):
        total = float(raw_weights.sum())
        super().__init__(b, raw_weights / total, 1 / total)
        self.b32, self.w32 = b.astype(np.float32), raw_weights.astype(np.float32)

    def predict(self, X):
        X32 = X.astype(np.float32)
        categories = np.zeros(len(X), dtype=int)
        for profile in self.b32:
            weight = np.zeros(len(X), dtype=np.float32)
            for i in range(len(self.w32)):
                weight += np.where(X32[:, i] >= profile[i], self.w32[i], np.float32(0))
            categories += weight >= np.float32(1)
        return categories


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


def learn_lincs(X, y, n, p, seed, seconds=LINCS_SECONDS):
    """B apprend un MR-Sort avec l'heuristique de lincs (Sobrie), sans se défendre."""
    problem = lc.generate_problem(n, p, seed)    # critères croissants dans [0, 1]
    alternatives = lc.Alternatives(problem, [
        lc.Alternative(f"x{k}", [lc.Performance(lc.Performance.Real(float(v))) for v in row], int(cat))
        for k, (row, cat) in enumerate(zip(X, y))])
    learning_set = lc.PreprocessedLearningSet(problem, alternatives)
    models = lc.LearnMrsortByWeightsProfilesBreed.ModelsBeingLearned(learning_set, models_count=LINCS_MODELS,
                                                                     random_seed=seed)
    profiles_init = lc.InitializeProfilesForProbabilisticMaximalDiscriminationPowerPerCriterion(learning_set, models)
    weights_opt = lc.OptimizeWeightsUsingGlop(learning_set, models)
    profiles_improve = lc.ImproveProfilesWithAccuracyHeuristicOnCpu(learning_set, models)
    breeding = lc.ReinitializeLeastAccurate(models, profiles_initialization_strategy=profiles_init,
                                            weights_optimization_strategy=weights_opt, count=LINCS_MODELS // 2)
    termination = lc.TerminateWhenAny([
        lc.TerminateAtAccuracy(models, target_accuracy=len(y)),
        lc.TerminateAfterIterationsWithoutProgress(models, max_iterations_count=LINCS_NO_PROGRESS),
        lc.TerminateAfterSeconds(seconds)])
    model = lc.LearnMrsortByWeightsProfilesBreed(learning_set, models, profiles_init, weights_opt,
                                                 profiles_improve, breeding, termination).perform()
    b = np.array([av.real_thresholds.thresholds for av in model.accepted_values]).T
    weights = np.array(model.sufficient_coalitions[0].weights.criterion_weights)
    if weights.sum() == 0:   # aucune coalition suffisante : tout va dans la pire catégorie
        return MRSort(b, np.full(n, 1 / n), np.inf)
    return LincsMRSort(b, weights)


# ------------------------------------------------------------------ attaques (C ne connaît que n, p et [0, 1]^n)
def noise(count, n, p, rng):
    """S1 : points uniformes, catégories tirées au hasard."""
    return rng.random((count, n)), rng.integers(0, p, count)


def mrsort(count, n, p, rng):
    """S2 : points uniformes classés par un MR-Sort tiré au hasard par C."""
    X = rng.random((count, n))
    return X, random_model(n, p, rng).predict(X)


def extreme(count, n, p, rng):
    """S3 : points uniformes, tous dans la meilleure ou tous dans la pire catégorie (tirée au hasard)."""
    return rng.random((count, n)), np.full(count, rng.choice([0, p - 1]))


def dictator(count, n, p, rng):
    """S4 : points uniformes classés par un MR-Sort où un seul critère, tiré au hasard, décide de tout."""
    X = rng.random((count, n))
    w = np.zeros(n)
    w[rng.integers(n)] = 1
    b = np.sort(rng.random((p - 1, n)), axis=0)
    return X, MRSort(b, w, 1.0).predict(X)


def anti_monotone(count, n, p, rng):
    """S5 : points uniformes classés à l'envers d'un MR-Sort tiré au hasard (catégorie p - 1 - k)."""
    X = rng.random((count, n))
    return X, p - 1 - random_model(n, p, rng).predict(X)


def extreme_center(count, n, p, rng):
    """S6 : comme S3, mais avec des points au centre de l'espace, là où la catégorie d'un MR-Sort est
    incertaine (près des coins, elle est presque toujours la pire ou la meilleure)."""
    return rng.uniform(0.25, 0.75, (count, n)), np.full(count, rng.choice([0, p - 1]))


ATTACKS = {"noise": noise, "mrsort": mrsort, "extreme": extreme, "dictator": dictator,
           "anti_monotone": anti_monotone, "extreme_center": extreme_center}


# ------------------------------------------------------------------ évaluation
def draw_problem(rng):
    """Tire un nouveau problème : n, p, le modèle A, ses données d'entraînement et le jeu de test."""
    n, p = int(rng.integers(N_RANGE[0], N_RANGE[1] + 1)), int(rng.integers(P_RANGE[0], P_RANGE[1] + 1))
    model_a = random_model(n, p, rng)
    X_a, X_test = rng.random((M_TRAIN, n)), rng.random((M_TEST, n))
    return n, p, X_a, model_a.predict(X_a), X_test, model_a.predict(X_test)


def poisoned_agreement(X_a, y_a, X_c, y_c, X_test, y_test, n, p, rng):
    """B apprend sur les données de A et de C remélangées ; renvoie l'accord avec A sur le jeu de test."""
    X, y = np.vstack([X_a, X_c]), np.concatenate([y_a, y_c])
    order = rng.permutation(len(y))                                # B ne voit pas l'ordre d'arrivée
    model_b = learn_lincs(X[order], y[order], n, p, int(rng.integers(1 << 30)))
    return (model_b.predict(X_test) == y_test).mean()


def confidence(scores):
    """Moyenne et demi-largeur de l'intervalle de confiance à 95 %."""
    scores = np.asarray(scores)
    return scores.mean(), 1.96 * scores.std(ddof=1) / np.sqrt(len(scores))


if __name__ == "__main__":
    n_models = int(sys.argv[1]) if len(sys.argv) > 1 else N_MODELS
    rng = np.random.default_rng(SEED)
    # une case = une stratégie et une proportion ; chaque case a ses propres modèles A, tirés indépendamment
    cells = [("none", None, 0.0)] + [(s, a, share) for s, a in ATTACKS.items() for share in POISON_SHARES]
    fields = ["model", "n", "p", "strategy", "poison_share", "agreement", "time_s"]
    with open("results_jalon3_attacks.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        model_id = 0
        for strategy, attack, share in cells:
            scores = []
            for _ in range(n_models):
                start = time.time()
                n, p, X_a, y_a, X_test, y_test = draw_problem(rng)
                count = round(M_TRAIN * share / (1 - share))
                X_c, y_c = attack(count, n, p, rng) if attack else (np.empty((0, n)), np.empty(0, dtype=int))
                agreement = poisoned_agreement(X_a, y_a, X_c, y_c, X_test, y_test, n, p, rng)
                writer.writerow({"model": model_id, "n": n, "p": p, "strategy": strategy,
                                 "poison_share": f"{share:.3f}", "agreement": f"{agreement:.4f}",
                                 "time_s": f"{time.time() - start:.1f}"})
                f.flush()
                model_id += 1
                scores.append(agreement)
            mean, half_width = confidence(scores)
            print(f"{strategy:15s} C={share:4.0%} : accord {mean:.1%} ± {half_width:.1%}", flush=True)
