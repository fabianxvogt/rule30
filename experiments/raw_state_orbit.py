#!/usr/bin/env python3
"""
Study the raw-state orbit under center column driving:
- How many distinct raw states are visited?
- Do raw states repeat?
- If the trajectory enters a cycle at the raw-state level, what's the cycle length?
- How does it relate to the class orbit?
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
    
    for h in [8, 10, 12, 15, 18, 20]:
        print(f"\n=== h={h} ===")
        q = build_quotient(h)
        total_classes = max(q.values()) + 1
        next_state, class_table = make_transition_tables(q, h)
        
        # Trace trajectory from all-zeros
        state = 0
        raw_visited = set()
        class_visited = set()
        first_raw_repeat = None
        
        steps = min(len(bits), 1000000)
        
        # Track for shorter prefix too
        milestones = [1000, 10000, 100000, 500000, 1000000]
        
        for t in range(steps):
            raw_visited.add(state)
            class_visited.add(class_table[state])
            
            state = next_state[bits[t]][state]
            
            if state in raw_visited and first_raw_repeat is None:
                first_raw_repeat = t + 1
            
            if (t + 1) in milestones:
                print(f"  After {t+1:>8d} steps: {len(raw_visited):>8d}/{2**h} raw states "
                      f"({100*len(raw_visited)/2**h:.1f}%), "
                      f"{len(class_visited)}/{total_classes} classes")
        
        if first_raw_repeat:
            print(f"  First raw-state repeat at step: {first_raw_repeat}")
        else:
            print(f"  No raw-state repeat in {steps} steps")
        
        print(f"  Final: {len(raw_visited)} distinct raw states visited, "
              f"{len(class_visited)}/{total_classes} classes")


if __name__ == "__main__":
    main()
