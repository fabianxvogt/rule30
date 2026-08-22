#!/usr/bin/env python3
"""
Investigate classes that are hard to reach in the TRUE right-half dynamics.

For each horizon h, identify which classes take the longest to appear
(or are never reached within the available steps).
"""
from __future__ import annotations

import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient


def run_true_coverage_detailed(h, max_steps):
    """Return dict mapping class_id -> first_visit_time (or None if never visited)."""
    q = build_quotient(h)
    total_classes = max(q.values()) + 1
    
    # Build inverse map: class_id -> set of h-tuples
    class_to_tuples = {}
    for tup, cid in q.items():
        class_to_tuples.setdefault(cid, set()).add(tup)
    
    # Load center column bits
    bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "results", "center-column-1000000.txt")
    with open(bits_file) as f:
        bits = [int(c) for c in f.read().strip() if c in '01']
    
    max_steps = min(max_steps, len(bits))
    W = max_steps + h + 10
    
    state = np.zeros(W + 2, dtype=np.uint8)
    
    first_visit = {}
    initial_prefix = tuple(state[1:h+1])
    cid = q.get(initial_prefix)
    if cid is not None:
        first_visit[cid] = 0
    
    for t in range(max_steps):
        state[0] = bits[t]
        state[W + 1] = 0
        
        new_state = np.zeros(W + 2, dtype=np.uint8)
        new_state[1:W+1] = state[0:W] ^ (state[1:W+1] | state[2:W+2])
        state = new_state
        
        prefix = tuple(state[1:h+1])
        cid = q.get(prefix)
        
        if cid is not None and cid not in first_visit:
            first_visit[cid] = t + 1
    
    return first_visit, total_classes, class_to_tuples, q


def run_truncated_coverage_detailed(h, max_steps):
    """Return dict mapping class_id -> first_visit_time for truncated dynamics."""
    from fast_class_coverage2 import build_quotient, make_transition_tables
    
    q = build_quotient(h)
    total_classes = max(q.values()) + 1
    
    cls_of, trans = make_transition_tables(q, h)
    
    bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "results", "center-column-1000000.txt")
    with open(bits_file) as f:
        bits = [int(c) for c in f.read().strip() if c in '01']
    
    max_steps = min(max_steps, len(bits))
    
    first_visit = {}
    current = 0  # start from all-zeros h-tuple → class 0
    first_visit[cls_of[current]] = 0
    
    for t in range(max_steps):
        current = trans[bits[t]][current]
        c = cls_of[current]
        if c not in first_visit:
            first_visit[c] = t + 1
    
    return first_visit, total_classes


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--horizon", type=int, default=19)
    parser.add_argument("--max-steps", type=int, default=999999)
    args = parser.parse_args()
    
    h = args.horizon
    max_steps = args.max_steps
    
    print(f"h={h}, Running true coverage with {max_steps} steps...")
    sys.stdout.flush()
    
    t0 = time.time()
    true_first, total, class_to_tuples, q = run_true_coverage_detailed(h, max_steps)
    t1 = time.time()
    print(f"  True: {len(true_first)}/{total} classes visited in {t1-t0:.1f}s")
    
    # Find missing classes in true system
    all_classes = set(range(total))
    true_missing = all_classes - set(true_first.keys())
    
    if true_missing:
        print(f"\n  Missing classes in TRUE system ({len(true_missing)}):")
        for cid in sorted(true_missing):
            tuples = class_to_tuples.get(cid, set())
            size = len(tuples)
            sample = sorted(tuples)[:3]
            sample_str = [str(t) for t in sample]
            print(f"    Class {cid}: {size} tuple(s), e.g. {', '.join(sample_str)}")
    
    # Last 10 classes to be visited
    if true_first:
        sorted_visits = sorted(true_first.items(), key=lambda x: x[1], reverse=True)
        print(f"\n  Last 10 classes visited (true):")
        for cid, step in sorted_visits[:10]:
            tuples = class_to_tuples.get(cid, set())
            size = len(tuples)
            print(f"    Class {cid}: first visit at step {step}, {size} tuple(s)")
    
    # Also run truncated for comparison
    print(f"\nRunning truncated coverage with {max_steps} steps...")
    sys.stdout.flush()
    
    t0 = time.time()
    trunc_first, total2 = run_truncated_coverage_detailed(h, max_steps)
    t1 = time.time()
    print(f"  Truncated: {len(trunc_first)}/{total2} classes visited in {t1-t0:.1f}s")
    
    trunc_missing = all_classes - set(trunc_first.keys())
    if trunc_missing:
        print(f"\n  Missing classes in TRUNCATED system ({len(trunc_missing)}):")
        for cid in sorted(trunc_missing):
            tuples = class_to_tuples.get(cid, set())
            size = len(tuples)
            sample = sorted(tuples)[:3]
            sample_str = [str(t) for t in sample]
            print(f"    Class {cid}: {size} tuple(s), e.g. {', '.join(sample_str)}")
    
    # Check overlap of missing classes
    if true_missing and trunc_missing:
        overlap = true_missing & trunc_missing
        print(f"\n  Missing in BOTH: {len(overlap)} classes")
        true_only = true_missing - trunc_missing
        trunc_only = trunc_missing - true_missing
        print(f"  Missing in true only: {len(true_only)}")
        print(f"  Missing in truncated only: {len(trunc_only)}")
    
    # For classes that appear in both, compare arrival times
    common = set(true_first.keys()) & set(trunc_first.keys())
    if common:
        diffs = [(cid, true_first[cid], trunc_first[cid]) for cid in common]
        true_earlier = sum(1 for _, t, tr in diffs if t < tr)
        trunc_earlier = sum(1 for _, t, tr in diffs if tr < t)
        same_time = sum(1 for _, t, tr in diffs if t == tr)
        print(f"\n  Among {len(common)} commonly visited classes:")
        print(f"    True arrives first: {true_earlier}")
        print(f"    Truncated arrives first: {trunc_earlier}")
        print(f"    Same time: {same_time}")


if __name__ == "__main__":
    main()
