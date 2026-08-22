#!/usr/bin/env python3
"""
Critical check: Is each f_b (for fixed b) a bijection on {0,1}^h?

Universal Bijectivity says: for fixed s_0, the map (b_0,...,b_{h-1}) -> s_h is bijective.
This means the whole map Phi_{s_0} is a bijection.

But Phi_{s_0}(b_0,...,b_{h-1}) = f_{b_{h-1}} ∘ ... ∘ f_{b_0}(s_0).

For this to be bijective for ALL s_0, we need each f_b to be a bijection???
No! That's too strong. The bijectivity is over the (b_0,...,b_{h-1}) input.

So separately: is f_0 : {0,1}^h → {0,1}^h a bijection? (where f_b(s) is the 
next truncated state when driving bit is b)

Let's check!
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import make_transition_tables, build_quotient


def check_bijectivity(h):
    q = build_quotient(h)
    trans, cls_of = make_transition_tables(q, h)
    N = 1 << h
    
    for b in range(2):
        image = set(trans[b])
        is_bij = (len(image) == N)
        print(f"  f_{b}: |image| = {len(image)}/{N} {'BIJECTION' if is_bij else 'NOT bijection'}")
        
        if not is_bij:
            # Count preimage sizes
            preimage_count = {}
            for s in range(N):
                ns = trans[b][s]
                preimage_count[ns] = preimage_count.get(ns, 0) + 1
            
            max_pre = max(preimage_count.values())
            n_not_hit = N - len(image)
            print(f"    max preimage size = {max_pre}")
            print(f"    states not in image = {n_not_hit}")


def main():
    for h in range(3, 16):
        print(f"h={h}:")
        check_bijectivity(h)


if __name__ == "__main__":
    main()
