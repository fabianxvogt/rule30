#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path


def next_row(row: list[int]) -> list[int]:
    extended = [0, *row, 0]
    output: list[int] = []
    for index in range(1, len(extended) - 1):
        left = extended[index - 1]
        center = extended[index]
        right = extended[index + 1]
        neighborhood = (left << 2) | (center << 1) | right
        output.append(1 if neighborhood in {1, 2, 3, 4} else 0)
    return output


def generate_center_column_slow(steps: int) -> list[int]:
    width = 2 * steps + 1
    row = [0] * width
    center = width // 2
    row[center] = 1

    column = [row[center]]
    for _ in range(steps):
        row = next_row(row)
        column.append(row[center])
    return column


def generate_center_column_bitwise(steps: int) -> list[int]:
    state = 1
    column: list[int] = []
    for index in range(steps + 1):
        column.append((state >> index) & 1)
        state = state ^ ((state << 1) | (state << 2))
    return column


def generate_center_column(steps: int, engine: str) -> list[int]:
    if engine == "bitwise":
        return generate_center_column_bitwise(steps)
    if engine == "slow":
        return generate_center_column_slow(steps)
    raise ValueError(f"unknown engine: {engine}")


def find_eventual_period(
    sequence: list[int], max_period: int, min_repetitions: int
) -> tuple[int, int] | None:
    length = len(sequence)
    for period in range(1, max_period + 1):
        matched_suffix = 0
        for index in range(length - 1, period - 1, -1):
            if sequence[index] != sequence[index - period]:
                break
            matched_suffix += 1

        if matched_suffix >= period * (min_repetitions - 1):
            start = length - matched_suffix - period
            return start, period
    return None


def repeated_blocks(sequence: list[int], block_size: int) -> dict[str, int]:
    counts: dict[str, int] = {}
    if block_size <= 0 or block_size > len(sequence):
        return counts
    for start in range(0, len(sequence) - block_size + 1):
        block = "".join(str(bit) for bit in sequence[start : start + block_size])
        counts[block] = counts.get(block, 0) + 1
    return counts


def distinct_blocks(sequence: list[int], block_size: int) -> int:
    if block_size <= 0 or block_size > len(sequence):
        return 0
    blocks = {
        "".join(str(bit) for bit in sequence[start : start + block_size])
        for start in range(0, len(sequence) - block_size + 1)
    }
    return len(blocks)


def autocorrelation_mismatches(sequence: list[int], shift: int) -> int:
    if shift <= 0 or shift >= len(sequence):
        return 0
    mismatches = 0
    for index in range(len(sequence) - shift):
        if sequence[index] != sequence[index + shift]:
            mismatches += 1
    return mismatches


def transform_sequence(
    sequence: list[int], transform: str, transform_shift: int, transform_width: int
) -> list[int]:
    if transform == "identity":
        return sequence

    if transform == "running-parity":
        parity = 0
        output: list[int] = []
        for bit in sequence:
            parity ^= bit
            output.append(parity)
        return output

    if transform == "xor-shift":
        if transform_shift < 1:
            raise ValueError("--transform-shift must be positive for xor-shift")
        return [
            sequence[index] ^ sequence[index + transform_shift]
            for index in range(len(sequence) - transform_shift)
        ]

    if transform == "window-parity":
        if transform_width < 1:
            raise ValueError("--transform-width must be positive for window-parity")
        if transform_width > len(sequence):
            return []
        return [
            sum(sequence[index : index + transform_width]) % 2
            for index in range(len(sequence) - transform_width + 1)
        ]

    raise ValueError(f"unknown transform: {transform}")


def write_output(path: Path, sequence: list[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(str(bit) for bit in sequence) + "\n", encoding="ascii")


def read_input_bits(path: Path) -> list[int]:
    text = path.read_text(encoding="ascii")
    bits = [character for character in text if character in {"0", "1"}]
    if not bits:
        raise ValueError(f"no bits found in {path}")
    return [int(bit) for bit in bits]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate the Rule 30 center column and test simple periodicity hypotheses."
    )
    parser.add_argument("--steps", type=int, default=1024, help="Number of Rule 30 updates to run.")
    parser.add_argument(
        "--max-period",
        type=int,
        default=128,
        help="Largest candidate eventual period to test.",
    )
    parser.add_argument(
        "--report-prefix",
        type=int,
        default=64,
        help="How many initial bits of the center column to print.",
    )
    parser.add_argument(
        "--block-size",
        type=int,
        default=8,
        help="Window size for repeated finite-block counts.",
    )
    parser.add_argument(
        "--min-repetitions",
        type=int,
        default=4,
        help="Minimum number of full repeats required before reporting an eventual period.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path for saving the generated center-column bits.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Optional path to an existing bit-sequence file to analyze instead of generating Rule 30 data.",
    )
    parser.add_argument(
        "--engine",
        choices=["bitwise", "slow"],
        default="bitwise",
        help="Generator backend. 'bitwise' is much faster and matches the slow reference.",
    )
    parser.add_argument(
        "--complexity-max-k",
        type=int,
        default=12,
        help="Largest block length k for which to report distinct block counts.",
    )
    parser.add_argument(
        "--correlation-max-shift",
        type=int,
        default=8,
        help="Largest shift for which to report mismatch counts against the shifted sequence.",
    )
    parser.add_argument(
        "--transform",
        choices=["identity", "running-parity", "xor-shift", "window-parity"],
        default="identity",
        help="Optional derived sequence to analyze instead of the raw center column.",
    )
    parser.add_argument(
        "--transform-shift",
        type=int,
        default=1,
        help="Shift used by the xor-shift transform.",
    )
    parser.add_argument(
        "--transform-width",
        type=int,
        default=2,
        help="Window width used by the window-parity transform.",
    )
    args = parser.parse_args()

    if args.steps < 0:
        raise SystemExit("--steps must be non-negative")
    if args.max_period < 1:
        raise SystemExit("--max-period must be positive")
    if args.min_repetitions < 2:
        raise SystemExit("--min-repetitions must be at least 2")

    if args.input is not None:
        base_sequence = read_input_bits(args.input)
    else:
        base_sequence = generate_center_column(args.steps, args.engine)
    sequence = transform_sequence(
        base_sequence, args.transform, args.transform_shift, args.transform_width
    )
    prefix = "".join(str(bit) for bit in sequence[: args.report_prefix])

    print(f"steps={args.steps}")
    print(f"engine={args.engine}")
    if args.input is not None:
        print(f"input={args.input}")
    print(f"transform={args.transform}")
    print(f"length={len(sequence)}")
    print(f"prefix={prefix}")

    period = find_eventual_period(sequence, args.max_period, args.min_repetitions)
    if period is None:
        print(
            f"eventual_period=none_up_to_{args.max_period}_with_{args.min_repetitions}_repetitions"
        )
    else:
        start, size = period
        print(f"eventual_period=start:{start},period:{size}")

    block_counts = repeated_blocks(sequence, args.block_size)
    if block_counts:
        most_common = sorted(block_counts.items(), key=lambda item: (-item[1], item[0]))[:10]
        print("most_common_blocks=")
        for block, count in most_common:
            print(f"  {block}: {count}")

    if args.complexity_max_k > 0:
        print("distinct_block_counts=")
        for block_size in range(1, args.complexity_max_k + 1):
            print(f"  k={block_size}: {distinct_blocks(sequence, block_size)}")

    if args.correlation_max_shift > 0:
        print("shift_mismatches=")
        for shift in range(1, args.correlation_max_shift + 1):
            mismatches = autocorrelation_mismatches(sequence, shift)
            comparisons = len(sequence) - shift
            print(f"  shift={shift}: mismatches={mismatches}/{comparisons}")

    if args.output is not None:
        write_output(args.output, sequence)
        print(f"wrote={args.output}")


if __name__ == "__main__":
    main()