#!/usr/bin/env python3
"""
Find the last-visited (rarest) predictive-state classes and characterize them.

For the trajectory-driven by the center column, some classes take much longer
than the coupon-collector average to be visited for the first time.  This script
finds those rare classes, identifies which raw right-half states belong to them,
and tries to characterize what makes them rare.
"""

from __future__ import annotations

import argparse
import sys
import os
from itertools import product

sys.path.insert(0, os.path.dirname(__file__))
from rule30_center_column import generate_center_column_bitwise


def rule30_next(state: tuple[int, ...], boundary_bit: int) -> tuple[int, ...]:
    w = len(state)
    if w == 0:
        return ()
    row = (boundary_bit,) + state + (0,)
    return tuple(row[i] ^ (row[i + 1] | row[i + 2]) for i in range(w))


def build_quotient_at_horizon(h, prev_class):
    if h == 0:
        return {(): 0}
    signatures = {}
    for state in product(range(2), repeat=h):
        fb = state[0]
        if prev_class is None:
            sig = (fb, 0, 0)
        else:
            s0 = rule30_next(state, 0)[:h - 1]
            s1 = rule30_next(state, 1)[:h - 1]
            sig = (fb, prev_class[s0], prev_class[s1])
        signatures[state] = sig
    sig_to_id: dict = {}
    stc: dict = {}
    for state, sig in signatures.items():
        if sig not in sig_to_id:
            sig_to_id[sig] = len(sig_to_id)
        stc[state] = sig_to_id[sig]
    return stc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--horizon", type=int, default=14,
                        help="Horizon to analyze (default: 14)")
    parser.add_argument("--steps", type=int, default=200000,
                        help="Number of center-column steps (default: 200000)")
    parser.add_argument("--top-rare", type=int, default=10,
                        help="Number of rarest classes to display")
    args = parser.parse_args()

    h = args.horizon
    steps = args.steps
    top_k = args.top_rare

    print(f"Generating {steps} center-column bits...")
    center = generate_center_column_bitwise(steps - 1)
    assert len(center) == steps
    print("Done.")
    print()

    print(f"Building quotient maps h=0..{h}...")
    prev = None
    all_q = {}
    for hh in range(h + 1):
        cm = build_quotient_at_horizon(hh, prev)
        all_q[hh] = cm
        prev = cm
    q = all_q[h]
    total_classes = max(q.values()) + 1
    print(f"Done. |S_{h}| = {total_classes} classes.")
    print()

    # Build reverse map: class_id -> list of raw states in that class
    class_to_states: dict[int, list[tuple[int, ...]]] = {i: [] for i in range(total_classes)}
    for state, cid in q.items():
        class_to_states[cid].append(state)

    # Trace trajectory and record first-visit times
    state: tuple[int, ...] = (0,) * h
    first_visit: dict[int, int] = {}
    visit_count: dict[int, int] = {i: 0 for i in range(total_classes)}

    cid = q[state]
    first_visit[cid] = 0
    visit_count[cid] += 1

    for t, bit in enumerate(center[:-1], start=1):
        nxt = rule30_next(state, bit)
        state = nxt[:h]
        cid = q[state]
        if cid not in first_visit:
            first_visit[cid] = t
        visit_count[cid] += 1

    covered = len(first_visit)
    unvisited = [cid for cid in range(total_classes) if cid not in first_visit]

    print(f"After {steps} steps: {covered}/{total_classes} classes visited.")
    if unvisited:
        print(f"Unvisited class ids: {unvisited}")
    print()

    # Sort by first-visit time (rarest = visited latest)
    sorted_by_fv = sorted(first_visit.items(), key=lambda x: -x[1])
    print(f"Top {top_k} rarest classes (by first-visit time):")
    print()
    for rank, (cid, fvt) in enumerate(sorted_by_fv[:top_k], 1):
        states_in_class = class_to_states[cid]
        mean_weight = sum(sum(s) for s in states_in_class) / len(states_in_class)
        # Characterize: are all states in the class have many 1s? few 1s?
        one_counts = sorted(sum(s) for s in states_in_class)
        print(f"  Rank {rank:2d}: class {cid:4d}, first_visit={fvt:7d}, "
              f"visits={visit_count[cid]:5d}, "
              f"size={len(states_in_class):3d}, "
              f"mean_ones={mean_weight:.2f}, "
              f"one_count_range=[{one_counts[0]},{one_counts[-1]}]")

    print()
    print("First member of each rare class (raw bit pattern):")
    for rank, (cid, fvt) in enumerate(sorted_by_fv[:top_k], 1):
        s = class_to_states[cid][0]
        bits = "".join(map(str, s))
        print(f"  Rank {rank:2d} class {cid:4d}: {bits} (first_visit={fvt})")

    # Visit count distribution
    counts = sorted(visit_count.values())
    total_visits = sum(counts)
    min_count = counts[0]
    max_count = counts[-1]
    p10 = counts[len(counts) // 10]
    p90 = counts[9 * len(counts) // 10]
    print()
    print("Visit count distribution:")
    print(f"  total steps recorded: {total_visits}")
    print(f"  min visits: {min_count}")
    print(f"  10th percentile: {p10}")
    print(f"  90th percentile: {p90}")
    print(f"  max visits: {max_count}")
    print(f"  mean visits: {total_visits/total_classes:.1f}")
    print()
    print(f"  Gini coefficient of visit distribution: "
          f"{gini(list(visit_count.values())):.4f}")
    print("  (Gini=0 -> uniform; Gini=1 -> one class gets everything)")

    # Check if unvisited classes have special structure
    if unvisited:
        print()
        print("Unvisited classes:")
        for cid in unvisited:
            for s in class_to_states[cid][:3]:
                bits = "".join(map(str, s))
                print(f"  class {cid:4d}, state {bits}")


def gini(values: list[int]) -> float:
    n = len(values)
    if n == 0:
        return 0.0
    values = sorted(values)
    total = sum(values)
    if total == 0:
        return 0.0
    cum = 0
    area_under = 0.0
    for i, v in enumerate(values):
        cum += v
        area_under += cum / total
    return 1 - 2 * area_under / n + 1 / n


if __name__ == "__main__":
    main()
