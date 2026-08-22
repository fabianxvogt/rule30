#!/usr/bin/env python3
"""
Fast search for the first time all S_h classes are visited by the center-column trajectory.
Uses integer bitwise operations for speed.

Also identifies which class is last (or missing) and characterizes it.
"""
from __future__ import annotations
import sys
import os
from itertools import product
sys.path.insert(0, os.path.dirname(__file__))


def rule30_next_tuple(state: tuple[int, ...], boundary_bit: int) -> tuple[int, ...]:
    w = len(state)
    row = (boundary_bit,) + state + (0,)
    return tuple(row[i] ^ (row[i+1] | row[i+2]) for i in range(w))


def build_quotient_at_horizon(h, prev_class):
    if h == 0:
        return {(): 0}
    signatures = {}
    for state in product(range(2), repeat=h):
        fb = state[0]
        if prev_class is None:
            sig = (fb, 0, 0)
        else:
            s0 = rule30_next_tuple(state, 0)[:h - 1]
            s1 = rule30_next_tuple(state, 1)[:h - 1]
            sig = (fb, prev_class[s0], prev_class[s1])
        signatures[state] = sig
    sig_to_id: dict = {}
    stc: dict = {}
    for state, sig in signatures.items():
        if sig not in sig_to_id:
            sig_to_id[sig] = len(sig_to_id)
        stc[state] = sig_to_id[sig]
    return stc


def make_int_transition_table(q: dict, h: int):
    """Build a transition table: (state_int, bit) -> (next_state_int, class_id).
    state is encoded as h-bit integer with bit 0 = leftmost cell."""
    n = 1 << h
    next_state_table = [[0] * n, [0] * n]   # [bit][state_int]
    class_table = [0] * n                     # state_int -> class_id

    for state_tuple, cid in q.items():
        state_int = 0
        for i, b in enumerate(state_tuple):
            state_int |= (b << i)
        class_table[state_int] = cid
        for bit in range(2):
            ns_tuple = rule30_next_tuple(state_tuple, bit)[:h]
            ns_int = 0
            for i, b in enumerate(ns_tuple):
                ns_int |= (b << i)
            next_state_table[bit][state_int] = ns_int

    return next_state_table, class_table


def generate_center_column_bitwise_fast(steps: int) -> list:
    """Generate center column bits efficiently using numpy."""
    try:
        import numpy as np
        # Use numpy uint8 arrays for the row (much faster than Python lists)
        # At step t, the active region has width 2t+1 centered at position steps+1
        width = 2 * steps + 3
        center_idx = steps + 1
        row = np.zeros(width, dtype=np.uint8)
        row[center_idx] = 1
        
        result = [0] * (steps + 1)
        result[0] = 1
        
        for t in range(1, steps + 1):
            # Rule 30: new[i] = row[i-1] ^ (row[i] | row[i+1])
            # Only compute in the active region
            lo = center_idx - t
            hi = center_idx + t + 1
            left = row[lo-1:hi-1]
            center = row[lo:hi]
            right = row[lo+1:hi+1]
            row[lo:hi] = center ^ (left | right)
            result[t] = int(row[center_idx])
        
        return result
    except ImportError:
        from rule30_center_column import generate_center_column_bitwise
        return generate_center_column_bitwise(steps)


def main():
    h = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    steps = int(sys.argv[2]) if len(sys.argv) > 2 else 5_000_000

    print(f"Building quotient maps h=0..{h}...")
    prev = None
    for hh in range(h + 1):
        print(f"  h={hh}...", end="\r", flush=True)
        cm = build_quotient_at_horizon(hh, prev)
        prev = cm
    q = cm
    total_classes = max(q.values()) + 1
    print(f"|S_{h}| = {total_classes} classes                    ")

    print(f"Building integer transition table...")
    next_state_table, class_table = make_int_transition_table(q, h)
    print(f"Done. Table size: {len(class_table)} states")

    print(f"Generating {steps} center-column bits...")
    center = generate_center_column_bitwise_fast(steps - 1)
    print(f"Done ({len(center)} bits). Tracing trajectory at h={h}...")

    state_int = 0  # all-zeros initial state
    visited = set()
    first_visit: dict[int, int] = {}

    # Initial state class
    cid = class_table[state_int]
    visited.add(cid)
    first_visit[cid] = 0

    for t in range(1, steps):
        bit = center[t - 1]
        state_int = next_state_table[bit][state_int]
        cid = class_table[state_int]
        if cid not in visited:
            visited.add(cid)
            first_visit[cid] = t
            if len(visited) == total_classes:
                print(f"\nAll {total_classes} classes visited at step {t}! (ratio: {t/total_classes:.1f}x)")
                break
        if t % 1_000_000 == 0:
            print(f"  t={t//1000}k: {len(visited)}/{total_classes} classes visited...")

    missing = [cid for cid in range(total_classes) if cid not in visited]
    print(f"\n--- Result ---")
    print(f"After {min(steps, t+1)} steps: {len(visited)}/{total_classes} classes visited.")
    print(f"Missing: {len(missing)} class(es).")

    if missing:
        print(f"\nUnvisited class(es):")
        for cid in missing:
            states_in_class = [s for s, c in q.items() if c == cid]
            print(f"  Class {cid}: {len(states_in_class)} raw states")
            for s in sorted(states_in_class)[:8]:
                bits = "".join(map(str, s))
                weight = sum(s)
                print(f"    {bits}  (weight={weight})")
            if len(states_in_class) > 8:
                print(f"    ... and {len(states_in_class)-8} more")

    # Show rarest classes (latest first visit)
    print(f"\nTop 10 rarest (latest first-visit time):")
    sorted_fv = sorted(first_visit.items(), key=lambda x: -x[1])
    for cid, fvt in sorted_fv[:10]:
        states_in_class = [s for s, c in q.items() if c == cid]
        bits = "".join(map(str, states_in_class[0]))
        weight = sum(states_in_class[0])
        print(f"  class {cid}: first_visit={fvt:8d}  size={len(states_in_class):3d}  ex={bits}  (wt={weight})")

    # Visit count stats
    visit_count = {cid: 0 for cid in range(total_classes)}
    # We would need to rerun to count visits, skip for now

    print(f"\nSaturation ratio: {max(fvt for fvt in first_visit.values()) / total_classes:.1f}x")


if __name__ == "__main__":
    main()
