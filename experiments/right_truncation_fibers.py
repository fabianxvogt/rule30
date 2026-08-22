#!/usr/bin/env python3
"""Measure fiber sizes of the well-defined right-truncation map S_h -> S_{h-1}."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from fast_class_coverage2 import build_quotient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-horizon", type=int, default=21)
    args = parser.parse_args()

    print("h |S_h| fiber-size distribution for right truncation")
    print("-- ----- -----------------------------------------")
    for h in range(2, args.max_horizon + 1):
        qh = build_quotient(h)
        qprev = build_quotient(h - 1)
        states_by_class: dict[int, list[tuple[int, ...]]] = defaultdict(list)
        for state, class_id in qh.items():
            states_by_class[class_id].append(state)

        fiber: dict[int, list[int]] = defaultdict(list)
        for class_id, states in states_by_class.items():
            targets = {qprev[state[:-1]] for state in states}
            if len(targets) != 1:
                raise RuntimeError(f"right truncation failed at h={h}, class={class_id}")
            fiber[next(iter(targets))].append(class_id)

        dist = Counter(len(classes) for classes in fiber.values())
        print(f"{h:2d} {len(states_by_class):5d} {dict(sorted(dist.items()))}")


if __name__ == "__main__":
    main()