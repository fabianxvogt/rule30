#!/usr/bin/env python3
"""
The constant-1 input is a SYNCHRONIZING WORD: Attractor(f_1) = {single state}.

This means: repeatedly applying f_1 (boundary bit = 1) sends ALL states to a 
single fixed point (or cycle of length 1).

Verify this and measure the sync time (how many steps of all-1 input to synchronize).
Then: if the center column contains a run of k consecutive 1s, the system synchronized
to within a small set after those k steps.

After synchronization, the next h bits determine the state uniquely (by Universal Bijectivity).
So: if the center column contains ALL (h+k)-bit substrings starting with 1^k, the system 
visits all 2^h states.

Check: what is the synchronization time for f_1?
Check: does the center column have long runs of 1s?
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import rule30_next_tuple


def build_maps(h):
    N = 1 << h
    f = [dict(), dict()]
    for b in range(2):
        for s_int in range(N):
            state = tuple((s_int >> i) & 1 for i in range(h))
            ns = rule30_next_tuple(state, b)[:h]
            ns_int = sum(bit << i for i, bit in enumerate(ns))
            f[b][s_int] = ns_int
    return f


def apply_map(f_b, state_set):
    return frozenset(f_b[s] for s in state_set)


def sync_time_f1(h, f):
    """How many applications of f_1 to go from all 2^h states to 1 state?"""
    N = 1 << h
    current = frozenset(range(N))
    for step in range(10*N):
        current = apply_map(f[1], current)
        if len(current) == 1:
            return step + 1, next(iter(current))
    return None, None


def sync_profile_f1(h, f, max_steps=200):
    """Track |image of f_1^k| as function of k."""
    N = 1 << h
    current = frozenset(range(N))
    profile = [(0, N)]
    for step in range(1, max_steps+1):
        current = apply_map(f[1], current)
        profile.append((step, len(current)))
        if len(current) == 1:
            break
    return profile


def check_center_column_runs(bit_file, max_bits=None):
    """Check maximum run lengths of 0s and 1s in the center column."""
    with open(bit_file, 'r') as fp:
        bits = fp.read().strip()
    if max_bits:
        bits = bits[:max_bits]
    
    n = len(bits)
    max_run_1 = 0
    max_run_0 = 0
    current_run = 1
    
    for i in range(1, n):
        if bits[i] == bits[i-1]:
            current_run += 1
        else:
            if bits[i-1] == '1':
                max_run_1 = max(max_run_1, current_run)
            else:
                max_run_0 = max(max_run_0, current_run)
            current_run = 1
    
    # Handle last run
    if bits[-1] == '1':
        max_run_1 = max(max_run_1, current_run)
    else:
        max_run_0 = max(max_run_0, current_run)
    
    return max_run_1, max_run_0, n


def check_center_column_run_distribution(bit_file, max_bits=None):
    """Count runs of each length for 0s and 1s."""
    with open(bit_file, 'r') as fp:
        bits = fp.read().strip()
    if max_bits:
        bits = bits[:max_bits]
    
    n = len(bits)
    runs_0 = {}  # length -> count
    runs_1 = {}
    
    current_bit = bits[0]
    current_run = 1
    
    for i in range(1, n):
        if bits[i] == current_bit:
            current_run += 1
        else:
            if current_bit == '1':
                runs_1[current_run] = runs_1.get(current_run, 0) + 1
            else:
                runs_0[current_run] = runs_0.get(current_run, 0) + 1
            current_bit = bits[i]
            current_run = 1
    
    # Handle last run
    if current_bit == '1':
        runs_1[current_run] = runs_1.get(current_run, 0) + 1
    else:
        runs_0[current_run] = runs_0.get(current_run, 0) + 1
    
    return runs_0, runs_1, n


def main():
    print("=" * 60)
    print("SYNCHRONIZATION VIA CONSTANT-1 INPUT")
    print("=" * 60)
    
    for h in range(2, 21):
        f = build_maps(h)
        t, fixed = sync_time_f1(h, f)
        if t is not None:
            state = tuple((fixed >> i) & 1 for i in range(h))
            print(f"  h={h:2d}: sync time = {t:5d}, fixed point = {fixed} = {state[:min(8,h)]}...")
        else:
            print(f"  h={h:2d}: NO sync in 10N steps!")
    
    print("\n" + "=" * 60)
    print("SYNC PROFILE (image size as function of #steps)")
    print("=" * 60)
    
    for h in [10, 15, 18, 20]:
        print(f"\n  h={h}, N={1<<h}:")
        f = build_maps(h)
        profile = sync_profile_f1(h, f, max_steps=min(500, 5*(1<<h)))
        for step, size in profile:
            if step <= 5 or step % (h//2) == 0 or size <= 5 or step == len(profile)-1:
                print(f"    step {step:4d}: |image| = {size}")
    
    print("\n" + "=" * 60)
    print("CENTER COLUMN RUN ANALYSIS")
    print("=" * 60)
    
    bit_files = [
        ("results/center-column-128.txt", None),
        ("results/center-column-100000.txt", None),
        ("results/center-column-1000000.txt", None),
    ]
    
    # Check if 15M file exists
    if os.path.exists("results/center-column-15000000.txt"):
        bit_files.append(("results/center-column-15000000.txt", None))
    
    for fname, maxb in bit_files:
        if not os.path.exists(fname):
            continue
        max1, max0, n = check_center_column_runs(fname, maxb)
        print(f"\n  {fname} ({n} bits):")
        print(f"    Max run of 1s: {max1}")
        print(f"    Max run of 0s: {max0}")
        
        runs0, runs1, _ = check_center_column_run_distribution(fname, maxb)
        
        print(f"    Run distribution for 1s:")
        for length in sorted(runs1.keys()):
            if length <= 10 or runs1[length] <= 5:
                print(f"      length {length}: {runs1[length]} occurrences")
        
        print(f"    Run distribution for 0s:")
        for length in sorted(runs0.keys()):
            if length <= 10 or runs0[length] <= 5:
                print(f"      length {length}: {runs0[length]} occurrences")


if __name__ == "__main__":
    main()
