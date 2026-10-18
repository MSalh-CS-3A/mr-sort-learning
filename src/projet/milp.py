"""MILP conjoint à marge : les affectations restent des variables libres.

Les indicateurs monotones sur les valeurs distinctes représentent toutes les
positions de profil sur l'entraînement, y compris le seuil lincs ``None``.
La marge de rejet restreint la formulation : aucune exactitude du problème
continu sans marge n'est annoncée.
"""

from __future__ import annotations

import math
import time

from lincs import classification as lc
from threadpoolctl import threadpool_limits

from .core import Config, Model, Seeds, Solution, evaluate
from .data import Instance
from .search import SearchResult


def solve_joint_milp(instance: Instance, config: Config, seed: int = 0,
                     warm_start: Solution | None = None) -> SearchResult:
    import gurobipy as gp
    from gurobipy import GRB

    if instance.n < 2:
        raise ValueError("Deux groupes non vides demandent au moins deux observations.")
    started = time.monotonic()
    events, trace = [], []
    seeds = Seeds(seed)
    solver_seed = seeds.next("milp")
    extra = {"formulation": "joint_rank_margin_v1", "score_margin": config.score_margin,
             "feasibility_tol": config.feasibility_tol, "integrality_tol": config.integrality_tol,
             "optimal_for_margin_formulation": False,
             "objective": None, "bound": None, "gap": None,
             "warm_start": "not_provided" if warm_start is None else "not_checked"}
    best = None
    status, reason = "no_solution", "no_incumbent"
    counters = {"wpb_calls": 0, "candidates_evaluated": 0}
    cap = config.milp_seconds

    def elapsed():
        return time.monotonic()-started

    try:
        with threadpool_limits(limits=1), gp.Env(empty=True) as env:
            env.setParam("OutputFlag", 0)
            env.start()
            with gp.Model("Inv2MRSort", env=env) as model:
                model.Params.Threads = 1
                model.Params.Seed = solver_seed
                model.Params.FeasibilityTol = config.feasibility_tol
                model.Params.IntFeasTol = config.integrality_tol
                model.Params.MIPGap = 0
                model.Params.MIPGapAbs = 0
                n, m, H = instance.n, instance.m, instance.C-1
                problem = instance.problem()
                domains = [c.real_values if c.is_real else c.integer_values for c in problem.criteria]
                values = [sorted({row[j] for row in instance.x}, reverse=d.is_decreasing)
                          for j, d in enumerate(domains)]
                ranks = [{v: r for r, v in enumerate(column)} for column in values]
                z = model.addVars(n, vtype=GRB.BINARY, name="group")
                errors = model.addVars(n, vtype=GRB.BINARY, name="error")
                weights = model.addVars(2, m, lb=0, ub=1, name="weight")
                model.addConstr(gp.quicksum(z.values()) >= 1)
                model.addConstr(gp.quicksum(z.values()) <= n-1)
                model.addConstr(z[0] == 0, name="global_symmetry")
                q, t = {}, {}
                for k in range(2):
                    for h in range(H):
                        for j in range(m):
                            if elapsed() >= cap:
                                raise TimeoutError("Budget épuisé pendant la construction.")
                            for r in range(len(values[j])):
                                key = k, h, j, r
                                q[key] = model.addVar(vtype=GRB.BINARY, name=f"q_{k}_{h}_{j}_{r}")
                                t[key] = model.addVar(lb=0, ub=1, name=f"t_{k}_{h}_{j}_{r}")
                                model.addConstr(t[key] <= weights[k, j])
                                model.addConstr(t[key] <= q[key])
                                model.addConstr(t[key] >= weights[k, j]+q[key]-1)
                                if r:
                                    model.addConstr(q[k, h, j, r-1] <= q[key])
                                if h:
                                    model.addConstr(q[key] <= q[k, h-1, j, r])
                eps = config.score_margin
                for i, category in enumerate(instance.y):
                    if i % 32 == 0 and elapsed() >= cap:
                        raise TimeoutError("Budget épuisé pendant la construction.")
                    for k in range(2):
                        assigned = z[i] if k else 1-z[i]
                        if category > 0:
                            lower = gp.quicksum(t[k, category-1, j, ranks[j][instance.x[i][j]]] for j in range(m))
                            # S>=0 : M=1 suffit pour désactiver la borne inférieure.
                            model.addConstr(lower >= assigned-errors[i])
                        if category < H:
                            upper = gp.quicksum(t[k, category, j, ranks[j][instance.x[i][j]]] for j in range(m))
                            # S<=m : cette borne est valide pour tous les poids.
                            model.addConstr(upper <= 1-eps+(m-1+eps)*(1-assigned+errors[i]))
                model.setObjective(gp.quicksum(errors.values()), GRB.MINIMIZE)
                model.update()
                extra.update(variables=model.NumVars, constraints=model.NumConstrs)

                if warm_start is not None:
                    warm = warm_start
                    if warm.assignments[0]:
                        warm = evaluate(instance, tuple(1-v for v in warm.assignments), warm.models[1], warm.models[0])
                    native = [md.native(instance) for md in warm.models]
                    ws, qs = {}, {}
                    valid = True
                    for k in range(2):
                        coalitions = native[k].sufficient_coalitions
                        if any(not c.is_weights for c in coalitions):
                            valid = False
                            break
                        raw = list(coalitions[0].weights.criterion_weights)
                        if any(list(c.weights.criterion_weights) != raw for c in coalitions):
                            valid = False
                            break
                        for j, weight in enumerate(raw):
                            ws[k, j] = min(1.0, weight)
                            accepted = native[k].accepted_values[j]
                            thresholds = (accepted.real_thresholds if problem.criteria[j].is_real else accepted.integer_thresholds).thresholds
                            for h, threshold in enumerate(thresholds):
                                for r, v in enumerate(values[j]):
                                    qs[k, h, j, r] = int(threshold is not None and
                                                        (v >= threshold if domains[j].is_increasing else v <= threshold))
                    for i, category in enumerate(instance.y):
                        if not valid:
                            break
                        k = warm.assignments[i]
                        if warm.predictions[k][i] != category:
                            continue
                        def warm_score(h):
                            return math.fsum(ws[k, j]*qs[k, h, j, ranks[j][instance.x[i][j]]] for j in range(m))
                        if category > 0 and warm_score(category-1) < 1:
                            valid = False
                        if category < H and warm_score(category) > 1-eps:
                            valid = False
                    if valid:
                        for i in range(n):
                            z[i].Start = warm.assignments[i]
                            errors[i].Start = int(warm.predictions[warm.assignments[i]][i] != instance.y[i])
                        for key, value in ws.items():
                            weights[key].Start = value
                        for key, value in qs.items():
                            q[key].Start = value
                            t[key].Start = value*ws[key[0], key[2]]
                        extra["warm_start"] = "provided_and_margin_valid"
                    else:
                        extra["warm_start"] = "skipped_incompatible_margin_or_family"
                remaining = cap-elapsed()
                if remaining <= 0:
                    raise TimeoutError("Budget épuisé avant la résolution.")
                model.Params.TimeLimit = remaining

                def callback(active, where):
                    if where == GRB.Callback.MIPSOL:
                        incumbent = int(round(active.cbGet(GRB.Callback.MIPSOL_OBJ)))
                        previous = min((row["best_LG"] for row in trace), default=instance.n+1)
                        if incumbent < previous:
                            # Trace de l'objectif du solveur, pas encore une validation lincs.
                            trace.append({"time": elapsed(), "current_LG": incumbent,
                                          "best_LG": incumbent, "event": "milp_incumbent_unvalidated"})
                model.optimize(callback)
                extra["solver_status"] = {GRB.OPTIMAL: "OPTIMAL", GRB.TIME_LIMIT: "TIME_LIMIT",
                                          GRB.INFEASIBLE: "INFEASIBLE", GRB.INTERRUPTED: "INTERRUPTED"}.get(model.Status, str(model.Status))
                reason = extra["solver_status"].lower()
                bound = model.ObjBound
                extra["bound"] = bound if math.isfinite(bound) else None
                if model.SolCount:
                    extra["objective"] = int(round(model.ObjVal))
                    extra["gap"] = model.MIPGap if math.isfinite(model.MIPGap) else None
                    models = []
                    for k in range(2):
                        accepted_values = []
                        for j in range(m):
                            thresholds = []
                            for h in range(H):
                                first = next((r for r in range(len(values[j])) if q[k, h, j, r].X > 0.5), None)
                                if first is None:
                                    threshold = None
                                elif first == 0:
                                    threshold = domains[j].min_value if domains[j].is_increasing else domains[j].max_value
                                else:
                                    threshold = values[j][first]
                                if threshold is not None and problem.criteria[j].is_integer:
                                    threshold = int(threshold)
                                thresholds.append(threshold)
                            cls = lc.AcceptedValues.RealThresholds if problem.criteria[j].is_real else lc.AcceptedValues.IntegerThresholds
                            accepted_values.append(lc.AcceptedValues(cls(thresholds)))
                        coalition = lc.SufficientCoalitions(lc.SufficientCoalitions.Weights(
                            [max(0.0, min(1.0, weights[k, j].X)) for j in range(m)]))
                        native_model = lc.Model(problem, accepted_values, [coalition]*H)
                        models.append(Model.capture(instance, native_model))
                    assignments = tuple(int(z[i].X > 0.5) for i in range(n))
                    best = evaluate(instance, assignments, *models)
                    bad_unrelaxed = [i for i in range(n) if errors[i].X < 0.5 and
                                     best.predictions[assignments[i]][i] != instance.y[i]]
                    extra["validation_unrelaxed_errors"] = bad_unrelaxed
                    extra["reconstructed_LG"] = best.loss
                    status = "invalid_numerical" if bad_unrelaxed else "ok"
                    extra["optimal_for_margin_formulation"] = model.Status == GRB.OPTIMAL and not bad_unrelaxed
                    trace.append({"time": elapsed(), "current_LG": best.loss,
                                  "best_LG": best.loss, "event": "milp_validated" if not bad_unrelaxed else "milp_invalid_numerical"})
    except TimeoutError as exc:
        reason = "construction_timeout"
        events.append({"event": reason, "message": str(exc)})
    except gp.GurobiError as exc:
        status = "license_limit" if exc.errno == 10010 else "solver_error"
        reason = status
        events.append({"event": status, "code": exc.errno, "message": str(exc)})
    except (ValueError, RuntimeError) as exc:
        status, reason = "invalid_numerical", "reconstruction_failed"
        events.append({"event": reason, "message": str(exc)})
    duration = elapsed()
    overrun = [{"allowed": cap, "elapsed": duration, "excess": duration-cap}] if duration > cap else []
    return SearchResult(best, status, reason, duration, trace, events, seeds.records, counters, overrun, extra)
