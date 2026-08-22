#!/usr/bin/env python3
"""
Verify the precise propagation front property:

CLAIM (Propagation Front Lemma):
Let s, s' be two truncated width-h trajectories that differ only in boundary bit b_k 
(at step k). Let Δ^(t)_j := s^(t)_j ⊕ s'^(t)_j.

Then:
(i)   Δ^(t)_j = 0 for all j > t - k - 1  (beyond the front)
(ii)  Δ^(t)_{t-k-1} depends only on bits {s^(t-1)_{j} : j ≤ t-k-1}  
(iii) Δ^(t)_{t-k} = 1 for all t ≥ k+1 (the front is always lit)

Wait, more precisely:
- At step k+1: Δ at position 0 = 1, all other 0
- At step k+j+1: Δ at position j = Δ_{j-1} ⊕ (change in OR term)
  Since positions j, j+1 had Δ=0 at previous step, the OR term is unchanged.
  So Δ_j = Δ_{j-1, previous} = ... = 1.

The key: the front at position j at time k+j+1 has Δ_j = 1 because:
  s'_{j} = s_{j-1} ⊕ (s_j ∨ s_{j+1})
  In the alternate trajectory: s''_{j} = s''_{j-1} ⊕ (s''_j ∨ s''_{j+1})
  
  Since Δ_j = 0 and Δ_{j+1} = 0 at the PREVIOUS step:
    s''_j = s_j and s''_{j+1} = s_{j+1}
  So: s''_{j}^{new} = s''_{j-1} ⊕ (s_j ∨ s_{j+1})
  And: s_{j}^{new} = s_{j-1} ⊕ (s_j ∨ s_{j+1})
  
  Therefore: Δ_j^{new} = s''_{j-1} ⊕ s_{j-1} = Δ_{j-1} = 1. ✓

This is a completely clean proof! The front position j at time k+j+1 
ALWAYS has Δ=1 because:
  1. Positions j, j+1 haven't been reached yet (Δ=0 at previous step)
  2. Left-permutativity means Δ at position j = Δ at position j-1 (XOR transfer)
  3. And by induction, Δ at position 0 was 1 at time k+1

Let me verify this proof is really correct by checking ALL possible cases, not just random.
"""
from __future__ import annotations
import os, sys, itertools
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import rule30_next_tuple


def main():
    # Exhaustive test for small h
    for h in range(1, 15):
        total_tests = 0
        failures = 0
        
        # For efficiency: test only position 0 flip at step 0
        # (the general case follows by relabeling)
        
        if 2**h * 2**h <= 2**20:  # affordable
            for s_mask in range(2**h):
                s0 = tuple((s_mask >> i) & 1 for i in range(h))
                for b_mask in range(2**h):
                    boundary = [(b_mask >> i) & 1 for i in range(h)]
                    boundary_flip = list(boundary)
                    boundary_flip[0] = 1 - boundary_flip[0]
                    
                    state_a = s0
                    state_b = s0
                    
                    ok = True
                    for t in range(h):
                        state_a = rule30_next_tuple(state_a, boundary[t])[:h]
                        state_b = rule30_next_tuple(state_b, boundary_flip[t])[:h]
                        
                        # Check that position t has Δ=1
                        if state_a[t] == state_b[t]:
                            ok = False
                            break
                        
                        # Check that positions > t have Δ=0
                        for j in range(t+1, h):
                            if state_a[j] != state_b[j]:
                                ok = False
                                break
                        if not ok:
                            break
                    
                    total_tests += 1
                    if not ok:
                        failures += 1
                        if failures <= 3:
                            print(f"  h={h}: FAILURE for s0={''.join(str(x) for x in s0)}, "
                                  f"boundary={boundary[:5]}...")
            
            print(f"h={h}: {total_tests} exhaustive tests, {failures} failures → "
                  f"{'PROVED (exhaustive)' if failures == 0 else 'DISPROVED'}")
        else:
            # Sample randomly
            import random
            random.seed(42)
            for _ in range(100000):
                s0 = tuple(random.randint(0, 1) for _ in range(h))
                boundary = [random.randint(0, 1) for _ in range(h)]
                boundary_flip = list(boundary)
                boundary_flip[0] = 1 - boundary_flip[0]
                
                state_a = s0
                state_b = s0
                
                ok = True
                for t in range(h):
                    state_a = rule30_next_tuple(state_a, boundary[t])[:h]
                    state_b = rule30_next_tuple(state_b, boundary_flip[t])[:h]
                    
                    if state_a[t] == state_b[t]:
                        ok = False
                        break
                    for j in range(t+1, h):
                        if state_a[j] != state_b[j]:
                            ok = False
                            break
                    if not ok:
                        break
                
                total_tests += 1
                if not ok:
                    failures += 1
                    if failures <= 3:
                        print(f"  h={h}: FAILURE for s0={''.join(str(x) for x in s0[:8])}...")
            
            print(f"h={h}: {total_tests} random tests, {failures} failures → "
                  f"{'ALL PASS' if failures == 0 else 'DISPROVED'}")


if __name__ == "__main__":
    main()
