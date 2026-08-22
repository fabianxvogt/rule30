#!/usr/bin/env python3
"""
Study synchronization and the "uncertainty set" in the class-level dynamics.

Given uncertainty about which class we're in, how does the uncertainty evolve?

Define: after seeing center-column bits c(0), ..., c(t-1), the set of possible 
raw states is the image of f_{c(t-1)} ∘ ... ∘ f_{c(0)} applied to the starting state.
Since we know the starting state (all-zeros in the truncated system), the trajectory is 
deterministic. But from the CLASS perspective, we might lose track.

Key question: is the class-level dynamics "essentially deterministic"?
For each class, what fraction of the time is there ambiguity about the next class?
"""
from __future__ import annotations
import os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables


def main():
    bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "results", "center-column-1000000.txt")
    with open(bits_file) as f:
        bits = [int(c) for c in f.read().strip() if c in '01']
    
    for h in [10, 12, 15, 18]:
        print(f"\n=== h={h} ===")
        q = build_quotient(h)
        total_classes = max(q.values()) + 1
        next_state, class_table = make_transition_tables(q, h)
        
        # Build class-indexed: for each class and each bit, what are the possible next classes?
        class_to_states = defaultdict(list)
        for state_int in range(1 << h):
            u = tuple((state_int >> i) & 1 for i in range(h))
            cid = q[u]
            class_to_states[cid].append(state_int)
        
        # For each (class, bit), count number of distinct next classes
        multi_count = 0
        total_pairs = 0
        for cid in range(total_classes):
            for b in [0, 1]:
                next_classes = set()
                for si in class_to_states[cid]:
                    nc = class_table[next_state[b][si]]
                    next_classes.add(nc)
                total_pairs += 1
                if len(next_classes) > 1:
                    multi_count += 1
        
        print(f"  {multi_count}/{total_pairs} (class,bit) pairs have nondeterministic class transition")
        print(f"  ({100*multi_count/total_pairs:.1f}%)")
        
        # Now trace the ACTUAL trajectory and see where nondeterminism kicks in
        state = 0
        class_deterministic_steps = 0
        class_nondeterministic_steps = 0
        
        steps = min(len(bits), 100000)
        
        for t in range(steps):
            cid = class_table[state]
            b = bits[t]
            
            # Check: all states in same class produce same next class?
            actual_next = class_table[next_state[b][state]]
            
            possible_nexts = set()
            for si in class_to_states[cid]:
                possible_nexts.add(class_table[next_state[b][si]])
            
            if len(possible_nexts) > 1:
                class_nondeterministic_steps += 1
            else:
                class_deterministic_steps += 1
            
            state = next_state[b][state]
        
        print(f"  Trajectory (first {steps} steps): {class_deterministic_steps} deterministic, "
              f"{class_nondeterministic_steps} nondeterministic "
              f"({100*class_nondeterministic_steps/steps:.1f}%)")
        
        # What's the class-level "diameter" of the nondeterminism?
        # When nondeterminism occurs, how many options are there?
        if h <= 15:
            branch_counts = []
            state = 0
            for t in range(steps):
                cid = class_table[state]
                b = bits[t]
                possible_nexts = set()
                for si in class_to_states[cid]:
                    possible_nexts.add(class_table[next_state[b][si]])
                if len(possible_nexts) > 1:
                    branch_counts.append(len(possible_nexts))
                state = next_state[b][state]
            
            if branch_counts:
                print(f"  When nondeterministic: always exactly {set(branch_counts)} options")


if __name__ == "__main__":
    main()
