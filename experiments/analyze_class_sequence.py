#!/usr/bin/env python3
"""
Analyze the predictive-state class-count sequence for recurrences and patterns.
"""

from __future__ import annotations

seq = [1, 2, 3, 5, 7, 11, 16, 25, 35, 52, 71, 104, 141, 203, 272, 387, 517, 733, 971, 1364, 1792]

print("Sequence:", seq)
diffs = [seq[i] - seq[i - 1] for i in range(1, len(seq))]
print("First differences:", diffs)

# Split by parity of h
odd_h_terms = seq[1::2]   # h=1,3,5,7,9,11,13,15,17,19
even_h_terms = seq[0::2]  # h=0,2,4,6,8,10,12,14,16,18,20
print("Odd-h  subsequence (h=1,3,5,...): ", odd_h_terms)
print("Even-h subsequence (h=0,2,4,...): ", even_h_terms)

print()
print("=== k=2 recurrences ===")
for c1 in range(-5, 6):
    for c2 in range(-5, 6):
        ok = all(c1 * seq[i - 1] + c2 * seq[i - 2] == seq[i] for i in range(2, len(seq)))
        if ok:
            print(f"  a(n) = {c1}*a(n-1) + {c2}*a(n-2)")

print()
print("=== k=3 recurrences ===")
for c1 in range(-3, 4):
    for c2 in range(-3, 4):
        for c3 in range(-3, 4):
            ok = all(c1 * seq[i - 1] + c2 * seq[i - 2] + c3 * seq[i - 3] == seq[i]
                     for i in range(3, len(seq)))
            if ok:
                print(f"  a(n) = {c1}*a(n-1) + {c2}*a(n-2) + {c3}*a(n-3)")

print()
print("=== k=4 recurrences ===")
for c1 in range(-3, 4):
    for c2 in range(-3, 4):
        for c3 in range(-3, 4):
            for c4 in range(-3, 4):
                ok = all(c1 * seq[i - 1] + c2 * seq[i - 2] + c3 * seq[i - 3] + c4 * seq[i - 4] == seq[i]
                         for i in range(4, len(seq)))
                if ok:
                    print(f"  a(n) = {c1}*a(n-1) + {c2}*a(n-2) + {c3}*a(n-3) + {c4}*a(n-4)")

print()
print("=== Even-h subsequence recurrences ===")
ev = even_h_terms
print("  Even-h terms:", ev)
for c1 in range(-5, 6):
    for c2 in range(-5, 6):
        ok = all(c1 * ev[i - 1] + c2 * ev[i - 2] == ev[i] for i in range(2, len(ev)))
        if ok:
            print(f"  ev(n) = {c1}*ev(n-1) + {c2}*ev(n-2)")
for c1 in range(-3, 4):
    for c2 in range(-3, 4):
        for c3 in range(-3, 4):
            ok = all(c1 * ev[i - 1] + c2 * ev[i - 2] + c3 * ev[i - 3] == ev[i]
                     for i in range(3, len(ev)))
            if ok:
                print(f"  ev(n) = {c1}*ev(n-1) + {c2}*ev(n-2) + {c3}*ev(n-3)")

print()
print("=== Odd-h subsequence recurrences ===")
od = odd_h_terms
print("  Odd-h terms:", od)
for c1 in range(-5, 6):
    for c2 in range(-5, 6):
        ok = all(c1 * od[i - 1] + c2 * od[i - 2] == od[i] for i in range(2, len(od)))
        if ok:
            print(f"  od(n) = {c1}*od(n-1) + {c2}*od(n-2)")
for c1 in range(-3, 4):
    for c2 in range(-3, 4):
        for c3 in range(-3, 4):
            ok = all(c1 * od[i - 1] + c2 * od[i - 2] + c3 * od[i - 3] == od[i]
                     for i in range(3, len(od)))
            if ok:
                print(f"  od(n) = {c1}*od(n-1) + {c2}*od(n-2) + {c3}*od(n-3)")

print()
print("=== a(n) - a(n-2) differences (stride-2 differences) ===")
stride2 = [seq[i] - seq[i - 2] for i in range(2, len(seq))]
print(stride2)

print()
print("=== Ratios a(n)/a(n-2) ===")
for i in range(2, len(seq)):
    print(f"  h={i}: {seq[i]/seq[i-2]:.6f}")

print()
print("=== Dominant growth rate analysis ===")
import math
for i in range(4, len(seq)):
    rate = seq[i] / seq[i - 1]
    lograte = math.log(seq[i] / seq[i - 2]) / 2  # log per step from stride-2
    print(f"  h={i}: ratio={rate:.6f}  log_rate_per_2_steps={lograte:.6f}  "
          f"implied_base_per_step={math.exp(lograte):.6f}")
