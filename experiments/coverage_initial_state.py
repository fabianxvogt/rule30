#!/usr/bin/env python3
"""
Test: does the center-column-driven truncated trajectory achieve full coverage
regardless of the INITIAL STATE?

If so, then coverage is a property of the driving sequence, not the starting point.
If not, then coverage depends on starting from all-zeros.
"""
from __future__ import annotations

import os
import sys
import time
import random

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables


def check_coverage_from_state(trans, cls_of, total_classes, bits, start_raw, max_steps):
    """Check if starting from start_raw, we achieve full coverage."""
    current = start_raw
    visited = set()
    visited.add(cls_of[current])
    
    for t in range(min(max_steps, len(bits))):
        current = trans[bits[t]][current]
        visited.add(cls_of[current])
        if len(visited) == total_classes:
            return t + 1  # saturation step
    
    return None  # not converged


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--horizon", type=int, default=15)
    parser.add_argument("--num-starts", type=int, default=100)
    parser.add_argument("--max-steps", type=int, default=200000)
    args = parser.parse_args()
    
    h = args.horizon
    
    bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "results", "center-column-1000000.txt")
    with open(bits_file) as f:
        bits = [int(c) for c in f.read().strip() if c in '01']
    
    q = build_quotient(h)
    total_classes = max(q.values()) + 1
    trans, cls_of = make_transition_tables(q, h)
    
    n = 1 << h
    
    print(f"h={h}, |S_{h}|={total_classes}, testing {args.num_starts} random starting states")
    print(f"Max steps: {args.max_steps}")
    
    # Test from all-zeros first
    t0 = time.time()
    sat = check_coverage_from_state(trans, cls_of, total_classes, bits, 0, args.max_steps)
    print(f"\nAll-zeros (raw=0): sat_step = {sat}")
    
    # Test from all-ones
    all_ones = n - 1
    sat = check_coverage_from_state(trans, cls_of, total_classes, bits, all_ones, args.max_steps)
    print(f"All-ones (raw={all_ones}): sat_step = {sat}")
    
    # Test from random starting states
    random.seed(42)
    results = []
    for i in range(args.num_starts):
        start = random.randint(0, n - 1)
        sat = check_coverage_from_state(trans, cls_of, total_classes, bits, start, args.max_steps)
        results.append((start, sat))
    
    converged = [(s, sat) for s, sat in results if sat is not None]
    not_converged = [(s, sat) for s, sat in results if sat is None]
    
    print(f"\nOut of {args.num_starts} random starts:")
    print(f"  Converged: {len(converged)}")
    print(f"  Not converged: {len(not_converged)}")
    
    if converged:
        sats = [s for _, s in converged]
        print(f"  Min sat_step: {min(sats)}")
        print(f"  Max sat_step: {max(sats)}")
        print(f"  Mean sat_step: {sum(sats)/len(sats):.0f}")
    
    if not_converged:
        print(f"\n  Non-converging starting states (first 10):")
        for start, _ in not_converged[:10]:
            # How many classes visited?
            current = start
            visited = set()
            visited.add(cls_of[current])
            for t in range(min(args.max_steps, len(bits))):
                current = trans[bits[t]][current]
                visited.add(cls_of[current])
            print(f"    raw={start}: {len(visited)}/{total_classes} classes visited")
    
    elapsed = time.time() - t0
    print(f"\nTotal time: {elapsed:.1f}s")
    
    # Also test: starting from a point in the periodic part of the trajectory
    # (after T steps), does a SHIFTED version achieve coverage?
    print(f"\n--- Shifted start test ---")
    # Drive from zeros for T steps, then record the state, then test from there
    # with the remaining bits
    for T_shift in [100, 1000, 10000]:
        current = 0
        for t in range(T_shift):
            current = trans[bits[t]][current]
        
        # Now check coverage using bits[T_shift:]
        remaining_bits = bits[T_shift:]
        sat = check_coverage_from_state(trans, cls_of, total_classes, remaining_bits, current, args.max_steps)
        print(f"  Start after {T_shift} steps: sat_step = {sat} (from shifted bits)")


if __name__ == "__main__":
    main()
