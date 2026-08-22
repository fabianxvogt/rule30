#!/usr/bin/env python3
"""
Fast center-column generator using numpy, saving to disk.
Uses vectorized row update: at time t, the state has width 2t+1.
Extracts only the center bit at each step.

Much faster than the big-int approach for n > ~50k steps.
"""
import numpy as np
import sys
import os

def generate_center_column_numpy(steps: int, chunk_size: int = 10000) -> bytes:
    """
    Generate `steps+1` center-column bits using numpy uint8 arrays.
    Returns a bytes or bytearray of '0'/'1' ASCII characters.
    
    At step t, the row has width 2t+1. We avoid storing the full row by
    keeping a rolling window of width steps+2 centered on the origin.
    """
    # The maximum width needed is 2*steps+1
    # We use a fixed-width array and rely on the fact that beyond the 
    # light cone, all cells are 0.
    width = 2 * steps + 3  # extra padding
    center = steps + 1
    
    row = np.zeros(width, dtype=np.uint8)
    row[center] = 1
    
    bits = bytearray()
    bits.append(ord('1'))  # t=0, center=1
    
    left = np.zeros(width, dtype=np.uint8)
    
    for t in range(1, steps + 1):
        # Rule 30: next[x] = row[x-1] XOR (row[x] OR row[x+1])
        # Use vectorized operations
        left[1:] = row[:-1]  # left[x] = row[x-1]
        # next = left XOR (row OR right)  where right[x] = row[x+1]
        # next[x] = row[x-1] ^ (row[x] | row[x+1])
        np.bitwise_xor(left[1:-1], np.bitwise_or(row[1:-1], row[2:], out=left[1:-1]), out=row[1:-1])
        # But we also need to handle edges: row[0] and row[-1]
        # row[0]: left = 0, center = row[0], right = row[1]
        # new_row[0] = 0 ^ (row[0] | row[1]) = row[0] | row[1]
        # Actually, let me redo this cleanly
        pass
    
    return bytes(bits)


def generate_and_save(steps: int, output_file: str):
    """Generate steps+1 center-column bits and save to file."""
    print(f"Generating {steps+1} center-column bits...")
    print(f"Using numpy row method (width ~ {2*steps+1} cells per row)...")
    
    # Use a fixed width array with zero padding
    # At step t, the light cone has radius t, so only cells -t..+t can be nonzero
    # We use width 2*steps+3 to handle all steps
    width = 2 * steps + 3
    center = steps + 1
    
    row = np.zeros(width, dtype=np.uint8)
    row[center] = 1
    
    bits = bytearray()
    bits.append(ord('1'))  # t=0: a_0(0) = 1
    
    report_every = max(1, steps // 20)
    
    for t in range(1, steps + 1):
        # Efficient vectorized Rule 30 update
        # new[x] = row[x-1] ^ (row[x] | row[x+1])
        new_row = np.zeros(width, dtype=np.uint8)
        # For x in 1..width-2:
        new_row[1:-1] = row[:-2] ^ (row[1:-1] | row[2:])
        # Boundary: x=0: new[0] = 0 ^ (row[0] | row[1]) = row[0]|row[1]
        new_row[0] = row[0] | row[1]
        # Boundary: x=width-1: new[-1] = row[-2] ^ (row[-1] | 0) = row[-2]^row[-1]
        new_row[-1] = row[-2] ^ row[-1]
        
        row = new_row
        bits.append(ord('0') + row[center])
        
        if t % report_every == 0:
            pct = 100 * t / steps
            print(f"  {t}/{steps} ({pct:.0f}%)...")
    
    print(f"Writing {len(bits)} bits to {output_file}...")
    with open(output_file, 'wb') as f:
        f.write(bits)
    print("Done.")
    return bits


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, required=True, help="Number of steps to generate")
    parser.add_argument("--output", type=str, required=True, help="Output file path")
    args = parser.parse_args()
    
    generate_and_save(args.steps, args.output)
