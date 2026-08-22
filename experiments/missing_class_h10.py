#!/usr/bin/env python3
"""
For h=10 with p=16 (exhaustive): max 70/71 classes.
Which class is the hardest to reach? And at what period does it first become reachable?

Also: extend the exhaustive search for h=10 to find the EXACT min_p.
p=16 exhaustive gives max 70/71.
For p=17..20, use massive random sampling to narrow down.
"""
from __future__ import annotations
import os, sys, time, random
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables

random.seed(42)


def find_missing_classes(trans, cls_of, total, word_ints, max_reps=1000):
    """Find which classes are NOT visited."""
    state = 0
    visited = set()
    visited.add(cls_of[state])
    p = len(word_ints)
    for rep in range(max_reps):
        for b in word_ints:
            state = trans[b][state]
            visited.add(cls_of[state])
            if len(visited) == total:
                return set()
    return set(range(total)) - visited


def main():
    h = 10
    q = build_quotient(h)
    total = max(q.values()) + 1
    trans, cls_of = make_transition_tables(q, h)
    N = 1 << h
    
    print(f"h={h}, |S_h|={total}, N={N}")
    
    # PART 1: At p=16 (exhaustive best = 70/71), which class is missing?
    print("\n=== PART 1: Missing class analysis at p=16 ===")
    missing_count = {}  # class_id -> count of times it's the missing one
    n_near_full = 0
    
    for w_int in range(1 << 16):
        word = [(w_int >> i) & 1 for i in range(16)]
        missing = find_missing_classes(trans, cls_of, total, word, max_reps=200)
        if len(missing) == 1:
            n_near_full += 1
            for m in missing:
                missing_count[m] = missing_count.get(m, 0) + 1
    
    print(f"Words achieving 70/71: {n_near_full} out of {1<<16}")
    print("Missing class distribution:")
    for cid, cnt in sorted(missing_count.items(), key=lambda x: -x[1]):
        print(f"  class {cid}: missing in {cnt} words")
    
    # Map class IDs to representative states
    class_to_states = {}
    for s_int in range(N):
        c = cls_of[s_int]
        if c not in class_to_states:
            class_to_states[c] = []
        class_to_states[c].append(s_int)
    
    # Show the stubborn classes
    stubborn_classes = set(missing_count.keys())
    print(f"\nStubborn classes: {stubborn_classes}")
    for c in stubborn_classes:
        states = class_to_states[c]
        print(f"  class {c}: {len(states)} states, examples: {[bin(s) for s in states[:5]]}")
    
    # PART 2: Which classes are NEVER visited at p=13 (exhaustive best: 68/71)?
    print("\n=== PART 2: Class reachability by period ===")
    for p in [8, 10, 12, 13, 14, 15, 16]:
        t0 = time.time()
        ever_visited = set()
        
        n_words = 1 << p if p <= 16 else 50000
        for w_int in range(n_words):
            if p <= 16:
                word = [(w_int >> i) & 1 for i in range(p)]
            else:
                word = [random.randint(0, 1) for _ in range(p)]
            
            state = 0
            visited = set()
            visited.add(cls_of[state])
            for rep in range(200):
                for b in word:
                    state = trans[b][state]
                    visited.add(cls_of[state])
            ever_visited |= visited
        
        dt = time.time() - t0
        never = set(range(total)) - ever_visited
        print(f"  p={p:3d}: {len(ever_visited)}/{total} classes reachable by SOME word, "
              f"never: {sorted(never) if len(never) <= 10 else f'{len(never)} classes'} [{dt:.1f}s]")
    
    # PART 3: Try p=17..25 with larger random samples
    print("\n=== PART 3: Extended random search p=17..30 ===")
    for p in range(17, 31):
        t0 = time.time()
        max_classes = 0
        n_full = 0
        for trial in range(200000):
            word = [random.randint(0, 1) for _ in range(p)]
            state = 0
            visited = set()
            visited.add(cls_of[state])
            for rep in range(200):
                for b in word:
                    state = trans[b][state]
                    visited.add(cls_of[state])
                    if len(visited) == total:
                        break
                if len(visited) == total:
                    break
            if len(visited) > max_classes:
                max_classes = len(visited)
            if len(visited) == total:
                n_full += 1
        
        dt = time.time() - t0
        print(f"  p={p:3d}: max {max_classes}/{total} ({100*max_classes/total:.1f}%) "
              f"full={n_full}/200K [{dt:.1f}s]")
        
        if n_full > 0 or time.time() - t0 > 300:
            if n_full > 0:
                print(f"  >>> First full coverage found at p={p}!")
            break


if __name__ == "__main__":
    main()
