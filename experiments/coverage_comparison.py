#!/usr/bin/env python3
"""
Compare coverage: TRUE right-half dynamics vs TRUNCATED (zero-padded) dynamics.
"""

from __future__ import annotations

import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables


def main():
    bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "results", "center-column-1000000.txt")
    with open(bits_file) as f:
        bits = [int(c) for c in f.read().strip() if c in '01']
    
    N = len(bits) - 1  # max steps available
    
    print(f"{'h':>3} {'|S_h|':>7} {'trunc_sat':>12} {'true_sat':>12} {'trunc_ratio':>12} {'true_ratio':>12}")
    print("-" * 65)
    
    for h in range(2, 19):
        q = build_quotient(h)
        total_classes = max(q.values()) + 1
        
        # --- TRUNCATED system ---
        next_state, class_table = make_transition_tables(q, h)
        state_trunc = 0
        visited_trunc = {class_table[state_trunc]}
        trunc_sat = None
        
        for t in range(1, min(N, 500001)):
            state_trunc = next_state[bits[t-1]][state_trunc]
            visited_trunc.add(class_table[state_trunc])
            if len(visited_trunc) == total_classes:
                trunc_sat = t
                break
        
        # --- TRUE system ---
        max_steps = min(N, 500000)
        W = max_steps + h + 10
        state_true = np.zeros(W + 2, dtype=np.uint8)
        visited_true = set()
        prefix = tuple(state_true[1:h+1])
        cid = q.get(prefix)
        if cid is not None:
            visited_true.add(cid)
        
        true_sat = None
        for t in range(max_steps):
            state_true[0] = bits[t]
            state_true[W + 1] = 0
            new_state = np.zeros(W + 2, dtype=np.uint8)
            new_state[1:W+1] = state_true[0:W] ^ (state_true[1:W+1] | state_true[2:W+2])
            state_true = new_state
            
            prefix = tuple(state_true[1:h+1])
            cid = q.get(prefix)
            if cid is not None and cid not in visited_true:
                visited_true.add(cid)
                if len(visited_true) == total_classes:
                    true_sat = t + 1
                    break
        
        trunc_str = str(trunc_sat) if trunc_sat else f">{min(N, 500000)}"
        true_str = str(true_sat) if true_sat else f">{max_steps}({len(visited_true)}/{total_classes})"
        
        trunc_ratio = f"{trunc_sat/total_classes:.1f}x" if trunc_sat else "N/A"
        true_ratio = f"{true_sat/total_classes:.1f}x" if true_sat else "N/A"
        
        print(f"{h:3d} {total_classes:7d} {trunc_str:>12} {true_str:>12} {trunc_ratio:>12} {true_ratio:>12}")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
