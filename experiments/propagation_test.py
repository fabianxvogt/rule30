#!/usr/bin/env python3
"""
Verify the key propagation lemma for the universal bijectivity proof:

Claim: For any state s ∈ {0,1}^h and boundary bit b:
  Let s' = rule30_next(s, b) and s'' = rule30_next(s, 1-b).
  Then:
    s'[0] ≠ s''[0]  (position 0 always flips)
    s'[j] = s''[j]  for j ≥ 1  (other positions don't change)

This follows directly from the update formula:
    s'[0] = b XOR (s[0] OR s[1])
    s'[j] = s[j-1] XOR (s[j] OR s[j+1])  for j ≥ 1

Since only position 0 depends on b, this is immediate.

Then the propagation: after position 0 changes at time k,
at time k+1, positions 0 and 1 differ (since s'[1] depends on s[0]).
At time k+2, positions 0, 1, 2 differ (possibly).
At time k+j, positions 0 through j can differ.

The diagonal property (position j always affected after j propagation steps)
comes from:
    s'[j] = s[j-1] XOR ...
The first XOR term ensures that a difference at position j-1 always
propagates to position j: if s[j-1] changes (toggled), then 
s[j-1] XOR (s[j] OR s[j+1]) changes too.

Wait — that's only true if the XOR is with a FIXED right side.
Let's check: if positions j-1, j, j+1 can ALL differ...

Actually, let me be more careful. Let Δ_j = s'[j] XOR s''[j].

After one step:
  Δ_0 = 1 (boundary bit differs)
  Δ_j = 0 for j ≥ 1

After two steps: Let the two paths be s -> s' and s -> s'' (differ only at pos 0).
  Next step applied to s' with same b_next, and to s'' with same b_next:
  
  For position 0: 
    new_0' = b_next XOR (s'[0] OR s'[1])
    new_0'' = b_next XOR (s''[0] OR s''[1])
    Since s'[0] ≠ s''[0] and s'[1] = s''[1]:
    Δ_0^(new) = (s'[0] OR s'[1]) XOR (s''[0] OR s''[1])
    
  For position 1:
    new_1' = s'[0] XOR (s'[1] OR s'[2])
    new_1'' = s''[0] XOR (s''[1] OR s''[2])
    Since s'[1] = s''[1] and s'[2] = s''[2]:
    Δ_1^(new) = s'[0] XOR s''[0] = 1. ← ALWAYS 1!
    
  For position 2:
    new_2' = s'[1] XOR (s'[2] OR s'[3])
    new_2'' = s''[1] XOR (s''[2] OR s''[3])
    = 0 since all inputs are the same.

So after the FIRST propagation step: Δ_0 = ?, Δ_1 = 1, Δ_j = 0 for j ≥ 2.

KEY: Position 1 is ALWAYS affected, because s'[1] = s[0] XOR ..., and the 
left-permutative structure means s[0] XOR (right stuff) always toggles when s[0] toggles.

More generally, at position j ≥ 1:
    new_j = s[j-1] XOR (s[j] OR s[j+1])

If we flip s[j-1], the output toggles: 
    new_j XOR new_j' = Δ_{j-1} = 1 (by assumption that j-1 position differs)

But if ALSO s[j] and/or s[j+1] differ, then the XOR of the right side might also change,
potentially canceling. 

HOWEVER: the structure is s[j-1] XOR f(s[j], s[j+1]). If only s[j-1] changes,
the output changes. If s[j] also changes, we get:
    (s[j-1] XOR 1) XOR f(s[j] XOR Δ_j, s[j+1] XOR Δ_{j+1})
  = s[j-1] XOR 1 XOR f(...)

The "1" from the j-1 position is always present. The f(...) change depends on Δ_j, Δ_{j+1}.

So Δ_j^(new) = 1 XOR (change in f(s[j], s[j+1])).

This CAN be 0! The left-permutativity at position j is:
    position j depends on j-1 in a XOR fashion,
    so differing j-1 ALWAYS adds a 1 to the difference.
    But if the (s_j OR s_{j+1}) part also differs by 1, they cancel.

So the diagonal being always 1 is NOT trivially guaranteed. It must be because
the "leading front" of the difference propagates in a specific pattern.

Let me verify: can Δ_j ever become 0 at the propagation front?
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import rule30_next_tuple
import random


def trace_propagation(h, s0, boundary_bits):
    """Trace how a boundary-bit difference at step 0 propagates through subsequent steps."""
    # Path A: boundary_bits as given
    # Path B: boundary_bits with b[0] flipped
    bits_a = list(boundary_bits)
    bits_b = list(boundary_bits)
    bits_b[0] = 1 - bits_b[0]
    
    state_a = s0
    state_b = s0
    
    diffs = []
    for t in range(len(boundary_bits)):
        state_a = rule30_next_tuple(state_a, bits_a[t])[:h]
        state_b = rule30_next_tuple(state_b, bits_b[t])[:h]
        
        delta = tuple(a ^ b for a, b in zip(state_a, state_b))
        diffs.append(delta)
    
    return diffs


def main():
    random.seed(42)
    
    for h in [8, 12, 16]:
        print(f"\n=== h={h} ===")
        
        # Test: flip b_0, trace Δ for h steps
        s0 = tuple(random.randint(0, 1) for _ in range(h))
        boundary = [random.randint(0, 1) for _ in range(h)]
        
        diffs = trace_propagation(h, s0, boundary)
        
        print(f"  Propagation of b_0 flip (Δ pattern):")
        for t, d in enumerate(diffs):
            d_str = ''.join(str(x) for x in d)
            front = max(j for j in range(h) if d[j] == 1) if any(d) else -1
            # Check if Δ[t] = 1 (the "front" position = t)
            print(f"    t={t+1}: Δ={d_str}  front_pos={front}  Δ[{t}]={d[t]}")
        
        # Specifically: does Δ[t][t] always = 1? 
        # (The "leading front" at position t after t propagation steps from a flip at pos 0)
        print(f"\n  Systematic check: flip b_0, check Δ[t][t] for 1000 random (s0, boundary):")
        all_ok = True
        for trial in range(1000):
            s0 = tuple(random.randint(0, 1) for _ in range(h))
            boundary = [random.randint(0, 1) for _ in range(h)]
            diffs = trace_propagation(h, s0, boundary)
            for t in range(h):
                if diffs[t][t] != 1:
                    all_ok = False
                    print(f"    FAIL: trial={trial}, t={t}, s0={''.join(str(x) for x in s0)}")
                    break
            if not all_ok:
                break
        print(f"    All Δ[t][t]=1? {all_ok}")


if __name__ == "__main__":
    main()
