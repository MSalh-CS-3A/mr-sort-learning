import csv
import io
import sys
import time
from pathlib import Path

import numpy as np
import lincs.classification as lc

# ------------------------------------------------------------------ réglages
MAX_ITERATIONS = 8
MOVED_FRACTION = 0.10       # au plus 10 % des objets changent de segment par itération
MIN_SIZE = 0.15             # chaque segment garde au moins 15 % des objets

LINCS_MODELS = 9            # nombre de modèles en parallèle dans l'heuristique de lincs
LINCS_NO_PROGRESS = 10      # arrêt de lincs après 10 itérations sans progrès...
LINCS_SECONDS = 4.0         # ... ou après 4 s

SEED = 0


# ------------------------------------------------------------------ données
def load_dataset(csv_path):
    """Renvoie (problem, X, y) avec X de forme (m, n) et y les indices de catégorie (0 = pire)."""
    text = "kind: classification-problem\n" + (Path(csv_path).parent / "problem.yml").read_text(encoding="utf-8") # ajoute l'en-tête manquant pour que lincs puisse traiter le problème
    problem = lc.Problem.load(io.StringIO(text))
    with open(csv_path, encoding="utf-8") as f:
        alternatives = lc.Alternatives.load(problem, f)
    X = np.array([[p.real.value for p in a.profile] for a in alternatives.alternatives])
    y = np.array([a.category_index for a in alternatives.alternatives])
    return problem, X, y


# ------------------------------------------------------------------ modèle MR-Sort
class MRSort:
    """Modèle MR-Sort : profils b (p-1, n), poids w normalisés (somme 1), seuil lam."""

    def __init__(self, b, w, lam):
        self.b, self.w, self.lam = b, w, lam

    @classmethod
    def from_lincs(cls, model):
        """Convertit un modèle lincs (poids avec seuil de majorité à 1) en poids de somme 1 et seuil lam."""
        b = np.array([av.real_thresholds.thresholds for av in model.accepted_values]).T   # b contient les p-1 frontières, chacune définie par n réels : matrice (p-1, n)
        weights = np.array(model.sufficient_coalitions[0].weights.criterion_weights)
        total = weights.sum()
        return cls(b, weights / total, 1.0 / total) # lincs fixe le seuil à 1 : on ramène les poids à une somme de 1, et lambda = 1 / somme

    def concordances(self, X):
        """Poids de la coalition de chaque objet pour chaque profil : tableau (m, p-1)."""
        return np.stack([(X >= profile) @ self.w for profile in self.b], axis=1)

    def predict(self, X):
        return (self.concordances(X) >= self.lam).sum(axis=1)

    def error_and_margin(self, X, y):
        """Écart de catégorie |prédite - réelle| et marge de concordance par rapport à la catégorie réelle :
        marge = min( concordance(x, b^{k-1}) - lam , lam - concordance(x, b^k) )."""
        c = self.concordances(X)
        n_profiles = c.shape[1]
        margin = np.full(len(y), np.inf)
        low = y >= 1                       # x doit atteindre le profil b^{k-1}
        margin[low] = c[low, y[low] - 1] - self.lam 
        high = y <= n_profiles - 1         # x ne doit pas atteindre le profil b^k
        margin[high] = np.minimum(margin[high], self.lam - c[high, y[high]]) # marge négative : x mal classé (pénalité) ; marge positive : x bien classé (bonus)
        return np.abs(self.predict(X) - y), margin


def learn(problem, X, y, seed):
    """Apprend un modèle MR-Sort avec l'heuristique de lincs (LearnMrsortByWeightsProfilesBreed)."""
    alternatives = lc.Alternatives(problem, [
        lc.Alternative(f"x{k}", [lc.Performance(lc.Performance.Real(float(v))) for v in row], int(cat))
        for k, (row, cat) in enumerate(zip(X, y))])
    learning_set = lc.PreprocessedLearningSet(problem, alternatives)
    models = lc.LearnMrsortByWeightsProfilesBreed.ModelsBeingLearned(learning_set, models_count=LINCS_MODELS,
                                                                     random_seed=seed) # apprentissage de plusieurs modèles en parallèle
    profiles_init = lc.InitializeProfilesForProbabilisticMaximalDiscriminationPowerPerCriterion(learning_set, models)
    weights_opt = lc.OptimizeWeightsUsingGlop(learning_set, models)
    profiles_improve = lc.ImproveProfilesWithAccuracyHeuristicOnCpu(learning_set, models)
    breeding = lc.ReinitializeLeastAccurate(models, profiles_initialization_strategy=profiles_init,
                                            weights_optimization_strategy=weights_opt, count=LINCS_MODELS // 2) # à chaque itération, les modèles les moins performants repartent de zéro, ce qui peut permettre de sortir d'un optimum local
    termination = lc.TerminateWhenAny([
        lc.TerminateAtAccuracy(models, target_accuracy=len(y)),
        lc.TerminateAfterIterationsWithoutProgress(models, max_iterations_count=LINCS_NO_PROGRESS),
        lc.TerminateAfterSeconds(LINCS_SECONDS)]) # 3 cas d'arrêt : tous les objets bien classés, trop de tours sans progrès ou limite de temps atteinte
    model = lc.LearnMrsortByWeightsProfilesBreed(learning_set, models, profiles_init, weights_opt,
                                                 profiles_improve, breeding, termination).perform()
    return MRSort.from_lincs(model)


# ------------------------------------------------------------------ heuristique inv-2-MR-Sort
def evaluate(models, segment, X, y):
    """Qualité d'une partition : proportion d'objets bien classés par le modèle de leur segment,
    puis marge totale (critère secondaire)."""
    correct, margin = 0, 0.0
    for j in (0, 1):
        inside = segment == j
        e, g = models[j].error_and_margin(X[inside], y[inside])
        correct += (e == 0).sum()
        margin += g.sum() # marge totale : les éléments bien classés donnent une marge positive, les mal classés une marge négative
    return correct / len(y), margin


def alternate_learning(problem, X, y, segment, rng, log=None):
    """À partir d'une partition de départ, alterne apprentissage d'un modèle par segment (lincs) et
    réaffectation des objets au modèle qui les explique le mieux (écart de catégorie, puis marge).
    Renvoie la meilleure partition rencontrée."""
    m = len(y)
    min_size = int(np.ceil(MIN_SIZE * m))
    max_moves = max(1, int(MOVED_FRACTION * m))
    best = None

    for j in (0, 1):  # pour éviter un segment quasi vide, on s'assure que chaque segment contient au moins un certain pourcentage des éléments
        missing = min_size - (segment == j).sum()
        if missing > 0:
            others = np.flatnonzero(segment != j)
            segment[rng.choice(others, missing, replace=False)] = j

    for iteration in range(MAX_ITERATIONS):
        models = [learn(problem, X[segment == j], y[segment == j], int(rng.integers(1 << 30)))
                  for j in (0, 1)]
        score = evaluate(models, segment, X, y)
        if best is None or score > best[0]: # on compare non pas au modèle précédent, mais au meilleur modèle rencontré dans la boucle
            best = (score, segment.copy(), models)
        if log:
            log(f"    itération {iteration + 1} : {score[0]:.1%} bien classés, "
                f"segments {np.bincount(segment, minlength=2).tolist()}")

        # Métrique : écart de catégorie, puis marge (plus grande = mieux)
        e = np.empty((2, m))
        g = np.empty((2, m))
        for j in (0, 1):
            e[j], g[j] = models[j].error_and_margin(X, y)
        own, other, idx = segment, 1 - segment, np.arange(m)
        error_gain = e[own, idx] - e[other, idx]      # > 0 : l'autre modèle se trompe moins, il faut changer l'élément de segment
        margin_gain = g[other, idx] - g[own, idx]     # > 0 : l'autre modèle a une meilleure marge
        candidates = np.flatnonzero((error_gain > 0) | ((error_gain == 0) & (margin_gain > 1e-9)))
        if len(candidates) == 0: 
            break
        order = candidates[np.lexsort((-margin_gain[candidates], -error_gain[candidates]))][:max_moves] # priorité aux objets dont l'erreur baisse le plus, puis, à égalité, à ceux dont la marge augmente le plus

        sizes = np.bincount(segment, minlength=2)
        moved = 0
        for x in order:   # déplacement en respectant la taille minimale
            if sizes[segment[x]] - 1 >= min_size:
                sizes[segment[x]] -= 1
                segment[x] = 1 - segment[x]
                sizes[segment[x]] += 1
                moved += 1
        if moved == 0:
            break

    (accuracy, _), segment, models = best
    return {"accuracy": accuracy, "segment": segment, "models": models}


def inv_two_mrsort_random(problem, X, y, rng, log=None):
    """Partition de départ aléatoire : chaque objet est tiré à pile ou face."""
    segment = rng.integers(0, 2, len(y))
    return alternate_learning(problem, X, y, segment, rng, log)


def inv_two_mrsort_misclassified(problem, X, y, rng, log=None):
    """On suppose qu'un modèle MR-Sort unique ne classera probablement pas correctement tout le dataset, mais
    qu'il sera proche de l'un des deux modèles : sa partition bien classés / mal classés constitue donc un bon
    point de départ."""
    single = learn(problem, X, y, int(rng.integers(1 << 30)))
    misclassified = single.predict(X) != y
    result = alternate_learning(problem, X, y, misclassified.astype(int), rng, log)
    result["single_accuracy"] = 1 - misclassified.mean()
    return result


# ------------------------------------------------------------------ lancement
def run(csv_path, rng, verbose=False):
    """Lance les deux heuristiques sur un dataset et mesure le temps de chacune."""
    problem, X, y = load_dataset(csv_path)
    results = {}
    for name, method in (("random", inv_two_mrsort_random), ("misclassified", inv_two_mrsort_misclassified)):
        if verbose:
            print(f"Départ {name} :")
        start_time = time.time()
        results[name] = method(problem, X, y, rng, log=print if verbose else None)
        results[name]["time"] = time.time() - start_time
    results["n"], results["p"], results["m"] = X.shape[1], len(problem.ordered_categories), len(y)
    return results


if __name__ == "__main__":
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "Datasets-Step2") # on lance sur un seul dataset ou sur tout le dossier
    rng = np.random.default_rng(SEED) 

    if target.is_file(): # cas où l'on lance sur un seul dataset
        results = run(target, rng, verbose=True)
        print(f"\n1 modèle : {results['misclassified']['single_accuracy']:.1%}")
        for name in ("random", "misclassified"):
            result = results[name]
            print(f"\nDépart {name} : 2 modèles {result['accuracy']:.1%}, "
                  f"segments {np.bincount(result['segment']).tolist()} ({result['time']:.0f} s)")
            for j, model in enumerate(result["models"], start=1):
                print(f"Modèle {j} : lambda = {model.lam:.3f}, w = {np.round(model.w, 3).tolist()}")
                for h, profile in enumerate(model.b, start=1):
                    print(f"   b^{h} = {np.round(profile, 3).tolist()}")
        sys.exit(0)

    files = sorted(target.rglob("*.csv"))
    output = Path("results_step2.csv")
    done = set()
    if output.exists():   # reprise : on ne refait pas les datasets déjà traités
        with open(output, encoding="utf-8") as f:
            done = {row["file"] for row in csv.DictReader(f)}
    fields = ["file", "type", "n", "p", "m", "split", "noise", "single_accuracy",
              "random_accuracy", "random_time_s", "misclassified_accuracy", "misclassified_time_s"]
    with open(output, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not done:
            writer.writeheader()
        for k, path in enumerate(files, start=1):
            name = path.relative_to(target).as_posix()
            if name in done:
                continue
            results = run(path, rng)
            parts = path.stem.split("_")       # n0300_rep50-50_noise00
            writer.writerow({
                "file": name, "type": path.parts[-3], "n": results["n"], "p": results["p"], "m": results["m"],
                "split": parts[1][3:], "noise": int(parts[2][5:]),
                "single_accuracy": f"{results['misclassified']['single_accuracy']:.4f}",
                "random_accuracy": f"{results['random']['accuracy']:.4f}",
                "random_time_s": f"{results['random']['time']:.1f}",
                "misclassified_accuracy": f"{results['misclassified']['accuracy']:.4f}",
                "misclassified_time_s": f"{results['misclassified']['time']:.1f}"})
            f.flush()
            print(f"[{k}/{len(files)}] {name} : 1 modèle {results['misclassified']['single_accuracy']:.1%}, "
                  f"départ aléatoire {results['random']['accuracy']:.1%}, "
                  f"départ mal classés {results['misclassified']['accuracy']:.1%}", flush=True)
