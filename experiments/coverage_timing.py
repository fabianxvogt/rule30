#!/usr/bin/env python3
"""
Study how many steps the Rule 30 trajectory needs to cover all predictive-state
classes at each horizon h.

If the trajectory is eventually periodic with period p, then at each horizon h the
projected sequence is also eventually periodic with period dividing p.  An eventually
periodic sequence of period p can visit at most p distinct states.  So if we observe
that the trajectory (when projected to S_h) visits ALL |S_h| classes, and |S_h| is
unbounded, that alone does not give a contradiction.  But if the time to cover all
classes grows roughly like |S_h|, that tells us the trajectory is "spread out" in S_h
in a way that is very hard to explain by a finite-period orbit.

We also look for FIRST RETURN TIMES: how long does the trajectory take to return to
a class for the first time?  If the trajectory were periodic with period p, every
class would have return time exactly p.  We measure the distribution of return times.
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


def analyze_coverage_timing(
    center: list[int],
    h: int,
    q: dict[tuple[int, ...], int],
    total_classes: int,
) -> dict:
    """Return statistics about how long it takes to cover all classes."""
    state: tuple[int, ...] = (0,) * h
    first_visit: dict[int, int] = {}
    cid = q[state]
    if cid not in first_visit:
        first_visit[cid] = 0

    for t, bit in enumerate(center[:-1], start=1):
        nxt = rule30_next(state, bit)
        state = nxt[:h]
        cid = q[state]
        if cid not in first_visit:
            first_visit[cid] = t
        if len(first_visit) == total_classes:
            break

    # First-visit times
    fv_times = sorted(first_visit.values())
    covered = len(first_visit)
    last_new = fv_times[-1] if fv_times else 0

    return {
        "h": h,
        "total_classes": total_classes,
        "covered": covered,
        "saturation_step": last_new if covered == total_classes else None,
        "fv_mean": sum(fv_times) / len(fv_times) if fv_times else 0,
        "fv_max": fv_times[-1] if fv_times else 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-horizon", type=int, default=16)
    parser.add_argument("--steps", type=int, default=200000)
    args = parser.parse_args()

    max_h = args.max_horizon
    steps = args.steps

    print(f"Generating {steps} center-column bits (fast bitwise)...")
    center = generate_center_column_bitwise(steps - 1)
    assert len(center) == steps
    print("Done.")
    print()

    print(f"Building quotient maps h=0..{max_h}...")
    quotients: dict[int, dict] = {}
    prev = None
    for h in range(max_h + 1):
        cm = build_quotient_at_horizon(h, prev)
        quotients[h] = cm
        prev = cm
    print("Done.")
    print()

    print("Coverage timing analysis:")
    print()
    hdr = (f"{'h':>3} | {'|S_h|':>7} | {'covered':>7} | "
           f"{'sat_step':>10} | {'sat/|S_h|':>10} | {'fv_mean':>9} | {'fv_max':>9}")
    print(hdr)
    print("-" * len(hdr))

    for h in range(1, max_h + 1):
        q = quotients[h]
        total_classes = max(q.values()) + 1
        stats = analyze_coverage_timing(center, h, q, total_classes)
        sat = stats["saturation_step"]
        ratio = (sat / total_classes) if sat is not None else float("inf")
        sat_str = str(sat) if sat is not None else ">%d" % steps
        print(f"{h:>3} | {total_classes:>7} | {stats['covered']:>7} | "
              f"{sat_str:>10} | {ratio:>10.2f} | "
              f"{stats['fv_mean']:>9.1f} | {stats['fv_max']:>9}")

    print()
    print("Notes:")
    print("  sat_step   = first time step at which all |S_h| classes have been visited.")
    print("  sat/|S_h|  = saturation step / total number of classes.")
    print("               If trajectory ~ random walk on |S_h| states, coupon-collector")
    print("               theory predicts sat ~ |S_h| * ln(|S_h|) steps.")
    print("               If trajectory were periodic with period p, sat <= p,")
    print("               and all classes would have first-visit time < p.")
    print("  fv_mean    = mean first-visit time across all classes.")
    print("  fv_max     = last first-visit time (same as sat_step if all covered).")


if __name__ == "__main__":
    main()
