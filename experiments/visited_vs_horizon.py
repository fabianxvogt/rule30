#!/usr/bin/env python3
"""
For each horizon h, count how many classes are visited by the first N steps 
of the center column trajectory, for various small N.

Question: if the center column had period p, then at most p classes could be
visited at each h (plus possibly a pre-period of at most h+T). Can we show
that N visited classes grows with h even for FIXED N?

For the actual center column with N=10^6 steps, this will show the pattern.
But more interesting: for a GENERIC eventually periodic sequence with period p,
the number of classes visited is ≤ p. We want to show Rule 30 does better.
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables


def main():
    # Load center column bits
    bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "results", "center-column-1000000.txt")
    with open(bits_file) as f:
        bits = [int(c) for c in f.read().strip() if c in '01']
    
    N = len(bits)
    print(f"Loaded {N} center column bits")
    
    thresholds = [100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]
    
    print(f"\n{'h':>3} {'|S_h|':>7}", end="")
    for t in thresholds:
        print(f"  {'N='+str(t):>10}", end="")
    print()
    print("-" * (12 + 12 * len(thresholds)))
    
    for h in range(1, 22):
        q = build_quotient(h)
        total_classes = max(q.values()) + 1
        next_state, class_table = make_transition_tables(q, h)
        
        state = 0
        visited = set()
        visited.add(class_table[state])
        
        result = {}
        ti = 0
        
        for t in range(1, min(N, max(thresholds) + 1)):
            state = next_state[bits[t-1]][state]
            visited.add(class_table[state])
            
            while ti < len(thresholds) and thresholds[ti] == t:
                result[t] = len(visited)
                ti += 1
        
        # Fill remaining
        for t in thresholds:
            if t not in result:
                result[t] = len(visited)
        
        print(f"{h:3d} {total_classes:7d}", end="")
        for t in thresholds:
            v = result.get(t, 0)
            pct = v * 100 / total_classes if total_classes > 0 else 0
            print(f"  {v:5d}({pct:3.0f}%)", end="")
        print()


if __name__ == "__main__":
    main()
