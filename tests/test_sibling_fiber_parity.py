from __future__ import annotations

import ast
from collections import Counter
import hashlib
from itertools import product
import os
from pathlib import Path
import re
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
    def test_cli_lower_boundary_report_structure_is_bounded_and_ordered(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        script = repository_root / "experiments" / "sibling_fiber_parity.py"
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        limits = (
            "Limits: raw tuple-state partitions only; implementation hard cap "
            f"h={MAX_HORIZON}; no claim for larger horizons, an infinite quotient, "
            "center-column coverage, or periodicity."
        )
        pair_row_pattern = re.compile(
            r"^\s*(\d+)\s+(\([^)]*\))\s+(\([^)]*\))\s+"
            r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)$"
        )
        reports: dict[tuple[int, bool], list[str]] = {}

        for horizon in (0, 3):
            for report_distances in (False, True):
                command = [
                    sys.executable,
                    str(script),
                    "--max-horizon",
                    str(horizon),
                ]
                if report_distances:
                    command.append("--report-distances")
                report = subprocess.run(
                    command,
                    cwd=repository_root,
                    env=environment,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(report.returncode, 0, report.stderr)
                self.assertEqual(report.stderr, "")
                lines = report.stdout.splitlines()
                reports[(horizon, report_distances)] = lines

                self.assertEqual(
                    lines[:4],
                    [
                        f"Bounds: requested max horizon={horizon}; "
                        f"implementation hard cap={MAX_HORIZON}",
                        "Raw sibling-fiber parity check (EMPIRICAL; exact within bound)",
                        "h |S_h| n1 n2 same-ell share-tau0 share-tau1 "
                        "share-both share-neither coll0 coll1",
                        "-- ----- -- -- --------- ---------- ---------- "
                        "---------- ------------ ----- -----",
                    ],
                )
                summary_rows = lines[4 : 4 + horizon]
                self.assertEqual(
                    [int(row.split()[0]) for row in summary_rows],
                    list(range(1, horizon + 1)),
                )
                self.assertEqual(lines[-1], limits)

                if not report_distances:
                    self.assertEqual(lines[4 + horizon], limits)
                    self.assertNotIn(
                        "Pairwise raw signature distances (exact within bound)",
                        lines,
                    )
                    self.assertNotIn(
                        "h first-state second-state leading-equal full d0 d1",
                        lines,
                    )
                    continue

                self.assertEqual(lines[4 + horizon], "")
                pair_section = 5 + horizon
                pair_header = 6 + horizon
                self.assertEqual(
                    lines[pair_section],
                    "Pairwise raw signature distances (exact within bound)",
                )
                self.assertEqual(
                    lines[pair_header],
                    "h first-state second-state leading-equal full d0 d1",
                )
                pair_rows = lines[pair_header + 1 : -1]
                expected_pair_count = {0: 0, 3: 4}[horizon]
                self.assertEqual(len(pair_rows), expected_pair_count)
                pair_keys = []
                for row in pair_rows:
                    match = pair_row_pattern.fullmatch(row)
                    self.assertIsNotNone(match, row)
                    assert match is not None
                    first_state = ast.literal_eval(match.group(2))
                    second_state = ast.literal_eval(match.group(3))
                    self.assertLess(first_state, second_state)
                    pair_keys.append(
                        (int(match.group(1)), first_state, second_state)
                    )
                self.assertEqual(pair_keys, sorted(pair_keys))

            self.assertEqual(
                reports[(horizon, False)][: 4 + horizon],
                reports[(horizon, True)][: 4 + horizon],
            )
            self.assertEqual(
                reports[(horizon, False)][-1],
                reports[(horizon, True)][-1],
            )

    def test_cli_omitted_flags_use_bounded_default_without_distances(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        script = repository_root / "experiments" / "sibling_fiber_parity.py"
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"

        report = subprocess.run(
            [sys.executable, str(script)],
            cwd=repository_root,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(report.returncode, 0, report.stderr)
        self.assertEqual(report.stderr, "")
        lines = report.stdout.splitlines()
        self.assertEqual(
            lines[0],
            "Bounds: requested max horizon=13; implementation hard cap=13",
        )
        self.assertEqual(
            lines[-1],
            "Limits: raw tuple-state partitions only; implementation hard cap "
            "h=13; no claim for larger horizons, an infinite quotient, "
            "center-column coverage, or periodicity.",
        )
        summary_rows = [line for line in lines if line[:2].strip().isdigit()]
        self.assertEqual(
            [int(line[:2]) for line in summary_rows], list(range(1, MAX_HORIZON + 1))
        )
        self.assertEqual(summary_rows[-1].split()[:4], ["13", "203", "79", "62"])
        self.assertNotIn("Pairwise raw signature distances", report.stdout)

    def test_cli_default_distance_report_is_exact_and_cap_bounded(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        script = repository_root / "experiments" / "sibling_fiber_parity.py"
        environment = os.environ.copy()
        environment.update(PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")

        report = subprocess.run(
            [sys.executable, str(script), "--report-distances"],
            cwd=repository_root,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(report.returncode, 0, report.stderr)
        self.assertEqual(report.stderr, "")
        self.assertEqual(
            hashlib.sha256(report.stdout.encode("utf-8")).hexdigest(),
            "1c2e5f3ec1cb6f7de7de55a2d167ef4912128f3da0bc9135f6646dc0631981d4",
        )

        lines = report.stdout.splitlines()
        summary_header = lines.index(
            "h |S_h| n1 n2 same-ell share-tau0 share-tau1 "
            "share-both share-neither coll0 coll1"
        )
        pair_section = lines.index(
            "Pairwise raw signature distances (exact within bound)"
        )
        pair_header = lines.index("h first-state second-state leading-equal full d0 d1")
        summary_rows = [
            line
            for line in lines[summary_header + 2 : pair_section]
            if line[:2].strip().isdigit()
        ]
        pair_rows = [
            line for line in lines[pair_header + 1 : -1] if line[:2].strip().isdigit()
        ]
        self.assertEqual(len(summary_rows), MAX_HORIZON)
        self.assertEqual(len(pair_rows), 202)
        self.assertEqual(
            max(int(line[:2]) for line in summary_rows + pair_rows), MAX_HORIZON
        )
        self.assertEqual(
            sum(line[:2].strip() == str(MAX_HORIZON) for line in pair_rows), 62
        )

    def test_cli_bounded_reports_are_seed_and_invocation_stable(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        script = repository_root / "experiments" / "sibling_fiber_parity.py"
        expected = {
            False: (
                700,
                "450388b40f3cc1c1ad85482067c3a8cdfa39da2b7a4637d9760a02ed52319063",
            ),
            True: (
                983,
                "f31ad843c1a021d7555f23c28958025764630113e789a74a9d692b22f95af0aa",
            ),
        }

        for seed in ("0", "42"):
            for invocation in (
                [sys.executable, str(script)],
                [sys.executable, "-m", "experiments.sibling_fiber_parity"],
            ):
                for report_distances in (False, True):
                    command = invocation + ["--max-horizon", "3"]
                    if report_distances:
                        command.append("--report-distances")
                    environment = os.environ.copy()
                    environment.update(
                        PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED=seed
                    )
                    report = subprocess.run(
                        command,
                        cwd=repository_root,
                        env=environment,
                        capture_output=True,
                        text=False,
                        check=False,
                    )
                    self.assertEqual(report.returncode, 0, report.stderr)
                    self.assertEqual(report.stderr, b"")
                    self.assertEqual(
                        (len(report.stdout), hashlib.sha256(report.stdout).hexdigest()),
                        expected[report_distances],
                        msg=(
                            f"seed={seed}, invocation={invocation}, "
                            f"report_distances={report_distances}"
                        ),
                    )

    def test_cli_rejects_non_integer_horizon_contract(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        script = repository_root / "experiments" / "sibling_fiber_parity.py"
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"

        report = subprocess.run(
            [
                sys.executable,
                str(script),
                "--max-horizon",
                "not-an-integer",
                "--report-distances",
            ],
            cwd=repository_root,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(report.returncode, 2)
        self.assertEqual(report.stdout, "")
        self.assertEqual(
            report.stderr,
            """usage: sibling_fiber_parity.py [-h] [--max-horizon MAX_HORIZON]
                               [--report-distances]
sibling_fiber_parity.py: error: argument --max-horizon: invalid int value: 'not-an-integer'
""",
        )

    def test_cli_rejects_negative_horizon_contract(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        script = repository_root / "experiments" / "sibling_fiber_parity.py"
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"

        report = subprocess.run(
            [
                sys.executable,
                str(script),
                "--max-horizon",
                "-1",
                "--report-distances",
            ],
            cwd=repository_root,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(report.returncode, 2)
        self.assertEqual(report.stdout, "")
        self.assertIn(
            f"horizon must be an integer in [0, {MAX_HORIZON}]",
            report.stderr,
        )

    def test_cli_zero_horizon_contract(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        script = repository_root / "experiments" / "sibling_fiber_parity.py"
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"

        report = subprocess.run(
            [
                sys.executable,
                str(script),
                "--max-horizon",
                "0",
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
        self.assertEqual(
            report.stdout,
            """Bounds: requested max horizon=0; implementation hard cap=13
Raw sibling-fiber parity check (EMPIRICAL; exact within bound)
h |S_h| n1 n2 same-ell share-tau0 share-tau1 share-both share-neither coll0 coll1
-- ----- -- -- --------- ---------- ---------- ---------- ------------ ----- -----

Pairwise raw signature distances (exact within bound)
h first-state second-state leading-equal full d0 d1
Limits: raw tuple-state partitions only; implementation hard cap h=13; no claim for larger horizons, an infinite quotient, center-column coverage, or periodicity.
""",
        )

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
        self.assertEqual(
            report.stdout,
            """Bounds: requested max horizon=3; implementation hard cap=13
Raw sibling-fiber parity check (EMPIRICAL; exact within bound)
h |S_h| n1 n2 same-ell share-tau0 share-tau1 share-both share-neither coll0 coll1
-- ----- -- -- --------- ---------- ---------- ---------- ------------ ----- -----
 1     2  0  1         0          1          1          1            0     1     1
 2     3  1  1         1          0          0          0            1     0     0
 3     5  1  2         2          1          1          0            0     1     1

Pairwise raw signature distances (exact within bound)
h first-state second-state leading-equal full d0 d1
 1 (0,) (1,)             0    2  0  0
 2 (0, 0) (0, 1)             1    4  2  2
 3 (0, 0, 0) (0, 0, 1)             1    4  4  0
 3 (1, 0, 0) (1, 0, 1)             1    4  0  4
Limits: raw tuple-state partitions only; implementation hard cap h=13; no claim for larger horizons, an infinite quotient, center-column coverage, or periodicity.
""",
        )

        over_cap = subprocess.run(
            [
                sys.executable,
                str(script),
                "--max-horizon",
                str(MAX_HORIZON + 1),
                "--report-distances",
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

        at_cap = subprocess.run(
            [
                sys.executable,
                str(script),
                "--max-horizon",
                str(MAX_HORIZON),
            ],
            cwd=repository_root,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(at_cap.returncode, 0, at_cap.stderr)
        self.assertEqual(at_cap.stderr, "")
        self.assertIn(
            "Bounds: requested max horizon=13; implementation hard cap=13",
            at_cap.stdout,
        )
        self.assertIn("13   203 79 62", at_cap.stdout)

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
