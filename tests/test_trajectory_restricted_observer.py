from __future__ import annotations

import unittest

from experiments.trajectory_restricted_observer import measure


class TrajectoryRestrictedObserverTests(unittest.TestCase):
    def test_small_exact_partition_counts_and_controls(self) -> None:
        report = measure([1, 1, 0, 1, 1, 1, 0, 0, 1, 1], 6)
        rows = report["rows"]
        self.assertEqual(
            [row["full_predictive_classes"] for row in rows],
            [1, 2, 3, 5, 7, 11, 16],
        )
        self.assertEqual(report["input"]["slow_reference_checked"], 10)
        self.assertTrue(all(report["controls"]["integer_tuple_reference_checked"].values()))

    def test_trajectory_classes_are_a_restriction_of_full_classes(self) -> None:
        report = measure([1, 1, 0, 1, 1, 1, 0, 0, 1, 1], 5)
        for row in report["rows"]:
            self.assertLessEqual(
                row["trajectory_predictive_classes"],
                row["full_predictive_classes"],
            )
            self.assertLessEqual(row["trajectory_raw_states"], row["raw_states"])


if __name__ == "__main__":
    unittest.main()
