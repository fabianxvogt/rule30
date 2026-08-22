#!/usr/bin/env python3
"""
Fast search for when all S_h predictive-state classes are first visited.

Uses integer lookup tables for O(1) trajectory steps, and loads precomputed
center-column bits from a file (or generates them with big-int method).

Usage:
  python3 fast_class_coverage.py --horizon H --file results/center-column-1000000.txt
  python3 fast_class_coverage.py --horizon H --steps N
"""
from __future__ import annotations

import argparse
import sys
import os
from itertools import product

sys.path.insert(0, os.path.dirname(__file__))


def rule30_next_tuple(state: tuple, boundary_bit: int) -> tuple:
    w = len(state)
    row = (boundary_bit,) + state + (0,)
    return tuple(row[i] ^ (row[i+1] | row[i+2]) for i in range(w))


def build_quotient(h: int) -> dict:
    """Build quotient map from h-tuples to class IDs."""
    prev = None
    for hh in range(h + 1):
        if hh == 0:
            cm = {(): 0}
        else:
            signatures = {}
            for state in product(range(2), repeat=hh):
                fb = state[0]
                if prev is None:
                    sig = (fb, 0, 0)
                else:
                    s0 = rule30_next_tuple(state, 0)[:hh - 1]
                    s1 = rule30_next_tuple(state, 1)[:hh - 1]
                    sig = (fb, prev[s0], prev[s1])
                signatures[state] = sig
            sig_to_id: dict = {}
            cm = {}
            for state, sig in signatures.items():
                if sig not in sig_to_id:
                    sig_to_id[sig] = len(sig_to_id)
                cm[state] = sig_to_id[sig]
        prev = cm
    return cm


def make_transition_tables(q: dict, h: int):
    """Build integer-indexed lookup tables for fast trajectory tracing.
    
    Returns:
        next_state[bit][state_int] -> next_state_int
        class_table[state_int] -> class_id
    """
    n = 1 << h
    next_state = [[0] * n, [0] * n]
    class_table = [0] * n

    for state_tuple, cid in q.items():
        # Encode tuple as integer: bit i = state_tuple[i], LSB = leftmost
        state_int = sum(b << i for i, b in enumerate(state_tuple))
        class_table[state_int] = cid
        for bit in range(2):
            ns = rule30_next_tuple(state_tuple, bit)[:h]
            ns_int = sum(b << i for i, b in enumerate(ns))
            next_state[bit][state_int] = ns_int

    return next_state, class_table


def generate_bits(steps: int) -> list:
    """Generate center column bits using big-integer method."""
    from rule30_center_column import generate_center_column_bitwise
    return generate_center_column_bitwise(steps)


def load_bits(filepath: str) -> list:
    """Load precomputed center column bits from file."""
    print(f"Loading bits from {filepath}...")
    with open(filepath) as f:
        content = f.read().strip()
    bits = [int(b) for b in content if b in '01']
    print(f"Loaded {len(bits)} bits.")
    return bits


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--horizon", type=int, default=20)
    parser.add_argument("--steps", type=int, default=0,
                        help="Number of steps to generate (0 = use --file)")
    parser.add_argument("--file", type=str, default="",
                        help="Path to precomputed center-column bit file")
    args = parser.parse_args()

    h = args.horizon
    print(f"Building quotient maps h=0..{h}...")
    q = build_quotient(h)
    total_classes = max(q.values()) + 1
    print(f"|S_{h}| = {total_classes} classes")

    print("Building integer transition tables...")
    next_state, class_table = make_transition_tables(q, h)
    print(f"Done. Table size: {len(class_table)} states")

    # Load or generate center column bits
    if args.file:
        center = load_bits(args.file)
    elif args.steps > 0:
        print(f"Generating {args.steps} center-column bits...")
        center = generate_bits(args.steps - 1)
        print(f"Generated {len(center)} bits.")
    else:
        print("Error: specify --file or --steps")
        sys.exit(1)

    steps = len(center)
    print(f"Tracing trajectory at h={h} for {steps} steps...")

    state_int = 0  # all-zeros initial state
    visited: set = set()
    first_visit: dict = {}

    cid = class_table[state_int]
    visited.add(cid)
    first_visit[cid] = 0

    sat_step = None
    for t in range(1, steps):
        bit = center[t - 1]
        state_int = next_state[bit][state_int]
        cid = class_table[state_int]
        if cid not in visited:
            visited.add(cid)
            first_visit[cid] = t
            if len(visited) == total_classes:
                sat_step = t
                print(f"  All {total_classes} classes covered at step {t} "
                      f"(ratio: {t/total_classes:.1f}x)!")
                break
        if t % 500_000 == 0:
            print(f"  t={t//1000}k: {len(visited)}/{total_classes} classes visited...")

    missing = [cid for cid in range(total_classes) if cid not in visited]
    print(f"\n=== Result at h={h} ===")
    print(f"Steps examined: {min(steps, (sat_step or steps-1)+1)}")
    print(f"Classes visited: {len(visited)}/{total_classes}")
    print(f"Missing: {len(missing)}")

    if missing:
        print(f"\nUnvisited class(es):")
        for cid in missing:
            states_in_class = [s for s, c in q.items() if c == cid]
            print(f"  Class {cid}: {len(states_in_class)} raw states")
            for s in sorted(states_in_class)[:8]:
                bits_str = "".join(map(str, s))
                weight = sum(s)
                print(f"    {bits_str}  (weight={weight})")

    print(f"\nTop 10 rarest (latest first-visit):")
    sorted_fv = sorted(first_visit.items(), key=lambda x: -x[1])
    for cid, fvt in sorted_fv[:10]:
        states_in_class = [s for s, c in q.items() if c == cid]
        ex = "".join(map(str, states_in_class[0]))
        wt = sum(states_in_class[0])
        print(f"  class {cid:4d}: first_visit={fvt:8d}  "
              f"size={len(states_in_class):3d}  ex={ex}  (wt={wt})")

    if sat_step is not None:
        print(f"\nSaturation ratio: {sat_step/total_classes:.1f}x")
    else:
        print(f"\nNot fully saturated. Coverage: {len(visited)}/{total_classes}")


if __name__ == "__main__":
    main()
