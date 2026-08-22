#!/usr/bin/env python3

from __future__ import annotations

import argparse
from itertools import product


def evolve_state(state: tuple[int, ...], boundary_bit: int) -> tuple[int, ...]:
    width = len(state)
    row = [0, *state, 0]
    next_row = [0] * (width + 2)
    next_row[1] = boundary_bit ^ (row[1] | row[2])
    for position in range(2, width + 1):
        next_row[position] = row[position - 1] ^ (row[position] | row[position + 1])
    return tuple(next_row[1 : width + 1])


def simulate_response(initial_state: tuple[int, ...], boundary_word: tuple[int, ...]) -> tuple[int, ...]:
    state = initial_state
    output: list[int] = []
    for boundary_bit in boundary_word:
        output.append(state[0])
        state = evolve_state(state, boundary_bit)
    return tuple(output)


def build_classes(horizon: int) -> tuple[dict[tuple[int, ...], int], list[list[tuple[int, ...]]]]:
    signatures: dict[tuple[tuple[int, ...], ...], list[tuple[int, ...]]] = {}
    for state in product((0, 1), repeat=horizon):
        signature = tuple(
            simulate_response(state, boundary_word)
            for boundary_word in product((0, 1), repeat=horizon)
        )
        signatures.setdefault(signature, []).append(state)

    classes = list(signatures.values())
    state_to_class: dict[tuple[int, ...], int] = {}
    for class_id, states in enumerate(classes):
        for state in states:
            state_to_class[state] = class_id
    return state_to_class, classes


def check_nested_transition(
    classes_h: list[list[tuple[int, ...]]],
    state_to_class_h_minus_1: dict[tuple[int, ...], int],
) -> tuple[bool, dict[tuple[int, int], int]]:
    transition_map: dict[tuple[int, int], int] = {}
    for class_id, states in enumerate(classes_h):
        for boundary_bit in (0, 1):
            targets = {
                state_to_class_h_minus_1[evolve_state(state, boundary_bit)[:-1]]
                for state in states
            }
            if len(targets) != 1:
                return False, {}
            transition_map[(class_id, boundary_bit)] = next(iter(targets))
    return True, transition_map


def class_summary(classes: list[list[tuple[int, ...]]]) -> list[tuple[int, str]]:
    summary: list[tuple[int, str]] = []
    for states in classes:
        representative = min(states)
        summary.append((len(states), "".join(str(bit) for bit in representative)))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build nested predictive-state quotients for right-half boundary states."
    )
    parser.add_argument("--max-horizon", type=int, default=9, help="Largest horizon to analyze.")
    parser.add_argument(
        "--report-horizon",
        type=int,
        help="Optional horizon for which to print class representatives, sizes, and transitions.",
    )
    args = parser.parse_args()

    if args.max_horizon < 2:
        raise SystemExit("--max-horizon must be at least 2")

    built: dict[int, tuple[dict[tuple[int, ...], int], list[list[tuple[int, ...]]]]] = {}
    for horizon in range(1, args.max_horizon + 1):
        built[horizon] = build_classes(horizon)

    print("horizon_summary=")
    for horizon in range(1, args.max_horizon + 1):
        _, classes = built[horizon]
        print(f"  h={horizon} classes={len(classes)} raw_states={2 ** horizon}")

    print("nested_transition_checks=")
    for horizon in range(2, args.max_horizon + 1):
        state_to_class_h_minus_1, _ = built[horizon - 1]
        _, classes_h = built[horizon]
        is_well_defined, transition_map = check_nested_transition(classes_h, state_to_class_h_minus_1)
        distinct_targets = len(set(transition_map.values())) if transition_map else 0
        print(
            f"  h={horizon}->h={horizon - 1} well_defined={is_well_defined} "
            f"domain_classes={len(classes_h)} target_classes={distinct_targets}"
        )

    if args.report_horizon is not None:
        horizon = args.report_horizon
        if not (2 <= horizon <= args.max_horizon):
            raise SystemExit("--report-horizon must lie between 2 and --max-horizon")
        state_to_class_h_minus_1, _ = built[horizon - 1]
        _, classes_h = built[horizon]
        is_well_defined, transition_map = check_nested_transition(classes_h, state_to_class_h_minus_1)
        print(f"class_report_h={horizon} well_defined={is_well_defined}")
        summaries = class_summary(classes_h)
        for class_id, (size, representative) in enumerate(summaries):
            zero_target = transition_map.get((class_id, 0))
            one_target = transition_map.get((class_id, 1))
            print(
                f"  class={class_id} size={size} rep={representative} "
                f"on0={zero_target} on1={one_target}"
            )


if __name__ == "__main__":
    main()