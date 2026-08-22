#!/usr/bin/env python3
"""Quick check: f_1 sync for even h (syncs to (0,1,0,1,...)), odd h (doesn't sync to 1 state).
Also check center column run lengths."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import rule30_next_tuple


def build_f1(h):
    N = 1 << h
    f1 = [0] * N
    for s_int in range(N):
        state = tuple((s_int >> i) & 1 for i in range(h))
        ns = rule30_next_tuple(state, 1)[:h]
        f1[s_int] = sum(bit << i for i, bit in enumerate(ns))
    return f1


def sync_info(h):
    N = 1 << h
    f1 = build_f1(h)
    current = set(range(N))
    for step in range(min(500, 10*N)):
        current = set(f1[s] for s in current)
        if len(current) == 1:
            return step + 1, len(current)
    return None, len(current)


def main():
    print("=== f_1 synchronization ===")
    print(f"{'h':>3} {'sync_time':>10} {'final_|img|':>12}")
    for h in range(2, 19):
        t, sz = sync_info(h)
        if t:
            print(f"{h:3d} {t:10d} {1:12d}")
        else:
            print(f"{h:3d} {'---':>10} {sz:12d}")
    
    # For odd h, what's the 2-state attractor?
    print("\n=== Odd h: 2-state attractor of f_1 ===")
    for h in [3, 5, 7, 9, 11, 13, 15]:
        N = 1 << h
        f1 = build_f1(h)
        current = set(range(N))
        for _ in range(500):
            current = set(f1[s] for s in current)
        print(f"  h={h}: attractor = {sorted(current)}")
        for s in sorted(current):
            ns = f1[s]
            state = tuple((s >> i) & 1 for i in range(h))
            ns_state = tuple((ns >> i) & 1 for i in range(h))
            print(f"    {s} -> {ns} : {state} -> {ns_state}")
    
    # Center column run analysis
    print("\n=== Center column max run lengths ===")
    for fname in ["results/center-column-128.txt", 
                   "results/center-column-100000.txt",
                   "results/center-column-1000000.txt",
                   "results/center-column-15000000.txt"]:
        if not os.path.exists(fname):
            continue
        with open(fname) as fp:
            bits = fp.read().strip()
        n = len(bits)
        
        # Find max runs
        max_run = {0: 0, 1: 0}
        run = 1
        for i in range(1, n):
            if bits[i] == bits[i-1]:
                run += 1
            else:
                max_run[int(bits[i-1])] = max(max_run[int(bits[i-1])], run)
                run = 1
        max_run[int(bits[-1])] = max(max_run[int(bits[-1])], run)
        
        print(f"  {fname} ({n} bits):")
        print(f"    Max run of 1s: {max_run[1]}")
        print(f"    Max run of 0s: {max_run[0]}")
        
        # Expected max run ~ log2(n)*2 for fair coin
        import math
        expected = math.log2(n) * 1.5
        print(f"    Expected for random (1.5*log2(n)): {expected:.1f}")


if __name__ == "__main__":
    main()
