#!/usr/bin/env python3
"""Check structural patterns in the 2-way collisions of c -> (on0, on1)."""

from __future__ import annotations

import argparse
from collections import defaultdict
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from fast_class_coverage2 import build_quotient, rule30_next_tuple


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-horizon", type=int, default=18)
    args = parser.parse_args()

    for h in range(2, args.max_horizon + 1):
        qh = build_quotient(h)
        qprev = build_quotient(h - 1)
        states_by_class: dict[int, list[tuple[int, ...]]] = defaultdict(list)
        for state, class_id in qh.items():
            states_by_class[class_id].append(state)

        pair_to_classes: dict[tuple[int, int], list[int]] = defaultdict(list)
        for class_id, states in states_by_class.items():
            pair = []
            for bit in (0, 1):
                next_classes = {qprev[rule30_next_tuple(state, bit)[:-1]] for state in states}
                if len(next_classes) != 1:
                    raise RuntimeError(f"cross-horizon relation failed at h={h}, class={class_id}")
                pair.append(next(iter(next_classes)))
            pair_to_classes[(pair[0], pair[1])].append(class_id)

        ok = True
        doubles = 0
        for pair, classes in pair_to_classes.items():
            if len(classes) > 2:
                ok = False
                print(f"h={h}: multiplicity > 2 for pair {pair}: {classes}")
                break
            if len(classes) == 2:
                doubles += 1
                first_bits = sorted({min(states_by_class[class_id])[0] for class_id in classes})
                if first_bits != [0, 1]:
                    ok = False
                    print(f"h={h}: leading-bit split failed for pair {pair}: classes={classes}")
                    break

        if ok:
            print(f"h={h}: ok, double-collisions={doubles}")


if __name__ == "__main__":
    main()