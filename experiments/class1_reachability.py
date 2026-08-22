#!/usr/bin/env python3
"""
Investigate reachability of state 0^{h-1}1 (the unique representative of class 1).

Key questions:
1. What are the preimages of this state under f_0 and f_1?
2. Does this state survive in the attractor of F_w for typical period-p words?
3. How often does the transient from s=0 visit this state?

This addresses whether Proposition 13 can be salvaged via a structural argument
about fiber-1 classes.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables
import numpy as np
from itertools import product as iprod

def analyze_class1(h, verbose=True):
    """Analyze reachability of the class-1 state for horizon h."""
    q = build_quotient(h)
    next_state, class_table = make_transition_tables(q, h)
    N = 1 << h
    num_classes = max(class_table) + 1
    
    # Find class 1 state(s)
    class1_states = [s for s in range(N) if class_table[s] == 1]
    if verbose:
        print(f"\n=== h={h}, N={N}, |S_h|={num_classes} ===")
        print(f"Class 1 states: {class1_states} (count={len(class1_states)})")
    
    # State 0^{h-1}1 = integer 2^{h-1}
    target = 1 << (h-1)
    assert target in class1_states, f"Expected {target} in class 1"
    
    # Preimages of target under f_0 and f_1
    pre0 = [s for s in range(N) if next_state[0][s] == target]
    pre1 = [s for s in range(N) if next_state[1][s] == target]
    if verbose:
        print(f"Preimages of state {target} under f_0: {len(pre0)} states")
        print(f"Preimages of state {target} under f_1: {len(pre1)} states")
        print(f"Total preimages: {len(pre0) + len(pre1)}")
    
    # What fraction of the state space can reach target in k steps?
    reachable_to_target = {target}
    for k in range(1, min(3*h, 50)):
        new_reach = set()
        for s in range(N):
            if next_state[0][s] in reachable_to_target or next_state[1][s] in reachable_to_target:
                new_reach.add(s)
        if new_reach == reachable_to_target:
            if verbose:
                print(f"Backward reachable set stabilized at k={k}: {len(reachable_to_target)} states ({len(reachable_to_target)/N:.4f})")
            break
        reachable_to_target = new_reach
    else:
        if verbose:
            print(f"Backward reachable at k={min(3*h,50)}: {len(reachable_to_target)} states ({len(reachable_to_target)/N:.4f})")
    
    return next_state, class_table, N, num_classes, target, pre0, pre1

def check_attractor_membership(h, p_values, num_samples=10000):
    """Check how often class-1 state is in the attractor of F_w."""
    next_state, class_table, N, num_classes, target, _, _ = analyze_class1(h, verbose=True)
    
    for p in p_values:
        in_attractor = 0
        transient_visits = 0  # from s=0
        total_coverage = 0
        
        trials = min(num_samples, 2**p if p <= 20 else num_samples)
        exhaustive = (2**p <= num_samples)
        
        for trial in range(trials):
            if exhaustive:
                word = tuple((trial >> i) & 1 for i in range(p))
            else:
                word = tuple(np.random.randint(0, 2, p))
            
            # Compute F_w (composite map for one period)
            Fw = list(range(N))  # identity
            for bit in word:
                Fw = [next_state[bit][s] for s in Fw]
            
            # Find attractor of F_w
            # Iterate F_w enough times to reach attractor
            # The attractor is the eventual image (intersection of F_w^k(S))
            image = set(range(N))
            for _ in range(N):  # at most N iterations needed
                image_new = set(Fw[s] for s in image)
                if image_new == image:
                    break
                image = image_new
            
            attractor = image
            if target in attractor:
                in_attractor += 1
            
            # Check transient from s=0: does it visit target?
            s = 0
            visited_target = False
            visited_classes = set()
            for step in range(N + p):  # enough to reach attractor + one cycle
                visited_classes.add(class_table[s])
                if s == target:
                    visited_target = True
                # Apply one full period
                for bit in word:
                    s = next_state[bit][s]
            
            # Actually trace micro-steps from s=0
            s = 0
            visited_target2 = False
            visited_classes2 = set()
            seen_states = set()
            for step in range(min((N + 1) * p, 100000)):
                visited_classes2.add(class_table[s])
                if s == target:
                    visited_target2 = True
                if s in seen_states and step >= p:
                    break
                if step % p == p - 1:
                    seen_states.add(s)
                bit = word[step % p]
                s = next_state[bit][s]
            
            if visited_target2:
                transient_visits += 1
            if len(visited_classes2) == num_classes:
                total_coverage += 1
        
        label = "EXHAUSTIVE" if exhaustive else f"RANDOM({trials})"
        print(f"\n  p={p} [{label}]:")
        print(f"    Target in attractor:     {in_attractor}/{trials} ({in_attractor/trials:.4f})")
        print(f"    Trajectory visits target: {transient_visits}/{trials} ({transient_visits/trials:.4f})")
        print(f"    Full class coverage:      {total_coverage}/{trials} ({total_coverage/trials:.4f})")

def preimage_tree(h):
    """Trace backwards from class-1 state to understand what driving sequences lead there."""
    next_state, class_table, N, num_classes, target, pre0, pre1 = analyze_class1(h, verbose=True)
    
    print(f"\nPreimage tree from state {target} (class 1):")
    current = {target}
    for depth in range(min(h+2, 15)):
        pre = {}
        for s in current:
            p0 = [x for x in range(N) if next_state[0][x] == s]
            p1 = [x for x in range(N) if next_state[1][x] == s]
            pre[s] = (p0, p1)
        new_states = set()
        total_pre = 0
        for s, (p0, p1) in pre.items():
            new_states.update(p0)
            new_states.update(p1)
            total_pre += len(p0) + len(p1)
        
        new_classes = set(class_table[s] for s in new_states)
        print(f"  depth {depth+1}: {len(new_states)} preimage states, {len(new_classes)} classes, "
              f"avg preimage {total_pre/max(len(current),1):.1f}")
        current = new_states
        if len(current) == N:
            print(f"  (full state space reached at depth {depth+1})")
            break

def main():
    print("=" * 70)
    print("CLASS 1 REACHABILITY ANALYSIS")
    print("=" * 70)
    
    # Part 1: Preimage structure for small h
    print("\n--- PART 1: Preimage structure ---")
    for h in range(3, 13):
        analyze_class1(h, verbose=True)
    
    # Part 2: Preimage tree
    print("\n--- PART 2: Preimage tree ---")
    for h in [6, 8, 10, 12]:
        preimage_tree(h)
    
    # Part 3: Attractor membership
    print("\n--- PART 3: Attractor and trajectory analysis ---")
    for h in [6, 8, 10]:
        print(f"\n{'='*50}")
        print(f"h = {h}")
        print(f"{'='*50}")
        check_attractor_membership(h, [4, 8, 12, 16], num_samples=10000)

if __name__ == "__main__":
    main()
