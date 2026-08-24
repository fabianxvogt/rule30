from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from experiments.rule30_successor import integer_successor


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "experiments" / "bitwise_successor_check.py"


def tuple_successor(state: int, boundary_bit: int, horizon: int) -> int:
    bits = tuple((state >> i) & 1 for i in range(horizon))
    next_bits = tuple(
        (boundary_bit if i == 0 else bits[i - 1])
        ^ (bits[i] | (bits[i + 1] if i + 1 < horizon else 0))
        for i in range(horizon)
    )
    return sum(bit << i for i, bit in enumerate(next_bits))


class IntegerSuccessorTests(unittest.TestCase):
    def test_zero_width_is_always_zero(self) -> None:
        self.assertEqual(integer_successor(0, 0, 0), 0)
        self.assertEqual(integer_successor(0, 1, 0), 0)

    def test_bit_zero_is_boundary_adjacent(self) -> None:
        self.assertEqual(integer_successor(0b101, 0, 3), 0b101)
        self.assertEqual(integer_successor(0b101, 1, 3), 0b100)

    def test_matches_tuple_reference_through_bounded_width(self) -> None:
        for horizon in range(9):
            for state in range(1 << horizon):
                for boundary_bit in (0, 1):
                    with self.subTest(
                        horizon=horizon, state=state, boundary_bit=boundary_bit
                    ):
                        self.assertEqual(
                            integer_successor(state, boundary_bit, horizon),
                            tuple_successor(state, boundary_bit, horizon),
                        )

    def test_checker_cli_output_remains_stable(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(CHECKER), "--max-horizon", "4"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(
            completed.stdout,
            "PASS: h=0..4, 31 state encodings and 62 boundary transitions checked\n",
        )
        self.assertEqual(completed.stderr, "")


if __name__ == "__main__":
    unittest.main()
