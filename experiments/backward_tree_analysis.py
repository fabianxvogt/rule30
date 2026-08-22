#!/usr/bin/env python3
"""
Detailed backward tree analysis from class-1 state.
For each state in the backward tree, show how many preimages under f_0 vs f_1.
Also: what is the REQUIRED driving sequence to reach class 1?
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables

def analyze_backward_tree(h):
    q = build_quotient(h)
    next_state, class_table = make_transition_tables(q, h)
    N = 1 << h
    target = 1 << (h - 1)  # state 0^{h-1}1

    print(f"\n=== h={h}, target state={target} (class {class_table[target]}) ===")

    # Build preimage lookup
    pre = [[[] for _ in range(N)], [[] for _ in range(N)]]
    for bit in range(2):
        for s in range(N):
            pre[bit][next_state[bit][s]].append(s)

    # Trace backward tree and check driving bit constraints
    current_level = {target}
    for depth in range(min(h + 2, 20)):
        # For each state in current level, count preimages under f_0 and f_1
        total_pre0 = 0
        total_pre1 = 0
        only_0 = 0  # states reachable only via f_0
        only_1 = 0  # states reachable only via f_1
        both = 0    # states reachable via both
        neither = 0  # shouldn't happen for reachable states

        next_level = set()
        for s in current_level:
            p0 = pre[0][s]
            p1 = pre[1][s]
            total_pre0 += len(p0)
            total_pre1 += len(p1)
            if p0 and p1:
                both += 1
            elif p0:
                only_0 += 1
            elif p1:
                only_1 += 1
            else:
                neither += 1
            next_level.update(p0)
            next_level.update(p1)

        print(f"  depth {depth}: {len(current_level)} states | "
              f"pre_0={total_pre0}, pre_1={total_pre1} | "
              f"only_0={only_0}, only_1={only_1}, both={both}")

        if len(next_level) == N:
            print(f"  (full space at depth {depth+1})")
            break
        current_level = next_level

    # Now: check for the UNIQUE reaching word
    # For Theorem 11: from any s_0, there's exactly one h-bit word reaching target
    # Let's verify this by counting for all start states how many paths reach target
    print(f"\n  Path counting from s=0 to target in exactly h={h} steps:")
    
    # Forward: from s=0, enumerate all 2^h words and see which reach target
    # For small h only
    if h <= 14:
        s0 = 0
        count = 0
        # Use dynamic programming
        # dp[step][state] = number of paths reaching that state in 'step' steps from s0
        dp_prev = {s0: 1}
        for step in range(h):
            dp_next = {}
            for s, cnt in dp_prev.items():
                for bit in range(2):
                    ns = next_state[bit][s]
                    dp_next[ns] = dp_next.get(ns, 0) + cnt
            dp_prev = dp_next
        
        paths_to_target = dp_prev.get(target, 0)
        print(f"    Paths from s=0 to target in {h} steps: {paths_to_target}")
        print(f"    (Expected: 1 by Universal Bijectivity)")
    
    # Also check: from s=0, what is the MINIMUM number of steps to reach target?
    visited = {0}
    frontier = {0}
    for step in range(1, min(3*h, 60)):
        next_frontier = set()
        for s in frontier:
            for bit in range(2):
                ns = next_state[bit][s]
                if ns not in visited:
                    visited.add(ns)
                    next_frontier.add(ns)
                    if ns == target:
                        print(f"\n  First time target reachable from s=0: step {step}")
        frontier = next_frontier
        if target in visited:
            break
    else:
        if target not in visited:
            print(f"\n  Target NOT reachable from s=0 in {min(3*h, 60)} steps!")

    # The key question: what's the minimum period p such that
    # the periodic trajectory from s=0 visits target?
    # The reaching word must appear as a SUBSTRING of the periodic extension.
    # From Theorem 11, there's exactly 1 word of length h reaching target from s=0.
    # What IS that word?
    if h <= 16:
        # Find the unique h-bit word that takes s=0 to target
        s = 0
        # Try all 2^h words
        reaching_word = None
        for w_int in range(1 << h):
            s = 0
            for i in range(h):
                bit = (w_int >> i) & 1
                s = next_state[bit][s]
            if s == target:
                word_bits = tuple((w_int >> i) & 1 for i in range(h))
                reaching_word = word_bits
                print(f"\n  Unique reaching word from s=0: {''.join(map(str, word_bits))}")
                break
        
        if reaching_word is None:
            print(f"\n  ERROR: No reaching word found!")

def main():
    for h in range(3, 15):
        analyze_backward_tree(h)

if __name__ == "__main__":
    main()
