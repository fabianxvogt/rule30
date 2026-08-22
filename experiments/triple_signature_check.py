#!/usr/bin/env python3
"""Check whether a class is uniquely determined by (leftmost bit, on0, on1)."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from fast_class_coverage2 import build_quotient, rule30_next_tuple


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-horizon", type=int, default=21)
    args = parser.parse_args()

    print("h injective_by_(bit,on0,on1) multiplicities")
    print("-- --------------------------- --------------")
    for h in range(2, args.max_horizon + 1):
        qh = build_quotient(h)
        qprev = build_quotient(h - 1)
        states_by_class: dict[int, list[tuple[int, ...]]] = defaultdict(list)
        for state, class_id in qh.items():
            states_by_class[class_id].append(state)

        key_to_classes: dict[tuple[int, int, int], list[int]] = defaultdict(list)
        for class_id, states in states_by_class.items():
            leading_bits = {state[0] for state in states}
            if len(leading_bits) != 1:
                raise RuntimeError(f"class {class_id} at h={h} has mixed leading bits")
            leading_bit = next(iter(leading_bits))

            pair = []
            for bit in (0, 1):
                next_classes = {qprev[rule30_next_tuple(state, bit)[:-1]] for state in states}
                if len(next_classes) != 1:
                    raise RuntimeError(f"cross-horizon relation failed at h={h}, class={class_id}")
                pair.append(next(iter(next_classes)))

            key_to_classes[(leading_bit, pair[0], pair[1])].append(class_id)

        multiplicities = Counter(len(classes) for classes in key_to_classes.values())
        injective = max(multiplicities) == 1
        print(f"{h:2d} {str(injective):>27s} {dict(sorted(multiplicities.items()))}")
        if not injective:
            for key, classes in key_to_classes.items():
                if len(classes) > 1:
                    print(f"   collision: key={key} classes={classes}")
                    break


if __name__ == "__main__":
    main()