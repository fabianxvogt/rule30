#!/usr/bin/env python3
"""
Check coverage of predictive-state classes using the TRUE right-half dynamics.

The true right-half of Rule 30 evolves as:
  a(x, t+1) = a(x-1, t) XOR (a(x, t) OR a(x+1, t))
with a(0, t) = center_column[t] as the left boundary.

We use a large simulation width (e.g., 300) so that the boundary effect at the
right edge doesn't affect the observed h bits for the time range we simulate.

We need width > T + h to be safe (light cone from right boundary can't reach
position 1 in T steps).
"""

from __future__ import annotations

import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--horizon", type=int, default=15)
    parser.add_argument("--max-steps", type=int, default=200000)
    args = parser.parse_args()
    
    h = args.horizon
    max_steps = args.max_steps
    
    # Simulation width: needs to be > max_steps + h
    W = max_steps + h + 10
    
    print(f"Building quotient for h={h}...")
    sys.stdout.flush()
    q = build_quotient(h)
    total_classes = max(q.values()) + 1
    print(f"|S_{h}| = {total_classes}")
    sys.stdout.flush()
    
    # Load center column bits
    bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "results", "center-column-1000000.txt")
    with open(bits_file) as f:
        bits = [int(c) for c in f.read().strip() if c in '01']
    
    max_steps = min(max_steps, len(bits))
    W = max_steps + h + 10
    
    print(f"Using {max_steps} center column bits, simulation width = {W}")
    print(f"Simulating true right-half dynamics...")
    sys.stdout.flush()
    
    # Use numpy for efficiency
    # State array: positions 0 (boundary), 1 through W, W+1 (right padding)
    state = np.zeros(W + 2, dtype=np.uint8)
    
    # Track coverage
    visited = set()
    initial_prefix = tuple(state[1:h+1])
    cid = q.get(initial_prefix)
    if cid is not None:
        visited.add(cid)
    
    t_start = time.time()
    last_report = t_start
    sat_step = None
    
    for t in range(max_steps):
        # Set boundary
        state[0] = bits[t]
        state[W + 1] = 0
        
        # Rule 30 evolution: new[x] = state[x-1] ^ (state[x] | state[x+1])
        new_state = np.zeros(W + 2, dtype=np.uint8)
        # Vectorized for positions 1 through W
        new_state[1:W+1] = state[0:W] ^ (state[1:W+1] | state[2:W+2])
        
        state = new_state
        
        # Observe h-prefix
        prefix = tuple(state[1:h+1])
        cid = q.get(prefix)
        
        if cid is not None and cid not in visited:
            visited.add(cid)
            if len(visited) == total_classes:
                sat_step = t + 1
                elapsed = time.time() - t_start
                print(f"\nAll {total_classes} classes covered at step {sat_step} "
                      f"(ratio: {sat_step/total_classes:.1f}x) [{elapsed:.1f}s]")
                sys.stdout.flush()
                break
        
        now = time.time()
        if now - last_report >= 10:
            elapsed = now - t_start
            rate = (t + 1) / elapsed
            remaining = total_classes - len(visited)
            print(f"  t={t+1}: {len(visited)}/{total_classes} "
                  f"({remaining} remaining) [{elapsed:.0f}s, {rate:.0f} steps/s]")
            sys.stdout.flush()
            last_report = now
    
    if sat_step is None:
        remaining = total_classes - len(visited)
        elapsed = time.time() - t_start
        print(f"\nNot converged after {max_steps} steps. "
              f"{len(visited)}/{total_classes} ({remaining} remaining) [{elapsed:.1f}s]")
    
    print("Done.")


if __name__ == "__main__":
    main()
