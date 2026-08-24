from __future__ import annotations

import unittest

import rule30
from experiments import rule30_successor


class Rule30FacadeTests(unittest.TestCase):
    def test_facade_exports_the_bounded_transition_surface(self) -> None:
        self.assertEqual(
            rule30.__all__,
            [
                "PredictivePartition",
                "evolve_integer_state",
                "integer_successor",
                "predictive_partition",
                "response_signature",
                "response_trace",
            ],
        )

    def test_facade_preserves_existing_implementation_objects(self) -> None:
        for name in rule30.__all__:
            with self.subTest(name=name):
                self.assertIs(getattr(rule30, name), getattr(rule30_successor, name))

    def test_facade_supports_bounded_predictive_partition_workflow(self) -> None:
        partition = rule30.predictive_partition(4)

        self.assertIsInstance(partition, rule30.PredictivePartition)
        self.assertEqual(partition.class_id(0), 0)
        self.assertEqual(
            partition.class_id(0b0101),
            next(
                class_id
                for class_id, members in enumerate(partition.classes)
                if 0b0101 in members
            ),
        )
        self.assertEqual(
            rule30.response_signature(0b0101, 4),
            rule30_successor.response_signature(0b0101, 4),
        )

    def test_existing_experiment_import_remains_usable(self) -> None:
        self.assertEqual(
            rule30_successor.integer_successor(0b101, 1, 3),
            rule30.integer_successor(0b101, 1, 3),
        )


if __name__ == "__main__":
    unittest.main()
