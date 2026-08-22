#!/usr/bin/env python3
"""
Verify that the trajectory at horizon h, projected via rho_h, equals the
trajectory at horizon h-1.

Specifically: rho_h maps an h-bit state to an (h-1)-bit state by dropping
the last bit. The claim is that if we track the driven right-half at width h
and width h-1 simultaneously, then rho(state_h(t)) = state_{h-1}(t) for all t.

This should follow from the fact that Rule 30 is local and the dropped bit
doesn't affect the first h-1 bits in the next step (it only affects bits at
distance ≤ 1, but the dropped bit is at position h-1, affecting only position h-2).

Wait, that's wrong: the dropped bit at position h-1 DOES affect position h-2
(which is within the h-1 retained bits)! So rho doesn't commute with the dynamics.

Let me check empirically.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, rule30_next_tuple


def main():
    bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "results", "center-column-1000000.txt")
    with open(bits_file) as f:
        bits = [int(c) for c in f.read().strip() if c in '01']
    
    print("Check: does rho(evolve_h(s, b)) == evolve_{h-1}(rho(s), b)?")
    print("(i.e., does truncation commute with one-step evolution?)\n")
    
    for h in range(3, 12):
        # Run both trajectories
        state_h = tuple([0] * h)
        state_hm1 = tuple([0] * (h - 1))
        
        mismatches = 0
        for t in range(100):
            bit = bits[t]
            
            # Evolve at width h, then truncate
            next_h = rule30_next_tuple(state_h, bit)[:h]
            truncated_h = next_h[:h-1]
            
            # Evolve at width h-1
            next_hm1 = rule30_next_tuple(state_hm1, bit)[:h-1]
            
            if truncated_h != next_hm1:
                mismatches += 1
                if mismatches <= 3:
                    print(f"  h={h}, t={t}: truncated evolved = {truncated_h}, "
                          f"direct evolved = {next_hm1}")
            
            state_h = next_h
            state_hm1 = next_hm1
        
        print(f"h={h}: mismatches in 100 steps = {mismatches}")
    
    print("\n\nSo rho does NOT commute with the dynamics!")
    print("The trajectory at horizon h, truncated, is NOT the trajectory at horizon h-1.")
    print("This means V_h(N) is NOT necessarily monotone in h.")


if __name__ == "__main__":
    main()
