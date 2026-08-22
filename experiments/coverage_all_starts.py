#!/usr/bin/env python3
"""
Comprehensive test: does coverage depend on initial state?
For each h, test multiple starting states with full 1M bits.
"""
from __future__ import annotations

import os
import sys
import time
import random

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables


def main():
    bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "results", "center-column-1000000.txt")
    with open(bits_file) as f:
        bits = [int(c) for c in f.read().strip() if c in '01']
    
    N = len(bits)
    random.seed(42)
    
    for h in range(10, 21):
        q = build_quotient(h)
        total = max(q.values()) + 1
        trans, cls_of = make_transition_tables(q, h)
        n = 1 << h
        
        num_starts = min(200, n)
        starts = [0, n-1]  # all-zeros, all-ones
        starts.extend(random.sample(range(1, n-1), min(num_starts - 2, n-2)))
        
        t0 = time.time()
        sat_steps = []
        not_conv = 0
        
        for start in starts:
            current = start
            visited = set()
            visited.add(cls_of[current])
            sat = None
            for t in range(N):
                current = trans[bits[t]][current]
                visited.add(cls_of[current])
                if len(visited) == total:
                    sat = t + 1
                    break
            sat_steps.append(sat)
            if sat is None:
                not_conv += 1
        
        elapsed = time.time() - t0
        
        converged = [s for s in sat_steps if s is not None]
        if converged:
            min_s = min(converged)
            max_s = max(converged)
            mean_s = sum(converged)/len(converged)
        else:
            min_s = max_s = mean_s = -1
        
        # Sat from zeros and ones
        zeros_sat = sat_steps[0]
        ones_sat = sat_steps[1]
        
        print(f"h={h:2d} |S|={total:5d} | {num_starts} starts: "
              f"{len(converged)} conv, {not_conv} not | "
              f"sat[0s]={zeros_sat}, sat[1s]={ones_sat} | "
              f"min={min_s}, max={max_s}, mean={mean_s:.0f} | "
              f"{elapsed:.1f}s")


if __name__ == "__main__":
    main()
