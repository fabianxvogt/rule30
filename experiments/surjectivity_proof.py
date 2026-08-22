#!/usr/bin/env python3
"""
PROVE: img(f_0) ∪ img(f_1) = {0,1}^h.

This means: for every target state t ∈ {0,1}^h, there exists a predecessor 
state s and boundary bit b such that f_b(s) = t.

From the Rule 30 update formula (truncated width h):
  t[0] = b ⊕ (s[0] ∨ s[1])
  t[j] = s[j-1] ⊕ (s[j] ∨ s[j+1])  for 1 ≤ j ≤ h-2
  t[h-1] = s[h-2] ⊕ s[h-1]  (zero padding at right)

Given target t, can we find s?

From position h-1 downward, we can use left-permutativity to reconstruct:
  t[j] = s[j-1] ⊕ (s[j] ∨ s[j+1])
  
  For j = h-1: t[h-1] = s[h-2] ⊕ s[h-1]
    → s[h-2] = t[h-1] ⊕ s[h-1]  — but s[h-1] is free!
    
Wait, reconstruction goes the OTHER way. Given t, we want to find s.
The system is:
  s[j-1] = t[j] ⊕ (s[j] ∨ s[j+1])  for j ≥ 1

This is a BACKWARD reconstruction from right to left. Starting from s[h-1] (free), 
we can determine s[h-2], then s[h-3], etc.

At j = h-1: t[h-1] = s[h-2] ⊕ s[h-1]  → s[h-2] = t[h-1] ⊕ s[h-1]
At j = h-2: t[h-2] = s[h-3] ⊕ (s[h-2] ∨ s[h-1])  → s[h-3] = t[h-2] ⊕ (s[h-2] ∨ s[h-1])
...continuing left until s[0]...

Then: t[0] = b ⊕ (s[0] ∨ s[1])  → b = t[0] ⊕ (s[0] ∨ s[1])

So for EVERY target t and EVERY choice of s[h-1] ∈ {0,1}:
1. s is uniquely determined (by backward reconstruction)
2. b is uniquely determined

This gives TWO predecessor pairs (s, b) — one for each choice of s[h-1].
The two predecessors use (possibly different) values of b.

If both predecessors use b=0 or both use b=1, then one of {img(f_0), img(f_1)} 
might miss the target. But can both predecessors use the same b?

Let's check: the two predecessors differ in s[h-1]. Does s[0] (and hence b) depend on s[h-1]?

Yes! The backward reconstruction propagates from right to left, so changing s[h-1] 
potentially changes ALL of s[h-2], s[h-3], ..., s[0], and hence b.

The question is: do the two choices of s[h-1] always lead to different values of b?

If YES: every target is in BOTH img(f_0) and img(f_1). Then img(f_0) = img(f_1) = {0,1}^h.
But we KNOW img(f_0) ≠ {0,1}^h (image is only ~60% of 2^h).

So the answer is NO: the two choices of s[h-1] sometimes give the same b,
leaving the target in only one of {img(f_0), img(f_1)}.

But they NEVER both give the same b for the SAME target... or do they?
If both choices give b=0, then t ∈ img(f_0) but t ∉ img(f_1).
If both give b=1, then t ∈ img(f_1) but t ∉ img(f_0).
If they give different b's, then t ∈ img(f_0) ∩ img(f_1).

So: img(f_0) ∪ img(f_1) = {0,1}^h iff for every target, at least one of the 
two predecessors exists. 

But we just showed: for EVERY target t and EVERY s[h-1], the predecessor pair (s, b) exists.
So every target has TWO predecessors (one for s[h-1]=0, one for s[h-1]=1).
These two predecessors might use the same or different b values.

If both use b=0: target is in img(f_0) (with multiplicity 2) and not in img(f_1).
If both use b=1: target is in img(f_1) (with multiplicity 2) and not in img(f_0).
If they use different b: target is in img(f_0) ∩ img(f_1).

In ALL cases, the target is in img(f_0) ∪ img(f_1). ∎

THIS IS A PROOF! Let me verify computationally.
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import rule30_next_tuple


def backward_reconstruct(target, s_last):
    """Given target t ∈ {0,1}^h and s[h-1], reconstruct the full predecessor s and b."""
    h = len(target)
    s = [0] * h
    s[h-1] = s_last
    
    # Backward reconstruction from position h-1 downward
    for j in range(h-1, 0, -1):
        # t[j] = s[j-1] ⊕ (s[j] ∨ s[j+1_or_0])
        if j == h-1:
            # t[h-1] = s[h-2] ⊕ s[h-1]
            s[j-1] = target[j] ^ s[j]
        else:
            s[j-1] = target[j] ^ (s[j] | s[j+1])
    
    # Determine b from position 0:
    # t[0] = b ⊕ (s[0] ∨ s[1])
    b = target[0] ^ (s[0] | s[1])
    
    return tuple(s), b


def verify_reconstruction(h, s, b, target):
    """Verify f_b(s) = target."""
    result = rule30_next_tuple(s, b)[:h]
    return result == target


def main():
    for h in [3, 5, 8, 10, 12, 15]:
        print(f"\n=== h={h} ===")
        N = 1 << h
        
        all_ok = True
        same_b_count = 0  # both predecessors use same b
        diff_b_count = 0  # predecessors use different b's
        
        max_check = min(N, 100000)
        import random
        random.seed(42)
        
        targets = range(N) if N <= 100000 else [random.randint(0, N-1) for _ in range(100000)]
        
        for t_int in targets:
            target = tuple((t_int >> i) & 1 for i in range(h))
            
            # Two predecessors: s[h-1]=0 and s[h-1]=1
            s0, b0 = backward_reconstruct(target, 0)
            s1, b1 = backward_reconstruct(target, 1)
            
            # Verify
            ok0 = verify_reconstruction(h, s0, b0, target)
            ok1 = verify_reconstruction(h, s1, b1, target)
            
            if not ok0 or not ok1:
                all_ok = False
                print(f"  VERIFICATION FAIL: target={target}, s0={s0}, b0={b0}, ok0={ok0}")
                break
            
            if b0 == b1:
                same_b_count += 1
            else:
                diff_b_count += 1
        
        print(f"  Reconstruction verified: {all_ok}")
        print(f"  Same-b pairs (target in only one img): {same_b_count}")
        print(f"  Diff-b pairs (target in both imgs):    {diff_b_count}")
        print(f"  |img(f_0) ∩ img(f_1)| predicted: {diff_b_count}")
        print(f"  |img(f_0) \\ img(f_1)| predicted: {same_b_count // 2}")
        
        if N <= 100000:
            # Verify match with direct computation
            img0, img1 = set(), set()
            for s_int in range(N):
                state = tuple((s_int >> i) & 1 for i in range(h))
                ns0 = rule30_next_tuple(state, 0)[:h]
                ns1 = rule30_next_tuple(state, 1)[:h]
                img0.add(ns0)
                img1.add(ns1)
            
            actual_inter = len(img0 & img1)
            actual_only0 = len(img0 - img1)
            actual_only1 = len(img1 - img0)
            actual_union = len(img0 | img1)
            print(f"  Direct: |img(f_0) ∩ img(f_1)| = {actual_inter}")
            print(f"  Direct: |img(f_0) \\ img(f_1)| = {actual_only0}")
            print(f"  Direct: |img(f_1) \\ img(f_0)| = {actual_only1}")
            print(f"  Direct: |img(f_0) ∪ img(f_1)| = {actual_union}/{N}")


if __name__ == "__main__":
    main()
