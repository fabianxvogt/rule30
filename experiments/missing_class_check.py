#!/usr/bin/env python3
"""
Quick check: which class is missing when starting from a non-zero state?
"""
from __future__ import annotations

import os
import sys
import random

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables


def main():
    h = 15
    
    bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "results", "center-column-1000000.txt")
    with open(bits_file) as f:
        bits = [int(c) for c in f.read().strip() if c in '01']
    
    q = build_quotient(h)
    total_classes = max(q.values()) + 1
    trans, cls_of = make_transition_tables(q, h)
    
    n = 1 << h
    
    # Class of all-zeros
    zeros_class = cls_of[0]
    print(f"Class of all-zeros state: {zeros_class}")
    
    # Try several starting states and find missing class
    random.seed(42)
    missing_classes = set()
    
    for _ in range(50):
        start = random.randint(1, n - 2)  # avoid 0 and all-1s
        current = start
        visited = set()
        visited.add(cls_of[current])
        for t in range(len(bits)):
            current = trans[bits[t]][current]
            visited.add(cls_of[current])
        
        all_classes = set(range(total_classes))
        missing = all_classes - visited
        if missing:
            missing_classes.update(missing)
            if len(missing_classes) <= 5:
                for c in missing:
                    # Find example state in this class
                    for tup, cid in q.items():
                        if cid == c:
                            print(f"  Missing class {c}: example state {''.join(str(b) for b in tup)}")
                            break
    
    print(f"\nAll missing classes across 50 random starts: {sorted(missing_classes)}")
    
    # Check: what is class 0?
    for tup, cid in q.items():
        if cid == zeros_class:
            print(f"All-zeros class ({zeros_class}): state {''.join(str(b) for b in tup)}")
            break
    
    # Deep check: from all-zeros start, at what step does the missing class first appear?
    if missing_classes:
        mc = min(missing_classes)
        current = 0
        for t in range(len(bits)):
            current = trans[bits[t]][current]
            if cls_of[current] == mc:
                print(f"\nClass {mc} first visited from all-zeros at step {t+1}")
                break
    
    # Check: from all-zeros with 0-indexed start
    print(f"\nh=15: from all-zeros, classes visited = {total_classes}")
    
    # Try starting from the state (1, 0, ..., 0)
    start_10 = 1  # LSB encoding: bit 0 = 1
    current = start_10
    visited = set()
    visited.add(cls_of[current])
    for t in range(len(bits)):
        current = trans[bits[t]][current]
        visited.add(cls_of[current])
    
    missing = set(range(total_classes)) - visited
    print(f"From state (1, 0, ...0): {len(visited)}/{total_classes}, missing: {sorted(missing)}")
    
    # Also for h=10 (smaller, maybe all start points work?)
    for h in [5, 8, 10, 12]:
        q2 = build_quotient(h)
        tc = max(q2.values()) + 1
        trans2, cls2 = make_transition_tables(q2, h)
        n2 = 1 << h
        
        all_cover = 0
        partial = 0
        for start in range(min(n2, 500)):
            current = start
            visited = set()
            visited.add(cls2[current])
            for t in range(min(200000, len(bits))):
                current = trans2[bits[t]][current]
                visited.add(cls2[current])
            if len(visited) == tc:
                all_cover += 1
            else:
                partial += 1
        
        print(f"h={h}: |S_{h}|={tc}, tested {min(n2, 500)} starts: {all_cover} full, {partial} partial")


if __name__ == "__main__":
    main()
