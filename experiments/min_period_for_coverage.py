#!/usr/bin/env python3
"""
For each h, find the minimum period p of a RANDOM periodic sequence that achieves
full coverage of S_h within 1M steps.

This gives a lower bound on p for coverage to be possible.
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
    N = 1000000
    
    for h in [8, 10, 12, 14, 15, 16]:
        q = build_quotient(h)
        total = max(q.values()) + 1
        trans, cls_of = make_transition_tables(q, h)
        
        print(f"\nh={h:2d} |S|={total:4d}")
        
        # Binary search for minimum period
        # Test periods: exponentially spaced
        for p in [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 50000, 100000]:
            if p > N // 2:
                break
            
            # Try 10 random sequences of this period
            successes = 0
            num_trials = 10
            for trial in range(num_trials):
                random.seed(h * 10000 + p * 100 + trial)
                base = [random.randint(0, 1) for _ in range(p)]
                per_bits = (base * (N // p + 1))[:N]
                sat = check_coverage(trans, cls_of, total, per_bits, N)
                if sat is not None:
                    successes += 1
            
            if successes > 0:
                max_visited = 0
                # For failed trials, how many classes were visited?
                for trial in range(num_trials):
                    random.seed(h * 10000 + p * 100 + trial)
                    base = [random.randint(0, 1) for _ in range(p)]
                    per_bits = (base * (N // p + 1))[:N]
                    current = 0
                    visited = set()
                    visited.add(cls_of[current])
                    for t in range(min(N, len(per_bits))):
                        current = trans[per_bits[t]][current]
                        visited.add(cls_of[current])
                    max_visited = max(max_visited, len(visited))
                
                print(f"  p={p:>6d}: {successes}/{num_trials} succeed, max_visited={max_visited}")
            else:
                # Check max classes visited
                max_visited = 0
                for trial in range(num_trials):
                    random.seed(h * 10000 + p * 100 + trial)
                    base = [random.randint(0, 1) for _ in range(p)]
                    per_bits = (base * (N // p + 1))[:N]
                    current = 0
                    visited = set()
                    visited.add(cls_of[current])
                    for t in range(min(N, len(per_bits))):
                        current = trans[per_bits[t]][current]
                        visited.add(cls_of[current])
                    max_visited = max(max_visited, len(visited))
                
                print(f"  p={p:>6d}: 0/{num_trials} succeed, max_visited={max_visited}/{total}")


if __name__ == "__main__":
    main()
