#!/usr/bin/env python3
"""
Deeper investigation of synchronizing properties:
1. Do sync words exist for larger h?
2. What is the "sync kernel" — the set of states that ALL words shrink to?
3. Investigate the constant-0 input attractor more carefully.
4. Check if the 0-input attractor + 1-input can break out.
"""
from __future__ import annotations
import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import rule30_next_tuple

random.seed(42)

def build_maps(h):
    N = 1 << h
    f = [dict(), dict()]
    for b in range(2):
        for s_int in range(N):
            state = tuple((s_int >> i) & 1 for i in range(h))
            ns = rule30_next_tuple(state, b)[:h]
            ns_int = sum(bit << i for i, bit in enumerate(ns))
            f[b][s_int] = ns_int
    return f


def apply_map(f_b, state_set):
    return frozenset(f_b[s] for s in state_set)


def find_attractor(f_b, h):
    """Find the attractor of repeated application of f_b starting from all states."""
    N = 1 << h
    current = frozenset(range(N))
    for _ in range(10*N):
        nxt = apply_map(f_b, current)
        if nxt == current:
            return current
        current = nxt
    return current


def sync_random_search(h, f, num_trials=10000, max_word_len=200):
    """Search many random words for synchronization."""
    N = 1 << h
    best_size = N
    best_word = None
    
    for trial in range(num_trials):
        word_len = random.randint(h, max_word_len)
        word = [random.randint(0, 1) for _ in range(word_len)]
        
        current = frozenset(range(N))
        for b in word:
            current = apply_map(f[b], current)
            if len(current) < best_size:
                best_size = len(current)
                best_word = word[:word.index(b) + 1] if b in word else word[:]
                if best_size == 1:
                    return best_size, best_word, trial
        
    return best_size, best_word, num_trials


def targeted_search(h, f, max_steps=500):
    """Try to break out of attractor by alternating strategies."""
    N = 1 << h
    
    # Strategy: use constant 0 to shrink, then try 1s to escape fixed points
    current = frozenset(range(N))
    word = []
    
    # Phase 1: shrink with 0
    for _ in range(5*h):
        new0 = apply_map(f[0], current)
        new1 = apply_map(f[1], current)
        if len(new0) <= len(new1):
            current = new0
            word.append(0)
        else:
            current = new1
            word.append(1)
    
    min_size = len(current)
    
    # Phase 2: try to break the cycle with various patterns
    patterns = [
        [1] * h,
        [0, 1] * (h // 2),
        [1, 0] * (h // 2),
        [1, 1, 0] * (h // 3 + 1),
    ]
    
    best_size = min_size
    for pat in patterns:
        test = current
        for b in pat:
            test = apply_map(f[b], test)
            if len(test) < best_size:
                best_size = len(test)
    
    # Phase 3: exhaustive short perturbation after shrinking
    # Try all 2^k perturbations for small k
    for k in range(1, min(16, h+1)):
        for bits in range(1 << k):
            test = current
            for j in range(k):
                b = (bits >> j) & 1
                test = apply_map(f[b], test)
            if len(test) < best_size:
                best_size = len(test)
                if best_size == 1:
                    return best_size
    
    return best_size


def main():
    for h in [3, 5, 8, 10, 12, 14]:
        print(f"\n=== h={h}, N={1<<h} ===")
        f = build_maps(h)
        
        # Attractor of f_0
        attr0 = find_attractor(f[0], h)
        attr1 = find_attractor(f[1], h)
        print(f"  |Attractor(f_0)| = {len(attr0)}")
        print(f"  |Attractor(f_1)| = {len(attr1)}")
        
        # Random search for sync words
        trials = min(50000, 100000 // (1 << max(0, h - 8)))
        word_len = max(200, 10 * h)
        best, bw, nt = sync_random_search(h, f, num_trials=trials, max_word_len=word_len)
        print(f"  Random search ({trials} trials, max len {word_len}): min image = {best}")
        if best == 1:
            print(f"    SYNC WORD FOUND at trial {nt}!")
        
        # Targeted search
        ts = targeted_search(h, f)
        print(f"  Targeted search: min image = {ts}")
        
        # What's the min image achievable from the 0-attractor?
        # Apply all 2-step combinations from attractor
        d0 = apply_map(f[0], attr0)
        d1 = apply_map(f[1], attr0)
        d00 = apply_map(f[0], d0)
        d01 = apply_map(f[1], d0)
        d10 = apply_map(f[0], d1)
        d11 = apply_map(f[1], d1)
        print(f"  From attr(f_0): |f_0|={len(d0)}, |f_1|={len(d1)}")
        print(f"  From attr(f_0): |f_00|={len(d00)}, |f_01|={len(d01)}, |f_10|={len(d10)}, |f_11|={len(d11)}")


if __name__ == "__main__":
    main()
