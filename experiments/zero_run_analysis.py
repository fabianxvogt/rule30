#!/usr/bin/env python3
"""Analyze zero-runs in center column to understand rarest class first-visit times."""
import sys, os

bits_file = "results/center-column-1000000.txt"
print(f"Loading {bits_file}...")
bits = open(bits_file).read().strip()
print(f"Loaded {len(bits)} bits.")

max_run = 0
max_run_start = 0
current_run = 0
current_run_start = 0

# Find first occurrence of runs of various lengths
first_run_of = {}
targets = set(range(1, 30))

for i, b in enumerate(bits):
    if b == '0':
        if current_run == 0:
            current_run_start = i
        current_run += 1
        if current_run > max_run:
            max_run = current_run
            max_run_start = current_run_start
        for t in list(targets):
            if current_run == t:
                first_run_of[t] = current_run_start
                targets.discard(t)
    else:
        current_run = 0

print(f"\nLongest zero-run: {max_run} starting at position {max_run_start}")
print(f"\nFirst occurrence of zero-run of length L:")
print(f"{'L':>4} | {'run_start':>10} | {'run_end':>10}")
print("-" * 35)
for t in range(1, 30):
    start = first_run_of.get(t, None)
    if start is not None:
        end = start + t - 1
        print(f"{t:>4} | {start:>10} | {end:>10}")
    else:
        print(f"{t:>4} | {'(not found)':>10}")

# Compare against measured saturation steps
print("\n\nComparison with saturation steps:")
print(f"{'h':>4} | {'|S_h|':>6} | {'sat_step':>10} | {'first_h_zero_run':>16} | {'difference':>12}")
print("-" * 60)
sat_data = [
    (16, 517,   104527),
    (17, 733,   203477),
    (18, 971,   429241),
    (19, 1364,  658581),
    (20, 1792,  877606),
]
for h, sh, sat in sat_data:
    run_start = first_run_of.get(h)
    if run_start is not None:
        end = run_start + h - 1
        diff = sat - end
        print(f"{h:>4} | {sh:>6} | {sat:>10} | {end:>16} | {diff:>12}")
    else:
        print(f"{h:>4} | {sh:>6} | {sat:>10} | {'(no h-zero-run)':>16} |")
