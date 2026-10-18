"""Exécutions identifiées par données/configuration/versions/code, reprenables."""

from __future__ import annotations

from dataclasses import asdict, replace
import hashlib
from importlib import metadata
import json
from pathlib import Path
import platform
import time

from threadpoolctl import threadpool_info, threadpool_limits

from .core import (Budget, Config, Exhausted, FitFailed, Seeds, fit_guarded,
                   predict, restore_solution, solution_payload)
from .data import Instance, digest, load_instance, write_json
from .milp import solve_joint_milp
from .search import SearchResult, solve


MINIMAL = (("A0", "uniform"), ("A1", "uniform"), ("A1", "gmm"),
           ("A3", "uniform"), ("A3", "gmm"))
EXTENDED = (("A0", "uniform"), *((a, i) for a in ("A1", "A2", "A3", "A4") for i in ("uniform", "gmm")))


def environment():
    packages = ("lincs", "gurobipy", "numpy", "scipy", "scikit-learn", "matplotlib", "threadpoolctl", "joblib")
    return {"python": platform.python_version(), "platform": platform.platform(),
            "packages": {p: metadata.version(p) for p in packages}, "threads": 1}


def code_hash():
    source = Path(__file__).parent
    hasher = hashlib.sha256()
    for path in sorted(source.glob("*.py")):
        hasher.update(path.name.encode())
        hasher.update(path.read_bytes())
    return hasher.hexdigest()


def identity(instance: Instance, config: Config, seed: int):
    value = {"dataset_path": str(Path(instance.dataset_path).resolve()),
             "dataset_hash": instance.dataset_hash, "problem_hash": instance.problem_hash,
             "config": asdict(config), "seed": seed, "environment": environment(),
             "code_hash": code_hash()}
    run_id = digest(json.dumps(value, sort_keys=True).encode())[:24]
    return run_id, value


def single_diagnostic(instance: Instance, config: Config, seed: int):
    budget, seeds = Budget(config.seconds, config.max_calls), Seeds(seed)
    best = None
    events, trace = [], []
    loss, predictions = None, None
    reason = "budget"
    with threadpool_limits(limits=1):
        while budget.available():
            try:
                model = fit_guarded(instance, range(instance.n), best, budget,
                                    seeds.next("wpb_single"), config, events)
                preds = predict(model, instance)
                candidate_loss = sum(a != b for a, b in zip(preds, instance.y))
                if best is None or candidate_loss < loss:
                    best, loss, predictions = model, candidate_loss, preds
                    trace.append({"time": budget.elapsed, "current_LG": loss, "best_LG": loss,
                                  "event": "single_diagnostic"})
                if not loss:
                    reason = "zero_loss"
                    break
            except Exhausted:
                break
            except FitFailed as exc:
                events.append({"event": "fit_failure", "message": str(exc)})
    return SearchResult(None, "ok" if best else "no_solution", reason, budget.elapsed,
                        trace, events, seeds.records, {"wpb_calls": budget.calls}, budget.overruns,
                        {"diagnostic": "single_model", "LG": loss,
                         "model": best.yaml if best else None,
                         "predictions": list(predictions) if predictions is not None else None})


def load_run(path: str | Path, instance: Instance):
    payload = json.loads(Path(path).read_text())
    key = payload["identity"]
    if key["dataset_hash"] != instance.dataset_hash or key["problem_hash"] != instance.problem_hash:
        raise ValueError("Les données ou le problème ont changé depuis cette exécution.")
    solution = restore_solution(payload["solution"], instance) if payload.get("solution") else None
    return payload, solution


def run_one(instance: Instance, config: Config, seed: int, output: str | Path,
            resume: bool = True, warm_start=None):
    run_id, key = identity(instance, config, seed)
    # Le point de départ influence le MILP et doit donc faire partie de l'identité.
    if warm_start is not None:
        key["warm_start_hash"] = digest(json.dumps(solution_payload(warm_start, instance), sort_keys=True).encode())
        run_id = digest(json.dumps(key, sort_keys=True).encode())[:24]
    folder = Path(output) / run_id
    result_path = folder / "result.json"
    if resume and result_path.exists():
        previous = json.loads(result_path.read_text())
        if previous.get("completed") and previous.get("identity") == key:
            load_run(result_path, instance)
            return previous, True
    base = {"schema_version": 1, "run_id": run_id, "identity": key,
            "dataset": {"path": instance.dataset_path, "hash": instance.dataset_hash,
                        "N": instance.n, "m": instance.m, "C": instance.C,
                        "category_names": instance.category_names, **instance.metadata},
            "method": config.heuristic, "initializer": config.initializer, "seed": seed,
            "completed": False, "status": "running"}
    write_json(result_path, base)
    try:
        if config.heuristic == "MILP":
            result = solve_joint_milp(instance, config, seed, warm_start)
        elif config.heuristic == "single":
            result = single_diagnostic(instance, config, seed)
        else:
            result = solve(instance, config, seed)
        # Gurobi peut absorber SIGINT et retourner INTERRUPTED sans lever
        # KeyboardInterrupt. Cette exécution doit rester à recalculer.
        if result.stop_reason == "interrupted":
            raise KeyboardInterrupt
        solution = solution_payload(result.best, instance) if result.best is not None else None
        if solution:
            restore_solution(solution, instance)
            for k, model in enumerate(result.best.models, 1):
                (folder / f"model{k}.yml").write_text(model.yaml)
            write_json(folder / "assignments.json", list(result.best.assignments))
        elif config.heuristic == "single" and result.extra.get("model"):
            (folder / "single_model.yml").write_text(result.extra["model"])
        write_json(folder / "trace.json", result.trace)
        with threadpool_limits(limits=1):
            pools = threadpool_info()
        payload = {**base, "completed": True, "status": result.status,
                   "stop_reason": result.stop_reason, "wall_time": result.wall_time,
                   "solution": solution, "trace": result.trace, "events": result.events,
                   "seed_chain": result.seeds, "counters": result.counters,
                   "overruns": result.overruns, "extra": result.extra,
                   "runtime_threadpools": pools}
        write_json(result_path, payload)
        return payload, False
    except KeyboardInterrupt:
        write_json(result_path, {**base, "status": "interrupted", "completed": False})
        raise
    except Exception as exc:
        write_json(result_path, {**base, "status": "failed", "completed": False,
                                 "error": repr(exc)})
        raise


def selected_paths(data_root: str | Path, pilot=False):
    names = {"n0300_rep50-50_noise00.csv", "n1200_rep75-25_noise10.csv"}
    return [p for p in sorted(Path(data_root).glob("*/*/*.csv")) if not pilot or p.name in names]


def batch(data_root, output, config: Config, seeds, methods=MINIMAL, pilot=False,
          resume=True, diagnostics=False, milp=False, limit=None):
    jobs = []
    for path in selected_paths(data_root, pilot):
        for method, initializer in methods:
            for seed in seeds:
                jobs.append((path, replace(config, heuristic=method, initializer=initializer), seed))
        if diagnostics:
            for seed in seeds:
                jobs.append((path, replace(config, heuristic="single", initializer="uniform"), seed))
        if milp and path.name.startswith("n0300"):
            for seed in seeds:
                jobs.append((path, replace(config, heuristic="MILP", initializer="uniform"), seed))
    if limit is not None:
        jobs = jobs[:limit]
    manifest = {"planned_jobs": len(jobs), "completed": 0, "reused": 0,
                "failed": 0, "entries": []}
    write_json(Path(output) / "manifest.json", manifest)
    cache = {}
    for number, (path, run_config, seed) in enumerate(jobs, 1):
        try:
            if path not in cache:
                started = time.monotonic()
                cache[path] = load_instance(path), time.monotonic()-started
            instance, load_time = cache[path]
            result, reused = run_one(instance, run_config, seed, output, resume)
            entry = {"run_id": result["run_id"], "dataset_path": str(path),
                     "method": run_config.heuristic, "initializer": run_config.initializer,
                     "seed": seed, "status": result["status"], "reused": reused,
                     "common_load_seconds": load_time,
                     "LG": result["solution"]["LG"] if result["solution"] else result["extra"].get("LG")}
            manifest["completed"] += 1
            manifest["reused"] += int(reused)
        except Exception as exc:
            entry = {"dataset_path": str(path), "method": run_config.heuristic,
                     "initializer": run_config.initializer, "seed": seed,
                     "status": "failed", "error": repr(exc)}
            manifest["failed"] += 1
        manifest["entries"].append(entry)
        write_json(Path(output) / "manifest.json", manifest)
        print(json.dumps({"progress": f"{number}/{len(jobs)}", **entry}, ensure_ascii=False), flush=True)
    return manifest
