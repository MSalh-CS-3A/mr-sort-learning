"""Lecture native lincs et audit, sans modification des données sources."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
from dataclasses import dataclass, field
import hashlib
from io import StringIO
import json
import math
from pathlib import Path
import re
from typing import Any, Iterable

from lincs import classification as lc


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class Instance:
    names: tuple[str, ...]
    x: tuple[tuple[float, ...], ...]
    y: tuple[int, ...]
    category_names: tuple[str, ...]
    problem_yaml: str
    dataset_path: str = "synthetic"
    dataset_hash: str = ""
    problem_hash: str = ""
    metadata: dict[str, Any] = field(default_factory=dict, compare=False)

    def __post_init__(self):
        p = self.problem()
        if not self.x or len(self.names) != len(self.x) or len(self.y) != len(self.x):
            raise ValueError("Dimensions de l'instance incohérentes ou jeu vide.")
        if len(set(self.names)) != self.n:
            raise ValueError("Les identifiants doivent être uniques dans un fichier.")
        if self.category_names != tuple(c.name for c in p.ordered_categories):
            raise ValueError("Catégories incohérentes avec le problème.")
        for row, label in zip(self.x, self.y):
            if len(row) != len(p.criteria) or not all(math.isfinite(v) for v in row):
                raise ValueError("Performances non finies ou dimension incorrecte.")
            if not 0 <= label < self.C:
                raise ValueError("Indice de catégorie hors domaine.")
            for v, c in zip(row, p.criteria):
                values = c.real_values if c.is_real else c.integer_values
                if not values.min_value <= v <= values.max_value:
                    raise ValueError("Performance hors domaine.")
        # Les fixtures ou utilisateurs de l'API peuvent construire une instance
        # sans fichier : son identité doit aussi dépendre des observations.
        if not self.dataset_hash:
            payload = {"names": self.names, "x": self.x, "y": self.y}
            object.__setattr__(self, "dataset_hash", digest(json.dumps(payload, sort_keys=True).encode()))
        if not self.problem_hash:
            object.__setattr__(self, "problem_hash", digest(self.problem_yaml.encode()))

    @property
    def n(self):
        return len(self.x)

    @property
    def m(self):
        return len(self.x[0])

    @property
    def C(self):
        return len(self.category_names)

    def problem(self):
        return lc.Problem.load(StringIO(self.problem_yaml))

    def alternatives(self, indices: Iterable[int] | None = None):
        p = self.problem()
        indices = range(self.n) if indices is None else indices
        return lc.Alternatives(p, [
            lc.Alternative(self.names[i], [
                lc.Performance(lc.Performance.Real(v)) if c.is_real
                else lc.Performance(lc.Performance.Integer(int(v)))
                for v, c in zip(self.x[i], p.criteria)
            ], self.y[i]) for i in indices
        ])


def normalized_problem(text: str) -> tuple[str, bool]:
    missing = not re.search(r"^kind\s*:", text, re.MULTILINE)
    return ("kind: classification-problem\n" + text if missing else text), missing


def load_instance(csv_path: str | Path, problem_path: str | Path | None = None) -> Instance:
    path = Path(csv_path)
    pp = Path(problem_path) if problem_path else path.parent / "problem.yml"
    raw_problem = pp.read_bytes()
    text, added_kind = normalized_problem(raw_problem.decode("utf-8-sig"))
    problem = lc.Problem.load(StringIO(text))
    if any(not (c.is_real or c.is_integer) for c in problem.criteria):
        raise ValueError("Cette version prend en charge les critères numériques uniquement.")
    if any(not ((c.real_values if c.is_real else c.integer_values).is_increasing
                or (c.real_values if c.is_real else c.integer_values).is_decreasing)
           for c in problem.criteria):
        raise ValueError("Critères non monotones non pris en charge.")
    raw = path.read_bytes()
    # Le schéma brut est contrôlé avant lincs : aucune colonne cachée n'entre
    # implicitement dans les critères ou dans l'apprentissage.
    reader = csv.DictReader(StringIO(raw.decode("utf-8-sig"), newline=""))
    expected = ["name", *(c.name for c in problem.criteria), "category"]
    if reader.fieldnames != expected:
        raise ValueError(f"Colonnes attendues : {expected}; reçues : {reader.fieldnames}.")
    rows = list(reader)
    if any(None in row or any(v is None or not v.strip() for v in row.values()) for row in rows):
        raise ValueError("Valeurs manquantes ou lignes de largeur incorrecte.")
    for row in rows:
        for criterion in problem.criteria:
            value = float(row[criterion.name])
            domain = criterion.real_values if criterion.is_real else criterion.integer_values
            if not math.isfinite(value) or not domain.min_value <= value <= domain.max_value:
                raise ValueError("Performance brute non finie ou hors domaine.")
    alts = lc.Alternatives.load(problem, StringIO(raw.decode("utf-8-sig")))
    x = tuple(tuple(float(v.real.value if v.is_real else v.integer.value)
                    for v in a.profile) for a in alts.alternatives)
    names = tuple(a.name for a in alts.alternatives)
    labels = tuple(a.category_index for a in alts.alternatives)
    match = re.fullmatch(r"n(\d+)_rep(\d+)-(\d+)_noise(\d+)", path.stem)
    meta: dict[str, Any] = {"type": path.parent.parent.name,
                            "configuration": path.parent.name,
                            "problem_path": str(pp), "kind_added_in_memory": added_kind}
    if match:
        meta.update(announced_n=int(match[1]), announced_ratio=f"{match[2]}-{match[3]}",
                    announced_noise=int(match[4]))
        if len(x) != meta["announced_n"]:
            raise ValueError("Nombre de lignes différent de la taille annoncée.")
    configuration = re.fullmatch(r"cr(\d+)_ca(\d+)", path.parent.name)
    if configuration and (len(problem.criteria), len(problem.ordered_categories)) != (int(configuration[1]), int(configuration[2])):
        raise ValueError("Dimensions différentes de la configuration annoncée.")
    return Instance(names, x, labels, tuple(c.name for c in problem.ordered_categories),
                    text, str(path), digest(raw), digest(raw_problem), meta)


def audit(data_root: str | Path) -> dict:
    root = Path(data_root)
    paths = sorted(root.glob("*/*/*.csv"))
    records, instances = [], {}
    for path in paths:
        try:
            instance = load_instance(path)
            instances[path] = instance
            groups = defaultdict(list)
            for i, row in enumerate(instance.x):
                groups[row].append(i)
            repeated = [indices for indices in groups.values() if len(indices) > 1]
            conflicting = [ids for ids in repeated if len({instance.y[i] for i in ids}) > 1]
            counts = Counter(instance.y)
            records.append({"path": str(path), "status": "ok", "dataset_hash": instance.dataset_hash,
                            "problem_hash": instance.problem_hash, **instance.metadata,
                            "N": instance.n, "m": instance.m, "C": instance.C,
                            "categories": list(instance.category_names),
                            "category_counts": {str(c): counts[c] for c in range(instance.C)},
                            "missing_categories": [c for c in range(instance.C) if not counts[c]],
                            "duplicate_performances": sum(len(ids)-1 for ids in repeated),
                            "conflicting_rows": conflicting,
                            "criteria": [{"name": c.name,
                                          "type": "real" if c.is_real else "integer",
                                          "direction": "increasing" if (c.real_values if c.is_real else c.integer_values).is_increasing else "decreasing",
                                          "min": (c.real_values if c.is_real else c.integer_values).min_value,
                                          "max": (c.real_values if c.is_real else c.integer_values).max_value}
                                         for c in instance.problem().criteria]})
        except Exception as exc:
            records.append({"path": str(path), "status": "invalid", "error": str(exc)})
    overlaps = []
    items = list(instances.items())
    sets = {p: set(inst.x) for p, inst in items}
    # Comparer les performances, jamais les noms "Alternative i" réutilisés.
    for index, (pa, a) in enumerate(items):
        for pb, b in items[index+1:]:
            if a.m != b.m:
                continue
            common = len(sets[pa] & sets[pb])
            noise_pair = pa.parent == pb.parent and pa.stem.replace("noise00", "noise10") == pb.stem
            size_pair = pa.parent == pb.parent and pa.name[5:] == pb.name[5:]
            if common or noise_pair or size_pair:
                overlaps.append({"a": str(pa), "b": str(pb), "shared_performances": common,
                                 "a_subset_b": sets[pa] <= sets[pb],
                                 "same_rows_in_order": a.x == b.x,
                                 "nominal_noise_pair": noise_pair,
                                 "nominal_size_pair": size_pair})
    return {"schema_version": 1, "csv_count": len(paths),
            "valid_count": len(instances), "records": records, "relationships": overlaps,
            "notes": ["Type B : difficulté annoncée supérieure à A (information utilisateur).",
                      "Mécanisme de bruit et modèles sources non fournis.",
                      "Comparaisons sur les valeurs numériques chargées par lincs.",
                      "dataset0.txt reste un cas de régression du jalon 1."]}


def write_json(path: str | Path, payload: Any):
    """Publication atomique : un fichier partiel n'est jamais une exécution terminée."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)
