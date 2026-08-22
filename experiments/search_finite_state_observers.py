#!/usr/bin/env python3

from __future__ import annotations

import argparse
from itertools import product
from pathlib import Path

from rule30_center_column import distinct_blocks, find_eventual_period, read_input_bits


def run_observer(
    sequence: list[int], transition_table: tuple[int, ...], output_table: tuple[int, ...], state_count: int
) -> list[int]:
    state = 0
    output: list[int] = []
    for bit in sequence:
        output.append(output_table[(state << 1) | bit])
        state = transition_table[(state << 1) | bit]
    return output


def score_sequence(
    sequence: list[int], max_period: int, min_repetitions: int, block_k: int
) -> tuple[int, int, int]:
    period = find_eventual_period(sequence, max_period, min_repetitions)
    period_score = max_period + 1 if period is None else period[1]
    complexity_score = distinct_blocks(sequence, block_k)
    ones = sum(sequence)
    balance_penalty = abs((2 * ones) - len(sequence))
    return period_score, complexity_score, balance_penalty


def symbol_count(sequence: list[int]) -> int:
    return len(set(sequence))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search small finite-state observers applied to a bit sequence."
    )
    parser.add_argument("--input", type=Path, required=True, help="Input bit-sequence file.")
    parser.add_argument("--prefix-length", type=int, default=200000, help="Prefix length to analyze.")
    parser.add_argument("--states", type=int, default=2, help="Number of observer states.")
    parser.add_argument("--max-period", type=int, default=512, help="Largest candidate eventual period to test.")
    parser.add_argument(
        "--min-repetitions",
        type=int,
        default=8,
        help="Minimum number of full repeats required before reporting an eventual period.",
    )
    parser.add_argument("--block-k", type=int, default=12, help="Block length used for complexity scoring.")
    parser.add_argument("--top", type=int, default=10, help="Number of best observers to print.")
    parser.add_argument(
        "--require-nonconstant",
        action="store_true",
        help="Ignore observers whose output uses only one symbol.",
    )
    parser.add_argument(
        "--min-balance-fraction",
        type=float,
        default=0.0,
        help="Require the fraction of ones in the output to lie between f and 1-f.",
    )
    args = parser.parse_args()

    sequence = read_input_bits(args.input)[: args.prefix_length]
    if not sequence:
        raise SystemExit("input prefix is empty")

    transition_size = args.states * 2
    transition_candidates = product(range(args.states), repeat=transition_size)
    output_candidates = list(product((0, 1), repeat=transition_size))

    ranked: list[tuple[tuple[int, int, int], tuple[int, ...], tuple[int, ...]]] = []

    for transition_table in transition_candidates:
        for output_table in output_candidates:
            observed = run_observer(sequence, transition_table, output_table, args.states)
            if args.require_nonconstant and symbol_count(observed) < 2:
                continue
            ones_fraction = sum(observed) / len(observed)
            if not (args.min_balance_fraction <= ones_fraction <= 1.0 - args.min_balance_fraction):
                continue
            score = score_sequence(observed, args.max_period, args.min_repetitions, args.block_k)
            ranked.append((score, transition_table, output_table))

    ranked.sort(key=lambda item: item[0])

    print(f"input={args.input}")
    print(f"prefix_length={len(sequence)}")
    print(f"states={args.states}")
    print(f"searched={len(ranked)}")
    print("best_observers=")
    for score, transition_table, output_table in ranked[: args.top]:
        period_score, complexity_score, balance_penalty = score
        observed = run_observer(sequence, transition_table, output_table, args.states)
        ones = sum(observed)
        print(
            "  "
            f"period_score={period_score} complexity_k{args.block_k}={complexity_score} "
            f"balance_penalty={balance_penalty} "
            f"ones={ones}/{len(observed)} transition={transition_table} output={output_table}"
        )


if __name__ == "__main__":
    main()