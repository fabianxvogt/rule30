#!/usr/bin/env python3
"""Search for simple recurrences among computed quotient statistics."""

from __future__ import annotations

import argparse
from collections import defaultdict
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from fast_class_coverage2 import build_quotient, rule30_next_tuple


def stats_for_h(h: int) -> dict[str, int]:
    qh = build_quotient(h)
    states_by_class: dict[int, list[tuple[int, ...]]] = defaultdict(list)
    for state, class_id in qh.items():
        states_by_class[class_id].append(state)

    lead0 = 0
    lead1 = 0
    for states in states_by_class.values():
        bit = next(iter({state[0] for state in states}))
        if bit == 0:
            lead0 += 1
        else:
            lead1 += 1

    if h == 1:
        return {
            "total": len(states_by_class),
            "lead0": lead0,
            "lead1": lead1,
            "distinct_pairs": 0,
            "double_pairs": 0,
        }

    qprev = build_quotient(h - 1)
    pair_to_classes: dict[tuple[int, int], list[int]] = defaultdict(list)
    for class_id, states in states_by_class.items():
        pair = []
        for bit in (0, 1):
            next_classes = {qprev[rule30_next_tuple(state, bit)[:-1]] for state in states}
            pair.append(next(iter(next_classes)))
        pair_to_classes[(pair[0], pair[1])].append(class_id)

    return {
        "total": len(states_by_class),
        "lead0": lead0,
        "lead1": lead1,
        "distinct_pairs": len(pair_to_classes),
        "double_pairs": sum(1 for classes in pair_to_classes.values() if len(classes) == 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-horizon", type=int, default=18)
    args = parser.parse_args()

    stats = {h: stats_for_h(h) for h in range(1, args.max_horizon + 1)}
    print("Checking simple identities:")
    formulas = [
        ("double_pairs(h) == lead1(h-1)", lambda h: stats[h]["double_pairs"] == stats[h - 1]["lead1"]),
        ("double_pairs(h) == lead0(h-1)", lambda h: stats[h]["double_pairs"] == stats[h - 1]["lead0"]),
        ("distinct_pairs(h) == total(h)-lead1(h)", lambda h: stats[h]["distinct_pairs"] == stats[h]["total"] - stats[h]["lead1"]),
        ("distinct_pairs(h) == total(h)-lead0(h)", lambda h: stats[h]["distinct_pairs"] == stats[h]["total"] - stats[h]["lead0"]),
        ("lead1(h) == double_pairs(h)+1", lambda h: stats[h]["lead1"] == stats[h]["double_pairs"] + 1),
        ("lead1(h) == double_pairs(h)", lambda h: stats[h]["lead1"] == stats[h]["double_pairs"]),
        ("lead0(h) == distinct_pairs(h)", lambda h: stats[h]["lead0"] == stats[h]["distinct_pairs"]),
    ]
    for name, predicate in formulas:
        holds = [h for h in range(2, args.max_horizon + 1) if predicate(h)]
        print(f"  {name}: holds for {holds}")


if __name__ == "__main__":
    main()