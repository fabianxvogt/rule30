#!/usr/bin/env python3
"""
Test: Is full subword complexity at length h SUFFICIENT for full state coverage?

We know:
- Center column: full complexity → full coverage ✓
- Random bits: full complexity → full coverage ✓  
- Periodic: limited complexity → limited coverage ✓

Can we find a sequence with full subword complexity that FAILS to give full coverage?

Approach: construct a de Bruijn sequence (which has full complexity) and test coverage.
A de Bruijn sequence of order h contains every h-bit pattern exactly once as a 
contiguous substring, in a cyclic string of length 2^h.

If we drive the system with a de Bruijn sequence (repeated), does it achieve full coverage?
By Universal Bijectivity, from any starting state, h consecutive bits map to a unique 
state. But the de Bruijn sequence only has 2^h starting positions...

Actually, with 2^h distinct h-grams starting from the sync point, we'd get 2^h distinct 
FINAL states (by Universal Bijectivity). But we also visit intermediate states along the way.

Let me test this carefully.
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


def de_bruijn_sequence(n):
    """Generate a de Bruijn sequence of order n over {0,1}."""
    # Standard algorithm
    k = 2
    a = [0] * (k * n)
    sequence = []
    
    def db(t, p):
        if t > n:
            if n % p == 0:
                for j in range(1, p + 1):
                    sequence.append(a[j])
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, k):
                a[t] = j
                db(t + 1, t)
    
    db(1, 1)
    return ''.join(map(str, sequence))


def simulate(bits, h, f):
    """Simulate from all-zeros, return set of visited states."""
    state = 0
    visited = {state}
    for ch in bits:
        state = f[int(ch)][state]
        visited.add(state)
    return visited


def main():
    print("=== De Bruijn Sequence Coverage Test ===\n")
    
    for h in [5, 6, 7, 8, 9, 10, 12]:
        N = 1 << h
        f = build_maps(h)
        
        # Generate de Bruijn sequence of order h
        db = de_bruijn_sequence(h)
        
        # Repeat it enough times
        n_repeats = max(10, 100000 // len(db))
        bits = db * n_repeats
        
        visited = simulate(bits, h, f)
        
        # Also try from the sync state (apply many 1s first, then de Bruijn)
        sync_bits = '1' * (4*h) + bits
        visited_sync = simulate(sync_bits, h, f)
        
        print(f"h={h:2d}: de Bruijn length={len(db)}, N={N}")
        print(f"  From all-zeros: visited {len(visited)}/{N} ({len(visited)/N*100:.1f}%)")
        print(f"  From sync+dB:   visited {len(visited_sync)}/{N} ({len(visited_sync)/N*100:.1f}%)")
        
        # Also test: single cycle of de Bruijn (2^h bits)
        visited_one = simulate(db, h, f)
        print(f"  Single cycle:   visited {len(visited_one)}/{N} ({len(visited_one)/N*100:.1f}%)")
        print()
    
    # Now the KEY test: construct a sequence with full subword complexity 
    # but designed to AVOID certain states.
    # Can we engineer such a sequence?
    print("=== Adversarial Test: Can we avoid a state with full complexity? ===\n")
    
    for h in [5, 8]:
        N = 1 << h
        f = build_maps(h)
        
        # Try: pick a target state to avoid. Generate long sequences with full 
        # subword complexity and check if any avoid the target.
        
        # Use random permutation of de Bruijn blocks
        import random
        random.seed(42)
        
        db = de_bruijn_sequence(h)
        
        # Try many random seeds/orderings
        best_unvisited = 0
        for trial in range(100):
            # Shuffle: create a random permutation of all h-grams and concatenate
            # This gives full complexity but different ordering
            grams = [format(i, f'0{h}b') for i in range(N)]
            random.shuffle(grams)
            
            # Overlap-free concatenation (just concatenate with h-1 overlap removed 
            # where possible - actually just concatenate naively)
            bits = ''.join(grams)
            # This has length h * 2^h and contains all h-grams at least once
            
            # Repeat
            bits = bits * 5
            visited = simulate(bits, h, f)
            unvisited = N - len(visited)
            if unvisited > best_unvisited:
                best_unvisited = unvisited
            
        print(f"h={h}: 100 random-order-grams trials, best unvisited = {best_unvisited}")
        
        # What about: concatenate all h-grams in a specific order designed to 
        # avoid a target state?
        # Pick target 1 and try to construct a driving sequence that avoids it
        target = 1
        
        # Greedy: at each step, pick the bit that does NOT lead to the target
        state = 0
        bits_avoid = []
        avoid_success = True
        for _ in range(10 * N):
            s0 = f[0][state]
            s1 = f[1][state]
            
            if s0 != target and s1 != target:
                # Both safe, pick 0
                state = s0
                bits_avoid.append('0')
            elif s0 != target:
                state = s0
                bits_avoid.append('0')
            elif s1 != target:
                state = s1
                bits_avoid.append('1')
            else:
                # Both lead to target! Can't avoid.
                avoid_success = False
                bits_avoid.append('0')
                state = s0
        
        bits_str = ''.join(bits_avoid)
        visited = simulate(bits_str, h, f)
        sw = len(set(bits_str[i:i+h] for i in range(len(bits_str) - h + 1)))
        
        print(f"h={h}: avoidance of state {target}: visited {len(visited)}/{N}, "
              f"subword complexity at length {h}: {sw}/{N}")
        print(f"  Avoidance always possible: {avoid_success}")
        print()


if __name__ == "__main__":
    main()
