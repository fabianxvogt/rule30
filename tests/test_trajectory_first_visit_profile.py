from __future__ import annotations

import unittest

from experiments.trajectory_first_visit_profile import measure
from rule30 import integer_successor, predictive_partition


class TrajectoryFirstVisitProfileTests(unittest.TestCase):
    def test_profile_uses_state_indexing_and_null_for_unseen_classes(self) -> None:
        report = measure([1, 1, 0, 1, 1, 1, 0, 0, 1, 1], 4)
        self.assertEqual(report["profiles"]["3"], [0, 1, 2, 3, None])
        self.assertEqual(report["rows"][3]["observed_classes"], 4)
        self.assertEqual(report["rows"][3]["bound_status"], "INCOMPLETE_INPUT")

    def test_complete_profile_checks_predeclared_bound(self) -> None:
        report = measure([1, 1, 0, 1, 1, 1, 0, 0, 1, 1], 4)
        row = report["rows"][4]
        self.assertEqual(row["full_predictive_classes"], 7)
        self.assertEqual(row["observed_classes"], 7)
        self.assertEqual(row["max_first_visit"], 6)
        self.assertEqual(row["bound_B_2_pow_h_plus_1"], 32)
        self.assertEqual(row["bound_status"], "PASS_BOUND")

    def test_projection_is_downward_only_and_lift_fails_at_q2_to_q3(self) -> None:
        higher = predictive_partition(3)
        lower = predictive_partition(2)
        state_higher = 0
        state_lower = 0
        seen_higher = set()
        seen_lower = set()
        # The retained center prefix starts with 11.  Include t=0,1,2.
        seen_higher.add(higher.class_id(state_higher))
        seen_lower.add(lower.class_id(state_lower))
        for boundary_bit in (1, 1):
            state_higher = integer_successor(state_higher, boundary_bit, 3)
            state_lower = integer_successor(state_lower, boundary_bit, 2)
            seen_higher.add(higher.class_id(state_higher))
            seen_lower.add(lower.class_id(state_lower))
        self.assertEqual(seen_lower, {0, 1, 2})
        self.assertEqual(seen_higher, {0, 1, 2})
        self.assertNotEqual(seen_higher, set(range(len(higher.classes))))
        self.assertEqual(
            higher.right_truncation_map(lower),
            (0, 1, 2, 1, 0),
        )


if __name__ == "__main__":
    unittest.main()
