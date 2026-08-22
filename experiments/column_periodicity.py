#!/usr/bin/env python3
"""
Check the temporal periodicity of right-half columns in Rule 30 from a single cell.
"""
import numpy as np

def rule30_evolve(steps):
    width = 2 * steps + 3
    center = steps + 1
    grid = np.zeros((steps + 1, width), dtype=np.int8)
    grid[0, center] = 1
    for t in range(steps):
        left = np.roll(grid[t], 1)
        right = np.roll(grid[t], -1)
        grid[t+1] = left ^ (grid[t] | right)
        grid[t+1, 0] = 0
        grid[t+1, -1] = 0
    return grid, center

steps = 2000
grid, center = rule30_evolve(steps)

# Check columns 1, 2, 3, ..., 10 to the right of center
# For each column, check if it becomes periodic
print("Right-half column periodicity analysis (Rule 30 from single cell)")
print("=" * 70)

for col_offset in range(1, 20):
    col = center + col_offset
    # Extract the column values after the light cone arrives
    start = col_offset + 10  # start a bit after light cone
    values = grid[start:, col]
    
    # Check for periodicity
    found_period = None
    for p in range(1, min(501, len(values) // 3)):
        # Check if values[i] == values[i+p] for all i in range
        check_len = min(1000, len(values) - p)
        if np.all(values[:check_len] == values[p:p+check_len]):
            found_period = p
            break
    
    if found_period:
        print(f"Column +{col_offset}: period = {found_period} "
              f"(verified over {check_len} steps, starting at t={start})")
        # Show first period
        if found_period <= 20:
            period_vals = ''.join(map(str, values[:found_period]))
            print(f"         pattern: {period_vals}")
    else:
        # Show stats
        print(f"Column +{col_offset}: no period ≤ 500 found "
              f"(checked from t={start})")

# Also show the center column
print(f"\nCenter column (col 0):")
values = grid[1:, center]
found_period = None
for p in range(1, min(501, len(values) // 3)):
    check_len = min(1000, len(values) - p)
    if np.all(values[:check_len] == values[p:p+check_len]):
        found_period = p
        break
if found_period:
    print(f"  period = {found_period}")
else:
    print(f"  no period ≤ 500 found")

# Column -1 (one to the left)
print(f"\nLeft columns:")
for col_offset in range(1, 20):
    col = center - col_offset
    start = col_offset + 10
    values = grid[start:, col]
    found_period = None
    for p in range(1, min(501, len(values) // 3)):
        check_len = min(1000, len(values) - p)
        if np.all(values[:check_len] == values[p:p+check_len]):
            found_period = p
            break
    if found_period:
        print(f"Column -{col_offset}: period = {found_period} "
              f"(verified over {check_len} steps)")
        if found_period <= 20:
            period_vals = ''.join(map(str, values[:found_period]))
            print(f"         pattern: {period_vals}")
    else:
        print(f"Column -{col_offset}: no period ≤ 500 found")
