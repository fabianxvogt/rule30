#!/usr/bin/env python3
"""
For 2-fiber siblings (c1, c2 with rho(c1)=rho(c2)), analyze how their children relate.

Key questions:
1. In even-h fibers (share neither), do their children form a specific pattern?
2. Are the children of siblings themselves siblings (in S_{h-1} rho-fibers)?
3. The tree structure: how does the rho-fiber tree interact with the tau-children tree?
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
    print("2-FIBER SIBLING CHILD ANALYSIS")
    print("="*80)
    
    for h in range(3, 20):
        info_h = compute_all_maps(h)
        info_prev = compute_all_maps(h - 1)
        
        n_h = len(info_h)
        n_prev = len(info_prev)
        
        # Build rho fiber map for S_h
        by_rho_h = defaultdict(list)
        for cid, ci in info_h.items():
            by_rho_h[ci['rho']].append(cid)
        
        # Build rho fiber map for S_{h-1}
        by_rho_prev = defaultdict(list)
        for cid, ci in info_prev.items():
            by_rho_prev[ci['rho']].append(cid)
        
        # For each class d in S_{h-1}, make a lookup: which fiber does it belong to?
        fiber_of = {}  # class in S_{h-1} -> (rho_value, set of siblings)
        for d_rho, classes in by_rho_prev.items():
            for c in classes:
                fiber_of[c] = (d_rho, frozenset(classes))
        
        # Analyze 2-fiber siblings at horizon h
        n_2fibers = 0
        
        # For even h: share neither tau_0 nor tau_1
        # Check if children of siblings are themselves siblings (in rho-fibers of S_{h-1})
        children_siblings_tau0 = 0  # tau_0(c1) and tau_0(c2) are in same rho-fiber at S_{h-1}
        children_siblings_tau1 = 0
        children_siblings_both = 0
        
        # Check if the pairs (tau_0(c1), tau_0(c2)) relate via rho
        for d, classes in by_rho_h.items():
            if len(classes) != 2:
                continue
            n_2fibers += 1
            c1, c2 = classes
            i1, i2 = info_h[c1], info_h[c2]
            
            # Are tau_0(c1) and tau_0(c2) in the same rho-fiber of S_{h-1}?
            t0_sibs = fiber_of[i1['tau_0']][1] if i1['tau_0'] in fiber_of else {i1['tau_0']}
            t0_same_fiber = i2['tau_0'] in t0_sibs
            
            t1_sibs = fiber_of[i1['tau_1']][1] if i1['tau_1'] in fiber_of else {i1['tau_1']}
            t1_same_fiber = i2['tau_1'] in t1_sibs
            
            if t0_same_fiber:
                children_siblings_tau0 += 1
            if t1_same_fiber:
                children_siblings_tau1 += 1
            if t0_same_fiber and t1_same_fiber:
                children_siblings_both += 1
        
        print(f"\nh={h} ({'even' if h%2==0 else 'odd'}): |S_h|={n_h}, 2-fibers: {n_2fibers}")
        print(f"  Children in same S_{{h-1}} rho-fiber (tau_0): {children_siblings_tau0}/{n_2fibers}")
        print(f"  Children in same S_{{h-1}} rho-fiber (tau_1): {children_siblings_tau1}/{n_2fibers}")
        print(f"  Both children in same fibers: {children_siblings_both}/{n_2fibers}")
        
        # Deeper: for even h (share neither), do the children's rho-values differ in a 
        # structured way? Let's check if tau_b(c1) and tau_b(c2) have the same rho
        # (which by the commuting square = tau_b(rho(c1)) = tau_b(rho(c2)) = tau_b(d))
        # This MUST be true since rho(c1) = rho(c2) = d and commuting square holds!
        if h >= 4:
            commuting_confirms = 0
            for d, classes in by_rho_h.items():
                if len(classes) != 2:
                    continue
                c1, c2 = classes
                i1, i2 = info_h[c1], info_h[c2]
                
                # rho(tau_0(c1)) = tau_0(rho(c1)) = tau_0(d)
                # rho(tau_0(c2)) = tau_0(rho(c2)) = tau_0(d)
                # So rho(tau_0(c1)) = rho(tau_0(c2))
                r_t0_c1 = info_prev[i1['tau_0']]['rho']
                r_t0_c2 = info_prev[i2['tau_0']]['rho']
                r_t1_c1 = info_prev[i1['tau_1']]['rho']
                r_t1_c2 = info_prev[i2['tau_1']]['rho']
                
                if r_t0_c1 == r_t0_c2 and r_t1_c1 == r_t1_c2:
                    commuting_confirms += 1
            
            print(f"  Commuting square confirms rho(tau_b(c1))=rho(tau_b(c2)): {commuting_confirms}/{n_2fibers}")
        
        # So the siblings' children are always in the same rho-fiber of S_{h-1}!
        # The question is: are they the SAME element or a DIFFERENT element?
        # For even h: different (share neither)
        # For odd h: same for one, different for the other
        
        # KEY INSIGHT: For even h, siblings (c1,c2) with rho(c1)=rho(c2)=d have:
        #   tau_0(c1) != tau_0(c2) but rho(tau_0(c1)) = rho(tau_0(c2))
        #   tau_1(c1) != tau_1(c2) but rho(tau_1(c1)) = rho(tau_1(c2))
        # So the children are distinct elements within the same S_{h-1} rho-fiber.
        # This means the S_{h-1} rho-fiber must also have size >= 2.
        
        # For even h, verify: when c1,c2 are in a 2-fiber, are tau_0(c1),tau_0(c2) 
        # in a 2-fiber of S_{h-1}? (They must be, since they're distinct with same rho.)
        if h % 2 == 0 and h >= 4:
            children_form_2fiber = 0
            for d, classes in by_rho_h.items():
                if len(classes) != 2:
                    continue
                c1, c2 = classes
                i1, i2 = info_h[c1], info_h[c2]
                
                # tau_0(c1) and tau_0(c2) must be distinct with same rho
                if i1['tau_0'] != i2['tau_0']:
                    r1 = info_prev[i1['tau_0']]['rho']
                    r2 = info_prev[i2['tau_0']]['rho']
                    if r1 == r2:
                        children_form_2fiber += 1
            
            print(f"  Even h: tau_0 children form 2-fibers in S_{{h-1}}: {children_form_2fiber}/{n_2fibers}")


if __name__ == "__main__":
    main()
