#!/usr/bin/env python3
"""
Coverage check for large horizons using array-based Rule 30 simulation.

The center column bits are generated using a numpy array that grows naturally
with each step. This is O(n) per step (for width n), so O(n^2) total, but
numpy vectorization makes it fast.
"""

from __future__ import annotations

import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--horizon", type=int, required=True)
    parser.add_argument("--max-steps", type=int, default=20_000_000)
    parser.add_argument("--save-bits", type=str, default="",
                        help="Path to save generated bits")
    args = parser.parse_args()

    h = args.horizon
    max_steps = args.max_steps

    print(f"Building quotient maps for h={h}...")
    sys.stdout.flush()
    t0 = time.time()
    q = build_quotient(h)
    t1 = time.time()
    total_classes = max(q.values()) + 1
    print(f"|S_{h}| = {total_classes} classes (built in {t1-t0:.1f}s)")
    sys.stdout.flush()

    print("Building transition tables...")
    sys.stdout.flush()
    next_state, class_table = make_transition_tables(q, h)
    print(f"Table built.")
    sys.stdout.flush()

    # Rule 30 center column using numpy array simulation
    # The row grows by 1 on each side each step. Use a pre-allocated large array.
    width = 2 * max_steps + 3
    center_pos = max_steps + 1
    
    row = np.zeros(width, dtype=np.uint8)
    row[center_pos] = 1
    
    # Pre-allocate a second array for double-buffering
    new_row = np.zeros(width, dtype=np.uint8)
    
    # Trajectory state
    traj_state = 0  # all-zeros h-bit state (encoded as integer)
    visited = set()
    cid = class_table[traj_state]
    visited.add(cid)
    
    t_start = time.time()
    last_report = t_start
    sat_step = None
    
    if args.save_bits:
        bits_buffer = bytearray(max_steps)
        bits_buffer[0] = 1  # first bit is 1
    
    print(f"Starting trajectory (max {max_steps:,d} steps)...")
    sys.stdout.flush()
    
    for t in range(1, max_steps):
        # Rule 30 step using vectorized numpy in the active region
        # Active region grows by 1 each side: [center_pos - t, center_pos + t]
        lo = center_pos - t
        hi = center_pos + t + 1  # exclusive
        
        # Ensure we don't go out of bounds
        lo = max(lo, 1)
        hi = min(hi, width - 1)
        
        # new[i] = row[i-1] ^ (row[i] | row[i+1])
        new_row[lo:hi] = row[lo-1:hi-1] ^ (row[lo:hi] | row[lo+1:hi+1])
        
        # Swap buffers
        row[lo:hi] = new_row[lo:hi]
        # Zero out anything outside active region (shouldn't matter, but be safe)
        
        # Center column bit
        bit = int(row[center_pos])
        
        if args.save_bits:
            bits_buffer[t] = bit
        
        # Advance trajectory
        traj_state = next_state[bit][traj_state]
        cid = class_table[traj_state]
        
        if cid not in visited:
            visited.add(cid)
            if len(visited) == total_classes:
                sat_step = t
                elapsed = time.time() - t_start
                print(f"\nAll {total_classes} classes covered at step {t:,d} "
                      f"(ratio: {t/total_classes:.1f}x) [{elapsed:.1f}s]")
                sys.stdout.flush()
                break
        
        now = time.time()
        if now - last_report >= 30:
            elapsed = now - t_start
            rate = t / elapsed
            remaining = total_classes - len(visited)
            print(f"  t={t:,d}: {len(visited)}/{total_classes} classes "
                  f"({remaining} remaining) [{elapsed:.0f}s, {rate:.0f} steps/s]")
            sys.stdout.flush()
            last_report = now
    
    if sat_step is None:
        remaining = total_classes - len(visited)
        elapsed = time.time() - t_start
        print(f"\nNot converged after {max_steps:,d} steps. "
              f"{len(visited)}/{total_classes} classes ({remaining} remaining) [{elapsed:.1f}s]")
    
    if args.save_bits:
        n_written = (sat_step or max_steps - 1) + 1
        with open(args.save_bits, 'w') as f:
            f.write(''.join(chr(48 + bits_buffer[i]) for i in range(n_written)))
            f.write('\n')
        print(f"Saved {n_written} bits to {args.save_bits}")
    
    print("Done.")


if __name__ == "__main__":
    main()
