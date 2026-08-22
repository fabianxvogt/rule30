#!/usr/bin/env python3

from __future__ import annotations

import argparse
from itertools import product


def simulate_response(initial_state: tuple[int, ...], boundary_word: tuple[int, ...]) -> tuple[int, ...]:
    horizon = len(boundary_word)
    width = len(initial_state)
    row = [0, *initial_state, 0]
    outputs: list[int] = []

    for step in range(horizon):
        outputs.append(row[1])
        next_row = [0] * (width + 2)
        next_row[1] = boundary_word[step] ^ (row[1] | row[2])
        for position in range(2, width + 1):
            next_row[position] = row[position - 1] ^ (row[position] | row[position + 1])
        row = next_row

    return tuple(outputs)


def state_signature(initial_state: tuple[int, ...], horizon: int) -> tuple[tuple[int, ...], ...]:
    signatures: list[tuple[int, ...]] = []
    for boundary_word in product((0, 1), repeat=horizon):
        signatures.append(simulate_response(initial_state, boundary_word))
    return tuple(signatures)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute behavioral equivalence classes of finite right-half states."
    )
    parser.add_argument(
        "--horizon",
        type=int,
        default=8,
        help="Number of future steps and boundary-input bits considered.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of largest equivalence classes to print.",
    )
    args = parser.parse_args()

    if args.horizon < 1:
        raise SystemExit("--horizon must be positive")

    width = args.horizon
    classes: dict[tuple[tuple[int, ...], ...], list[tuple[int, ...]]] = {}

    for initial_state in product((0, 1), repeat=width):
        signature = state_signature(initial_state, args.horizon)
        classes.setdefault(signature, []).append(initial_state)

    class_sizes = sorted((len(states), states[0]) for states in classes.values())
    class_sizes.reverse()

    print(f"horizon={args.horizon}")
    print(f"state_width={width}")
    print(f"total_states={2 ** width}")
    print(f"equivalence_classes={len(classes)}")
    print(f"compression_ratio={(2 ** width) / len(classes):.3f}")
    print("largest_classes=")
    for size, representative in class_sizes[: args.top]:
        print(f"  size={size} representative={''.join(str(bit) for bit in representative)}")


if __name__ == "__main__":
    main()