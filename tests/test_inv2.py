import os
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"
os.environ.setdefault("MPLCONFIGDIR", "/tmp/projet-test-matplotlib")

from dataclasses import asdict, replace
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from lincs import classification as lc
import numpy as np

from projet.core import (Budget, Config, Exhausted, Model, Seeds, evaluate, fit_guarded,
                         partition_key, predict, restore_solution, solution_payload, valid_assignments)
from projet.data import Instance, audit, load_instance
from projet.initializers import component_order, initialize, uniform
from projet.milp import solve_joint_milp
from projet.runner import batch, identity, load_run, run_one, selected_paths
from projet.search import Search, SearchResult, local_neighbors, obvious_moves, solve


def instance(x=((.1,), (.9,), (.4,), (.6,)), y=(0, 1, 0, 1), C=2, decreasing=False):
    direction = lc.Criterion.PreferenceDirection.decreasing if decreasing else lc.Criterion.PreferenceDirection.increasing
    p = lc.Problem([lc.Criterion(f"x{j}", lc.Criterion.RealValues(direction, 0, 1))
                    for j in range(len(x[0]))], [lc.Category(str(c)) for c in range(C)])
    stream = StringIO()
    p.dump(stream)
    return Instance(tuple(f"a{i}" for i in range(len(x))), tuple(tuple(row) for row in x),
                    tuple(y), tuple(str(c) for c in range(C)), stream.getvalue())


def constant(data, category):
    thresholds = [0.0]*category+[None]*(data.C-1-category)
    if data.problem().criteria[0].real_values.is_decreasing:
        thresholds = [1.0]*category+[None]*(data.C-1-category)
    p = data.problem()
    coalition = lc.SufficientCoalitions(lc.SufficientCoalitions.Weights([1.0]*data.m))
    native = lc.Model(p, [lc.AcceptedValues(lc.AcceptedValues.RealThresholds(thresholds)) for _ in range(data.m)],
                      [coalition]*(data.C-1))
    return Model.capture(data, native)


class DataAndCoreTests(unittest.TestCase):
    def test_real_data_and_audit(self):
        report = audit("data")
        self.assertEqual((report["csv_count"], report["valid_count"]), (72, 72))
        self.assertTrue(all(r["kind_added_in_memory"] for r in report["records"]))
        self.assertEqual(len(selected_paths("data", pilot=True)), 12)
        data = load_instance("data/type_b/cr10_ca05/n0300_rep50-50_noise00.csv")
        self.assertEqual((data.n, data.m, data.C), (300, 10, 5))

    def test_missing_value_audited_invalid(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)/"type_a"/"cr01_ca02"
            target.mkdir(parents=True)
            (target/"problem.yml").write_text(instance().problem_yaml)
            (target/"n0002_rep50-50_noise00.csv").write_text("name,x0,category\na,,0\nb,0.5,1\n")
            report = audit(folder)
            self.assertEqual(report["valid_count"], 0)
            self.assertIn("manquantes", report["records"][0]["error"])

    def test_native_boundary_and_none(self):
        data = instance(x=((.5,), (.499,), (1.,)), y=(1, 0, 1))
        p = data.problem()
        coalition = lc.SufficientCoalitions(lc.SufficientCoalitions.Weights([1.0]))
        native = lc.Model(p, [lc.AcceptedValues(lc.AcceptedValues.RealThresholds([.5]))], [coalition])
        model = Model.capture(data, native)
        self.assertEqual(predict(model, data), (1, 0, 1))
        self.assertEqual(predict(constant(data, 0), data), (0, 0, 0))

    def test_loss_immutability_and_roundtrip(self):
        data = instance()
        original = data.x, data.y
        state = evaluate(data, (1, 0, 0, 1), constant(data, 0), constant(data, 1))
        self.assertEqual(state.loss, 2)
        restored = restore_solution(solution_payload(state, data), data)
        self.assertEqual(restored, state)
        self.assertEqual((data.x, data.y), original)
        payload = solution_payload(state, data)
        payload["LG"] = 99
        with self.assertRaises(ValueError):
            restore_solution(payload, data)
        for invalid in ((0,)*4, (1,)*4, (0, 1), (0, 1, 2, 0), (0, 1, .5, 0)):
            with self.assertRaises(ValueError):
                evaluate(data, invalid, *state.models)

    def test_guard_rejects_bad_model_and_handles_failure(self):
        data = instance()
        old, bad = constant(data, 0), constant(data, 1)
        budget = Budget(10)
        events = []
        got = fit_guarded(data, [0, 2], old, budget, 0, Config(), events,
                          trainer=lambda *args: bad)
        self.assertIs(got, old)
        def fails(*args):
            raise RuntimeError("simulated WPB failure")
        self.assertIs(fit_guarded(data, [0, 2], old, budget, 1, Config(), events, fails), old)
        self.assertEqual(len(events), 1)
        exhausted = Budget(1, max_calls=1)
        exhausted.calls = 1
        self.assertIs(fit_guarded(data, [0, 2], old, exhausted, 2, Config()), old)
        with self.assertRaises(Exhausted):
            fit_guarded(data, [0, 2], None, exhausted, 2, Config())

    def test_guard_keeps_old_on_tie(self):
        data = instance()
        old = constant(data, 0)
        got = fit_guarded(data, [0, 1], old, Budget(10), 1, Config(), trainer=lambda *args: constant(data, 1))
        self.assertIs(got, old)

    def test_budget_overrun_and_call_limit(self):
        now = [0.0]
        budget = Budget(1, max_calls=1, clock=lambda: now[0])
        data = instance()
        def trainer(*args):
            now[0] = 2.0
            return constant(data, 0)
        fit_guarded(data, [0, 2], None, budget, 4, Config(wpb_seconds=.5), trainer=trainer)
        self.assertEqual(budget.overruns[0]["excess"], 1.5)
        self.assertFalse(budget.available())

    def test_seed_streams_are_independent(self):
        a, b = Seeds(3), Seeds(3)
        first = a.next("partition")
        a.next("wpb")
        self.assertEqual(first, b.next("partition"))
        self.assertEqual(a.next("partition"), b.next("partition"))

    def test_real_wpb_singleton_with_absent_categories(self):
        data = instance(C=3)
        model = fit_guarded(data, [0], None, Budget(3), 3, Config(wpb_seconds=.1))
        self.assertEqual(predict(model, data, [0]), (0,))


class InitializationAndSearchTests(unittest.TestCase):
    def test_uniform_and_symmetry(self):
        rng = np.random.default_rng(12)
        for n in (2, 3, 30):
            for _ in range(50):
                z = uniform(n, rng)
                self.assertTrue(valid_assignments(z, n))
                self.assertEqual(partition_key(z), partition_key([1-v for v in z]))
        with self.assertRaises(ValueError):
            uniform(1, rng)

    def test_gmm_ties_exclusive_and_means_order(self):
        data = instance(x=((.1,), (.2,), (.7,), (.8,)), y=(0, 0, 1, 1))
        self.assertEqual(component_order(np.array([[.5, .5], [.5, .5]])), [0, 1])
        class FakeGMM:
            means_ = np.array([[.2], [.8]])
            converged_ = True
            def __init__(self, **kwargs):
                pass
            def fit(self, values):
                return self
            def predict_proba(self, values):
                return np.array([[.5, .5], [.1, .9]])
        with patch("sklearn.mixture.GaussianMixture", FakeGMM):
            z = initialize(data, Config(initializer="gmm"), Seeds(4))
        self.assertEqual(z, (0, 1, 0, 1))

    def test_gmm_fallback_and_decreasing_real(self):
        data = instance(x=((.5,), (.5,), (.5,)), y=(0, 1, 2), C=3, decreasing=True)
        events = []
        z = initialize(data, Config(initializer="gmm"), Seeds(2), events=events)
        self.assertTrue(valid_assignments(z, data.n))
        self.assertEqual(sum(e["event"] == "gmm_fallback" and "category" in e for e in events), 3)
        original = data.x
        actual = instance(decreasing=True)
        self.assertTrue(valid_assignments(initialize(actual, Config(initializer="gmm"), Seeds(1)), actual.n))
        self.assertEqual(data.x, original)

    def test_a1_guard_bound_and_nonempty_repair(self):
        data = instance()
        state = evaluate(data, (1, 0, 0, 1), constant(data, 0), constant(data, 1))
        z, r = obvious_moves(data, state)
        self.assertEqual((z, r), ((0, 1, 0, 1), 2))
        search = Search(data, Config(max_restarts=1), 0, trainer=lambda *args: constant(data, 1))
        search.record(state, "initial")
        result = search.a1(state)
        self.assertLessEqual(result.loss, state.loss-r)
        all_low = instance(y=(0, 0, 0, 0))
        bad = evaluate(all_low, (0, 0, 1, 1), constant(all_low, 1), constant(all_low, 0))
        self.assertEqual(obvious_moves(all_low, bad), ((0, 1, 1, 1), 1))

    def test_a2_plateau_cycle_stops(self):
        data = instance(x=((.5,),)*3, y=(0, 1, 2), C=3)
        state = evaluate(data, (0, 1, 0), constant(data, 0), constant(data, 1))
        search = Search(data, Config(stagnation=3), 0, trainer=lambda *args: constant(data, 2))
        search.record(state, "initial")
        new = search.a2(state)
        self.assertEqual(new.loss, state.loss)
        self.assertEqual(search.counters["accepted_moves"], 1)
        self.assertEqual(search.events[-1]["stagnation"], 3)
        self.assertLessEqual(search.budget.calls, 2)

    def test_a3_rejection_does_not_mutate_current(self):
        data = instance()
        state = evaluate(data, (0, 0, 0, 1), constant(data, 0), constant(data, 1))
        worse = evaluate(data, (1, 0, 0, 1), *state.models)
        search = Search(data, Config(), 1)
        search.record(state, "initial")
        with patch.object(search, "candidate", return_value=worse), patch("projet.search.local_neighbors", return_value=[worse.assignments]):
            result = search.a3(state)
        self.assertIs(result, state)
        self.assertIs(search.best, state)
        self.assertEqual(state.assignments, (0, 0, 0, 1))

    def test_local_neighbors_are_valid_unique_and_include_swaps(self):
        data = instance(x=tuple((i/20,) for i in range(20)), y=(0, 1)*10)
        state = evaluate(data, (0,)*10+(1,)*10, constant(data, 0), constant(data, 1))
        neighbors = local_neighbors(data, state, np.random.default_rng(0))
        self.assertEqual(len(neighbors), 16)
        self.assertEqual(len({partition_key(z) for z in neighbors}), len(neighbors))
        self.assertEqual([sum(a != b for a, b in zip(state.assignments, z)) for z in neighbors], [1]*8+[2]*8)

    def test_a4_keeps_best_after_degrading_perturbation(self):
        data = instance(y=(0, 0, 1, 1))
        good = evaluate(data, (0, 0, 0, 1), constant(data, 0), constant(data, 1))
        worse = evaluate(data, (0, 1, 0, 1), *good.models)
        search = Search(data, Config(perturbations=1), 2)
        search.record(good, "initial")
        with patch.object(search, "a3", side_effect=lambda state: state), patch.object(search, "candidate", return_value=worse):
            current = search.a4(good)
        self.assertEqual(current.loss, 2)
        self.assertEqual(search.best.loss, 1)
        self.assertEqual(search.trace[-1]["current_LG"], 2)
        self.assertEqual(search.trace[-1]["best_LG"], 1)

    def test_all_searches_run_with_real_wpb(self):
        data = instance(x=((.5,),)*6, y=(0, 1, 2, 0, 1, 2), C=3)
        for heuristic in ("A0", "A1", "A2", "A3", "A4"):
            with self.subTest(heuristic=heuristic):
                result = solve(data, Config(heuristic=heuristic, seconds=2, wpb_seconds=.05,
                                           max_calls=8, max_restarts=1, stagnation=3), 3)
                self.assertEqual(result.status, "ok")
                self.assertIsNotNone(result.best)
                self.assertGreaterEqual(result.best.loss, 2)
                self.assertTrue(valid_assignments(result.best.assignments, data.n))


class MilpAndRunnerTests(unittest.TestCase):
    def test_anytime_cohort_does_not_change_as_late_solutions_arrive(self):
        from projet.analysis import anytime_statistics
        curves = [[np.nan, .2, .1, .1], [np.nan, np.nan, .9, .8]]
        rows = anytime_statistics(curves, [0, 1, 2, 3], total_runs=3)
        self.assertEqual([r["available_runs"] for r in rows], [0, 1, 2, 2])
        self.assertEqual([r["total_runs"] for r in rows], [3]*4)
        self.assertIsNone(rows[1]["median_complete_cohort_error_rate"])
        self.assertEqual(rows[1]["median_best_error_rate"], .2)
        cohort = [r["median_complete_cohort_error_rate"] for r in rows if r["median_complete_cohort_error_rate"] is not None]
        np.testing.assert_allclose(cohort, [.5, .45])
        self.assertTrue(all(b <= a for a, b in zip(cohort, cohort[1:])))

    def test_analysis_reports_missing_solutions_without_fake_quality(self):
        from projet.analysis import analyze
        with tempfile.TemporaryDirectory() as folder:
            run_dir = Path(folder)/"runs"/"missing"
            run_dir.mkdir(parents=True)
            (run_dir/"result.json").write_text(json.dumps({
                "completed": True, "status": "no_solution", "method": "A1", "initializer": "uniform",
                "identity": {"config": asdict(Config())}, "dataset": {"path": "example.csv"},
                "seed": 0, "stop_reason": "budget", "wall_time": 10, "solution": None,
            }))
            report = analyze(Path(folder)/"runs", Path(folder)/"analysis")
            row = report["summary"][0]
            self.assertEqual((row["attempted_runs"], row["runs"], row["missing_or_invalid_runs"]), (1, 0, 1))
            self.assertIsNone(row["median_error_rate"])
            self.assertEqual(row["zero_frequency"], 0)
            self.assertTrue((Path(folder)/"analysis"/"failures.csv").exists())

    def test_integer_milp_threshold_reconstruction(self):
        for direction, x in ((lc.Criterion.PreferenceDirection.increasing, (1., 5., 9.)),
                             (lc.Criterion.PreferenceDirection.decreasing, (9., 5., 1.))):
            with self.subTest(direction=direction):
                p = lc.Problem([lc.Criterion("integer", lc.Criterion.IntegerValues(direction, 0, 10))],
                               [lc.Category(str(c)) for c in range(3)])
                stream = StringIO()
                p.dump(stream)
                data = Instance(("a", "b", "c"), tuple((v,) for v in x), (0, 1, 2),
                                ("0", "1", "2"), stream.getvalue())
                result = solve_joint_milp(data, Config(milp_seconds=5), 0)
                self.assertEqual(result.status, "ok", result.events)
                self.assertEqual(result.best.loss, 0)

    def test_joint_milp_known_optimum_identical_three_categories(self):
        data = instance(x=((.5,),)*3, y=(0, 1, 2), C=3)
        result = solve_joint_milp(data, Config(milp_seconds=5), 0)
        self.assertEqual(result.status, "ok", result.events)
        self.assertTrue(result.extra["optimal_for_margin_formulation"])
        self.assertEqual((result.extra["objective"], result.extra["bound"], result.best.loss), (1, 1, 1))

    def test_joint_milp_warm_start_does_not_fix_partition(self):
        data = instance(x=((.5,),)*4, y=(0, 1, 0, 1))
        warm = evaluate(data, (0, 0, 1, 1), constant(data, 0), constant(data, 1))
        result = solve_joint_milp(data, Config(milp_seconds=5), 0, warm)
        self.assertEqual(result.status, "ok", result.events)
        self.assertEqual(result.best.loss, 0)
        self.assertNotEqual(partition_key(result.best.assignments), partition_key(warm.assignments))
        self.assertEqual(result.extra["warm_start"], "provided_and_margin_valid")

    def test_milp_reconstructs_decreasing_criterion(self):
        data = instance(x=((.9,), (.6,), (.3,)), y=(0, 1, 2), C=3, decreasing=True)
        result = solve_joint_milp(data, Config(milp_seconds=5), 1)
        self.assertEqual(result.status, "ok", result.events)
        self.assertEqual(result.best.loss, 0)

    def test_milp_incompatible_warm_start_skipped(self):
        data = instance()
        p = data.problem()
        almost = lc.SufficientCoalitions(lc.SufficientCoalitions.Weights([.99999]))
        native = lc.Model(p, [lc.AcceptedValues(lc.AcceptedValues.RealThresholds([0.0]))], [almost])
        warm = evaluate(data, (0, 0, 1, 1), Model.capture(data, native), constant(data, 1))
        result = solve_joint_milp(data, Config(milp_seconds=5), 2, warm)
        self.assertEqual(result.extra["warm_start"], "skipped_incompatible_margin_or_family")

    def test_resume_identity_reload_and_partial_run(self):
        data = instance()
        cfg = Config(max_calls=2)
        state = evaluate(data, (0, 1, 0, 1), constant(data, 0), constant(data, 1))
        result = SearchResult(state, "ok", "zero_loss", .01, [], [], [], {}, [])
        with tempfile.TemporaryDirectory() as folder, patch("projet.runner.solve", return_value=result) as fake:
            first, reused = run_one(data, cfg, 3, folder)
            self.assertFalse(reused)
            second, reused = run_one(data, cfg, 3, folder)
            self.assertTrue(reused)
            self.assertEqual(fake.call_count, 1)
            path = Path(folder)/first["run_id"]/"result.json"
            self.assertEqual(load_run(path, data)[1], state)
            first["completed"] = False
            first["status"] = "interrupted"
            path.write_text(json.dumps(first))
            run_one(data, cfg, 3, folder)
            self.assertEqual(fake.call_count, 2)
            changed, reused = run_one(data, replace(cfg, seconds=31), 3, folder)
            self.assertFalse(reused)
            self.assertNotEqual(changed["run_id"], first["run_id"])
            with patch("projet.runner.code_hash", return_value="new_code"):
                self.assertNotEqual(identity(data, cfg, 3)[0], first["run_id"])

    def test_synthetic_instance_identity_includes_observed_data(self):
        a = instance()
        b = instance(y=(1, 0, 1, 0))
        self.assertNotEqual(identity(a, Config(), 0)[0], identity(b, Config(), 0)[0])

    def test_interrupted_job_is_not_completed(self):
        data = instance()
        with tempfile.TemporaryDirectory() as folder, patch("projet.runner.solve", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                run_one(data, Config(), 0, folder)
            payload = json.loads(next(Path(folder).rglob("result.json")).read_text())
            self.assertFalse(payload["completed"])
            self.assertEqual(payload["status"], "interrupted")

    def test_solver_interruption_is_not_completed(self):
        data = instance()
        result = SearchResult(None, "no_solution", "interrupted", .01, [], [], [], {}, [])
        with tempfile.TemporaryDirectory() as folder, patch("projet.runner.solve_joint_milp", return_value=result):
            with self.assertRaises(KeyboardInterrupt):
                run_one(data, Config(heuristic="MILP"), 0, folder)
            payload = json.loads(next(Path(folder).rglob("result.json")).read_text())
            self.assertFalse(payload["completed"])


if __name__ == "__main__":
    unittest.main()
