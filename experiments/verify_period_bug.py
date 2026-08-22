#!/usr/bin/env python3
"""
Verify that the machine state period under periodic driving can exceed p.
Find concrete examples where the macro-cycle length ℓ > 1.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables
import numpy as np

def compute_macro_cycle(h, word):
    """Compute the macro-cycle length of F_w and the machine state period."""
    q = build_quotient(h)
    next_state, class_table = make_transition_tables(q, h)
    N = 1 << h
    p = len(word)
    
    # Compute F_w: composite map for one period
    Fw = list(range(N))
    for bit in word:
        Fw = [next_state[bit][Fw[s]] for s in range(N)]
    
    # Trace from s=0
    s = 0
    # Apply micro-steps and track macro-states
    macro_states = [s]
    for period_num in range(N + 10):
        # Apply one period
        for bit in word:
            s = next_state[bit][s]
        macro_states.append(s)
        # Check for macro-cycle
        for j in range(len(macro_states) - 1):
            if macro_states[-1] == macro_states[j]:
                transient = j
                cycle_len = len(macro_states) - 1 - j
                micro_period = cycle_len * p
                return transient, cycle_len, micro_period
    
    return None, None, None

def main():
    print("Verifying machine state period under periodic driving")
    print("=" * 70)
    
    for h in [4, 6, 8, 10]:
        q = build_quotient(h)
        next_state, class_table = make_transition_tables(q, h)
        N = 1 << h
        num_classes = max(class_table) + 1
        
        print(f"\nh={h}, N={N}, |S_h|={num_classes}")
        print("-" * 50)
        
        # Test all words of length p for small p
        for p in [2, 3, 4, 5]:
            max_cycle = 0
            total_words = 1 << p
            cycle_dist = {}
            
            for w_int in range(total_words):
                word = tuple((w_int >> i) & 1 for i in range(p))
                trans, cycle, micro_p = compute_macro_cycle(h, word)
                if cycle is not None:
                    max_cycle = max(max_cycle, cycle)
                    cycle_dist[cycle] = cycle_dist.get(cycle, 0) + 1
            
            print(f"  p={p}: max macro-cycle = {max_cycle}, "
                  f"max micro-period = {max_cycle * p}")
            # Show distribution
            for cyc in sorted(cycle_dist.keys()):
                print(f"    cycle_len={cyc}: {cycle_dist[cyc]} words "
                      f"(micro_period={cyc*p})")
        
        # Also test random longer words
        for p in [10, 20]:
            max_cycle = 0
            max_micro = 0
            cycles = []
            for _ in range(1000):
                word = tuple(np.random.randint(0, 2, p))
                trans, cycle, micro_p = compute_macro_cycle(h, word)
                if cycle is not None:
                    max_cycle = max(max_cycle, cycle)
                    max_micro = max(max_micro, micro_p)
                    cycles.append(cycle)
            
            mean_cycle = np.mean(cycles) if cycles else 0
            print(f"  p={p} (1000 random): max macro-cycle={max_cycle}, "
                  f"max micro-period={max_micro}, mean cycle={mean_cycle:.1f}")
    
    # CRITICAL TEST: Find a specific example where ℓ > 1 and show the
    # machine state does not have period p
    print("\n" + "=" * 70)
    print("CONCRETE EXAMPLE: machine state period > p")
    print("=" * 70)
    
    h = 6
    q = build_quotient(h)
    next_state, class_table = make_transition_tables(q, h)
    N = 1 << h
    
    for p in [2, 3]:
        for w_int in range(1 << p):
            word = tuple((w_int >> i) & 1 for i in range(p))
            trans, cycle, micro_p = compute_macro_cycle(h, word)
            if cycle is not None and cycle > 1:
                print(f"\nh={h}, p={p}, word={''.join(map(str,word))}: "
                      f"macro-transient={trans}, macro-cycle={cycle}, "
                      f"micro-period={micro_p}")
                
                # Show the full trajectory
                s = 0
                print(f"  Trajectory from s=0:")
                for t in range(micro_p * 3 + trans * p + 10):
                    bit = word[t % p]
                    cls = class_table[s]
                    if t <= trans * p + micro_p * 2 + 5:
                        mark = ""
                        if t > 0 and t % p == 0:
                            mark = f" <-- period boundary (macro step {t//p})"
                        print(f"    t={t:3d}: state={s:3d}, class={cls:2d}, "
                              f"input={bit}{mark}")
                    s = next_state[bit][s]
                
                # Verify: state at t and t+p differ
                s1 = 0
                states = []
                for t in range((trans + cycle + 5) * p):
                    states.append(s1)
                    bit = word[t % p]
                    s1 = next_state[bit][s1]
                
                # Check if state at t == state at t+p for t in periodic regime
                start = (trans + 1) * p
                same_at_p = all(states[start + i] == states[start + i + p] 
                                for i in range(micro_p))
                same_at_mp = all(states[start + i] == states[start + i + micro_p] 
                                for i in range(micro_p))
                
                print(f"\n  Period check: states repeat with period p={p}? {same_at_p}")
                print(f"  Period check: states repeat with period {micro_p}? {same_at_mp}")
                
                # Count distinct classes in one micro-period
                classes_in_period = set()
                for i in range(start, start + micro_p):
                    classes_in_period.add(class_table[states[i]])
                print(f"  Distinct classes in one micro-period: "
                      f"{len(classes_in_period)}")
                
                # Only show first example for each (h,p)
                break

if __name__ == "__main__":
    main()
