#!/usr/bin/env python3
"""Check whether a predictive class is uniquely determined by (last bit, right-truncation class)."""

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

    print("h classes_have_constant_lastbit injective_by_(lastbit,trunc) multiplicities")
    print("-- --------------------------- ----------------------------- --------------")
    for h in range(2, args.max_horizon + 1):
        qh = build_quotient(h)
        qprev = build_quotient(h - 1)
        states_by_class: dict[int, list[tuple[int, ...]]] = defaultdict(list)
        for state, class_id in qh.items():
            states_by_class[class_id].append(state)

        constant_last = True
        key_to_classes: dict[tuple[int, int], list[int]] = defaultdict(list)
        for class_id, states in states_by_class.items():
            last_bits = {state[-1] for state in states}
            if len(last_bits) != 1:
                constant_last = False
                continue
            trunc_targets = {qprev[state[:-1]] for state in states}
            if len(trunc_targets) != 1:
                raise RuntimeError(f"right truncation not well-defined at h={h}, class={class_id}")
            key = (next(iter(last_bits)), next(iter(trunc_targets)))
            key_to_classes[key].append(class_id)

        multiplicities = Counter(len(classes) for classes in key_to_classes.values()) if key_to_classes else Counter()
        injective = bool(multiplicities) and max(multiplicities) == 1 and constant_last
        print(f"{h:2d} {str(constant_last):>27s} {str(injective):>29s} {dict(sorted(multiplicities.items()))}")
        if constant_last and not injective:
            for key, classes in key_to_classes.items():
                if len(classes) > 1:
                    print(f"   collision: key={key} classes={classes[:8]}")
                    break


if __name__ == "__main__":
    main()