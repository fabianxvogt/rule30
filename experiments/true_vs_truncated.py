#!/usr/bin/env python3
"""
The right-half of Rule 30 spacetime evolves as an infinite system. The 
"width-h truncated system" with zero padding is only an APPROXIMATION.

For the first h steps, the approximation is exact (the "light cone" hasn't
reached position h yet). After that, the truncated system diverges from the
true system.

The predictive-state analysis is really about the OBSERVATION of the true
infinite system through a window of width h. At time t, we observe 
(a_1(t), ..., a_h(t)) from the true Rule 30 spacetime.

Question: does the observed h-tuple at time t always match some trajectory
of the width-h truncated system? Not necessarily — but the PREDICTIVE CLASS
of the observed h-tuple is what matters.

Key theorem candidate: the PREDICTIVE CLASS of the observed h-tuple at time t
is well-defined and depends only on the full right-half state at time t.

Let me verify this by simulating the TRUE right-half (with large enough width)
and comparing the observed h-tuples with the truncated system.
"""

from __future__ import annotations

import os
import sys
from itertools import product

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, rule30_next_tuple


def simulate_true_right_half(center_bits, width):
    """Simulate the right half of Rule 30 spacetime.
    
    The right half has positions 1, 2, ..., width. Position 0 (center) is
    the boundary, given by center_bits.
    
    The full right half evolves as:
    - a(x, t+1) = a(x-1, t) XOR (a(x, t) OR a(x+1, t))
    - For x=1: left neighbor is a(0, t) = center_bits[t]
    - For x=width: right neighbor is 0 (far enough right that it's still 0)
    
    Returns list of tuples: state at each time step.
    """
    # Initial state: all zeros
    state = [0] * (width + 2)  # state[x] for x = 0, 1, ..., width+1
    
    states = [tuple(state[1:width+1])]  # initial state at positions 1..width
    
    for t in range(len(center_bits)):
        # Set boundary: position 0 = center bit
        state[0] = center_bits[t]
        # Position width+1 stays 0 (padding)
        state[width + 1] = 0
        
        new_state = [0] * (width + 2)
        for x in range(1, width + 1):
            left = state[x - 1]
            center = state[x]
            right = state[x + 1]
            new_state[x] = left ^ (center | right)
        
        state = new_state
        states.append(tuple(state[1:width+1]))
    
    return states


def main():
    bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "results", "center-column-1000000.txt")
    with open(bits_file) as f:
        bits = [int(c) for c in f.read().strip() if c in '01']
    
    T = 200  # Time steps to simulate
    W = 100  # Width of "true" right half (large enough)
    
    print(f"Simulating true right-half with width={W} for {T} steps")
    true_states = simulate_true_right_half(bits[:T], W)
    
    # Now compare with truncated system for various h
    for h in [5, 10, 15, 20]:
        print(f"\n--- h={h} ---")
        
        # Truncated system: width-h with zero padding
        trunc_state = tuple([0] * h)
        
        mismatches = 0
        for t in range(T):
            # True h-prefix
            true_prefix = true_states[t][:h]
            
            if true_prefix != trunc_state:
                mismatches += 1
                if mismatches <= 3:
                    print(f"  t={t}: true prefix = {true_prefix}, truncated = {trunc_state}")
            
            # Advance truncated system
            trunc_state = rule30_next_tuple(trunc_state, bits[t])[:h]
        
        print(f"  Mismatches: {mismatches}/{T}")
        
        # After time h, the truncated and true systems diverge because the 
        # light cone from position h reaches the observed region.
        
        # But: both true_prefix and trunc_state are h-tuples that can be
        # assigned to predictive classes. Do they get the same class?
        q_h = build_quotient(h)
        
        trunc_state2 = tuple([0] * h)
        class_mismatches = 0
        for t in range(T):
            true_prefix = true_states[t][:h]
            
            true_class = q_h.get(true_prefix)
            trunc_class = q_h.get(trunc_state2)
            
            if true_class is None or trunc_class is None:
                print(f"  t={t}: class lookup failed! true={true_prefix}, trunc={trunc_state2}")
                break
            
            if true_class != trunc_class:
                class_mismatches += 1
                if class_mismatches <= 5:
                    print(f"  t={t}: true class = {true_class}, trunc class = {trunc_class}")
            
            trunc_state2 = rule30_next_tuple(trunc_state2, bits[t])[:h]
        
        print(f"  Class mismatches: {class_mismatches}/{T}")


if __name__ == "__main__":
    main()
