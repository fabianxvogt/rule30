#!/usr/bin/env python3
"""
Investigate the structure of the rarest (last-visited) classes.

Key question: the "period-3 pattern" classes like 010010010010... are consistently
among the last visited. Why? Is this related to subword frequency in the center column?
"""
from __future__ import annotations

import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient


def count_subword_occurrences(bits, word, max_start=None):
    """Count occurrences of word as a subword starting at positions 0..max_start-1."""
    h = len(word)
    if max_start is None:
        max_start = len(bits) - h + 1
    else:
        max_start = min(max_start, len(bits) - h + 1)
    
    count = 0
    for i in range(max_start):
        if tuple(bits[i:i+h]) == word:
            count += 1
    return count


def main():
    bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "results", "center-column-1000000.txt")
    with open(bits_file) as f:
        bits = [int(c) for c in f.read().strip() if c in '01']
    
    N = len(bits)
    print(f"Loaded {N} center column bits\n")
    
    # For h=18-20, find the rarest classes and check subword frequencies
    for h in [18, 19, 20]:
        q = build_quotient(h)
        total = max(q.values()) + 1
        
        # Build class → tuples mapping
        class_tuples = {}
        for tup, cid in q.items():
            class_tuples.setdefault(cid, []).append(tup)
        
        # Count how many times each length-h subword appears
        # (faster: scan once)
        subword_count = Counter()
        for i in range(N - h + 1):
            w = tuple(bits[i:i+h])
            subword_count[w] += 1
        
        # For each class, find the total frequency of its member tuples as subwords
        class_freq = {}
        for cid, tuples in class_tuples.items():
            freq = sum(subword_count.get(t, 0) for t in tuples)
            class_freq[cid] = freq
        
        # Find classes with zero subword frequency  
        zero_freq = [c for c, f in class_freq.items() if f == 0]
        
        # Sort by frequency
        sorted_by_freq = sorted(class_freq.items(), key=lambda x: x[1])
        
        print(f"h={h}: |S_{h}| = {total}")
        print(f"  Classes with zero subword frequency: {len(zero_freq)}")
        print(f"  Rarest 10 classes by subword frequency:")
        print(f"  {'Class':>6} {'Freq':>8} {'#tuples':>8} {'Example':>30}")
        for cid, freq in sorted_by_freq[:10]:
            tuples = class_tuples[cid]
            example = ''.join(str(b) for b in sorted(tuples)[0])
            print(f"  {cid:>6} {freq:>8} {len(tuples):>8} {example:>30}")
        
        # Compare with trajectory rarest (known from previous analysis)
        print()


if __name__ == "__main__":
    main()
