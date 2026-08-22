#!/usr/bin/env python3
"""
Compute how the image of the composite map F_w = f_{b_{p-1}} ∘ ... ∘ f_{b_0}
shrinks as a function of p.

Also compute the attractor size of F_w (the eventual image F_w^∞({0,1}^h)).

Key observation: f_b is NOT a bijection, so iterating F_w contracts the state space.
The attractor size limits how many distinct states (and classes) the periodic 
trajectory can visit.
"""
from __future__ import annotations
import os, sys, time, random
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables

random.seed(42)


def image_of_composition(trans, word_ints, N):
    """Compute |img(f_{b_{k-1}} ∘ ... ∘ f_{b_0})| for each prefix."""
    current = set(range(N))
    sizes = [N]
    for b in word_ints:
        current = {trans[b][s] for s in current}
        sizes.append(len(current))
    return sizes


def attractor_of_F(trans, word_ints, N, max_iter=100):
    """Compute the attractor of F_w = f_{b_{p-1}} ∘ ... ∘ f_{b_0}.
    
    The attractor is the fixed set: S such that F_w(S) = S.
    Computed by iterating F_w on the full set until stabilization.
    """
    current = set(range(N))
    for _ in range(max_iter):
        next_set = current.copy()
        for b in word_ints:
            next_set = {trans[b][s] for s in next_set}
        if len(next_set) == len(current):
            break
        current = next_set
    return current


def main():
    print("IMAGE CONTRACTION AND ATTRACTOR SIZES")
    print("=" * 60)
    
    for h in [5, 8, 10, 12, 14]:
        q = build_quotient(h)
        total_classes = max(q.values()) + 1
        trans, cls_of = make_transition_tables(q, h)
        N = 1 << h
        
        print(f"\nh={h}, N={N}, |S_h|={total_classes}")
        
        # Single-step image sizes
        for b in range(2):
            img = set(trans[b])
            print(f"  |img(f_{b})| = {len(img)}/{N} = {len(img)/N:.4f}")
        
        # Image shrinkage for random words
        for p in [5, 10, 20, 50]:
            if h >= 14 and p > 20:
                break
            
            n_trials = min(1000, 1 << min(p, 14))
            
            max_attractor = 0
            min_attractor = N
            total_attractor = 0
            max_classes_in_attractor = 0
            
            for trial in range(n_trials):
                word = [random.randint(0, 1) for _ in range(p)]
                att = attractor_of_F(trans, word, N)
                att_size = len(att)
                max_attractor = max(max_attractor, att_size)
                min_attractor = min(min_attractor, att_size)
                total_attractor += att_size
                
                # Classes in attractor
                att_classes = set(cls_of[s] for s in att)
                max_classes_in_attractor = max(max_classes_in_attractor, len(att_classes))
            
            avg_att = total_attractor / n_trials
            print(f"  p={p:3d}: attractor min={min_attractor} avg={avg_att:.0f} max={max_attractor} "
                  f"max_classes_in_att={max_classes_in_attractor}/{total_classes}")
        
        # Image contraction for a specific word
        word = [random.randint(0, 1) for _ in range(50)]
        sizes = image_of_composition(trans, word, N)
        print(f"  Image contraction (random 50-bit word):")
        for i in [1, 2, 5, 10, 20, 50]:
            if i < len(sizes):
                print(f"    after {i:3d} steps: {sizes[i]:6d}/{N} ({sizes[i]/N:.4f})")
    
    # Detailed analysis for h=10,12: how does max attractor class count compare
    # to total class count?
    print("\n" + "=" * 60)
    print("MAX CLASSES IN ATTRACTOR vs |S_h|")
    print("This bounds the classes reachable in the periodic part of trajectory")
    print("=" * 60)
    
    for h in [8, 10, 12]:
        q = build_quotient(h)
        total_classes = max(q.values()) + 1
        trans, cls_of = make_transition_tables(q, h)
        N = 1 << h
        
        print(f"\nh={h}, N={N}, |S_h|={total_classes}")
        
        for p in [5, 10, 15, 20, 30, 50, 100]:
            t0 = time.time()
            n_trials = min(10000, 1 << min(p, 14))
            
            max_att_size = 0
            max_att_classes = 0
            max_traj_classes = 0  # classes in full trajectory (transient + cycle)
            
            for trial in range(n_trials):
                word = [random.randint(0, 1) for _ in range(p)]
                
                # Attractor
                att = attractor_of_F(trans, word, N)
                att_classes = set(cls_of[s] for s in att)
                max_att_size = max(max_att_size, len(att))
                max_att_classes = max(max_att_classes, len(att_classes))
                
                # Full trajectory from state 0
                state = 0
                visited_classes = set()
                visited_classes.add(cls_of[state])
                for rep in range(200):
                    for b in word:
                        state = trans[b][state]
                        visited_classes.add(cls_of[state])
                max_traj_classes = max(max_traj_classes, len(visited_classes))
            
            dt = time.time() - t0
            print(f"  p={p:4d}: max_att_size={max_att_size:5d} max_att_classes={max_att_classes:4d} "
                  f"max_traj_classes={max_traj_classes:4d}/{total_classes} [{dt:.1f}s]")
            
            if dt > 60:
                break


if __name__ == "__main__":
    main()
