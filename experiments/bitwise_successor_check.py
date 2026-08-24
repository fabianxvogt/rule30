#!/usr/bin/env python3
"""Exhaustively cross-check the integer Rule 30 successor.

Encoding invariant: a width-h tuple (s[0], ..., s[h-1]) is encoded as
sum(s[i] << i for i in range(h)). Therefore integer bit 0 is the
leftmost, boundary-adjacent cell, and increasing bit indices move right.

For boundary bit b and width mask M = 2**h - 1, the tuple reference
next[i] = left[i] XOR (state[i] OR right[i]) becomes:

    (((state << 1) & M) | b) XOR (state | (state >> 1))

with the result masked to width h.
"""

from __future__ import annotations

import argparse

from fast_class_coverage2 import rule30_next_tuple
from rule30_successor import integer_successor

DEFAULT_MAX_HORIZON = 12


def decode_state(state: int, horizon: int) -> tuple[int, ...]:
        return tuple((state >> i) & 1 for i in range(horizon))


def encode_state(state: tuple[int, ...]) -> int:
        return sum(bit << i for i, bit in enumerate(state))


def main(max_horizon: int = DEFAULT_MAX_HORIZON) -> None:
        roundtrips = transitions = 0
        for horizon in range(max_horizon + 1):
                for state in range(1 << horizon):
                        decoded = decode_state(state, horizon)
                        if encode_state(decoded) != state:
                                raise AssertionError(("round-trip", horizon, state))
                        roundtrips += 1
                        for boundary_bit in (0, 1):
                                expected = encode_state(
                                        rule30_next_tuple(decoded, boundary_bit)
                                )
                                actual = integer_successor(state, boundary_bit, horizon)
                                if actual != expected:
                                        raise AssertionError(
                                                (horizon, state, boundary_bit, actual, expected)
                                        )
                                transitions += 1
        print(
                f"PASS: h=0..{max_horizon}, {roundtrips} state encodings and {transitions} boundary transitions checked"
        )


if __name__ == "__main__":
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument(
                "--max-horizon",
                type=int,
                default=DEFAULT_MAX_HORIZON,
                help=f"highest width to check (default: {DEFAULT_MAX_HORIZON})",
        )
        args = parser.parse_args()
        if args.max_horizon < 0:
                parser.error("--max-horizon must be non-negative")
        main(args.max_horizon)
