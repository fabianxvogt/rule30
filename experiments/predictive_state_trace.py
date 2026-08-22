#!/usr/bin/env python3

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from predictive_state_automaton import build_classes, evolve_state
from rule30_center_column import read_input_bits


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Trace visited predictive-state classes along the real center-column-driven evolution."
    )
    parser.add_argument("--input", type=Path, required=True, help="Center-column bit-sequence file.")
    parser.add_argument("--horizon", type=int, default=10, help="Predictive-state horizon.")
    parser.add_argument("--steps", type=int, default=5000, help="Number of boundary-driven steps to trace.")
    parser.add_argument("--top", type=int, default=20, help="Number of most-visited classes to print.")
    args = parser.parse_args()

    center = read_input_bits(args.input)
    if len(center) < args.steps:
        raise SystemExit("input sequence shorter than requested steps")

    state_to_class, classes = build_classes(args.horizon)
    state = tuple(0 for _ in range(args.horizon))
    visits: Counter[int] = Counter()
    first_seen: dict[int, int] = {}

    for step in range(args.steps):
        class_id = state_to_class[state]
        visits[class_id] += 1
        first_seen.setdefault(class_id, step)
        state = evolve_state(state, center[step])

    print(f"input={args.input}")
    print(f"horizon={args.horizon}")
    print(f"steps={args.steps}")
    print(f"total_classes={len(classes)}")
    print(f"visited_classes={len(visits)}")
    print("most_visited=")
    for class_id, count in visits.most_common(args.top):
        representative = min(classes[class_id])
        rep = "".join(str(bit) for bit in representative)
        print(
            f"  class={class_id} count={count} first_seen={first_seen[class_id]} rep={rep} size={len(classes[class_id])}"
        )


if __name__ == "__main__":
    main()