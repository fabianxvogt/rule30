#!/usr/bin/env python3
"""
Check whether Rule 30 from a single cell has any permanently zero columns
in the interior of the light cone.
"""
import numpy as np

def rule30_evolve(steps):
    """Evolve Rule 30 from single cell for given steps.
    Returns 2D array of the spacetime pattern.
    """
    width = 2 * steps + 3
    center = steps + 1
    grid = np.zeros((steps + 1, width), dtype=np.int8)
    grid[0, center] = 1
    
    for t in range(steps):
        left = np.roll(grid[t], 1)
        right = np.roll(grid[t], -1)
        grid[t+1] = left ^ (grid[t] | right)
        # Zero out edges to prevent wrap-around effects
        grid[t+1, 0] = 0
        grid[t+1, -1] = 0
    
    return grid, center

def check_zero_columns(steps):
    grid, center = rule30_evolve(steps)
    print(f"Rule 30 evolved for {steps} steps")
    print(f"Grid shape: {grid.shape}")
    
    # For each column in the light cone, check the last time it's nonzero
    nonzero_cols = []
    for col in range(grid.shape[1]):
        rel = col - center  # position relative to center
        # Column is in light cone from time |rel| onwards
        first_time = abs(rel)
        if first_time > steps:
            continue
        
        # Check if column is ever nonzero AND then becomes permanently zero
        values = grid[first_time:, col]
        if np.any(values):
            last_nonzero = first_time + np.max(np.where(values > 0))
            still_active = (last_nonzero == steps)
            if not still_active:
                nonzero_cols.append((rel, last_nonzero, steps - last_nonzero))
    
    if nonzero_cols:
        print(f"\nColumns that became permanently zero (within {steps} steps):")
        for rel, last_nz, duration in sorted(nonzero_cols, key=lambda x: x[2], reverse=True)[:20]:
            print(f"  Column {rel:+4d}: last nonzero at t={last_nz}, "
                  f"zero for {duration} steps")
    else:
        print(f"\nNo columns became permanently zero within {steps} steps")
    
    # Check specifically the left-edge property
    print(f"\nLeft edge check (a_{{-t}}(t) for t=1..{min(steps,30)}):")
    for t in range(1, min(steps + 1, 31)):
        val = grid[t, center - t]
        if val != 1:
            print(f"  a_{{-{t}}}({t}) = {val} -- UNEXPECTED!")
    print(f"  All equal to 1 (as expected)")
    
    # Check right edge
    print(f"\nRight edge check (a_{{t}}(t) for t=1..{min(steps,30)}):")
    for t in range(1, min(steps + 1, 31)):
        val = grid[t, center + t]
        if val != 1:
            print(f"  a_{{{t}}}({t}) = {val} -- UNEXPECTED!")
    print(f"  All equal to 1 (as expected)")
    
    # Check for INTERIOR columns that go to zero
    # Look at the left half (columns < center)
    print(f"\nChecking left-half columns that are zero for the last 100 steps:")
    count = 0
    for col in range(center - steps, center):
        rel = col - center
        if steps > 100 and np.all(grid[steps-100:, col] == 0):
            count += 1
    print(f"  {count} left-half columns are zero for last 100 steps")
    
    if steps > 100:
        print(f"\nChecking left-half columns that are zero for last 50 steps:")
        count = 0
        examples = []
        for col in range(center - steps, center):
            rel = col - center
            if np.all(grid[steps-50:, col] == 0):
                count += 1
                if len(examples) < 5:
                    examples.append(rel)
        print(f"  {count} left-half columns are zero for last 50 steps")
        if examples:
            print(f"  Examples: {examples}")

# Run for various sizes
for steps in [100, 500, 1000]:
    check_zero_columns(steps)
    print()
