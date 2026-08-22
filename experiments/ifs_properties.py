#!/usr/bin/env python3
"""
IFS properties: images of f_0 and f_1, their intersection, and the 
"attractor" of the IFS.

The IFS attractor A is the unique compact set satisfying A = f_0(A) ∪ f_1(A).
For finite state space, this is the eventually-reachable set from any starting point
under all possible input sequences.

Also: does the IFS have an "open set condition" analog?
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import rule30_next_tuple


def compute_images(h):
    """Compute images of f_0 and f_1 on {0,1}^h."""
    N = 1 << h
    img = [set(), set()]
    
    for s_int in range(N):
        state = tuple((s_int >> i) & 1 for i in range(h))
        for b in [0, 1]:
            ns = rule30_next_tuple(state, b)[:h]
            ns_int = sum(bit << i for i, bit in enumerate(ns))
            img[b].add(ns_int)
    
    return img[0], img[1]


def compute_attractor(h, img0, img1, next_state):
    """Compute the IFS attractor: start from all states, iterate forward 
    until stable."""
    N = 1 << h
    current = set(range(N))
    
    for iteration in range(100):
        # Forward image: apply f_0 and f_1 to current set
        new = set()
        for s in current:
            new.add(next_state[0][s])
            new.add(next_state[1][s])
        
        if new == current:
            return current, iteration
        
        # Actually the attractor is: start from full set, intersect with images
        # A = f_0(A) ∪ f_1(A)
        # Start with A = {0,...,N-1}, then A' = f_0(A) ∪ f_1(A)
        # A' might be smaller if not all states are in the image
        if len(new) >= len(current):
            # Growing or stable - this means everything is reachable
            return current, iteration
        current = new
    
    return current, -1


def compute_backward_attractor(h, next_state):
    """Alternatively: the backward attractor is the set of states reachable 
    from all-zeros by arbitrary input sequences.
    
    Start with {0^h}, apply f_0 and f_1, take union, iterate until stable.
    """
    N = 1 << h
    reached = {0}  # start from all-zeros
    
    for iteration in range(N):
        new_reached = set(reached)
        for s in reached:
            new_reached.add(next_state[0][s])
            new_reached.add(next_state[1][s])
        
        if new_reached == reached:
            return reached, iteration
        reached = new_reached
    
    return reached, -1


def main():
    from fast_class_coverage2 import build_quotient, make_transition_tables
    
    for h in [5, 8, 10, 12, 15]:
        print(f"\n=== h={h} ===")
        N = 1 << h
        
        q = build_quotient(h)
        next_state, class_table = make_transition_tables(q, h)
        
        img0, img1 = compute_images(h)
        
        print(f"  |img(f_0)| = {len(img0)}/{N} = {len(img0)/N:.3f}")
        print(f"  |img(f_1)| = {len(img1)}/{N} = {len(img1)/N:.3f}")
        print(f"  |img(f_0) ∩ img(f_1)| = {len(img0 & img1)}")
        print(f"  |img(f_0) ∪ img(f_1)| = {len(img0 | img1)}/{N} = {len(img0 | img1)/N:.3f}")
        
        # States NOT in any image:
        unreachable = set(range(N)) - (img0 | img1)
        print(f"  States not in any image: {len(unreachable)}")
        
        # Forward attractor
        reached, iters = compute_backward_attractor(h, next_state)
        print(f"  Reachable from all-zeros: {len(reached)}/{N} (in {iters} iterations)")
        
        # Iterate images:
        # A_0 = {0,...,N-1}
        # A_1 = f_0(A_0) ∪ f_1(A_0) = img(f_0) ∪ img(f_1)
        # A_2 = f_0(A_1) ∪ f_1(A_1)
        # ...
        # The intersection ∩ A_n is the "forward attractor"
        A = set(range(N))
        for k in range(50):
            A_next = set()
            for s in A:
                A_next.add(next_state[0][s])
                A_next.add(next_state[1][s])
            if len(A_next) == len(A):
                print(f"  Forward attractor = {len(A)}/{N} (stable after {k} iterations)")
                if len(A) == N:
                    print(f"  → ALL states are in the forward attractor (IFS is surjective!)")
                break
            A = A_next
        else:
            print(f"  Forward attractor not stable after 50 iterations: {len(A)}/{N}")
        
        # Check: is every state reachable from EVERY state?
        # (IFS is topologically mixing)
        if h <= 10:
            all_reach_all = True
            min_reach = N
            for start in range(N):
                reached_s = {start}
                for _ in range(N):
                    new_r = set(reached_s)
                    for s in reached_s:
                        new_r.add(next_state[0][s])
                        new_r.add(next_state[1][s])
                    if new_r == reached_s:
                        break
                    reached_s = new_r
                if len(reached_s) < N:
                    all_reach_all = False
                    min_reach = min(min_reach, len(reached_s))
            
            if all_reach_all:
                print(f"  IFS is TOPOLOGICALLY MIXING (all states reach all states) ✓")
            else:
                print(f"  IFS NOT mixing (min reachable = {min_reach})")


if __name__ == "__main__":
    main()
