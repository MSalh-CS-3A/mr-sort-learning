"""Vérifications fonctionnelles avec de vrais appels au solveur GUROBI."""

import tempfile
from pathlib import Path
import unittest

from mrsort import LearningSet, MRSortModel, load_dataset, train


class DataAndPredictionTests(unittest.TestCase):
    def test_course_dataset(self):
        data = load_dataset(Path(__file__).resolve().parent / "data" / "dataset0.txt")
        self.assertEqual((len(data.names), len(data.criteria), data.n_categories), (60, 5, 3))

    def test_parser_handles_tabs_and_explicit_name_header(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.txt"
            path.write_text("id\tM\tP\tcateg.\na\t12,5\t11\t2\t\t\nb\t10\t13\t1\n")
            self.assertEqual(load_dataset(path).performances, ((12.5, 11.0), (10.0, 13.0)))

    def test_admission_example_and_equality(self):
        model = MRSortModel((0.25, 0.15, 0.2, 0.4), ((12, 12, 12, 12),), 0.66)
        self.assertEqual([model.predict(x) for x in [(11,12,13,12),(13,12,15,10),(11,13,11,13),(12,12,16,12)]], [2,1,1,2])
        equal = MRSortModel((0.5, 0.5), ((12,12),), 0.5, numerical_tolerance=0)
        self.assertEqual(equal.predict((12,0)), 2)

    def test_ordered_categories(self):
        model = MRSortModel((1,), ((10,), (20,)), 1, numerical_tolerance=0)
        self.assertEqual([model.predict((x,)) for x in [0,10,19,20,25]], [1,2,2,3,3])

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            LearningSet(("a",), ("M",), ((float("nan"),),), (1,), 2)
        with self.assertRaises(ValueError):
            MRSortModel((1,), ((20,), (10,)), 0.5)


class OptimizationTests(unittest.TestCase):
    def test_binary_training_restores_known_model(self):
        data = LearningSet(("Alice","Bob","Charlie","David"), ("M","P","L","H"),
                           ((11,12,13,12),(13,12,15,10),(11,13,11,13),(12,12,16,12)), (2,1,1,2), 2)
        result = train(data, upper_bound=20, time_limit=10)
        self.assertTrue(result.optimal)
        self.assertEqual(result.objective, 0)
        self.assertEqual(result.predictions, data.categories)

    def test_conflicting_identical_objects_require_one_error(self):
        data = LearningSet(("u","v"), ("M",), ((12,), (12,)), (1,2), 2)
        result = train(data, upper_bound=20, time_limit=10)
        self.assertTrue(result.optimal)
        self.assertEqual(result.objective, 1)
        self.assertEqual(len(result.misclassified_objects), 1)

    def test_multicategory_training_and_shared_comparisons(self):
        data = LearningSet(("a","b","c","d"), ("M",), ((5,), (15,), (15,), (25,)), (1,2,2,3), 3)
        result = train(data, upper_bound=30, time_limit=10)
        self.assertTrue(result.optimal)
        self.assertEqual(result.objective, 0)
        self.assertEqual(result.predictions, data.categories)
        self.assertEqual(result.solver_variables, 16)

    def test_majority_of_conflicting_labels_is_preserved(self):
        # Tous les objets identiques reçoivent la même prédiction. La classe
        # majoritaire minimise donc le nombre d'erreurs : un objet sacrifié.
        data = LearningSet(("u","v","w"), ("M",), ((12,), (12,), (12,)), (1,2,2), 2)
        result = train(data, upper_bound=20, time_limit=10)
        self.assertEqual(result.objective, 1)
        self.assertEqual(result.training_accuracy, 2/3)


if __name__ == "__main__":
    unittest.main()
