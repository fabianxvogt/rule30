#!/usr/bin/env python3
"""
Analyze which (ell, tau_0, tau_1) triples are admissible at each horizon h.

For each h, a class c in S_h is characterized by (ell(c), tau_0(c), tau_1(c))
where ell is the leading bit and tau_b are child classes in S_{h-1}.

We know:
  - ell(tau_0(c)) != ell(tau_1(c))  [Proposition 11h]
  - rho_{h-1}(tau_0(c)) = rho_{h-1}(tau_1(c))  [commuting square + ...]

This script explores what OTHER constraints exist on admissible triples.
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, rule30_next_tuple


def analyze_horizon(h: int):
    """Return detailed analysis of admissible triples at horizon h."""
    qh = build_quotient(h)
    qprev = build_quotient(h - 1)
    
    if h >= 3:
        qprev2 = build_quotient(h - 2)
    else:
        qprev2 = None
    
    # Group states by class
    states_by_class_h: dict[int, list[tuple]] = defaultdict(list)
    for state, cid in qh.items():
        states_by_class_h[cid].append(state)
    
    states_by_class_prev: dict[int, list[tuple]] = defaultdict(list)
    for state, cid in qprev.items():
        states_by_class_prev[cid].append(state)
    
    # Compute ell, tau_0, tau_1, rho for each class in S_h
    class_info = {}
    for cid in sorted(states_by_class_h):
        rep = states_by_class_h[cid][0]
        ell = rep[0]
        
        # tau_0 and tau_1
        tau = {}
        for b in (0, 1):
            next_states = {qprev[rule30_next_tuple(s, b)[:-1]] for s in states_by_class_h[cid]}
            assert len(next_states) == 1, f"tau_{b} not well-defined at h={h}, class={cid}"
            tau[b] = next_states.pop()
        
        # rho_h
        rho_targets = {qprev[s[:-1]] for s in states_by_class_h[cid]}
        assert len(rho_targets) == 1, f"rho not well-defined at h={h}, class={cid}"
        rho = rho_targets.pop()
        
        class_info[cid] = {
            'ell': ell,
            'tau_0': tau[0],
            'tau_1': tau[1],
            'rho': rho,
        }
    
    # Compute ell and rho for S_{h-1} classes
    prev_class_info = {}
    for cid in sorted(states_by_class_prev):
        rep = states_by_class_prev[cid][0]
        ell = rep[0]
        if qprev2 is not None:
            rho_targets = {qprev2[s[:-1]] for s in states_by_class_prev[cid]}
            assert len(rho_targets) == 1
            rho = rho_targets.pop()
        else:
            rho = None
        prev_class_info[cid] = {'ell': ell, 'rho': rho}
    
    return class_info, prev_class_info


def main():
    print("="*80)
    print("ADMISSIBLE TRIPLE ANALYSIS")
    print("="*80)
    
    for h in range(2, 22):
        class_info, prev_info = analyze_horizon(h)
        n_classes = len(class_info)
        n_prev = len(prev_info)
        
        # Collect all admissible triples
        triples = set()
        for cid, info in class_info.items():
            triples.add((info['ell'], info['tau_0'], info['tau_1']))
        
        # Check constraint: ell(tau_0) != ell(tau_1)
        opposite_bits = all(
            prev_info[info['tau_0']]['ell'] != prev_info[info['tau_1']]['ell']
            for info in class_info.values()
        )
        
        # Check constraint: rho(tau_0) == rho(tau_1)  (from commuting square)
        if h >= 3:
            same_rho = all(
                prev_info[info['tau_0']]['rho'] == prev_info[info['tau_1']]['rho']
                for info in class_info.values()
            )
        else:
            same_rho = None
        
        # Count how many triples are "naively possible"
        # Constraint: ell in {0,1}, tau_0 in S_{h-1}, tau_1 in S_{h-1}
        # with ell(tau_0) != ell(tau_1) and rho(tau_0) == rho(tau_1)
        if h >= 3:
            # Group S_{h-1} classes by (rho, ell)
            by_rho_ell = defaultdict(list)
            for cid_prev, pinfo in prev_info.items():
                by_rho_ell[(pinfo['rho'], pinfo['ell'])].append(cid_prev)
            
            # Count compatible pairs: for each rho-fiber, count pairs with opposite ell
            naive_pairs = 0
            for rho_val in set(r for r, _ in by_rho_ell):
                c0 = len(by_rho_ell[(rho_val, 0)])  # classes with ell=0 in this fiber
                c1 = len(by_rho_ell[(rho_val, 1)])  # classes with ell=1 in this fiber
                naive_pairs += c0 * c1 + c1 * c0  # ordered pairs with opposite ell
            naive_triples = 2 * naive_pairs  # times 2 for the leading bit ell(c)
        else:
            naive_triples = None
        
        # Check: does every S_{h-1} class appear as tau_0 for some class?
        tau0_image = {info['tau_0'] for info in class_info.values()}
        tau1_image = {info['tau_1'] for info in class_info.values()}
        tau0_surj = len(tau0_image) == n_prev
        tau1_surj = len(tau1_image) == n_prev
        
        # Check: does every S_{h-1} class appear as rho for some class?
        rho_image = {info['rho'] for info in class_info.values()}
        rho_surj = len(rho_image) == n_prev
        
        print(f"\nh={h}: |S_h|={n_classes}, |S_{{h-1}}|={n_prev}")
        print(f"  Admissible triples: {len(triples)}")
        if naive_triples is not None:
            print(f"  Naively possible triples (with opposite-ell + same-rho): {naive_triples}")
            if naive_triples > 0:
                print(f"  Utilization: {len(triples)}/{naive_triples} = {len(triples)/naive_triples:.4f}")
            else:
                print(f"  WARNING: naive count is 0 but have {len(triples)} triples!")
        print(f"  Opposite leading bits: {opposite_bits}")
        if same_rho is not None:
            print(f"  Same rho for children: {same_rho}")
        print(f"  tau_0 surjective: {tau0_surj} ({len(tau0_image)}/{n_prev})")
        print(f"  tau_1 surjective: {tau1_surj} ({len(tau1_image)}/{n_prev})")
        print(f"  rho surjective: {rho_surj} ({len(rho_image)}/{n_prev})")
        
        # NEW: Check if rho(tau_0(c)) == rho(tau_1(c)) even when h >= 3
        # This would mean both children project to the same S_{h-2} class
        if h >= 3:
            children_same_grandparent = all(
                prev_info[info['tau_0']]['rho'] == prev_info[info['tau_1']]['rho']
                for info in class_info.values()
            )
            print(f"  Children share rho_{{h-1}} (grandparent): {children_same_grandparent}")
        
        # Analyze the rho-fiber structure: for classes c with same rho(c), 
        # what is the relationship between their tau_0, tau_1?
        by_rho = defaultdict(list)
        for cid, info in class_info.items():
            by_rho[info['rho']].append(cid)
        
        fiber_sizes = defaultdict(int)
        for rho_val, classes in by_rho.items():
            fiber_sizes[len(classes)] += 1
        
        # For 2-fibers, check the relationship
        split_patterns = defaultdict(int)
        for rho_val, classes in by_rho.items():
            if len(classes) == 2:
                c1, c2 = classes
                i1, i2 = class_info[c1], class_info[c2]
                # Record the relationship pattern
                same_tau0 = i1['tau_0'] == i2['tau_0']
                same_tau1 = i1['tau_1'] == i2['tau_1']
                same_ell = i1['ell'] == i2['ell']
                split_patterns[(same_ell, same_tau0, same_tau1)] += 1
        
        if split_patterns:
            print(f"  2-fiber splitting patterns (same_ell, same_tau0, same_tau1):")
            for pattern, count in sorted(split_patterns.items()):
                print(f"    {pattern}: {count}")


if __name__ == "__main__":
    main()
