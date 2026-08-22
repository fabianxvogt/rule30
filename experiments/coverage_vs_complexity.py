#!/usr/bin/env python3
"""
KEY INSIGHT: For any h (even or odd), after enough 1s, the system is in one of 
at most 2 states. Those 2 states differ only in the last bit.

After k more steps with arbitrary inputs, each of those 2 starting states 
produces a trajectory. By Universal Bijectivity, the map from (b_1,...,b_h) to 
final state is a bijection FROM EACH starting state.

So the set of reachable states from the post-sync state(s) depends on:
- Even h: 1 starting state → all 2^h final states (by Universal Bijectivity)
- Odd h: 2 starting states → 2 * 2^h images... but many overlap!

What fraction of CLASSES are covered from the near-sync point?

Actually, a MUCH cleaner approach:

For the coverage proof, we don't need synchronization at all.
We just need: for every class c ∈ S_h, the trajectory visits c.

The key fact is:
- From ANY state s, running h arbitrary bits produces ALL possible final states 
  (by Universal Bijectivity).
- So from any point in the trajectory, the next h bits determine which state we 
  reach next.
- If the center column sequence is "rich enough" in substrings of length h, 
  then the trajectory visits all states.

But this is EXACTLY the Coverage Hypothesis in its original form!

Let me instead explore: what is the ACTUAL condition on the driving sequence?

For a FIXED starting state s, the map (b_1,...,b_h) → final_state is a BIJECTION.
So visiting ALL 2^h states ⟺ seeing ALL 2^h h-bit patterns from position aligned 
to the start.

But the trajectory doesn't restart cleanly every h steps. It's continuous.

Let me think more carefully about what "reset + Universal Bijectivity" gives us.

After a sync word (run of 1s of length ~4h for even h):
- System is in a KNOWN state s*.
- Next h center-column bits (b_1,...,b_h) map to state via bijection.
- After those h bits, system is in some state s_h.
- Then the NEXT h bits map to state via another bijection (from s_h).
- And so on.

So the trajectory from s* generates states:
  s_0 = s*, s_h = Φ_{s*}(b_1...b_h), s_{2h} = Φ_{s_h}(b_{h+1}...b_{2h}), ...

But we want to cover ALL classes (which are quotients of ALL states).
The states at positions 0, h, 2h, 3h, ... are only N^(1/h)-th of all states.
What about intermediate states like s_1, s_2, ..., s_{h-1}?

Actually, a MUCH CLEANER version:

The trajectory visits state s_t at every step t.
s_{t+1} = f_{b_t}(s_t).

After sync at step T: s_T = s* (known).
s_{T+1} = f_{b_T}(s*), s_{T+2} = f_{b_{T+1}}(s_{T+1}), etc.

The state at step T+k depends on (b_T, b_{T+1}, ..., b_{T+k-1}).
For k = h, by Universal Bijectivity, s_{T+h} ranges over ALL of {0,1}^h as 
(b_T,...,b_{T+h-1}) ranges over {0,1}^h.

But the center column only produces ONE specific sequence (b_T, b_{T+1}, ...).
So s_{T+h} is ONE specific state.

The question is: as we vary T (i.e., look at different sync points in the center 
column), do we see different h-tuples (b_T,...,b_{T+h-1})?

If the center column has full subword complexity at length h (all 2^h h-bit 
patterns appear), and there are enough sync points, then YES.

But we need to be more precise. Let me count how many long-1-runs exist and 
whether they provide enough diversity.

Actually, the BETTER approach: forget sync words entirely.

Theorem: If the center column has FULL subword complexity at length h 
(every h-bit string appears as a contiguous substring), then the trajectory 
visits all 2^h states.

Proof attempt:
- Suppose the center column contains the substring w = (b_0,...,b_{h-1}) 
  starting at position t.
- At position t, the system is in some state s_t.
- The state at position t+h is Φ_{s_t}(w).
- By Universal Bijectivity, Φ_{s_t} is a bijection, so different w's give 
  different states from the same s_t.

But different occurrences of different w's start from DIFFERENT states s_t!
So Φ_{s_t}(w) and Φ_{s_{t'}}(w') don't trivially cover everything because 
s_t ≠ s_{t'} in general.

Hmm, this doesn't directly work. We need a cleverer argument.

What if we combine with the fact that the center column contains EVERY h-bit 
pattern? Then for each fixed starting state s, we'd need the specific w that 
maps s to each target. But we can't control which starting state we're in.

OK let me try yet another angle. EMPIRICALLY verify: is full subword complexity 
at length h sufficient (or necessary) for coverage?
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import rule30_next_tuple


def build_maps(h):
    N = 1 << h
    f = [[0]*N, [0]*N]
    for b in range(2):
        for s_int in range(N):
            state = tuple((s_int >> i) & 1 for i in range(h))
            ns = rule30_next_tuple(state, b)[:h]
            f[b][s_int] = sum(bit << i for i, bit in enumerate(ns))
    return f


def subword_complexity(bits, length):
    """Count distinct substrings of given length."""
    seen = set()
    for i in range(len(bits) - length + 1):
        seen.add(bits[i:i+length])
    return len(seen)


def check_coverage_vs_complexity(h, bits, f):
    """Simulate trajectory and check both class coverage and subword complexity."""
    N = 1 << h
    
    # Simulate from all-zeros
    state = 0
    visited_states = set()
    visited_states.add(state)
    
    for i, b in enumerate(bits):
        b_int = int(b)
        state = f[b_int][state]
        visited_states.add(state)
    
    # Subword complexities
    complexities = {}
    for l in [h, h+1, h+2, 2*h]:
        if l <= len(bits):
            complexities[l] = subword_complexity(bits, l)
    
    return len(visited_states), complexities


def main():
    # Use center column bits
    with open("results/center-column-1000000.txt") as fp:
        bits = fp.read().strip()
    
    print("=== Coverage vs Subword Complexity of Center Column ===")
    print(f"Using {len(bits)} center column bits\n")
    
    for h in [5, 8, 10, 12, 14, 16, 18, 20]:
        N = 1 << h
        if h > 16:
            # Only build maps for smaller h
            continue
        
        f = build_maps(h)
        n_visited, comps = check_coverage_vs_complexity(h, bits, f)
        
        sw_h = comps.get(h, 0)
        full_h = min(2**h, len(bits) - h + 1)
        
        print(f"h={h:2d}: visited {n_visited}/{N} states ({n_visited/N*100:.1f}%)")
        print(f"       subword complexity at length {h}: {sw_h}/{full_h} "
              f"({'FULL' if sw_h >= 2**h else f'{sw_h/2**h*100:.1f}%'})")
        print()
    
    # Now: test with RANDOM bits
    import random
    random.seed(123)
    random_bits = ''.join(str(random.randint(0,1)) for _ in range(len(bits)))
    
    print("=== Same analysis with RANDOM bits ===")
    for h in [5, 8, 10, 12, 14, 16]:
        N = 1 << h
        f = build_maps(h)
        n_visited, comps = check_coverage_vs_complexity(h, random_bits, f)
        
        sw_h = comps.get(h, 0)
        
        print(f"h={h:2d}: visited {n_visited}/{N} states ({n_visited/N*100:.1f}%)")
        print(f"       subword complexity at length {h}: {sw_h}/{2**h} "
              f"({'FULL' if sw_h >= 2**h else f'{sw_h/2**h*100:.1f}%'})")
        print()
    
    # Test with a PERIODIC sequence
    print("=== Same analysis with PERIODIC bits (period 31) ===")
    base = '0110100110010110101001011001011'  # some 31-bit pattern
    periodic_bits = (base * (len(bits) // len(base) + 1))[:len(bits)]
    
    for h in [5, 8, 10, 12]:
        N = 1 << h
        f = build_maps(h)
        n_visited, comps = check_coverage_vs_complexity(h, periodic_bits, f)
        
        sw_h = comps.get(h, 0)
        
        print(f"h={h:2d}: visited {n_visited}/{N} states ({n_visited/N*100:.1f}%)")
        print(f"       subword complexity at length {h}: {sw_h}/{2**h} "
              f"(max for period 31: {min(31, 2**h)})")
        print()


if __name__ == "__main__":
    main()
