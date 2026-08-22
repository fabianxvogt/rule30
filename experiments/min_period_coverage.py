#!/usr/bin/env python3
"""
For each h, find the minimum period p of a periodic sequence that achieves
full coverage of S_h classes.

KEY QUESTION: Does min_p(h) → ∞ as h → ∞?
If yes, then for any fixed period p, there exists h such that NO p-periodic 
sequence achieves full class coverage.

Approach:
  - For small p: exhaustive search over all 2^p binary words
  - For larger p: aggressive random sampling  
  - For each (h, p) pair: count maximum classes visited over all tested words

Uses fast integer-indexed transition tables.
"""
from __future__ import annotations

import os
import sys
import time
import random

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables

random.seed(42)


def classes_visited_periodic(trans, cls_of, total_classes, word_ints, max_reps=500):
    """Count distinct classes visited by periodic repetition of word.
    
    Returns (n_classes, is_full).
    Runs word for max_reps full repetitions or until all classes found.
    """
    state = 0
    visited = set()
    visited.add(cls_of[state])
    
    p = len(word_ints)
    for rep in range(max_reps):
        for b in word_ints:
            state = trans[b][state]
            visited.add(cls_of[state])
            if len(visited) == total_classes:
                return len(visited), True
    return len(visited), False


def check_period_exhaustive(trans, cls_of, total_classes, p, max_reps=500):
    """Exhaustively check ALL 2^p binary words. 
    Returns (found, max_classes, best_word)."""
    best = 0
    best_word = None
    for w_int in range(1 << p):
        word_ints = [(w_int >> i) & 1 for i in range(p)]
        nc, full = classes_visited_periodic(trans, cls_of, total_classes, word_ints, max_reps)
        if nc > best:
            best = nc
            best_word = ''.join(str(b) for b in word_ints)
        if full:
            return True, best, best_word
    return False, best, best_word


def check_period_random(trans, cls_of, total_classes, p, n_trials=10000, max_reps=500):
    """Random sampling of p-periodic words.
    Returns (found, max_classes, best_word)."""
    best = 0
    best_word = None
    for _ in range(n_trials):
        word_ints = [random.randint(0, 1) for _ in range(p)]
        nc, full = classes_visited_periodic(trans, cls_of, total_classes, word_ints, max_reps)
        if nc > best:
            best = nc
            best_word = ''.join(str(b) for b in word_ints)
        if full:
            return True, best, best_word
    return False, best, best_word


def main():
    print("MINIMUM PERIOD FOR FULL CLASS COVERAGE")
    print("=" * 60)
    print("For each h: find min p such that SOME p-periodic word covers all classes.")
    print()
    
    results = {}
    
    for h in [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]:
        t0 = time.time()
        q = build_quotient(h)
        total = max(q.values()) + 1
        trans, cls_of = make_transition_tables(q, h)
        
        print(f"h={h:2d}  |S_h|={total:5d}  N=2^{h}={1<<h}")
        
        found_min = None
        
        for p in range(1, 60):
            t1 = time.time()
            
            if p <= 16:
                found, mc, bw = check_period_exhaustive(trans, cls_of, total, p)
                method = "exhaustive"
            elif p <= 25:
                found, mc, bw = check_period_random(trans, cls_of, total, p, n_trials=50000)
                method = "random-50K"
            else:
                found, mc, bw = check_period_random(trans, cls_of, total, p, n_trials=10000)
                method = "random-10K"
            
            dt = time.time() - t1
            
            if found:
                print(f"  p={p:3d}: FULL ({total}/{total}) [{method}, {dt:.1f}s]")
                if found_min is None:
                    found_min = p
                    print(f"  >>> min_p({h}) ≤ {p}")
                break
            else:
                print(f"  p={p:3d}: max {mc:5d}/{total} ({100*mc/total:.1f}%) [{method}, {dt:.1f}s]")
            
            # Time budget: don't spend more than 60s per h
            if time.time() - t0 > 120:
                print(f"  (time limit reached)")
                break
        
        if found_min is None:
            print(f"  >>> min_p({h}) > tested range (NOT FOUND)")
        
        results[h] = found_min
        total_t = time.time() - t0
        print(f"  total time: {total_t:.1f}s\n")
    
    print("\n" + "=" * 60)
    print("SUMMARY: min_p(h) lower bounds")
    print("=" * 60)
    print(f"{'h':>4s}  {'|S_h|':>6s}  {'min_p':>6s}  {'ratio':>8s}")
    for h, mp in sorted(results.items()):
        q = build_quotient(h)
        total = max(q.values()) + 1
        if mp is not None:
            print(f"{h:4d}  {total:6d}  {mp:6d}  {mp/total:8.3f}")
        else:
            print(f"{h:4d}  {total:6d}  {'??':>6s}  {'??':>8s}")


if __name__ == "__main__":
    main()
