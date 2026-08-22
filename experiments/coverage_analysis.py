#!/usr/bin/env python3
"""
The de Bruijn sequence has full subword complexity at length h but FAILS coverage.
The center column and random bits achieve BOTH full complexity and full coverage.

What distinguishes them?

Key insight: the de Bruijn sequence of order h has length 2^h. Even repeated 10 times,
that's 10·2^h bits. But to cover all states via coupon-collector, we need ~h·2^h bits.

So maybe the issue is simply SEQUENCE LENGTH / state space size.

Let me check: how many bits does the de Bruijn sequence need to achieve full coverage?
And: is it about total length, or about the NUMBER OF DISTINCT CONTEXTS?

The real question: does any sufficiently long sequence with full subword complexity 
achieve full coverage? Or is there a sequence with full complexity at ALL lengths 
that still fails coverage? (A normal sequence, perhaps.)
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


def saturation_time(bits, h, f):
    """Simulate from all-zeros, return step when all states visited, or None."""
    N = 1 << h
    state = 0
    visited = {state}
    for i, ch in enumerate(bits):
        state = f[int(ch)][state]
        visited.add(state)
        if len(visited) == N:
            return i + 1
    return None


def main():
    print("=== De Bruijn sequence: how many repeats needed for full coverage? ===\n")
    
    for h in [5, 8, 10]:
        N = 1 << h
        f = build_maps(h)
        db = de_bruijn_sequence(h)
        
        # Try increasing repeats
        for n_rep in [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]:
            bits = db * n_rep
            if len(bits) > 10 * N * h:
                break
            sat = saturation_time(bits, h, f)
            total = len(bits)
            if sat:
                print(f"h={h:2d}: {n_rep:5d} repeats ({total:8d} bits): saturated at step {sat} "
                      f"(ratio = {sat/N:.1f}x, bits/N = {total/N:.0f})")
                break
            else:
                # Count visited
                state = 0
                visited = {state}
                for ch in bits:
                    state = f[int(ch)][state]
                    visited.add(state)
                print(f"h={h:2d}: {n_rep:5d} repeats ({total:8d} bits): visited {len(visited)}/{N} "
                      f"({len(visited)/N*100:.1f}%, bits/N = {total/N:.0f})")
        print()
    
    print("=== How long does RANDOM / CENTER-COLUMN take? ===\n")
    
    import random
    random.seed(42)
    
    with open("results/center-column-1000000.txt") as fp:
        center_bits = fp.read().strip()
    
    for h in [5, 8, 10, 12, 14]:
        N = 1 << h
        f = build_maps(h)
        
        # Center column
        sat_center = saturation_time(center_bits, h, f)
        
        # Random
        rnd_bits = ''.join(str(random.randint(0,1)) for _ in range(len(center_bits)))
        sat_random = saturation_time(rnd_bits, h, f)
        
        # De Bruijn (enough repeats)
        db = de_bruijn_sequence(h)
        db_long = db * max(1, 5 * h)  # generous
        sat_db = saturation_time(db_long, h, f)
        
        print(f"h={h:2d} (N={N:6d}): center_sat={sat_center or '>1M':>8}, "
              f"random_sat={sat_random or '>1M':>8}, deBruijn_sat={sat_db or '>'+str(len(db_long)):>8}")
        if sat_center and sat_random and sat_db:
            print(f"  Ratios: center/N={sat_center/N:.1f}, random/N={sat_random/N:.1f}, "
                  f"deBruijn/N={sat_db/N:.1f}")
    
    print("\n=== KEY QUESTION: Is there ANY sequence that avoids coverage indefinitely ===")
    print("=== while having full subword complexity at all lengths?              ===\n")
    
    # This is hard to test directly. But we can test:
    # Does the fixed-point-free property help? 
    # I.e., does the avoidance sequence have bounded subword complexity?
    
    for h in [5, 8]:
        N = 1 << h
        f = build_maps(h)
        
        # Construct an avoidance sequence (avoid state 1)
        target = 1
        state = 0
        bits_avoid = []
        for _ in range(100 * N):
            s0 = f[0][state]
            s1 = f[1][state]
            if s0 != target:
                state = s0
                bits_avoid.append('0')
            elif s1 != target:
                state = s1
                bits_avoid.append('1')
            else:
                state = s0
                bits_avoid.append('0')
        
        bits_str = ''.join(bits_avoid)
        
        print(f"h={h}: Avoidance sequence (target=1), length={len(bits_str)}")
        for l in range(1, min(h+3, 20)):
            sw = len(set(bits_str[i:i+l] for i in range(len(bits_str) - l + 1)))
            print(f"  subword complexity at length {l}: {sw}/{min(2**l, len(bits_str))}")
        print()
    
    # Check: is each avoiding state a "Garden of Eden" for some map?
    print("=== Which states can be avoided? ===\n")
    for h in [5, 8]:
        N = 1 << h
        f = build_maps(h)
        
        avoidable = []
        for target in range(N):
            # Can we always avoid target? Check if there exists a state with 
            # BOTH successors being target
            forced = False
            for s in range(N):
                if f[0][s] == target and f[1][s] == target:
                    forced = True
                    break
            if not forced:
                avoidable.append(target)
        
        print(f"h={h}: {len(avoidable)}/{N} states are avoidable (one step)")
        
        # For truly unavoidable: both f_0 and f_1 lead to that state from some state
        # Wait, "avoidable" = no state has both successors being target
        # "unavoidable" = there's a state where BOTH successors are target
        # If target is unavoidable, then when in that predecessor state, you MUST visit target.
        unavoidable = [t for t in range(N) if t not in avoidable]
        if unavoidable:
            print(f"  Unavoidable states: {unavoidable[:20]}{'...' if len(unavoidable) > 20 else ''}")
        else:
            print(f"  ALL states are avoidable!")


if __name__ == "__main__":
    main()
