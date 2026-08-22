#!/usr/bin/env python3
"""
Test: is the h-step evolution map bijective from EVERY starting state?

For each starting state s in {0,1}^h, define F_s: {0,1}^h -> {0,1}^h by
  F_s(b_0,...,b_{h-1}) = state after h steps of truncated width-h Rule 30
                         starting from s, with boundary bits b_0,...,b_{h-1}.

Theorem 11 says F_{0^h} is bijective. Is F_s bijective for all s?

Also: is even the SINGLE-STEP map bijective? That is, for fixed b,
is the map s -> rule30_next(s, b) a bijection on {0,1}^h?
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import rule30_next_tuple


def check_single_step_bijectivity(h):
    """Check if s -> rule30_next_tuple(s, b)[:h] is bijective for each b."""
    all_states = [tuple((mask >> i) & 1 for i in range(h)) for mask in range(2**h)]
    for b in [0, 1]:
        images = set()
        for s in all_states:
            img = rule30_next_tuple(s, b)[:h]
            images.add(img)
        bijective = len(images) == 2**h
        print(f"  h={h}, b={b}: {len(images)} images from {2**h} states → {'BIJECTIVE' if bijective else 'NOT bijective'}")
    return bijective
    

def check_multi_step_bijectivity(h, num_starts=None):
    """Check if F_s is bijective for all (or sampled) starting states."""
    if num_starts is None:
        num_starts = 2**h  # all starts
    
    all_starts = [tuple((mask >> i) & 1 for i in range(h)) for mask in range(min(num_starts, 2**h))]
    
    fail_count = 0
    for s in all_starts:
        seen = set()
        for mask in range(2**h):
            boundary = tuple((mask >> i) & 1 for i in range(h))
            state = s
            for b in boundary:
                state = rule30_next_tuple(state, b)[:h]
            seen.add(state)
        if len(seen) != 2**h:
            fail_count += 1
            if fail_count <= 3:
                print(f"  FAIL: start={''.join(str(x) for x in s)}, {len(seen)} distinct outputs")
    
    return fail_count


def main():
    print("=== Single-step bijectivity ===")
    for h in range(1, 14):
        check_single_step_bijectivity(h)
    
    print("\n=== Multi-step (h steps) bijectivity from all starts ===")
    for h in range(1, 14):
        if 2**h * 2**h > 10**8:  # too expensive
            print(f"  h={h}: skipping (too large)")
            continue
        fails = check_multi_step_bijectivity(h)
        total = 2**h
        print(f"  h={h}: {fails}/{total} failures → {'UNIVERSAL BIJECTIVITY' if fails == 0 else f'{fails} FAILURES'}")


if __name__ == "__main__":
    main()
