#!/usr/bin/env python3
"""Check whether a class is determined by right truncation plus one child tau_b."""

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

    print("h injective_by_(trunc,tau0) injective_by_(trunc,tau1)")
    print("-- ------------------------- -------------------------")
    for h in range(2, args.max_horizon + 1):
        qh = build_quotient(h)
        qprev = build_quotient(h - 1)
        states_by_class: dict[int, list[tuple[int, ...]]] = defaultdict(list)
        for state, class_id in qh.items():
            states_by_class[class_id].append(state)

        key0_to_classes: dict[tuple[int, int], list[int]] = defaultdict(list)
        key1_to_classes: dict[tuple[int, int], list[int]] = defaultdict(list)
        for class_id, states in states_by_class.items():
            trunc_targets = {qprev[state[:-1]] for state in states}
            if len(trunc_targets) != 1:
                raise RuntimeError(f"right truncation failed at h={h}, class={class_id}")
            trunc = next(iter(trunc_targets))

            tau0_targets = {qprev[rule30_next_tuple(state, 0)[:-1]] for state in states}
            tau1_targets = {qprev[rule30_next_tuple(state, 1)[:-1]] for state in states}
            if len(tau0_targets) != 1 or len(tau1_targets) != 1:
                raise RuntimeError(f"tau map failed at h={h}, class={class_id}")
            key0_to_classes[(trunc, next(iter(tau0_targets)))].append(class_id)
            key1_to_classes[(trunc, next(iter(tau1_targets)))].append(class_id)

        mult0 = Counter(len(v) for v in key0_to_classes.values())
        mult1 = Counter(len(v) for v in key1_to_classes.values())
        inj0 = max(mult0) == 1
        inj1 = max(mult1) == 1
        print(f"{h:2d} {str(inj0):>25s} {str(inj1):>25s}")
        if not inj0:
            for key, classes in key0_to_classes.items():
                if len(classes) > 1:
                    print(f"   tau0 collision: key={key} classes={classes[:8]}")
                    break
        if not inj1:
            for key, classes in key1_to_classes.items():
                if len(classes) > 1:
                    print(f"   tau1 collision: key={key} classes={classes[:8]}")
                    break


if __name__ == "__main__":
    main()