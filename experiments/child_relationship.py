#!/usr/bin/env python3
"""
Deep analysis of the relationship between tau_0(c) and tau_1(c) for classes c in S_h.

Questions:
1. What is the relationship between rho(tau_0(c)) and rho(tau_1(c))?
   (They need NOT be equal — commuting square says rho(tau_b(c)) = tau_b(rho(c)),
    so rho(tau_0(c)) = tau_0(rho(c)) and rho(tau_1(c)) = tau_1(rho(c)), which are
    two different children of rho(c) in S_{h-2}.)

2. What about the "sibling" structure? If c1, c2 are in the same rho-fiber
   (rho(c1) = rho(c2)), what is the relationship between their children?

3. For 2-fibers specifically: if rho(c1) = rho(c2) = d, with ell(c1) = ell(c2),
   what distinguishes c1, c2 in terms of their children?
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, rule30_next_tuple


def compute_all_maps(h):
    """Compute ell, tau_0, tau_1, rho for all classes at horizon h."""
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
    
    return info, qh, qprev


def main():
    print("="*80)
    print("CHILD RELATIONSHIP ANALYSIS")
    print("="*80)
    
    for h in range(3, 20):
        info_h, qh, _ = compute_all_maps(h)
        info_prev, _, _ = compute_all_maps(h - 1)
        
        n_h = len(info_h)
        
        # Q1: Relationship between rho(tau_0(c)) and rho(tau_1(c))
        # From commuting square: rho(tau_b(c)) = tau_b(rho(c))
        # So rho(tau_0(c)) = tau_0(rho(c)) and rho(tau_1(c)) = tau_1(rho(c))
        # These are the children of rho(c) in S_{h-2}
        
        # Verify: rho(tau_0(c)) == tau_0(rho(c)) and rho(tau_1(c)) == tau_1(rho(c))
        if h >= 3:
            info_prev2, _, _ = compute_all_maps(h - 2) if h >= 4 else ({}, None, None)
            
            commuting_ok = True
            for cid, ci in info_h.items():
                d = ci['rho']  # rho(c), a class in S_{h-1}
                di = info_prev[d]
                
                # rho of tau_0(c)
                tau0_rho = info_prev[ci['tau_0']].get('rho') if h >= 4 else None
                # tau_0 of rho(c)
                tau0_of_rho = di['tau_0']
                
                tau1_rho = info_prev[ci['tau_1']].get('rho') if h >= 4 else None
                tau1_of_rho = di['tau_1']
                
                if h >= 4:
                    if tau0_rho != tau0_of_rho or tau1_rho != tau1_of_rho:
                        commuting_ok = False
                        break
            
            if h >= 4:
                assert commuting_ok, f"Commuting square failed at h={h}"
        
        # Q2: For classes in the same rho-fiber, how do their children relate?
        by_rho = defaultdict(list)
        for cid, ci in info_h.items():
            by_rho[ci['rho']].append(cid)
        
        fiber_sizes = defaultdict(int)
        for d, classes in by_rho.items():
            fiber_sizes[len(classes)] += 1
        
        # For 2-fibers: detailed analysis
        n_2fibers = fiber_sizes.get(2, 0)
        
        # Patterns in 2-fibers
        share_tau0 = 0
        share_tau1 = 0
        share_both = 0
        share_neither = 0
        same_ell_count = 0
        diff_ell_count = 0
        
        # Check: in 2-fibers, what is the EXACT child relationship?
        for d, classes in by_rho.items():
            if len(classes) != 2:
                continue
            c1, c2 = classes
            i1, i2 = info_h[c1], info_h[c2]
            
            s_tau0 = i1['tau_0'] == i2['tau_0']
            s_tau1 = i1['tau_1'] == i2['tau_1']
            
            if s_tau0 and s_tau1:
                share_both += 1
            elif s_tau0:
                share_tau0 += 1
            elif s_tau1:
                share_tau1 += 1
            else:
                share_neither += 1
            
            if i1['ell'] == i2['ell']:
                same_ell_count += 1
            else:
                diff_ell_count += 1
        
        # Check: are tau_0 and tau_1 surjective onto S_{h-1}?
        tau0_img = {ci['tau_0'] for ci in info_h.values()}
        tau1_img = {ci['tau_1'] for ci in info_h.values()}
        n_prev = len(info_prev)
        
        # Check: for each class d in S_{h-1}, how many classes c in S_h have tau_0(c) = d?
        tau0_preimage = defaultdict(list)
        tau1_preimage = defaultdict(list)
        for cid, ci in info_h.items():
            tau0_preimage[ci['tau_0']].append(cid)
            tau1_preimage[ci['tau_1']].append(cid)
        
        tau0_preimage_sizes = defaultdict(int)
        tau1_preimage_sizes = defaultdict(int)
        for d in range(n_prev):
            if d in tau0_preimage:
                tau0_preimage_sizes[len(tau0_preimage[d])] += 1
            else:
                tau0_preimage_sizes[0] += 1
            if d in tau1_preimage:
                tau1_preimage_sizes[len(tau1_preimage[d])] += 1
            else:
                tau1_preimage_sizes[0] += 1
        
        print(f"\nh={h}: |S_h|={n_h}, |S_{{h-1}}|={n_prev}")
        print(f"  rho fibers: {dict(sorted(fiber_sizes.items()))}")
        print(f"  2-fibers ({n_2fibers} total):")
        print(f"    same ell: {same_ell_count}, diff ell: {diff_ell_count}")
        print(f"    share tau0 only: {share_tau0}")
        print(f"    share tau1 only: {share_tau1}")
        print(f"    share both: {share_both}")
        print(f"    share neither: {share_neither}")
        print(f"  tau_0 preimage sizes: {dict(sorted(tau0_preimage_sizes.items()))}")
        print(f"  tau_1 preimage sizes: {dict(sorted(tau1_preimage_sizes.items()))}")


if __name__ == "__main__":
    main()
