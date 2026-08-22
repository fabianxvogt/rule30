#!/usr/bin/env python3
"""
Synchronizing words for the truncated Rule 30 IFS.

A synchronizing word w = (b_1, ..., b_k) for the IFS {f_0, f_1} is a sequence 
such that f_{b_k} ∘ ... ∘ f_{b_1} maps ALL states to a SINGLE state.

If such words exist and appear as subwords of the center column, then the system 
resets to a known state, and from there Universal Bijectivity implies all 2^h 
states are visited in the next h steps.

We search for synchronizing words by iterating the "power set" construction:
start with S_0 = {0,1}^h, apply f_{b_k} to get S_k = f_{b_k}(S_{k-1}).
If |S_k| = 1 for some k, we found a synchronizing word.

This is equivalent to finding a "reset word" in automata theory.
By the Černý conjecture, if a sync word exists, its length ≤ (n-1)^2 where n = 2^h.
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import rule30_next_tuple


def build_maps(h):
    """Build f_0 and f_1 as lookup tables."""
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
    """Apply map f_b to a set of states."""
    return frozenset(f_b[s] for s in state_set)


def find_sync_word_bfs(h, max_depth=None):
    """BFS search for the shortest synchronizing word.
    
    State in BFS: a frozenset of reachable states (the "image set").
    Start: full set {0, ..., 2^h - 1}.
    Goal: any singleton set.
    """
    N = 1 << h
    if max_depth is None:
        max_depth = N  # generous bound
    
    f = build_maps(h)
    
    initial = frozenset(range(N))
    
    # BFS
    from collections import deque
    queue = deque()
    queue.append((initial, []))
    visited = {initial}
    
    step = 0
    while queue:
        current_set, word = queue.popleft()
        
        if len(word) > max_depth:
            break
        
        for b in range(2):
            next_set = apply_map(f[b], current_set)
            next_word = word + [b]
            
            if len(next_set) == 1:
                return next_word, next(iter(next_set))
            
            if next_set not in visited:
                visited.add(next_set)
                queue.append((next_set, next_word))
        
        step += 1
        if step % 10000 == 0:
            min_size = min(len(s) for s, _ in queue) if queue else 0
            print(f"  BFS step {step}, visited {len(visited)}, queue {len(queue)}, min image size {min_size}")
    
    return None, None


def greedy_sync_search(h, max_steps=1000):
    """Greedy: at each step pick b that minimizes |image|."""
    N = 1 << h
    f = build_maps(h)
    
    current = frozenset(range(N))
    word = []
    
    for step in range(max_steps):
        if len(current) == 1:
            return word, next(iter(current))
        
        # Try both bits, pick the one giving smaller image
        img0 = apply_map(f[0], current)
        img1 = apply_map(f[1], current)
        
        if len(img0) <= len(img1):
            current = img0
            word.append(0)
        else:
            current = img1
            word.append(1)
        
        if step < 30 or step % 50 == 0:
            print(f"  Step {step+1}: picked b={word[-1]}, |image| = {len(current)}")
    
    return None, None


def contraction_analysis(h, num_words=1000, word_length=None):
    """Analyze how quickly random/specific words shrink the state space."""
    import random
    random.seed(42)
    
    N = 1 << h
    if word_length is None:
        word_length = 4 * h
    
    f = build_maps(h)
    
    min_final = N
    best_word = None
    
    shrink_profile = [0] * (word_length + 1)
    shrink_count = [0] * (word_length + 1)
    
    for trial in range(num_words):
        word = [random.randint(0, 1) for _ in range(word_length)]
        current = frozenset(range(N))
        
        for t, b in enumerate(word):
            current = apply_map(f[b], current)
            shrink_profile[t+1] += len(current)
            shrink_count[t+1] += 1
        
        if len(current) < min_final:
            min_final = len(current)
            best_word = word[:]
    
    return shrink_profile, shrink_count, min_final, best_word


def main():
    # BFS for small h
    for h in [2, 3, 4, 5]:
        print(f"\n=== h={h}, N=2^{h}={1<<h} ===")
        word, target = find_sync_word_bfs(h, max_depth=100)
        if word is not None:
            print(f"  SYNC WORD FOUND! Length {len(word)}: {''.join(map(str, word))}")
            print(f"  All states map to: {target}")
        else:
            print(f"  No sync word found (depth ≤ 100)")
    
    # Greedy for medium h
    for h in [5, 8, 10]:
        print(f"\n=== h={h}, N={1<<h}: GREEDY SEARCH ===")
        word, target = greedy_sync_search(h, max_steps=500)
        if word is not None:
            print(f"  Greedy sync word found! Length {len(word)}")
            print(f"  All states map to: {target}")
        else:
            print(f"  Greedy did not find sync word in 500 steps")
    
    # Contraction analysis
    for h in [5, 8, 10, 12]:
        print(f"\n=== h={h}, N={1<<h}: RANDOM WORD CONTRACTION ===")
        word_len = 8 * h
        sp, sc, min_final, _ = contraction_analysis(h, num_words=500, word_length=word_len)
        
        print(f"  Average image size after k steps:")
        checkpoints = [1, 2, h//2, h, 2*h, 3*h, 4*h, 6*h, 8*h]
        for k in checkpoints:
            if k <= word_len and sc[k] > 0:
                avg = sp[k] / sc[k]
                print(f"    k={k:4d}: avg |image| = {avg:.1f} ({avg/(1<<h)*100:.2f}%)")
        print(f"  Min final image size ({word_len} steps): {min_final}")


if __name__ == "__main__":
    main()
