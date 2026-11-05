import csv
import sys
import time

import numpy as np
import lincs.classification as lc
from gurobipy import GRB, Model, quicksum

# ------------------------------------------------------------------ réglages
N_MODELS = 30                          # nombre de modèles A tirés
M_TRAIN = 300                          # données envoyées par A
M_TEST = 10000
POISON_SHARES = [0.0, 0.10, 0.25, 1 / 3, 0.50]   # part des données de C dans le dataset reçu par B
N_RANGE = (3, 6)                       # nombre de critères, tiré à chaque modèle
P_RANGE = (2, 4)                       # nombre de catégories, tiré à chaque modèle
TIME_LIMIT = 30.0                      # budget de chaque apprentissage, en secondes
EPS = 1e-4                             # petite constante de la question v (x_i < b_i), données dans [0, 1]
LINCS_MODELS = 9
LINCS_NO_PROGRESS = 20
SEED = 0


# ------------------------------------------------------------------ modèle MR-Sort
class MRSort:
    """Modèle MR-Sort : profils b (p-1, n), poids w de somme 1, seuil lam."""

    def __init__(self, b, w, lam):
        self.b, self.w, self.lam = b, w, lam

    def predict(self, X):
        return (np.stack([(X >= profile) @ self.w for profile in self.b], axis=1) >= self.lam - 1e-9).sum(axis=1)


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


# ------------------------------------------------------------------ apprentissage par B
def learn_lincs(X, y, n, p, seed):
    """Heuristique de lincs (Sobrie), arrêtée quand tout est bien classé, après LINCS_NO_PROGRESS itérations
    sans progrès ou après TIME_LIMIT secondes."""
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
        lc.TerminateAfterSeconds(TIME_LIMIT)])
    model = lc.LearnMrsortByWeightsProfilesBreed(learning_set, models, profiles_init, weights_opt,
                                                 profiles_improve, breeding, termination).perform()
    b = np.array([av.real_thresholds.thresholds for av in model.accepted_values]).T
    weights = np.array(model.sufficient_coalitions[0].weights.criterion_weights)
    if weights.sum() == 0:   # aucune coalition suffisante : tout va dans la pire catégorie
        return MRSort(b, np.full(n, 1 / n), np.inf), {}
    return MRSort(b, weights / weights.sum(), 1 / weights.sum()), {}


def learn_gurobi(X, y, n, p, seed):
    """Programme du jalon 1 (question vii, p catégories) : maximise la marge alpha."""
    m = len(y)
    M = 2.0                                          # majore |x_i - b_i| (x et b dans [0, 1 + EPS])
    mdl = Model("inv_mrsort_margin")
    mdl.Params.OutputFlag = 0
    mdl.Params.TimeLimit = TIME_LIMIT
    mdl.Params.Seed = seed % 2_000_000_000
    profiles = range(1, p)
    b = mdl.addVars(profiles, range(n), lb=0, ub=1 + EPS, name="b")
    w = mdl.addVars(n, lb=0, name="w")
    lam = mdl.addVar(lb=0, ub=1, name="lambda")
    alpha = mdl.addVar(lb=-GRB.INFINITY, name="alpha")
    mdl.setObjective(alpha, GRB.MAXIMIZE)
    mdl.addConstr(quicksum(w[i] for i in range(n)) == 1)
    for h in profiles:
        if h >= 2:
            for i in range(n):
                mdl.addConstr(b[h, i] >= b[h - 1, i])

    def concordance(k, h):
        terms = []
        for i in range(n):
            d = mdl.addVar(vtype=GRB.BINARY)
            wx = mdl.addVar(lb=0)
            mdl.addConstr(X[k, i] - b[h, i] >= M * (d - 1))       # delta = 1 <=> x_i >= b_i (question v)
            mdl.addConstr(X[k, i] - b[h, i] <= M * d - EPS)
            mdl.addConstr(wx <= w[i])                             # wx = w_i si delta = 1, 0 sinon (question vi)
            mdl.addConstr(wx <= d)
            mdl.addConstr(wx >= d + w[i] - 1)
            terms.append(wx)
        return quicksum(terms)

    for k in range(m):
        cat = int(y[k]) + 1                          # catégories numérotées de 1 à p dans le programme
        if cat >= 2:
            mdl.addConstr(concordance(k, cat - 1) - lam >= alpha)
        if cat <= p - 1:
            mdl.addConstr(lam - concordance(k, cat) >= alpha)
    mdl.optimize()
    info = {"gurobi_optimal": int(mdl.Status == GRB.OPTIMAL), "alpha": alpha.X if mdl.SolCount else np.nan}
    if mdl.SolCount == 0:
        return None, info
    model = MRSort(np.array([[b[h, i].X for i in range(n)] for h in profiles]),
                   np.array([w[i].X for i in range(n)]), lam.X)
    return model, info


LEARNERS = {"lincs": learn_lincs, "gurobi": learn_gurobi}


# ------------------------------------------------------------------ attaque S1 : bruit aléatoire
def noise_attack(count, n, p, rng):
    """Points uniformes dans [0, 1]^n, catégories tirées au hasard."""
    return rng.random((count, n)), rng.integers(0, p, count)


# ------------------------------------------------------------------ attaque S2 : un autre MR-Sort
def mrsort_attack(count, n, p, rng):
    """Points uniformes dans [0, 1]^n, classés par un MR-Sort tiré au hasard par C."""
    model_c = random_model(n, p, rng)
    X = rng.random((count, n))
    return X, model_c.predict(X)


ATTACKS = {"noise": noise_attack, "mrsort": mrsort_attack}


if __name__ == "__main__":
    n_models = int(sys.argv[1]) if len(sys.argv) > 1 else N_MODELS
    attack = sys.argv[2] if len(sys.argv) > 2 else "noise"
    rng = np.random.default_rng(SEED)
    fields = ["model", "n", "p", "poison_share", "learner", "agreement", "time_s", "gurobi_optimal", "alpha"]
    with open(f"results_jalon3_{attack}.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for k in range(n_models):
            n, p = int(rng.integers(N_RANGE[0], N_RANGE[1] + 1)), int(rng.integers(P_RANGE[0], P_RANGE[1] + 1))
            model_a = random_model(n, p, rng)
            X_a = rng.random((M_TRAIN, n))
            y_a = model_a.predict(X_a)
            X_test = rng.random((M_TEST, n))
            y_test = model_a.predict(X_test)
            X_c_pool, y_c_pool = ATTACKS[attack](M_TRAIN, n, p, rng)   # assez de points pour 50 %
            for share in POISON_SHARES:
                count = round(M_TRAIN * share / (1 - share))
                X = np.vstack([X_a, X_c_pool[:count]])
                y = np.concatenate([y_a, y_c_pool[:count]])
                order = rng.permutation(len(y))                    # B ne voit pas l'ordre d'arrivée
                X, y = X[order], y[order]
                seed = int(rng.integers(1 << 30))
                for name, learner in LEARNERS.items():
                    start = time.time()
                    model_b, info = learner(X, y, n, p, seed)
                    agreement = (model_b.predict(X_test) == y_test).mean() if model_b else np.nan
                    writer.writerow({"model": k, "n": n, "p": p, "poison_share": f"{share:.3f}", "learner": name,
                                     "agreement": f"{agreement:.4f}", "time_s": f"{time.time() - start:.1f}",
                                     "gurobi_optimal": info.get("gurobi_optimal", ""),
                                     "alpha": f"{info['alpha']:.4f}" if "alpha" in info else ""})
                    f.flush()
                    print(f"[modèle {k + 1}/{n_models}] n={n} p={p} C={share:.0%} {name:6s} : "
                          f"accord {agreement:.1%} ({time.time() - start:.0f} s)", flush=True)
