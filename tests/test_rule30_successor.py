from __future__ import annotations

import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

from experiments.rule30_successor import (
    evolve_integer_state,
    integer_successor,
    predictive_partition,
    response_signature,
    response_trace,
)


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


def tuple_state_successor(
    state: tuple[int, ...], boundary_bit: int
) -> tuple[int, ...]:
    row = (boundary_bit,) + state + (0,)
    return tuple(row[i] ^ (row[i + 1] | row[i + 2]) for i in range(len(state)))


class IntegerSuccessorTests(unittest.TestCase):
    def test_zero_width_is_always_zero(self) -> None:
        self.assertEqual(integer_successor(0, 0, 0), 0)
        self.assertEqual(integer_successor(0, 1, 0), 0)

    def test_bit_zero_is_boundary_adjacent(self) -> None:
        self.assertEqual(integer_successor(0b101, 0, 3), 0b101)
        self.assertEqual(integer_successor(0b101, 1, 3), 0b100)

    def test_empty_boundary_word_preserves_state(self) -> None:
        self.assertEqual(evolve_integer_state(0b101, (), 3), 0b101)

    def test_evolution_delegates_to_successive_successors(self) -> None:
        boundary_bits = (1, 0, 1, 1)
        expected = 0b0101
        for boundary_bit in boundary_bits:
            expected = integer_successor(expected, boundary_bit, 4)
        self.assertEqual(evolve_integer_state(0b0101, boundary_bits, 4), expected)

    def test_response_trace_samples_before_each_update(self) -> None:
        boundary_bits = (1, 0, 1, 1)
        expected = []
        state = 0b0101
        for boundary_bit in boundary_bits:
            expected.append(state & 1)
            state = integer_successor(state, boundary_bit, 4)
        self.assertEqual(response_trace(0b0101, boundary_bits, 4), tuple(expected))

    def test_response_trace_consumes_a_boundary_iterable_once(self) -> None:
        consumed = []

        def boundary_bits():
            for bit in (1, 0, 1):
                consumed.append(bit)
                yield bit

        response_trace(0b001, boundary_bits(), 3)
        self.assertEqual(consumed, [1, 0, 1])

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

    def test_evolution_matches_tuple_reference_for_bounded_words(self) -> None:
        for horizon in range(7):
            for state in range(1 << horizon):
                for word_length in range(5):
                    for boundary_word in range(1 << word_length):
                        boundary_bits = tuple(
                            (boundary_word >> i) & 1 for i in range(word_length)
                        )
                        expected = state
                        for boundary_bit in boundary_bits:
                            expected = tuple_successor(
                                expected, boundary_bit, horizon
                            )
                        with self.subTest(
                            horizon=horizon,
                            state=state,
                            boundary_bits=boundary_bits,
                        ):
                            self.assertEqual(
                                evolve_integer_state(state, boundary_bits, horizon),
                                expected,
                            )

    def test_response_signatures_preserve_bounded_quotient_partition(self) -> None:
        expected_class_counts = (1, 2, 3, 5, 7, 11, 16)
        for horizon in range(7):
            boundary_words = tuple(
                tuple((word >> i) & 1 for i in range(horizon))
                for word in range(1 << horizon)
            )
            integer_signatures = set()
            tuple_signatures = set()
            for state in range(1 << horizon):
                encoded_signature = tuple(
                    response_trace(state, boundary_word, horizon)
                    for boundary_word in boundary_words
                )
                tuple_state = tuple((state >> i) & 1 for i in range(horizon))
                reference_signature = tuple(
                    tuple(
                        (current_state[0] if current_state else 0)
                        for current_state in self._tuple_states(
                            tuple_state, boundary_word
                        )
                    )
                    for boundary_word in boundary_words
                )
                integer_signatures.add(encoded_signature)
                tuple_signatures.add(reference_signature)
            with self.subTest(horizon=horizon):
                self.assertEqual(integer_signatures, tuple_signatures)
                self.assertEqual(
                    len(integer_signatures), expected_class_counts[horizon]
                )

    def test_predictive_partition_matches_response_signatures(self) -> None:
        expected_class_counts = (1, 2, 3, 5, 7, 11, 16)
        for horizon in range(7):
            partition = predictive_partition(horizon)
            members = [
                state for class_members in partition.classes for state in class_members
            ]
            with self.subTest(horizon=horizon):
                self.assertEqual(partition.horizon, horizon)
                self.assertEqual(len(partition.classes), expected_class_counts[horizon])
                self.assertEqual(sorted(members), list(range(1 << horizon)))
                self.assertEqual(len(members), len(set(members)))
                self.assertEqual(
                    [partition.class_id(state) for state in members],
                    [
                        class_id
                        for class_id, class_members in enumerate(partition.classes)
                        for _ in class_members
                    ],
                )

    def test_predictive_partition_is_exact_for_finite_signatures(self) -> None:
        for horizon in range(7):
            partition = predictive_partition(horizon)
            signatures = {
                state: response_signature(state, horizon)
                for state in range(1 << horizon)
            }
            for left in range(1 << horizon):
                for right in range(1 << horizon):
                    with self.subTest(horizon=horizon, left=left, right=right):
                        same_class = partition.class_id(left) == partition.class_id(right)
                        self.assertEqual(same_class, signatures[left] == signatures[right])

    def test_right_truncation_map_is_exhaustively_well_defined(self) -> None:
        expected_fiber_distributions = (
            {2: 1},
            {1: 1, 2: 1},
            {1: 1, 2: 2},
            {1: 3, 2: 2},
            {1: 3, 2: 4},
            {1: 6, 2: 5},
        )

        for horizon in range(1, 7):
            higher = predictive_partition(horizon)
            lower = predictive_partition(horizon - 1)
            mapping = higher.right_truncation_map(lower)
            mask = (1 << (horizon - 1)) - 1

            self.assertEqual(len(mapping), len(higher.classes))
            for state in range(1 << horizon):
                with self.subTest(horizon=horizon, state=state):
                    self.assertEqual(
                        mapping[higher.class_id(state)],
                        lower.class_id(state & mask),
                    )

            fiber_sizes = Counter(Counter(mapping).values())
            self.assertEqual(
                dict(sorted(fiber_sizes.items())),
                expected_fiber_distributions[horizon - 1],
            )

    def test_right_truncation_map_requires_adjacent_horizons(self) -> None:
        partition = predictive_partition(3)
        with self.assertRaises(ValueError):
            partition.right_truncation_map(predictive_partition(3))
        with self.assertRaises(ValueError):
            partition.right_truncation_map(predictive_partition(1))

    def test_predictive_partition_rejects_invalid_horizons_and_states(self) -> None:
        with self.assertRaises(ValueError):
            predictive_partition(-1)
        with self.assertRaises(ValueError):
            response_signature(0, -1)
        with self.assertRaises(ValueError):
            response_signature(4, 2)
        with self.assertRaises(ValueError):
            predictive_partition(2).class_id(4)

    @staticmethod
    def _tuple_states(
        state: tuple[int, ...], boundary_bits: tuple[int, ...]
    ) -> tuple[tuple[int, ...], ...]:
        states = []
        for boundary_bit in boundary_bits:
            states.append(state)
            state = tuple_state_successor(state, boundary_bit)
        return tuple(states)

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
