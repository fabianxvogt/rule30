#!/usr/bin/env python3
"""
Under period-p driving, the trajectory is eventually periodic.
Let F = f_{b_{p-1}} ∘ ... ∘ f_{b_0} (the p-step composite).

The trajectory visits:
  s_0, s_1, ..., s_{T-1} (transient), then s_T, ..., s_{T+L-1} (cycle of F)

But within the cycle of F, the trajectory passes through p states per "macro-step"
(one for each application of f_{b_i}). So the actual trajectory visits:
  - T * p states in the transient (approximately)
  - L * p states in each cycle

Total distinct states visited ≤ (T + L) * p where T+L ≤ 2^h / (something).

But the actual number of DISTINCT CLASSES visited is what matters.

Let me compute, for each h and each p-periodic word:
  1. The period L of the composite F (acting on the all-zeros start point)
  2. The transient T
  3. The total number of distinct raw states visited 
  4. The total number of distinct classes visited
"""
from __future__ import annotations
import os, sys, time, random
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables

random.seed(42)


def trajectory_analysis(trans, cls_of, word_ints, h, max_steps=1000000):
    """Analyze trajectory under periodic driving.
    
    Returns:
        transient: number of steps before cycle
        cycle_len: length of the cycle
        n_states: number of distinct raw states visited  
        n_classes: number of distinct classes visited
    """
    p = len(word_ints)
    
    # Apply word repeatedly, track states at multiples of p
    state = 0
    macro_states = [state]  # states after 0, p, 2p, ... steps
    macro_state_first = {state: 0}  # state -> first macro-step index
    
    # Also track all micro-states and classes
    all_states = {state}
    all_classes = {cls_of[state]}
    
    for macro in range(1, max_steps // p + 1):
        for b in word_ints:
            state = trans[b][state]
            all_states.add(state)
            all_classes.add(cls_of[state])
        
        if state in macro_state_first:
            transient = macro_state_first[state]
            cycle_len = macro - transient
            return transient, cycle_len, len(all_states), len(all_classes)
        
        macro_state_first[state] = macro
        macro_states.append(state)
    
    return -1, -1, len(all_states), len(all_classes)  # didn't find cycle


def main():
    print("TRAJECTORY STRUCTURE UNDER PERIODIC DRIVING")
    print("=" * 60)
    print("F = composite map over one period. T = transient, L = cycle length of F.")
    print("n_states = distinct raw states, n_classes = distinct classes.")
    print()
    
    for h in [5, 8, 10, 12]:
        t0 = time.time()
        q = build_quotient(h)
        total = max(q.values()) + 1
        trans, cls_of = make_transition_tables(q, h)
        N = 1 << h
        
        print(f"h={h}, |S_h|={total}, N={N}")
        
        for p in [2, 5, 10, 15, 20, 30, 50]:
            if time.time() - t0 > 120:
                break
            
            # Sample many random words
            max_T = 0
            max_L = 0
            max_TL = 0
            max_states = 0
            max_classes = 0
            n_trials = min(5000, max(100, 2**min(p, 16)))
            n_full = 0
            
            for trial in range(n_trials):
                word = [random.randint(0, 1) for _ in range(p)]
                T, L, ns, nc = trajectory_analysis(trans, cls_of, word, h)
                max_T = max(max_T, T)
                max_L = max(max_L, L)
                max_TL = max(max_TL, T + L)
                max_states = max(max_states, ns)
                max_classes = max(max_classes, nc)
                if nc == total:
                    n_full += 1
            
            print(f"  p={p:3d}: max T={max_T:4d} L={max_L:4d} T+L={max_TL:4d} "
                  f"states={max_states:5d}/{N} classes={max_classes:4d}/{total} "
                  f"full={n_full}/{n_trials}")
        
        print(f"  [{time.time()-t0:.1f}s]\n")
    
    # Special section: for each h, try ALL words at small p and report
    # maximum classes + the T+L product
    print("\n" + "=" * 60)
    print("EXHAUSTIVE ANALYSIS AT SMALL PERIODS")
    print("=" * 60)
    
    for h in [5, 7, 8, 9, 10]:
        q = build_quotient(h)
        total = max(q.values()) + 1
        trans, cls_of = make_transition_tables(q, h)
        N = 1 << h
        
        print(f"\nh={h}, |S_h|={total}, N={N}")
        
        for p in range(1, min(15, h + 3)):
            t0 = time.time()
            if (1 << p) > 50000:
                break
            
            max_classes = 0
            max_raw = 0
            max_visit_in_cycle = 0  # p * L
            
            for w_int in range(1 << p):
                word = [(w_int >> i) & 1 for i in range(p)]
                T, L, ns, nc = trajectory_analysis(trans, cls_of, word, h)
                max_classes = max(max_classes, nc)
                max_raw = max(max_raw, ns)
                if L > 0:
                    max_visit_in_cycle = max(max_visit_in_cycle, p * L)
            
            dt = time.time() - t0
            print(f"  p={p:3d}: max_classes={max_classes:4d}/{total} ({100*max_classes/total:.0f}%) "
                  f"max_raw={max_raw:5d}/{N} max_p*L={max_visit_in_cycle:5d} "
                  f"[{dt:.1f}s]")


if __name__ == "__main__":
    main()
