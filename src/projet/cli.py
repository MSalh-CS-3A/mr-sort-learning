"""Interface de commande ; aucune campagne n'est lancée à l'import."""

from __future__ import annotations

import argparse
from dataclasses import asdict, replace
import json
import os
from pathlib import Path
import sys
import tomllib

# Doit précéder les imports des bibliothèques natives (dont lincs/matplotlib).
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"
os.environ.setdefault("MPLCONFIGDIR", f"/tmp/projet-matplotlib-{os.getuid()}")

from .core import Config
from .data import audit, load_instance, write_json
from .runner import EXTENDED, MINIMAL, batch, load_run, run_one, selected_paths


def config_from_file(path, base=None):
    base = base or Config()
    if path is None:
        return base
    with Path(path).open("rb") as stream:
        raw = tomllib.load(stream)
    values = {}
    allowed_sections = {"budget", "wpb", "initialization", "search", "milp"}
    for section, settings in raw.items():
        if section not in allowed_sections or not isinstance(settings, dict):
            raise ValueError(f"Section TOML inconnue : {section}.")
        for name, value in settings.items():
            if name not in asdict(base) or name in values:
                raise ValueError(f"Paramètre inconnu ou dupliqué : {name}.")
            values[name] = value
    return replace(base, **values)


def positive_int(text):
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError("Un entier positif est requis.")
    return value


def seed_list(text):
    try:
        seeds = [int(part) for part in text.split(",")]
    except ValueError:
        raise argparse.ArgumentTypeError("Graines entières séparées par des virgules.")
    if not seeds or any(s < 0 for s in seeds) or len(set(seeds)) != len(seeds):
        raise argparse.ArgumentTypeError("Graines positives ou nulles, sans doublon.")
    return seeds


def parser():
    root = argparse.ArgumentParser(description="Inv-2-MR-Sort : audit, heuristiques et MILP conjoint.")
    subs = root.add_subparsers(dest="command", required=True)
    audit_parser = subs.add_parser("audit", help="Inventaire sans apprentissage.")
    audit_parser.add_argument("--data", type=Path, default=Path("data"))
    audit_parser.add_argument("--output", type=Path, default=Path("results/jalon2/audit.json"))
    analysis = subs.add_parser("analyze", help="Tableaux et figures depuis les résultats sauvegardés.")
    analysis.add_argument("input", type=Path)
    analysis.add_argument("--output", type=Path)
    for command in ("run", "pilot", "campaign"):
        sub = subs.add_parser(command)
        sub.add_argument("--config", type=Path)
        sub.add_argument("--output", type=Path)
        sub.add_argument("--seconds", type=float)
        sub.add_argument("--wpb-seconds", type=float)
        sub.add_argument("--milp-seconds", type=float)
        sub.add_argument("--max-calls", type=positive_int)
        sub.add_argument("--no-resume", action="store_true")
        if command == "run":
            sub.add_argument("dataset", type=Path)
            sub.add_argument("--problem", type=Path)
            sub.add_argument("--method", choices=("A0", "A1", "A2", "A3", "A4", "MILP", "single"))
            sub.add_argument("--initializer", choices=("uniform", "gmm"))
            sub.add_argument("--seed", type=int, default=0)
            sub.add_argument("--warm-start", type=Path, help="result.json d'une solution compatible (MILP seulement).")
        else:
            sub.add_argument("--data", type=Path, default=Path("data"))
            sub.add_argument("--seeds", type=seed_list)
            sub.add_argument("--profile", choices=("minimal", "extended"), default="minimal")
            sub.add_argument("--include-diagnostic", action="store_true")
            sub.add_argument("--include-milp", action="store_true")
            sub.add_argument("--limit", type=positive_int, help="Limiter le nombre d'exécutions, pour vérification.")
            sub.add_argument("--dry-run", action="store_true", help="Afficher le coût maximal sans exécuter.")
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "audit":
            result = audit(args.data)
            write_json(args.output, result)
            print(json.dumps({"csv_count": result["csv_count"], "valid_count": result["valid_count"],
                              "output": str(args.output)}))
            return 0 if result["csv_count"] and result["csv_count"] == result["valid_count"] else 1
        if args.command == "analyze":
            from .analysis import analyze
            output = args.output or args.input / "analysis"
            result = analyze(args.input, output)
            print(json.dumps({"runs": result["valid_two_model_runs"], "output": str(output)}))
            return 0
        base = Config(seconds=10, wpb_seconds=.25) if args.command in {"run", "pilot"} else Config()
        config = config_from_file(args.config, base)
        updates = {name: getattr(args, name) for name in ("seconds", "wpb_seconds", "milp_seconds", "max_calls")
                   if getattr(args, name) is not None}
        for name in ("heuristic", "initializer"):
            value = getattr(args, "method" if name == "heuristic" else name, None)
            if value is not None:
                updates[name] = value
        config = replace(config, **updates)
        output = args.output or Path("results/jalon2") / args.command
        if args.command == "run":
            if args.seed < 0:
                raise ValueError("La graine doit être positive ou nulle.")
            instance = load_instance(args.dataset, args.problem)
            warm = None
            if args.warm_start:
                if config.heuristic != "MILP":
                    raise ValueError("--warm-start est réservé au MILP conjoint.")
                _, warm = load_run(args.warm_start, instance)
                if warm is None:
                    raise ValueError("Le démarrage ne contient pas de solution à deux modèles.")
            result, reused = run_one(instance, config, args.seed, output, not args.no_resume, warm)
            print(json.dumps({"run_id": result["run_id"], "status": result["status"],
                              "LG": result["solution"]["LG"] if result["solution"] else result["extra"].get("LG"),
                              "wall_time": result["wall_time"], "reused": reused,
                              "result": str(output / result["run_id"] / "result.json")}, ensure_ascii=False))
            return 0 if result["status"] in {"ok", "license_limit"} else 1
        paths = selected_paths(args.data, pilot=args.command == "pilot")
        if not paths:
            raise ValueError("Aucun CSV correspondant au protocole.")
        methods = MINIMAL if args.profile == "minimal" else EXTENDED
        seeds = args.seeds if args.seeds is not None else ([0, 1] if args.command == "pilot" else list(range(5)))
        count = len(paths)*len(seeds)*(len(methods)+int(args.include_diagnostic))
        milp_jobs = sum(p.name.startswith("n0300") for p in paths)*len(seeds) if args.include_milp else 0
        total = count+milp_jobs
        if args.limit:
            total = min(total, args.limit)
        if args.dry_run:
            print(json.dumps({"datasets": len(paths), "seeds": seeds, "methods": methods,
                              "jobs": total, "config": asdict(config),
                              "maximum_hours_before_overheads": (min(count, total)*config.seconds + max(0, total-count)*config.milp_seconds)/3600,
                              "output": str(output)}, ensure_ascii=False, indent=2))
            return 0
        result = batch(args.data, output, config, seeds, methods, args.command == "pilot",
                       not args.no_resume, args.include_diagnostic, args.include_milp, args.limit)
        return 1 if result["failed"] else 0
    except KeyboardInterrupt:
        print("Interrompu ; les exécutions terminées seront reprises sans recalcul.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 2
