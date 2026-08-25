from __future__ import annotations

from collections import Counter
from itertools import product
import os
from pathlib import Path
import subprocess
import sys
import unittest

from experiments.right_half_response_classes import state_signature
from experiments.sibling_fiber_parity import (
    MAX_HORIZON,
    MAX_RAW_STATES,
    _packed_signatures,
    _raw_successor,
    analyze,
    audit,
    raw_signature,
)
from rule30 import predictive_partition


class SiblingFiberParityTests(unittest.TestCase):
    def test_cli_report_and_cap_contract(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        script = repository_root / "experiments" / "sibling_fiber_parity.py"
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"

        report = subprocess.run(
            [
                sys.executable,
                str(script),
                "--max-horizon",
                "3",
                "--report-distances",
            ],
            cwd=repository_root,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(report.returncode, 0, report.stderr)
        self.assertEqual(report.stderr, "")
        self.assertIn(
            "Pairwise raw signature distances (exact within bound)",
            report.stdout,
        )
        self.assertIn(" 3 (0, 0, 0) (0, 0, 1)", report.stdout)
        self.assertIn("hard cap h=13", report.stdout)

        over_cap = subprocess.run(
            [
                sys.executable,
                str(script),
                "--max-horizon",
                str(MAX_HORIZON + 1),
            ],
            cwd=repository_root,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(over_cap.returncode, 2)
        self.assertEqual(over_cap.stdout, "")
        self.assertIn(
            f"horizon must be an integer in [0, {MAX_HORIZON}]",
            over_cap.stderr,
        )

    def test_empirical_bounded_table_through_horizon_thirteen(self) -> None:
        result = audit(MAX_HORIZON)
        summaries = result.summaries
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

        expected_pair_count = sum(row[3] for row in expected)
        self.assertEqual(len(result.pairwise_distances), expected_pair_count)
        for report in result.pairwise_distances:
            self.assertEqual(
                report.full_distance,
                2 ** (report.horizon // 2 + 1),
            )
            if report.horizon == 1:
                self.assertFalse(report.leading_bits_equal)
                self.assertEqual(
                    (
                        report.full_distance,
                        report.child_distance_0,
                        report.child_distance_1,
                    ),
                    (2, 0, 0),
                )
            else:
                self.assertTrue(report.leading_bits_equal)
                self.assertEqual(
                    report.full_distance,
                    report.child_distance_0 + report.child_distance_1,
                )

        h13 = [
            report
            for report in result.pairwise_distances
            if report.horizon == MAX_HORIZON
        ]
        self.assertEqual(len(h13), 62)
        self.assertEqual(
            {
                (
                    report.full_distance,
                    report.child_distance_0,
                    report.child_distance_1,
                )
                for report in h13
            },
            {(128, 0, 128), (128, 128, 0)},
        )
        self.assertEqual(
            Counter(
                (
                    report.full_distance,
                    report.child_distance_0,
                    report.child_distance_1,
                )
                for report in h13
            ),
            Counter({(128, 0, 128): 31, (128, 128, 0): 31}),
        )

        def direct_distance(
            first: tuple[int, ...], second: tuple[int, ...], horizon: int
        ) -> int:
            first_signature = raw_signature(first, horizon)
            second_signature = raw_signature(second, horizon)
            return sum(
                first_bit != second_bit
                for first_trace, second_trace in zip(
                    first_signature, second_signature
                )
                for first_bit, second_bit in zip(first_trace, second_trace)
            )

        for report in result.pairwise_distances:
            if report.horizon > 5:
                continue
            self.assertEqual(
                direct_distance(
                    report.first_state, report.second_state, report.horizon
                ),
                report.full_distance,
            )
            for boundary_bit, expected_distance in enumerate(
                (report.child_distance_0, report.child_distance_1)
            ):
                first_child = _raw_successor(
                    report.first_state, boundary_bit
                )[:-1]
                second_child = _raw_successor(
                    report.second_state, boundary_bit
                )[:-1]
                self.assertEqual(
                    direct_distance(first_child, second_child, report.horizon - 1),
                    expected_distance,
                )

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
