from __future__ import annotations

from itertools import product
import unittest

from experiments.right_half_response_classes import state_signature
from experiments.sibling_fiber_parity import (
    MAX_HORIZON,
    MAX_RAW_STATES,
    _packed_signatures,
    analyze,
    raw_signature,
)
from rule30 import predictive_partition


class SiblingFiberParityTests(unittest.TestCase):
    def test_empirical_bounded_table_through_horizon_thirteen(self) -> None:
        summaries = analyze(MAX_HORIZON)
        expected = (
            # h, |S_h|, n1, n2, same ell, share tau0, share tau1,
            # share both, share neither, collisions tau0, collisions tau1
            (1, 2, 0, 1, 0, 1, 1, 1, 0, 1, 1),
            (2, 3, 1, 1, 1, 0, 0, 0, 1, 0, 0),
            (3, 5, 1, 2, 2, 1, 1, 0, 0, 1, 1),
            (4, 7, 3, 2, 2, 0, 0, 0, 2, 0, 0),
            (5, 11, 3, 4, 4, 1, 3, 0, 0, 1, 3),
            (6, 16, 6, 5, 5, 0, 0, 0, 5, 0, 0),
            (7, 25, 7, 9, 9, 5, 4, 0, 0, 5, 4),
            (8, 35, 15, 10, 10, 0, 0, 0, 10, 0, 0),
            (9, 52, 18, 17, 17, 8, 9, 0, 0, 8, 9),
            (10, 71, 33, 19, 19, 0, 0, 0, 19, 0, 0),
            (11, 104, 38, 33, 33, 15, 18, 0, 0, 15, 18),
            (12, 141, 67, 37, 37, 0, 0, 0, 37, 0, 0),
            (13, 203, 79, 62, 62, 31, 31, 0, 0, 31, 31),
        )
        actual = tuple(
            (
                summary.horizon,
                summary.class_count,
                summary.singleton_fibers,
                summary.doubleton_fibers,
                summary.same_leading_bit_pairs,
                summary.share_tau0,
                summary.share_tau1,
                summary.share_both,
                summary.share_neither,
                summary.rho_tau0_collisions,
                summary.rho_tau1_collisions,
            )
            for summary in summaries
        )
        self.assertEqual(actual, expected)

    def test_horizon_one_is_an_explicit_degenerate_exception(self) -> None:
        partition = predictive_partition(1)
        lower = predictive_partition(0)
        fibers = partition.right_truncation_fibers(lower)
        nested = partition.nested_transition_map(lower)

        self.assertEqual(fibers, ((0, 1),))
        self.assertEqual(partition.class_members(0)[0] & 1, 0)
        self.assertEqual(partition.class_members(1)[0] & 1, 1)
        self.assertEqual(nested[0], (0, 0))
        self.assertEqual(nested[1], (0, 0))

    def test_experiment_has_a_hard_horizon_cap(self) -> None:
        self.assertEqual(MAX_HORIZON, 13)
        self.assertEqual(MAX_RAW_STATES, 1 << 13)
        with self.assertRaises(ValueError):
            analyze(MAX_HORIZON + 1)
        with self.assertRaises(ValueError):
            analyze(-1)
        with self.assertRaises(ValueError):
            raw_signature((), MAX_HORIZON + 1)

    def test_raw_signature_matches_explicit_tuple_reference(self) -> None:
        for horizon in range(5):
            for state in product((0, 1), repeat=horizon):
                self.assertEqual(
                    raw_signature(state, horizon),
                    state_signature(state, horizon),
                )

    def test_compact_raw_signatures_match_direct_raw_signatures(self) -> None:
        for horizon in range(1, 6):
            states = tuple(product((0, 1), repeat=horizon))
            compact = _packed_signatures(states, horizon)
            trace_bytes = max(1, (horizon + 7) // 8)
            for state in states:
                expected = b"".join(
                    int("".join(map(str, trace)) or "0", 2).to_bytes(
                        trace_bytes, "big"
                    )
                    for trace in raw_signature(state, horizon)
                )
                self.assertEqual(compact[state], expected)


if __name__ == "__main__":
    unittest.main()
