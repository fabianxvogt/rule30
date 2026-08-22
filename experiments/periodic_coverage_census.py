#!/usr/bin/env python3
"""
For small h: exactly characterize which periodic driving sequences achieve 
full class coverage, and which fail.

For h=5 (35 classes), enumerate all periodic sequences of period p <= 100
and check which achieve coverage.
"""
from __future__ import annotations
import os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables


def check_coverage(next_state, class_table, total_classes, period_bits, max_steps=None):
    """Check if periodic sequence of given bits achieves full class coverage."""
    p = len(period_bits)
    if max_steps is None:
        max_steps = total_classes * p * 10  # give it enough time
    
    state = 0
    visited = set()
    
    for t in range(max_steps):
        visited.add(class_table[state])
        if len(visited) == total_classes:
            return True, t
        state = next_state[period_bits[t % p]][state]
    
    return False, len(visited)


def main():
    for h in [5, 8]:
        print(f"\n=== h={h} ===")
        q = build_quotient(h)
        total_classes = max(q.values()) + 1
        next_state, class_table = make_transition_tables(q, h)
        
        print(f"  |S_{h}| = {total_classes}")
        
        # For each period p, count how many of the 2^p sequences achieve coverage
        for p in range(1, min(25 if h == 5 else 20, 25)):
            success = 0
            total = 1 << p
            
            if total > 100000:
                # Sample
                import random
                random.seed(42)
                total = 1000
                for _ in range(total):
                    bits = [random.randint(0, 1) for _ in range(p)]
                    ok, info = check_coverage(next_state, class_table, total_classes, bits)
                    if ok:
                        success += 1
            else:
                for mask in range(1 << p):
                    bits = [(mask >> i) & 1 for i in range(p)]
                    ok, info = check_coverage(next_state, class_table, total_classes, bits)
                    if ok:
                        success += 1
            
            frac = success / total
            print(f"  p={p:3d}: {success}/{total} achieve coverage ({100*frac:.1f}%)")
        
        # Also: characterize failing sequences for small p
        if h == 5:
            print(f"\n  Failing period-8 sequences for h=5:")
            for mask in range(1 << 8):
                bits = [(mask >> i) & 1 for i in range(8)]
                ok, info = check_coverage(next_state, class_table, total_classes, bits)
                if not ok:
                    bit_str = ''.join(str(b) for b in bits)
                    print(f"    {bit_str}: visited {info}/{total_classes}")


if __name__ == "__main__":
    main()
