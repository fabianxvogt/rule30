#!/usr/bin/env python3
"""
KEY COMPUTATION: Under periodic driving with period p, the composition 
F = f_{b_{p-1}} ∘ ... ∘ f_{b_0} maps {0,1}^h → {0,1}^h.

The trajectory under periodic driving is: s, F(s), F^2(s), ...
Eventually this enters a cycle. The number of distinct states visited is 
|transient| + |cycle| ≤ 2^h.

But the IMAGE of F^k shrinks with k (since individual maps have ~60% image).
The eventual image |Fix(F^∞)| (= IMAGE of F^N for large N) is the attractor 
of the periodic system.

If |attractor| < |S_h| (number of classes), then the trajectory cannot visit 
all classes — and coverage fails!

So: if the center column has period p, we need:
   |attractor of periodic composition| ≥ |S_h|

But we showed that compositions are STRONGLY contracting:
- Single step: ~60% image
- k steps: image shrinks as ~60%^k 

For a p-periodic system, the attractor size should be much smaller than 2^h 
(unless p is very large).

If we can show: |attractor| ≤ f(p, h) where f(p, h) < |S_h| for large h,
then periodic center column → contradiction.

Let me compute |attractor of F| for various p and h.
"""
from __future__ import annotations
import os, sys, itertools
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import rule30_next_tuple, build_quotient


def build_maps(h):
    N = 1 << h
    f = [[0]*N, [0]*N]
    for b in range(2):
        for s_int in range(N):
            state = tuple((s_int >> i) & 1 for i in range(h))
            ns = rule30_next_tuple(state, b)[:h]
            f[b][s_int] = sum(bit << i for i, bit in enumerate(ns))
    return f


def compose(f, word, N):
    """Compute the map F = f_{w[-1]} ∘ ... ∘ f_{w[0]}."""
    result = list(range(N))
    for b in word:
        result = [f[b][s] for s in result]
    return result


def image_of(F, N):
    """Size of image of map F."""
    return len(set(F))


def attractor_of(F, N):
    """Compute the eventual image (attractor) of iterating F.
    This is the fixed set of F^k for large k."""
    current = set(range(N))
    while True:
        nxt = set(F[s] for s in current)
        if nxt == current:
            return current
        current = nxt


def state_to_tuple(s_int, h):
    return tuple((s_int >> i) & 1 for i in range(h))

def count_classes_visited(f, word, h, q=None):
    """Trace trajectory under periodic word, count distinct classes visited."""
    N = 1 << h
    
    if q is None:
        q = build_quotient(h)
    
    state = 0
    classes_visited = set()
    classes_visited.add(q[state_to_tuple(state, h)])
    
    # Run enough for transient + several periods
    max_steps = min(10 * N, 100000)
    for step in range(max_steps):
        b = int(word[step % len(word)])
        state = f[b][state]
        classes_visited.add(q[state_to_tuple(state, h)])
    
    return len(classes_visited)


def main():
    print("=" * 70)
    print("PERIODIC DRIVING: ATTRACTOR SIZE vs CLASS COUNT")
    print("=" * 70)
    
    for h in [5, 8, 10, 12]:
        N = 1 << h
        f = build_maps(h)
        q = build_quotient(h)
        class_count = len(set(q.values()))
        
        print(f"\n=== h={h}, N={N}, |S_h|={class_count} ===")
        
        # For each period p, compute statistics over all 2^p words
        for p in [1, 2, 3, 4, 5, 8, 10, 15, 20]:
            if p > 15 and h > 8:
                continue  # too many words
            
            n_words = min(1 << p, 10000)
            
            attractor_sizes = []
            classes_covered = []
            
            if n_words == (1 << p):
                # Exhaustive
                words = [format(w, f'0{p}b') for w in range(n_words)]
            else:
                # Sample
                import random
                random.seed(42)
                words = [''.join(str(random.randint(0,1)) for _ in range(p)) for _ in range(n_words)]
            
            for word in words:
                F = compose(f, [int(c) for c in word], N)
                attr = attractor_of(F, N)
                attractor_sizes.append(len(attr))
                
                # Classes visited by trajectory
                if h <= 10 or n_words <= 1000:
                    cv = count_classes_visited(f, word, h, q)
                    classes_covered.append(cv)
                else:
                    classes_covered.append(0)
            
            avg_attr = sum(attractor_sizes) / len(attractor_sizes)
            max_attr = max(attractor_sizes)
            min_attr = min(attractor_sizes)
            avg_cv = sum(classes_covered) / len(classes_covered)
            max_cv = max(classes_covered)
            full_cv = sum(1 for cv in classes_covered if cv == class_count)
            
            print(f"  p={p:3d}: attractor avg={avg_attr:.1f}, min={min_attr}, max={max_attr} | "
                  f"classes avg={avg_cv:.1f}, max={max_cv}/{class_count}, "
                  f"full={full_cv}/{n_words}")
    
    # KEY: For the center column period p, the attractor must accommodate |S_h| classes.
    # If attractor_max(p) < |S_h| for all p-periodic words, then period p is impossible.
    print("\n" + "=" * 70)
    print("MAXIMUM ATTRACTOR SIZE AS FUNCTION OF p")
    print("=" * 70)
    
    for h in [5, 8, 10]:
        N = 1 << h
        f = build_maps(h)
        q_ = build_quotient(h)
        class_count = len(set(q_.values()))
        
        print(f"\nh={h}, N={N}, |S_h|={class_count}")
        print(f"{'p':>4} {'max |attr|':>12} {'max classes':>12} {'full coverage?':>15}")
        
        for p in range(1, min(25, h*3)):
            n_words = min(1 << p, 5000)
            
            if n_words == (1 << p):
                words = [format(w, f'0{p}b') for w in range(n_words)]
            else:
                import random
                random.seed(42 + p)
                words = [''.join(str(random.randint(0,1)) for _ in range(p)) for _ in range(n_words)]
            
            max_attr = 0
            max_cv = 0
            
            for word in words:
                F = compose(f, [int(c) for c in word], N)
                attr = attractor_of(F, N)
                max_attr = max(max_attr, len(attr))
                
                cv = count_classes_visited(f, word, h, q_)
                max_cv = max(max_cv, cv)
            
            q2 = build_quotient(h)
            class_count2 = len(set(q2.values()))
            
            enough = "YES" if max_cv >= class_count2 else "NO"
            print(f"{p:4d} {max_attr:12d} {max_cv:12d} {enough:>15}")


if __name__ == "__main__":
    main()
