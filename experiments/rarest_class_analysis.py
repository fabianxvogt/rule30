#!/usr/bin/env python3
"""
Analyze the boundary-word patterns that lead to the rarest (last-visited) classes.

For each horizon h, find the last few classes to be visited by the truncated trajectory,
and examine the boundary-word sequences that steer the system into those classes.

Also check: for each class c, what is the SHORTEST boundary word from all-zeros that
reaches some state in c? (This is the "BFS distance" from all-zeros to class c.)
"""
from __future__ import annotations

import os
import sys
import time
from collections import deque

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, rule30_next_tuple


def bfs_class_distances(q, h):
    """BFS from all-zeros to find min #steps to reach each class."""
    total_classes = max(q.values()) + 1
    start = (0,) * h
    start_class = q[start]
    
    # BFS on raw states
    visited = {start: 0}
    class_first = {start_class: 0}
    queue = deque([(start, 0)])
    
    while queue and len(class_first) < total_classes:
        state, depth = queue.popleft()
        if depth >= h + 5:  # Don't go too deep; Theorem 11 says h steps suffice
            continue
        for b in (0, 1):
            nxt = rule30_next_tuple(state, b)
            if nxt not in visited:
                visited[nxt] = depth + 1
                c = q[nxt]
                if c not in class_first:
                    class_first[c] = depth + 1
                queue.append((nxt, depth + 1))
    
    return class_first


def trajectory_approach_analysis(q, h, max_steps=None):
    """
    For each class, record:
    - First visit time in the center-column trajectory
    - The h-tuple that first visits it
    - The preceding h boundary bits (center column bits c(t-h)..c(t-1))
    """
    from fast_class_coverage2 import make_transition_tables
    
    trans, cls_of = make_transition_tables(q, h)
    total_classes = max(q.values()) + 1
    
    bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "results", "center-column-1000000.txt")
    with open(bits_file) as f:
        bits = [int(c) for c in f.read().strip() if c in '01']
    
    if max_steps is not None:
        max_steps = min(max_steps, len(bits))
    else:
        max_steps = len(bits)
    
    # Track raw states too
    state = (0,) * h
    first_visit = {}
    first_state = {}
    
    cid = cls_of[q[state]]
    if cid not in first_visit:
        first_visit[cid] = 0
        first_state[cid] = state
    
    current_raw = 0  # integer representation
    for t in range(max_steps):
        current_raw = trans[bits[t]][current_raw]
        c = cls_of[current_raw]
        if c not in first_visit:
            first_visit[c] = t + 1
            # Reconstruct the h-tuple
            tup = []
            v = current_raw
            for _ in range(h):
                tup.append(v & 1)
                v >>= 1
            first_state[c] = tuple(tup)
        if len(first_visit) == total_classes:
            break
    
    return first_visit, first_state


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-horizon", type=int, default=20)
    parser.add_argument("--min-horizon", type=int, default=15)
    args = parser.parse_args()
    
    bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "results", "center-column-1000000.txt")
    with open(bits_file) as f:
        bits = [int(c) for c in f.read().strip() if c in '01']
    
    for h in range(args.min_horizon, args.max_horizon + 1):
        t0 = time.time()
        print(f"\n{'='*60}")
        print(f"h = {h}")
        print(f"{'='*60}")
        
        q = build_quotient(h)
        total_classes = max(q.values()) + 1
        print(f"|S_{h}| = {total_classes}")
        
        # BFS distances
        print("Computing BFS distances from all-zeros...")
        class_dist = bfs_class_distances(q, h)
        max_dist = max(class_dist.values())
        dist_hist = {}
        for d in class_dist.values():
            dist_hist[d] = dist_hist.get(d, 0) + 1
        print(f"  Max BFS distance: {max_dist}")
        print(f"  Distance histogram: {dict(sorted(dist_hist.items()))}")
        
        # Trajectory analysis
        print("Computing trajectory first-visit times...")
        first_visit, first_state = trajectory_approach_analysis(q, h)
        
        if len(first_visit) < total_classes:
            missing = total_classes - len(first_visit)
            print(f"  WARNING: {missing} classes not visited in 1M steps")
        
        # Last 10 visited classes
        sorted_visits = sorted(first_visit.items(), key=lambda x: x[1], reverse=True)
        print(f"\n  Last 10 classes visited:")
        print(f"  {'Class':>6} {'Visit step':>10} {'BFS dist':>9} {'State':>30} {'Weight':>6}")
        for cid, step in sorted_visits[:10]:
            state = first_state.get(cid)
            if state:
                weight = sum(state)
                state_str = ''.join(str(b) for b in state)
            else:
                weight = -1
                state_str = "?"
            bfs = class_dist.get(cid, -1)
            print(f"  {cid:>6} {step:>10} {bfs:>9} {state_str:>30} {weight:>6}")
        
        # Correlation between BFS distance and visit time
        common = set(first_visit.keys()) & set(class_dist.keys())
        if common:
            from statistics import correlation
            try:
                xs = [class_dist[c] for c in common]
                ys = [first_visit[c] for c in common]
                corr = correlation(xs, ys)
                print(f"\n  Correlation(BFS dist, visit time): {corr:.3f}")
            except Exception:
                pass
        
        # Classes reachable in exactly h steps (maximum BFS distance)
        at_max_dist = [c for c, d in class_dist.items() if d == max_dist]
        print(f"\n  Classes at max BFS distance ({max_dist}): {len(at_max_dist)}")
        if len(at_max_dist) <= 5:
            for c in at_max_dist:
                visit = first_visit.get(c, float('inf'))
                print(f"    Class {c}: visit at step {visit}")
        
        elapsed = time.time() - t0
        print(f"\n  ({elapsed:.1f}s)")


if __name__ == "__main__":
    main()
