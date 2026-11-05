import csv
import sys
import time
from pathlib import Path

import numpy as np
import lincs.classification as lc
import liblincs

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))   # racine du dépôt : paquet jalon2
from jalon2 import jalon2_deux_mrsort as two
from jalon3_attacks import ATTACKS, M_TRAIN, LincsMRSort, confidence, draw_problem, learn_lincs

# ------------------------------------------------------------------ réglages
N_MODELS = 20                 # modèles A tirés indépendamment pour chaque case (défense, attaque, proportion)
POISON_SHARES = [1 / 3, 0.50]
two.TIME_LIMIT = 30.0         # budget de l'heuristique à deux modèles du jalon 2 (90 s par défaut)
OUTPUT = Path("results_jalon3_defenses.csv")
SEED = 2


class ExactMRSort(two.MRSort):
    """Modèle du jalon 2 dont la classification reproduit exactement lincs (float32, voir LincsMRSort) : la
    conversion from_lincs du jalon 2 classe en double précision et rejette des coalitions que lincs accepte.
    Sert pour les modèles renvoyés par l'heuristique à deux modèles ET pendant l'heuristique (réaffectation des
    objets). Les concordances normalisées ne servent plus qu'à la marge, critère secondaire.
    Le fichier du jalon 2 n'est pas modifié : on remplace sa classe MRSort depuis ce script."""

    @classmethod
    def from_lincs(cls, model):
        b = np.array([av.real_thresholds.thresholds for av in model.accepted_values]).T
        weights = np.array(model.sufficient_coalitions[0].weights.criterion_weights)
        if weights.sum() == 0:   # aucune coalition suffisante : tout va dans la pire catégorie
            converted = cls(b, np.zeros(len(weights)), np.inf)
            converted.exact = None
            return converted
        converted = cls(b, weights / weights.sum(), 1.0 / weights.sum())
        converted.exact = LincsMRSort(b, weights)
        return converted

    def predict(self, X):
        return self.exact.predict(X) if self.exact is not None else np.zeros(len(X), dtype=int)


two.MRSort = ExactMRSort      # utilisée par two.learn, donc par toute l'heuristique à deux modèles


# ------------------------------------------------------------------ défenses
def no_defense(X, y, n, p, rng):
    """D0 (anti-S1) : apprendre avec lincs sans se défendre."""
    return learn_lincs(X, y, n, p, int(rng.integers(1 << 30)))


def monotone_cleaning(X, y, n, p, rng):
    """D2 (anti-S3, S5, S6) : retirer les objets impliqués dans des violations de monotonie (un objet qui en
    domine un autre sur tous les critères mais a une catégorie inférieure), en retirant à chaque fois celui qui
    en a le plus, jusqu'à ce qu'il n'en reste plus ; puis apprendre avec lincs."""
    dominates = (X[None, :, :] >= X[:, None, :]).all(axis=2)       # dominates[i, j] : x_j domine x_i
    conflict = dominates & (y[None, :] < y[:, None])
    conflict = conflict | conflict.T
    counts = conflict.sum(axis=1)
    keep = np.ones(len(y), dtype=bool)
    while counts.max() > 0:
        i = int(np.argmax(counts))
        keep[i] = False
        counts -= conflict[:, i]
        counts[i] = 0
        conflict[i, :] = conflict[:, i] = False
    return learn_lincs(X[keep], y[keep], n, p, int(rng.integers(1 << 30)))


def two_models(X, y, n, p, rng):
    """Heuristique à deux modèles du jalon 2 (départ modèle unique). Rarement, lincs refuse un modèle intermédiaire
    (DataValidationException « After a null threshold... ») : on relance alors l'heuristique avec de nouvelles
    graines, au plus 3 fois."""
    for attempt in range(3):
        try:
            problem = lc.generate_problem(n, p, int(rng.integers(1 << 30)))
            result = two.inv_two_mrsort_single_model(problem, X, y, rng)
            return result["models"], np.bincount(result["segment"], minlength=2)
        except liblincs.DataValidationException as error:
            print(f"  lincs a échoué ({error}), nouvel essai", flush=True)
    raise RuntimeError("heuristique à deux modèles : 3 échecs de lincs")


def keep_largest(models, sizes, rng):
    """Modèle du plus grand segment, au hasard en cas d'égalité."""
    if sizes[0] == sizes[1]:
        return models[int(rng.integers(2))]
    return models[int(np.argmax(sizes))]


def largest_segment(X, y, n, p, rng):
    """D1 (anti-S2) : deux modèles, garder celui du plus grand segment."""
    models, sizes = two_models(X, y, n, p, rng)
    return keep_largest(models, sizes, rng)


def reject_dictator(X, y, n, p, rng):
    """D3 (anti-S4) : deux modèles ; si un seul des deux est dictatorial (un critère suffit à atteindre lambda),
    garder l'autre, sinon garder celui du plus grand segment."""
    models, sizes = two_models(X, y, n, p, rng)
    dictator = [m.exact is not None and bool(m.exact.w32.max() >= np.float32(1)) for m in models]   # comme lincs
    if dictator[0] != dictator[1]:
        return models[dictator.index(False)]
    return keep_largest(models, sizes, rng)


DEFENSES = {"none": no_defense, "monotone_cleaning": monotone_cleaning,       # rapides d'abord
            "largest_segment": largest_segment, "reject_dictator": reject_dictator}


if __name__ == "__main__":
    n_models = int(sys.argv[1]) if len(sys.argv) > 1 else N_MODELS
    # défense par défense (les rapides d'abord) ; pour chacune, la référence sans attaque puis les attaques
    cells = [c for d in DEFENSES for c in [(d, "none", 0.0)] + [(d, a, s) for a in ATTACKS for s in POISON_SHARES]]
    fields = ["model", "n", "p", "defense", "attack", "poison_share", "agreement", "time_s"]
    done = {}             # scores déjà obtenus pour chaque case
    if OUTPUT.exists():   # reprise : une case n'est complétée que des modèles qui lui manquent
        with open(OUTPUT, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                done.setdefault((row["defense"], row["attack"], row["poison_share"]), []).append(float(row["agreement"]))
    model_id = sum(len(s) for s in done.values())
    rng = np.random.default_rng([SEED, model_id])   # à chaque reprise, de nouveaux modèles A (pas ceux déjà tirés)
    with open(OUTPUT, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not done:
            writer.writeheader()
        for defense, attack, share in cells:
            scores = done.get((defense, attack, f"{share:.3f}"), [])
            if len(scores) >= n_models:
                continue
            for _ in range(n_models - len(scores)):
                start = time.time()
                n, p, X_a, y_a, X_test, y_test = draw_problem(rng)
                count = round(M_TRAIN * share / (1 - share))
                if attack == "none":
                    X_c, y_c = np.empty((0, n)), np.empty(0, dtype=int)
                else:
                    X_c, y_c = ATTACKS[attack](count, n, p, rng)
                X, y = np.vstack([X_a, X_c]), np.concatenate([y_a, y_c])
                order = rng.permutation(len(y))                    # B ne voit pas l'ordre d'arrivée
                model_b = DEFENSES[defense](X[order], y[order], n, p, rng)
                agreement = (model_b.predict(X_test) == y_test).mean()
                writer.writerow({"model": model_id, "n": n, "p": p, "defense": defense, "attack": attack,
                                 "poison_share": f"{share:.3f}", "agreement": f"{agreement:.4f}",
                                 "time_s": f"{time.time() - start:.1f}"})
                f.flush()
                model_id += 1
                scores.append(agreement)
            mean, half_width = confidence(scores)
            print(f"{defense:18s} {attack:15s} C={share:4.0%} : accord {mean:.1%} ± {half_width:.1%} "
                  f"({len(scores)} modèles)", flush=True)
