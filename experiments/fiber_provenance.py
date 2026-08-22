#!/usr/bin/env python3
"""
Track where 2-fibers come from across horizons.

Question: are ALL 2-fibers at horizon h-1 images (via tau_b) of 2-fibers at horizon h?
Or do some 2-fibers at h-1 appear "fresh" — not as children of any 2-fiber at h?

Also: count how the number of 2-fibers changes from h to h-1 via even/odd propagation.
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
    print("="*80)
    print("2-FIBER PROVENANCE ANALYSIS")
    print("="*80)
    
    prev_2fiber_rhos = None  # rho-values of 2-fibers at h
    
    for h in range(2, 20):
        info_h = compute_all_maps(h)
        info_prev = compute_all_maps(h - 1) if h >= 2 else {}
        
        n_h = len(info_h)
        
        # rho-fibers at horizon h
        by_rho = defaultdict(list)
        for cid, ci in info_h.items():
            by_rho[ci['rho']].append(cid)
        
        n_1fibers = sum(1 for v in by_rho.values() if len(v) == 1)
        n_2fibers = sum(1 for v in by_rho.values() if len(v) == 2)
        
        # Identify 2-fiber rho-values at h
        two_fiber_rhos_h = {d for d, classes in by_rho.items() if len(classes) == 2}
        
        # rho-fibers at horizon h-1
        if info_prev:
            by_rho_prev = defaultdict(list)
            for cid, ci in info_prev.items():
                by_rho_prev[ci['rho']].append(cid)
            two_fiber_rhos_prev = {d for d, classes in by_rho_prev.items() if len(classes) == 2}
        else:
            two_fiber_rhos_prev = set()
        
        # For each 2-fiber {c1, c2} at h, track what 2-fibers it produces at h-1
        # via tau_0 and tau_1
        produced_2fibers = set()  # rho-fiber ids at h-1 that come from 2-fibers at h
        
        for d, classes in by_rho.items():
            if len(classes) != 2:
                continue
            c1, c2 = classes
            i1, i2 = info_h[c1], info_h[c2]
            
            # Check tau_0
            if i1['tau_0'] != i2['tau_0'] and info_prev:
                # They're distinct, check if they form a 2-fiber at h-1
                r1 = info_prev[i1['tau_0']]['rho']
                r2 = info_prev[i2['tau_0']]['rho']
                assert r1 == r2  # guaranteed by commuting square
                if r1 in two_fiber_rhos_prev:
                    produced_2fibers.add(('tau_0', d, r1))
            
            # Check tau_1
            if i1['tau_1'] != i2['tau_1'] and info_prev:
                r1 = info_prev[i1['tau_1']]['rho']
                r2 = info_prev[i2['tau_1']]['rho']
                assert r1 == r2
                if r1 in two_fiber_rhos_prev:
                    produced_2fibers.add(('tau_1', d, r1))
        
        # Which 2-fibers at h-1 are explained by 2-fibers at h?
        explained = {x[2] for x in produced_2fibers}
        unexplained = two_fiber_rhos_prev - explained
        
        # Also check: do some 1-fibers at h produce new 2-fibers at h-1?
        # This happens when two distinct 1-fiber classes at h have children
        # that land in the same rho-fiber at h-1
        
        print(f"\nh={h} ({'even' if h%2==0 else 'odd'}): |S_h|={n_h}, "
              f"1-fibers={n_1fibers}, 2-fibers={n_2fibers}")
        print(f"  |S_{{h-1}}| 2-fibers: {len(two_fiber_rhos_prev)}")
        print(f"  2-fibers at h-1 explained by 2-fibers at h: {len(explained)}")
        print(f"  2-fibers at h-1 NOT from 2-fibers at h: {len(unexplained)}")
        
        # Track the flow: how many 2-fibers does each 2-fiber generate?
        # Even h: each generates 2 (one via tau_0, one via tau_1)
        # Odd h: each generates 1 (the non-shared tau)
        children_per_2fiber = defaultdict(int)
        for tag, src_d, tgt_d in produced_2fibers:
            children_per_2fiber[src_d] += 1
        
        gen_counts = defaultdict(int)
        for d in two_fiber_rhos_h:
            gen_counts[children_per_2fiber.get(d, 0)] += 1
        
        print(f"  2-fibers at h generating k 2-fibers at h-1: {dict(sorted(gen_counts.items()))}")


if __name__ == "__main__":
    main()
