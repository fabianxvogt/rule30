#!/usr/bin/env python3
"""Measure how often same-h predictive classes have non-unique next classes under a fixed bit."""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from fast_class_coverage2 import build_quotient, rule30_next_tuple


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report nondeterministic same-h class transitions under fixed boundary bits."
    )
    parser.add_argument("--max-horizon", type=int, default=12)
    args = parser.parse_args()

    print("h |S_h| nondet(class,bit) pairs")
    print("-- ----- ------------------------")
    for h in range(2, args.max_horizon + 1):
        q = build_quotient(h)
        class_ids = sorted(set(q.values()))
        nondet = 0
        examples: list[tuple[int, int, list[int]]] = []

        for cid in class_ids:
            states = [state for state, state_cid in q.items() if state_cid == cid]
            for bit in (0, 1):
                targets = sorted({q[rule30_next_tuple(state, bit)] for state in states})
                if len(targets) > 1:
                    nondet += 1
                    if len(examples) < 2:
                        examples.append((cid, bit, targets))

        print(f"{h:2d} {len(class_ids):5d} {nondet:24d}")
        for cid, bit, targets in examples:
            print(f"   example: class {cid} with bit {bit} has targets {targets}")


if __name__ == "__main__":
    main()