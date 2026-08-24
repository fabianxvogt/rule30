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

    def test_facade_exposes_bounded_cross_horizon_projection(self) -> None:
        higher = rule30.predictive_partition(4)
        lower = rule30.predictive_partition(3)

        mapping = higher.right_truncation_map(lower)

        self.assertEqual(
            mapping[higher.class_id(0b1010)], lower.class_id(0b0010)
        )
        self.assertEqual(
            mapping,
            rule30_successor.predictive_partition(4).right_truncation_map(
                rule30_successor.predictive_partition(3)
            ),
        )

    def test_facade_exposes_finite_class_and_fiber_introspection(self) -> None:
        higher = rule30.predictive_partition(4)
        lower = rule30.predictive_partition(3)

        self.assertEqual(higher.class_members(0), higher.classes[0])
        fibers = higher.right_truncation_fibers(lower)
        self.assertEqual(
            sorted(source_id for fiber in fibers for source_id in fiber),
            list(range(len(higher.classes))),
        )
        mapping = higher.right_truncation_map(lower)
        for lower_class_id, source_class_ids in enumerate(fibers):
            for source_class_id in source_class_ids:
                self.assertEqual(mapping[source_class_id], lower_class_id)

    def test_facade_exposes_finite_nested_transition_map(self) -> None:
        higher = rule30.predictive_partition(4)
        lower = rule30.predictive_partition(3)

        mapping = higher.nested_transition_map(lower)

        for state in range(1 << higher.horizon):
            source_class_id = higher.class_id(state)
            for boundary_bit in (0, 1):
                next_state = rule30.integer_successor(
                    state, boundary_bit, higher.horizon
                )
                self.assertEqual(
                    mapping[source_class_id][boundary_bit],
                    lower.class_id(next_state & 0b111),
                )

    def test_facade_exposes_finite_same_horizon_transition_relation(self) -> None:
        partition = rule30.predictive_partition(4)
        relation = partition.same_horizon_transition_relation()

        self.assertEqual(
            relation,
            rule30_successor.predictive_partition(
                4
            ).same_horizon_transition_relation(),
        )
        self.assertEqual(relation[1][0], frozenset({3, 5}))

    def test_facade_exposes_finite_class_trace(self) -> None:
        package_partition = rule30.predictive_partition(3)
        implementation_partition = rule30_successor.predictive_partition(3)
        bits = (1, 0, 1)

        self.assertEqual(
            package_partition.class_trace(0b001, bits),
            implementation_partition.class_trace(0b001, bits),
        )

    def test_existing_experiment_import_remains_usable(self) -> None:
        self.assertEqual(
            rule30_successor.integer_successor(0b101, 1, 3),
            rule30.integer_successor(0b101, 1, 3),
        )


if __name__ == "__main__":
    unittest.main()
