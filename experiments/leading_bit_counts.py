#!/usr/bin/env python3
"""Count predictive classes by common leading bit and compare to pair collisions."""

from __future__ import annotations

import argparse
from collections import defaultdict
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from fast_class_coverage2 import build_quotient, rule30_next_tuple


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-horizon", type=int, default=21)
    args = parser.parse_args()

    print("h total lead0 lead1 distinct_pairs double_pairs")
    print("-- ----- ----- ----- -------------- ------------")
    for h in range(1, args.max_horizon + 1):
        qh = build_quotient(h)
        states_by_class: dict[int, list[tuple[int, ...]]] = defaultdict(list)
        for state, class_id in qh.items():
            states_by_class[class_id].append(state)

        lead0 = 0
        lead1 = 0
        for states in states_by_class.values():
            bits = {state[0] for state in states}
            if len(bits) != 1:
                raise RuntimeError(f"mixed leading bits at h={h}")
            if next(iter(bits)) == 0:
                lead0 += 1
            else:
                lead1 += 1

        if h == 1:
            distinct_pairs = 0
            double_pairs = 0
        else:
            qprev = build_quotient(h - 1)
            pair_to_classes: dict[tuple[int, int], list[int]] = defaultdict(list)
            for class_id, states in states_by_class.items():
                pair = []
                for bit in (0, 1):
                    next_classes = {qprev[rule30_next_tuple(state, bit)[:-1]] for state in states}
                    if len(next_classes) != 1:
                        raise RuntimeError(f"bad pair map at h={h}, class={class_id}")
                    pair.append(next(iter(next_classes)))
                pair_to_classes[(pair[0], pair[1])].append(class_id)
            distinct_pairs = len(pair_to_classes)
            double_pairs = sum(1 for classes in pair_to_classes.values() if len(classes) == 2)

        print(f"{h:2d} {len(states_by_class):5d} {lead0:5d} {lead1:5d} {distinct_pairs:14d} {double_pairs:12d}")


if __name__ == "__main__":
    main()