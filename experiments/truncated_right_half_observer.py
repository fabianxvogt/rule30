#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from rule30_center_column import read_input_bits


def exact_adjacent_right_column(center: list[int]) -> list[int]:
    steps = len(center) - 1
    row = [0] * (steps + 2)
    output = [0]
    for time in range(steps):
        next_row = [0] * (steps + 2)
        next_row[1] = center[time] ^ (row[1] | row[2])
        for position in range(2, steps + 1):
            next_row[position] = row[position - 1] ^ (row[position] | row[position + 1])
        row = next_row
        output.append(row[1])
    return output


def truncated_adjacent_right_column(center: list[int], width: int) -> list[int]:
    if width < 1:
        raise ValueError("width must be positive")
    steps = len(center) - 1
    row = [0] * (width + 2)
    output = [0]
    for time in range(steps):
        next_row = [0] * (width + 2)
        next_row[1] = center[time] ^ (row[1] | row[2])
        for position in range(2, width + 1):
            next_row[position] = row[position - 1] ^ (row[position] | row[position + 1])
        row = next_row
        output.append(row[1])
    return output


def mismatch_count(left: list[int], right: list[int]) -> int:
    return sum(1 for a, b in zip(left, right) if a != b)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare finite-width right-half observers against the exact adjacent right column."
    )
    parser.add_argument("--input", type=Path, required=True, help="Center-column bit-sequence file.")
    parser.add_argument("--prefix-length", type=int, default=4000, help="Prefix length of center bits to use.")
    parser.add_argument("--max-width", type=int, default=12, help="Largest truncated width to test.")
    parser.add_argument("--report-prefix", type=int, default=64, help="How many output bits to print for the exact adjacent column.")
    args = parser.parse_args()

    center = read_input_bits(args.input)[: args.prefix_length]
    if len(center) < 2:
        raise SystemExit("need at least two center bits")

    exact = exact_adjacent_right_column(center)
    print(f"input={args.input}")
    print(f"prefix_length={len(center)}")
    print(f"exact_prefix={''.join(str(bit) for bit in exact[: args.report_prefix])}")
    print("width_results=")
    for width in range(1, args.max_width + 1):
        approx = truncated_adjacent_right_column(center, width)
        mismatches = mismatch_count(exact, approx)
        first_mismatch = next((index for index, (a, b) in enumerate(zip(exact, approx)) if a != b), None)
        print(
            f"  width={width} mismatches={mismatches}/{len(exact)} first_mismatch={first_mismatch} "
            f"observer_states={2 ** width}"
        )


if __name__ == "__main__":
    main()