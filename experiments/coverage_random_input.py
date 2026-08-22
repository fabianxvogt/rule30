#!/usr/bin/env python3
"""
Test: does coverage hold for RANDOM binary input sequences?

If yes, then coverage is a generic property of the truncated system.
If no, then it's specific to the Rule 30 center column.
"""
from __future__ import annotations

import os
import sys
import time
import random

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables


def check_coverage(trans, cls_of, total_classes, bits, max_steps):
    current = 0
    visited = set()
    visited.add(cls_of[current])
    for t in range(min(max_steps, len(bits))):
        current = trans[bits[t]][current]
        visited.add(cls_of[current])
        if len(visited) == total_classes:
            return t + 1
    return None


def main():
    bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "results", "center-column-1000000.txt")
    with open(bits_file) as f:
        real_bits = [int(c) for c in f.read().strip() if c in '01']
    
    N = len(real_bits)
    
    for h in range(10, 19):
        q = build_quotient(h)
        total = max(q.values()) + 1
        trans, cls_of = make_transition_tables(q, h)
        
        # Real center column
        real_sat = check_coverage(trans, cls_of, total, real_bits, N)
        
        # Random sequences (fair coin)
        random.seed(42)
        rand_sats = []
        num_trials = 20
        for _ in range(num_trials):
            rand_bits = [random.randint(0, 1) for _ in range(N)]
            sat = check_coverage(trans, cls_of, total, rand_bits, N)
            rand_sats.append(sat)
        
        conv = [s for s in rand_sats if s is not None]
        
        # Periodic sequences
        periodic_sats = {}
        for p in [2, 3, 5, 10, 50, 100, 1000]:
            # Generate random periodic sequence with period p
            random.seed(p * h)
            base = [random.randint(0, 1) for _ in range(p)]
            per_bits = (base * (N // p + 1))[:N]
            sat = check_coverage(trans, cls_of, total, per_bits, N)
            periodic_sats[p] = sat
        
        # All-zeros and all-ones driving sequences
        zeros_sat = check_coverage(trans, cls_of, total, [0]*N, N)
        ones_sat = check_coverage(trans, cls_of, total, [1]*N, N)
        alt_sat = check_coverage(trans, cls_of, total, [t % 2 for t in range(N)], N)
        
        print(f"\nh={h:2d} |S|={total:4d}")
        print(f"  Rule 30 center: sat={real_sat}")
        print(f"  Random (fair):  {len(conv)}/{num_trials} converged", end="")
        if conv:
            print(f", min={min(conv)}, max={max(conv)}, mean={sum(conv)/len(conv):.0f}")
        else:
            print()
        print(f"  Constant 0:     sat={zeros_sat}")
        print(f"  Constant 1:     sat={ones_sat}")
        print(f"  Alternating 01: sat={alt_sat}")
        per_strs = [f"p={p}:{s}" for p, s in sorted(periodic_sats.items())]
        print(f"  Periodic:       {', '.join(per_strs)}")


if __name__ == "__main__":
    main()
