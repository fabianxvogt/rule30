#!/usr/bin/env python3
"""
Investigate the unexplained 2-fibers at h=18 (even).
Are there really 2-fibers at h-1=17 not produced by any 2-fiber at h=18?
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
    h = 18
    info_h = compute_all_maps(h)
    info_prev = compute_all_maps(h - 1)
    
    # 2-fibers at h
    by_rho_h = defaultdict(list)
    for cid, ci in info_h.items():
        by_rho_h[ci['rho']].append(cid)
    two_fibers_h = {d: cs for d, cs in by_rho_h.items() if len(cs) == 2}
    
    # 2-fibers at h-1
    by_rho_prev = defaultdict(list)
    for cid, ci in info_prev.items():
        by_rho_prev[ci['rho']].append(cid)
    two_fibers_prev = {d: cs for d, cs in by_rho_prev.items() if len(cs) == 2}
    
    print(f"h={h}: {len(two_fibers_h)} 2-fibers")
    print(f"h-1={h-1}: {len(two_fibers_prev)} 2-fibers")
    
    # Track which 2-fibers at h-1 are produced
    produced = set()
    for d, (c1, c2) in two_fibers_h.items():
        i1, i2 = info_h[c1], info_h[c2]
        for b in (0, 1):
            t1 = i1[f'tau_{b}']
            t2 = i2[f'tau_{b}']
            if t1 != t2:
                r = info_prev[t1]['rho']
                assert r == info_prev[t2]['rho']
                if r in two_fibers_prev:
                    produced.add(r)
    
    unexplained = set(two_fibers_prev.keys()) - produced
    print(f"\nUnexplained 2-fibers at h-1: {len(unexplained)}")
    
    # For each unexplained 2-fiber, show the two classes and trace where they come from
    for d_rho in sorted(unexplained):
        c1, c2 = two_fibers_prev[d_rho]
        i1 = info_prev[c1]
        i2 = info_prev[c2]
        print(f"\n  Unexplained 2-fiber: rho={d_rho}, classes=[{c1}, {c2}]")
        print(f"    class {c1}: ell={i1['ell']}, tau_0={i1['tau_0']}, tau_1={i1['tau_1']}, rho={i1['rho']}")
        print(f"    class {c2}: ell={i2['ell']}, tau_0={i2['tau_0']}, tau_1={i2['tau_1']}, rho={i2['rho']}")
        
        # Who at h has tau_b mapping to c1 or c2?
        tau0_to_c1 = [c for c, ci in info_h.items() if ci['tau_0'] == c1]
        tau0_to_c2 = [c for c, ci in info_h.items() if ci['tau_0'] == c2]
        tau1_to_c1 = [c for c, ci in info_h.items() if ci['tau_1'] == c1]
        tau1_to_c2 = [c for c, ci in info_h.items() if ci['tau_1'] == c2]
        
        print(f"    Parents via tau_0: c1 <- {tau0_to_c1}, c2 <- {tau0_to_c2}")
        print(f"    Parents via tau_1: c1 <- {tau1_to_c1}, c2 <- {tau1_to_c2}")
        
        # Check if any pair of parents are NOT 2-fiber siblings
        # (they could be from different 1-fibers)
        for source_label, p1_list, p2_list in [
            ('tau_0', tau0_to_c1, tau0_to_c2),
            ('tau_1', tau1_to_c1, tau1_to_c2)
        ]:
            for p1 in p1_list:
                for p2 in p2_list:
                    rho_p1 = info_h[p1]['rho']
                    rho_p2 = info_h[p2]['rho']
                    same_fiber = rho_p1 == rho_p2
                    fiber_size = len(by_rho_h[rho_p1]) if same_fiber else None
                    print(f"    {source_label}: parent pair ({p1},{p2}) "
                          f"rho=({rho_p1},{rho_p2}) same_fiber={same_fiber} "
                          f"fiber_size={fiber_size}")


if __name__ == "__main__":
    main()
