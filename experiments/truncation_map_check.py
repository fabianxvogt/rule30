#!/usr/bin/env python3
"""Check whether simple truncations induce well-defined maps S_h -> S_{h-1}."""

from __future__ import annotations

import argparse
from collections import defaultdict
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from fast_class_coverage2 import build_quotient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-horizon", type=int, default=18)
    args = parser.parse_args()

    print("h left_truncation right_truncation")
    print("-- --------------- ----------------")
    for h in range(2, args.max_horizon + 1):
        qh = build_quotient(h)
        qprev = build_quotient(h - 1)
        states_by_class: dict[int, list[tuple[int, ...]]] = defaultdict(list)
        for state, class_id in qh.items():
            states_by_class[class_id].append(state)

        left_ok = True
        right_ok = True
        for states in states_by_class.values():
            left_targets = {qprev[state[1:]] for state in states}
            right_targets = {qprev[state[:-1]] for state in states}
            if len(left_targets) != 1:
                left_ok = False
            if len(right_targets) != 1:
                right_ok = False
        print(f"{h:2d} {str(left_ok):>15s} {str(right_ok):>16s}")


if __name__ == "__main__":
    main()