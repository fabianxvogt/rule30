#!/usr/bin/env python3
"""Study the valid cross-horizon transition pair c -> (on0, on1) from S_h to S_{h-1}."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from fast_class_coverage2 import build_quotient, rule30_next_tuple


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check whether S_h classes are identified by their two deterministic S_{h-1} targets."
    )
    parser.add_argument("--max-horizon", type=int, default=18)
    args = parser.parse_args()

    print("h |S_h| distinct (on0,on1) pairs injective multiplicities")
    print("-- ----- ---------------------- --------- --------------")
    for h in range(2, args.max_horizon + 1):
        qh = build_quotient(h)
        qprev = build_quotient(h - 1)
        pair_to_classes: dict[tuple[int, int], list[int]] = defaultdict(list)
        states_by_class: dict[int, list[tuple[int, ...]]] = defaultdict(list)

        for state, class_id in qh.items():
            states_by_class[class_id].append(state)

        for class_id in sorted(states_by_class):
            states = states_by_class[class_id]
            targets = []
            for bit in (0, 1):
                next_classes = {qprev[rule30_next_tuple(state, bit)[:-1]] for state in states}
                if len(next_classes) != 1:
                    raise RuntimeError(
                        f"cross-horizon transition not well-defined at h={h}, class={class_id}, bit={bit}"
                    )
                targets.append(next(iter(next_classes)))
            pair_to_classes[(targets[0], targets[1])].append(class_id)

        multiplicities = Counter(len(classes) for classes in pair_to_classes.values())
        injective = max(multiplicities) == 1
        print(
            f"{h:2d} {len(states_by_class):5d} {len(pair_to_classes):22d} "
            f"{str(injective):>9s} {dict(sorted(multiplicities.items()))}"
        )

        if not injective:
            for pair, classes in pair_to_classes.items():
                if len(classes) > 1:
                    print(f"   example collision: pair={pair} classes={classes[:8]}")
                    break


if __name__ == "__main__":
    main()