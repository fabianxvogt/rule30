#!/usr/bin/env python3
"""
Investigate the relationship between predictive-state classes and 
substrings/patterns in the center column.

Key question: does the center column trajectory visiting class c at step t
correspond to some specific pattern in the center column bits c(t), c(t+1), ...?

If each class corresponds to a distinct "future behavior" pattern, then
covering all classes means the trajectory sees all distinct futures. For a 
periodic sequence with period p, there are exactly p distinct futures (cyclic
shifts). So if |S_h| > p, we'd have a contradiction — but only if each 
future maps to a different class.

Let's check: does the window pattern of center column bits (c(t), ..., c(t+k-1))
determine the trajectory class at time t? If so, coverage = all length-k
substrings appear = periodicity implies k-word count ≤ p.
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
    
    for h in range(2, 16):
        q = build_quotient(h)
        total_classes = max(q.values()) + 1
        next_state, class_table = make_transition_tables(q, h)
        
        # Run trajectory and record (class, future_window) pairs
        state = 0
        
        # For each time t, record the class and the next-h bits of center column
        class_to_windows = defaultdict(set)
        window_to_classes = defaultdict(set)
        
        max_t = min(N - h, 100000)
        
        for t in range(max_t):
            cid = class_table[state]
            
            # Future window of length h
            if t + h <= N:
                window = tuple(bits[t:t+h])
                class_to_windows[cid].add(window)
                window_to_classes[window].add(cid)
            
            # Advance
            if t < N - 1:
                state = next_state[bits[t]][state]
        
        # Check: is the map class -> window injective? (i.e., does each class
        # always see the same next-h window?)
        # Obviously not — the class is about the RIGHT HALF state, not the future bits.
        
        # Check: is the window -> class map well-defined? 
        # (i.e., does the same future window always correspond to the same class?)
        ambiguous_windows = sum(1 for ws in window_to_classes.values() if len(ws) > 1)
        unique_windows = sum(1 for ws in window_to_classes.values() if len(ws) == 1)
        
        # How many distinct windows?
        distinct_windows = len(window_to_classes)
        
        # How many distinct classes visited with a unique window?
        multi_window_classes = sum(1 for ws in class_to_windows.values() if len(ws) > 1)
        
        print(f"\nh={h}: |S_h|={total_classes}, distinct_windows={distinct_windows}, "
              f"ambiguous_windows={ambiguous_windows}")
        print(f"  Classes with multiple windows: {multi_window_classes}/{total_classes}")
        
        # New approach: for window of length h, does it determine the class?
        # The right answer: no, because the class depends on the full right-half state,
        # which is built up from ALL past bits, not just the recent h bits.
        
        # But maybe: the map from TRAJECTORY class at time t to future output
        # center-column window c(t)...c(t+h-1) is related to the predictive response.
        
        # Actually, the predictive class of the right-half state s at time t determines
        # the output response R_h(s, beta) for each boundary word beta of length h.
        # The actual output is R_h(s, c(t)...c(t+h-1)) — the response to the ACTUAL
        # future center column bits.
        
        # So two states in the SAME class produce the SAME output under the same future
        # bits. The output at each step is the center column bit PRODUCED BY the 
        # right half... wait, that's the output of site x=1 under the Rule 30 update.
        
        # Actually, let me reconsider what the "response" is. The right-half driven
        # system RECEIVES the center column c(t) as boundary input and PRODUCES the
        # state of the right half. The "output" of the driven system is... what?
        
        # The response R_h(s, beta) as defined in the predictive-state construction
        # is the h-tuple of outputs generated over h steps. What is the "output" per step?
        # It's the leftmost bit of the evolved state, which is:
        #   s'_0 = c(t) XOR (s_0 OR s_1)
        # i.e., it depends on c(t) and the current state.
        
        # So the per-step output is NOT the center column itself. Let me check what it is.


if __name__ == "__main__":
    main()
