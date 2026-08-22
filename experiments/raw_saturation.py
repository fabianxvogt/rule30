#!/usr/bin/env python3
"""
Track: when does the center-column-driven trajectory first visit ALL 2^h raw states?
This is a much stronger property than class coverage!
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables


def main():
    bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "results", "center-column-1000000.txt")
    with open(bits_file) as f:
        bits = [int(c) for c in f.read().strip() if c in '01']
    
    for h in [8, 10, 12, 13, 14, 15]:
        print(f"\nh={h}")
        q = build_quotient(h)
        total_classes = max(q.values()) + 1
        next_state, class_table = make_transition_tables(q, h)
        
        N = 1 << h
        state = 0
        raw_visited = set()
        class_visited = set()
        
        class_sat_step = None
        raw_sat_step = None
        
        for t in range(min(len(bits), 1000000)):
            raw_visited.add(state)
            class_visited.add(class_table[state])
            
            if class_sat_step is None and len(class_visited) == total_classes:
                class_sat_step = t
            if raw_sat_step is None and len(raw_visited) == N:
                raw_sat_step = t
                break
            
            state = next_state[bits[t]][state]
        
        print(f"  |S_{h}| = {total_classes}, 2^{h} = {N}")
        print(f"  Class saturation at step: {class_sat_step}")
        print(f"  Raw saturation at step:   {raw_sat_step}")
        if raw_sat_step:
            print(f"  Raw sat / 2^h = {raw_sat_step / N:.2f}")
            print(f"  Raw sat / Class sat = {raw_sat_step / class_sat_step:.2f}")
        elif len(raw_visited) < N:
            print(f"  Raw states visited: {len(raw_visited)}/{N} ({100*len(raw_visited)/N:.1f}%)")


if __name__ == "__main__":
    main()
