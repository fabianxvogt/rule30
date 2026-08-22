#!/usr/bin/env python3
"""
Analyze the quotient-level dynamics more carefully.

From the quotient transition system perspective:
- From class c, input b → set of possible next classes (the "b-successors" of c)
- Under period-p driving, the trajectory is deterministic (given the initial raw state)
  but non-deterministic from the quotient perspective

KEY QUESTION: What is the maximum number of classes ANY deterministic trajectory 
through the NFA can visit, starting from the all-zero class, with a p-periodic input?

This is equivalent to asking: in the NFA (class transition system), starting from 
class 0, reading a p-periodic word, what is the maximum number of states visited?

Also compute: for each p, what fraction of the NFA's reachable set is achievable 
by a single deterministic trajectory?
"""
from __future__ import annotations
import os, sys, time, random
from itertools import product
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables, rule30_next_tuple


def build_nfa(q, h):
    """Build the NFA transition relation on classes.
    
    nfa[b][c] = set of classes reachable from c on input b.
    """
    N = 1 << h
    total = max(q.values()) + 1
    
    trans, cls_of = make_transition_tables(q, h)
    
    nfa = [{} for _ in range(2)]
    for b in range(2):
        for s in range(N):
            c = cls_of[s]
            ns = trans[b][s]
            nc = cls_of[ns]
            if c not in nfa[b]:
                nfa[b][c] = set()
            nfa[b][c].add(nc)
    
    return nfa, total, cls_of[0]  # start_class = class of state 0


def nfa_reachable(nfa, start, word, total):
    """Compute ALL classes reachable by the NFA reading word (non-deterministic).
    
    This gives the maximum possible set of classes that any trajectory could visit.
    """
    reachable = set()
    current = {start}
    reachable |= current
    
    for b in word:
        next_set = set()
        for c in current:
            if c in nfa[b]:
                next_set |= nfa[b][c]
        current = next_set
        reachable |= current
    
    return reachable


def nfa_periodic_reachable(nfa, start, word, total, max_reps=200):
    """Compute ALL classes reachable by reading word^∞ (until fixpoint)."""
    reachable = {start}
    for rep in range(max_reps):
        old_size = len(reachable)
        current = reachable.copy()
        for b in word:
            next_set = set()
            for c in current:
                if c in nfa[b]:
                    next_set |= nfa[b][c]
            current = next_set
            reachable |= current
        if len(reachable) == old_size:
            break
    return reachable


def main():
    print("QUOTIENT NFA ANALYSIS")
    print("=" * 60)
    
    for h in [5, 8, 10, 12]:
        t0 = time.time()
        q = build_quotient(h)
        total = max(q.values()) + 1
        nfa, _, start = build_nfa(q, h)
        trans, cls_of = make_transition_tables(q, h)
        N = 1 << h
        
        print(f"\nh={h}, |S_h|={total}, N={N}")
        
        # First: what's the non-determinism level?
        max_nd = 0
        avg_nd = 0
        count = 0
        for b in range(2):
            for c in range(total):
                if c in nfa[b]:
                    nd = len(nfa[b][c])
                    max_nd = max(max_nd, nd)
                    avg_nd += nd
                    count += 1
        avg_nd /= count if count > 0 else 1
        print(f"  Non-determinism: max={max_nd}, avg={avg_nd:.1f}")
        
        # For each period p: compare NFA reachability vs deterministic reachability
        for p in range(1, min(25, 3*h)):
            if time.time() - t0 > 60:
                break
            
            # Deterministic: sample random words, find max classes
            max_det = 0
            n_det = min(10000, 1 << p)
            for trial in range(n_det):
                if p <= 14 and trial < (1 << p):
                    word = [(trial >> i) & 1 for i in range(p)]
                else:
                    word = [random.randint(0, 1) for _ in range(p)]
                
                state = 0
                visited = set()
                visited.add(cls_of[state])
                for rep in range(200):
                    for b in word:
                        state = trans[b][state]
                        visited.add(cls_of[state])
                max_det = max(max_det, len(visited))
            
            # NFA: sample random words, find max NFA-reachable
            max_nfa = 0
            for trial in range(min(n_det, 10000)):
                if p <= 14 and trial < (1 << p):
                    word = [(trial >> i) & 1 for i in range(p)]
                else:
                    word = [random.randint(0, 1) for _ in range(p)]
                
                reachable = nfa_periodic_reachable(nfa, start, word, total)
                max_nfa = max(max_nfa, len(reachable))
            
            dt = time.time() - t0
            print(f"  p={p:3d}: det {max_det:4d}/{total}  nfa {max_nfa:4d}/{total}  "
                  f"gap={max_nfa - max_det}")
    
    # KEY TEST: For the NFA, starting from class 0, can ALL classes be reached
    # by SOME single periodic word of period p when we allow non-determinism?
    print("\n" + "=" * 60)
    print("NFA FULL REACHABILITY TEST")
    print("If NFA can't reach all classes with period-p word, neither can DFA")
    print("=" * 60)
    
    for h in [10, 12, 14]:
        if h > 12:
            break  # too expensive
        t0 = time.time()
        q = build_quotient(h)
        total = max(q.values()) + 1
        nfa, _, start = build_nfa(q, h)
        N = 1 << h
        
        print(f"\nh={h}, |S_h|={total}")
        
        # Try various periods
        for p in [5, 10, 15, 20, 30, 50]:
            if time.time() - t0 > 60:
                break
            
            max_nfa = 0
            n_trials = min(50000, 1 << p)
            n_full_nfa = 0
            
            for trial in range(n_trials):
                word = [random.randint(0, 1) for _ in range(p)]
                reachable = nfa_periodic_reachable(nfa, start, word, total, max_reps=50)
                nr = len(reachable)
                if nr > max_nfa:
                    max_nfa = nr
                if nr == total:
                    n_full_nfa += 1
            
            dt = time.time() - t0
            print(f"  p={p:3d}: max_nfa={max_nfa}/{total} ({100*max_nfa/total:.0f}%) "
                  f"full={n_full_nfa}/{n_trials} [{dt:.1f}s]")


if __name__ == "__main__":
    main()
