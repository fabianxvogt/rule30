#!/usr/bin/env python3
"""
Extended forgetting test: how long until states converge?
Also: do they ever reach the same EQUIVALENCE CLASS even if not the same state?
"""
from __future__ import annotations
import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, rule30_next_tuple


def main():
    bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "results", "center-column-1000000.txt")
    with open(bits_file) as f:
        bits = [int(c) for c in f.read().strip() if c in '01']
    
    for h in [5, 8, 10, 12, 15]:
        print(f"\n=== h={h} ===")
        q = build_quotient(h)
        cls_of = {}
        for state, cls in q.items():
            cls_of[state] = cls
        
        # Start from all-zeros vs all-ones
        z = tuple([0]*h)
        o = tuple([1]*h)
        
        max_steps = min(len(bits), 10000)
        
        state_z = z
        state_o = o
        
        first_same_class = None
        first_same_state = None
        same_class_count = 0
        
        for t in range(max_steps):
            state_z = rule30_next_tuple(state_z, bits[t])[:h]
            state_o = rule30_next_tuple(state_o, bits[t])[:h]
            
            cz = cls_of.get(state_z)
            co = cls_of.get(state_o)
            
            if cz == co:
                same_class_count += 1
                if first_same_class is None:
                    first_same_class = t + 1
            
            if state_z == state_o:
                if first_same_state is None:
                    first_same_state = t + 1
                    break  # once same, always same
        
        print(f"  First same CLASS: step {first_same_class}")
        print(f"  First same STATE: step {first_same_state}")
        print(f"  Same-class fraction in first {min(max_steps, t+1)} steps: {same_class_count}/{min(max_steps, t+1)} = {same_class_count/min(max_steps, t+1):.4f}")
        
        if first_same_state is None:
            # Check diff at various points
            state_z = z
            state_o = o
            for t in range(max_steps):
                state_z = rule30_next_tuple(state_z, bits[t])[:h]
                state_o = rule30_next_tuple(state_o, bits[t])[:h]
                if (t+1) in [h, 2*h, 5*h, 10*h, 50*h, 100*h, 1000*h]:
                    diff = sum(1 for a, b in zip(state_z, state_o) if a != b)
                    print(f"  t={t+1}: diff={diff}/{h}")
        
        # Now the key question: for Theorem 11 specifically
        # Theorem 11 says: starting from all-zeros, the map (b_0,...,b_{h-1}) -> state at time h 
        # is a bijection. This is about a SPECIFIC starting state.
        # Does it extend to: for ANY starting state, this map is a bijection?
        print(f"\n  Bijectivity from all-ones starting state:")
        seen_states = set()
        state = tuple([1]*h)
        for mask in range(2**h):
            boundary = tuple((mask >> i) & 1 for i in range(h))
            s = tuple([1]*h)
            for b in boundary:
                s = rule30_next_tuple(s, b)[:h]
            seen_states.add(s)
        print(f"  {len(seen_states)} distinct states from 2^{h}={2**h} boundary sequences: {'BIJECTIVE' if len(seen_states) == 2**h else 'NOT bijective'}")
        
        if h <= 10:
            # Check from a random starting state
            random.seed(99)
            rand_start = tuple(random.randint(0, 1) for _ in range(h))
            seen2 = set()
            for mask in range(2**h):
                boundary = tuple((mask >> i) & 1 for i in range(h))
                s = tuple(rand_start)
                for b in boundary:
                    s = rule30_next_tuple(s, b)[:h]
                seen2.add(s)
            print(f"  Random start {rand_start[:8]}...: {len(seen2)} distinct → {'BIJECTIVE' if len(seen2) == 2**h else 'NOT bijective'}")


if __name__ == "__main__":
    main()
