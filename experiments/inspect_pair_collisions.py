#!/usr/bin/env python3
"""Inspect collisions in the valid map c -> (on0, on1) from S_h to S_{h-1}^2."""

from __future__ import annotations

import argparse
from collections import defaultdict
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from fast_class_coverage2 import build_quotient, rule30_next_tuple


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--horizon", type=int, default=10)
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()

    h = args.horizon
    qh = build_quotient(h)
    qprev = build_quotient(h - 1)

    states_by_class: dict[int, list[tuple[int, ...]]] = defaultdict(list)
    for state, class_id in qh.items():
        states_by_class[class_id].append(state)

    pair_to_classes: dict[tuple[int, int], list[int]] = defaultdict(list)
    for class_id, states in states_by_class.items():
        targets = []
        for bit in (0, 1):
            next_classes = {qprev[rule30_next_tuple(state, bit)[:-1]] for state in states}
            if len(next_classes) != 1:
                raise RuntimeError(f"not well-defined at h={h}, class={class_id}")
            targets.append(next(iter(next_classes)))
        pair_to_classes[(targets[0], targets[1])].append(class_id)

    shown = 0
    for pair, classes in sorted(pair_to_classes.items()):
        if len(classes) != 2:
            continue
        print(f"pair={pair} classes={classes}")
        for class_id in classes:
            states = sorted(states_by_class[class_id])
            rep = ''.join(map(str, states[0]))
            print(f"  class={class_id} size={len(states)} rep={rep}")
        shown += 1
        if shown >= args.limit:
            break


if __name__ == "__main__":
    main()