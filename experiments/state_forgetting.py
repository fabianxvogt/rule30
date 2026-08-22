#!/usr/bin/env python3
"""
Check: does the truncated system forget its initial state after h steps?

For two different starting states s and s', driven by the same boundary bits,
do they converge to the same state after h steps?
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, rule30_next_tuple


def evolve_truncated(initial_state, boundary_bits, h):
    """Evolve the truncated system from initial_state with given boundary bits."""
    state = list(initial_state)
    for b in boundary_bits:
        new = list(rule30_next_tuple(tuple(state), b)[:h])
        state = new
    return tuple(state)


def main():
    for h in [5, 8, 10, 15]:
        print(f"\nh={h}")
        
        # Test: starting from all-zeros vs all-ones with the same boundary bits
        zeros = (0,) * h
        ones = (1,) * h
        
        # Use center column bits as boundary
        bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 "results", "center-column-1000000.txt")
        with open(bits_file) as f:
            bits = [int(c) for c in f.read().strip()[:2*h] if c in '01']
        
        # Evolve step by step and compare
        state_z = list(zeros)
        state_o = list(ones)
        
        for t in range(2*h):
            state_z = list(rule30_next_tuple(tuple(state_z), bits[t])[:h])
            state_o = list(rule30_next_tuple(tuple(state_o), bits[t])[:h])
            
            # Compare
            diff = sum(1 for a, b in zip(state_z, state_o) if a != b)
            if t < 5 or t >= h-2:
                z_str = ''.join(str(b) for b in state_z[:min(20, h)])
                o_str = ''.join(str(b) for b in state_o[:min(20, h)])
                if h > 20:
                    z_str += '...'
                    o_str += '...'
                print(f"  t={t+1}: diff={diff}, zeros→{z_str}, ones→{o_str}")
            elif t == 5:
                print(f"  ...")
        
        # Check: at what step do they first become equal?
        state_z = list(zeros)
        state_o = list(ones)
        
        boundary = bits[:2*h]
        
        converge_step = None
        for t in range(2*h):
            state_z = list(rule30_next_tuple(tuple(state_z), boundary[t])[:h])
            state_o = list(rule30_next_tuple(tuple(state_o), boundary[t])[:h])
            if tuple(state_z) == tuple(state_o):
                converge_step = t + 1
                break
        
        if converge_step:
            print(f"  Convergence at step {converge_step} (h={h})")
        else:
            diff = sum(1 for a, b in zip(state_z, state_o) if a != b)
            print(f"  No convergence after {2*h} steps (remaining diff={diff})")
        
        # Also test from 100 random pairs
        import random
        random.seed(42)
        converge_steps = []
        for _ in range(100):
            s1 = tuple(random.randint(0, 1) for _ in range(h))
            s2 = tuple(random.randint(0, 1) for _ in range(h))
            if s1 == s2:
                continue
            
            state1 = list(s1)
            state2 = list(s2)
            conv = None
            for t in range(min(5*h, len(bits))):
                state1 = list(rule30_next_tuple(tuple(state1), bits[t])[:h])
                state2 = list(rule30_next_tuple(tuple(state2), bits[t])[:h])
                if tuple(state1) == tuple(state2):
                    conv = t + 1
                    break
            converge_steps.append(conv)
        
        non_none = [c for c in converge_steps if c is not None]
        if non_none:
            print(f"  100 random pairs: {len(non_none)} converge, min={min(non_none)}, max={max(non_none)}, mean={sum(non_none)/len(non_none):.1f}")
        else:
            print(f"  100 random pairs: 0 converge within {min(5*h, len(bits))} steps")


if __name__ == "__main__":
    main()
