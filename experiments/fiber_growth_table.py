#!/usr/bin/env python3
"""
Build a compact table: |S_h|, # 1-fibers, # 2-fibers, # "new" 2-fibers (not from parents).

Let f(h) = # 2-fibers at h.
Theory predicts:
  Even h: each 2-fiber generates 2, so expects 2*f(h) to cover f(h-1)
  Odd h: each 2-fiber generates 1, so expects f(h) to cover f(h-1), plus fresh ones

Let's also compute the growth: |S_h| = n_1(h) + 2*n_2(h), and track the recurrence.
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, rule30_next_tuple


def compute_all_maps(h):
    qh = build_quotient(h)
    qprev = build_quotient(h - 1)
    
    states_by_class: dict[int, list[tuple]] = defaultdict(list)
    for state, cid in qh.items():
        states_by_class[cid].append(state)
    
    info = {}
    for cid in sorted(states_by_class):
        rep = states_by_class[cid][0]
        ell = rep[0]
        
        tau = {}
        for b in (0, 1):
            targets = {qprev[rule30_next_tuple(s, b)[:-1]] for s in states_by_class[cid]}
            assert len(targets) == 1
            tau[b] = targets.pop()
        
        rho_targets = {qprev[s[:-1]] for s in states_by_class[cid]}
        assert len(rho_targets) == 1
        rho = rho_targets.pop()
        
        info[cid] = {'ell': ell, 'tau_0': tau[0], 'tau_1': tau[1], 'rho': rho}
    
    return info


def main():
    data = []
    
    for h in range(1, 22):
        info_h = compute_all_maps(h)
        n_h = len(info_h)
        
        by_rho = defaultdict(list)
        for cid, ci in info_h.items():
            by_rho[ci['rho']].append(cid)
        
        n_1 = sum(1 for v in by_rho.values() if len(v) == 1)
        n_2 = sum(1 for v in by_rho.values() if len(v) == 2)
        
        data.append((h, n_h, n_1, n_2))
    
    print(f"{'h':>3} {'|S_h|':>7} {'n_1':>6} {'n_2':>6} {'n_1+2n_2':>9} {'delta':>7} {'ratio':>7} {'parity':>6}")
    print("-" * 60)
    
    for i, (h, n_h, n_1, n_2) in enumerate(data):
        check = n_1 + 2 * n_2
        assert check == n_h, f"Accounting error: {n_1} + 2*{n_2} = {check} != {n_h}"
        
        if i > 0:
            delta = n_h - data[i-1][1]
            ratio = n_h / data[i-1][1]
        else:
            delta = 0
            ratio = 0
        
        print(f"{h:3d} {n_h:7d} {n_1:6d} {n_2:6d} {check:9d} {delta:7d} {ratio:7.3f} {'even' if h%2==0 else 'odd':>6}")
    
    # Check: |S_h| = |S_{h-1}| + n_2(h)  (since n_1(h) classes are new singletons
    # and n_2(h) pairs add n_2(h) extra classes beyond |S_{h-1}|)
    # Actually: |S_h| = n_1(h) + 2*n_2(h) and |S_{h-1}| = n_1(h) + n_2(h) (each fiber
    # contributes exactly 1 class to |S_{h-1}|). So |S_h| - |S_{h-1}| = n_2(h).
    
    print("\n\nVerification: |S_h| - |S_{h-1}| == n_2(h)?")
    for i in range(1, len(data)):
        h, n_h, n_1, n_2 = data[i]
        _, n_prev, _, _ = data[i-1]
        delta = n_h - n_prev
        print(f"  h={h}: delta = {delta}, n_2 = {n_2}, match = {delta == n_2}")
    
    print("\n\nGrowth of n_2(h):")
    for i in range(2, len(data)):
        h, _, _, n_2 = data[i]
        _, _, _, n_2_prev = data[i-1]
        if n_2_prev > 0:
            ratio = n_2 / n_2_prev
            print(f"  h={h}: n_2={n_2}, ratio from prev={ratio:.3f}, parity={'even' if h%2==0 else 'odd'}")


if __name__ == "__main__":
    main()
