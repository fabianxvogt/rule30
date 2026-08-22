#!/usr/bin/env python3
"""
Compute fiber sizes (number of raw states per class) and correlate with
reachability under periodic driving.

If the hardest-to-reach classes have small fibers, this explains why 
periodic driving fails: the trajectory, constrained by image contraction,
is unlikely to hit states in small fibers.
"""
from __future__ import annotations
import os, sys, time, random
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables

random.seed(42)


def main():
    print("FIBER SIZES AND REACHABILITY")
    print("=" * 60)
    
    for h in [8, 10, 12, 14, 16]:
        q = build_quotient(h)
        total_classes = max(q.values()) + 1
        trans, cls_of = make_transition_tables(q, h)
        N = 1 << h
        
        # Compute fiber sizes
        fiber_size = Counter()
        for s in range(N):
            fiber_size[cls_of[s]] += 1
        
        sizes = sorted(fiber_size.values())
        print(f"\nh={h}, N={N}, |S_h|={total_classes}")
        print(f"  Fiber sizes: min={min(sizes)} max={max(sizes)} mean={sum(sizes)/len(sizes):.1f} median={sizes[len(sizes)//2]}")
        print(f"  Size distribution:", dict(Counter(sizes).most_common(10)))
        
        # Where are the smallest fibers?
        small_classes = [c for c, sz in fiber_size.items() if sz == min(sizes)]
        print(f"  Classes with min fiber ({min(sizes)} states): {small_classes[:10]}")
        
        if h <= 14:
            # For each class, at what step is it first visited under random driving?
            # Compare: small-fiber classes should be hit later
            n_trials = 10
            steps_per_trial = N * 20
            first_hit = {}
            
            for trial in range(n_trials):
                bits = [random.randint(0, 1) for _ in range(steps_per_trial)]
                state = 0
                visited = set()
                visited.add(cls_of[state])
                for t in range(steps_per_trial):
                    state = trans[bits[t]][state]
                    c = cls_of[state]
                    if c not in visited:
                        visited.add(c)
                        if c not in first_hit or t < first_hit[c]:
                            first_hit[c] = t
            
            # Sort classes by first hit time
            if first_hit:
                sorted_by_hit = sorted(first_hit.items(), key=lambda x: -x[1])
                print(f"  Hardest-to-reach classes (random driving):")
                for cid, step in sorted_by_hit[:10]:
                    print(f"    class {cid}: first hit at step {step}, fiber size={fiber_size[cid]}")
        
        # Check correlation: for period-50, which classes are MISSED?
        if h <= 14:
            p = 50
            n_trials_p = 10000
            class_visited_count = Counter()
            
            for trial in range(n_trials_p):
                word = [random.randint(0, 1) for _ in range(p)]
                state = 0
                visited = set()
                visited.add(cls_of[state])
                for rep in range(200):
                    for b in word:
                        state = trans[b][state]
                        visited.add(cls_of[state])
                for c in visited:
                    class_visited_count[c] += 1
            
            rarely_visited = [(c, cnt) for c, cnt in class_visited_count.items() if cnt < n_trials_p * 0.5]
            rarely_visited.sort(key=lambda x: x[1])
            
            never_visited = [c for c in range(total_classes) if c not in class_visited_count]
            
            if never_visited:
                print(f"  Period-{p}: {len(never_visited)} classes NEVER visited in {n_trials_p} trials")
                for c in never_visited[:5]:
                    print(f"    class {c}: fiber size={fiber_size[c]}")
            
            if rarely_visited:
                print(f"  Period-{p}: {len(rarely_visited)} classes visited <50% of trials")
                for c, cnt in rarely_visited[:10]:
                    print(f"    class {c}: visited {cnt}/{n_trials_p} ({100*cnt/n_trials_p:.1f}%), fiber={fiber_size[c]}")
    
    # KEY: How does max fiber size grow vs |S_h|?
    print("\n" + "=" * 60)
    print("FIBER SIZE STATISTICS vs h")
    print("=" * 60)
    print(f"{'h':>4} {'N':>8} {'|S_h|':>6} {'min_f':>6} {'max_f':>6} {'mean_f':>8} {'min_f/N':>10}")
    for h in range(3, 19):
        q = build_quotient(h)
        total = max(q.values()) + 1
        N = 1 << h
        trans, cls_of = make_transition_tables(q, h)
        
        fiber_size = Counter()
        for s in range(N):
            fiber_size[cls_of[s]] += 1
        
        sizes = list(fiber_size.values())
        print(f"{h:4d} {N:8d} {total:6d} {min(sizes):6d} {max(sizes):6d} {sum(sizes)/len(sizes):8.1f} {min(sizes)/N:10.6f}")


if __name__ == "__main__":
    main()
