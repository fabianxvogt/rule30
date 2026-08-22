#!/usr/bin/env python3
"""
Analyze the right-edge structure of Rule 30 from single cell.
Check the rightmost few columns (relative to the light cone edge).
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

steps = 200
grid, center = rule30_evolve(steps)

# Show the rightmost few cells at each time step (the "right edge" pattern)
print("Right edge pattern (columns t, t-1, t-2, t-3, ... at time t):")
print("Time  | edge-0  edge-1  edge-2  edge-3  edge-4  edge-5  edge-6  edge-7")
for t in range(1, 50):
    vals = []
    for d in range(8):
        if t - d >= 0:
            vals.append(grid[t, center + t - d])
        else:
            vals.append(-1)
    vstr = "  ".join(f"  {v:5d}" for v in vals)
    print(f"  {t:3d}  |{vstr}")

# Check if the diagonal column a_{t-d}(t) is eventually periodic for small d
print("\n\nDiagonal periodicity (a_{t-d}(t) for fixed d):")
for d in range(10):
    diag = [grid[t, center + t - d] for t in range(max(d+1, 1), steps+1)]
    diag_str = ''.join(map(str, diag[:80]))
    # Check for periodicity
    found_period = None
    for p in range(1, min(101, len(diag) // 3)):
        if all(diag[i] == diag[i+p] for i in range(min(100, len(diag) - p))):
            found_period = p
            break
    if found_period:
        print(f"  d={d}: period={found_period}, {diag_str[:40]}...")
    else:
        print(f"  d={d}: no period ≤ 100, {diag_str[:40]}...")

# Also check left edge
print("\n\nLeft edge pattern (columns -t, -t+1, -t+2, ... at time t):")
print("Time  | edge-0  edge-1  edge-2  edge-3  edge-4  edge-5  edge-6  edge-7")
for t in range(1, 50):
    vals = []
    for d in range(8):
        if t - d >= 0:
            vals.append(grid[t, center - t + d])
        else:
            vals.append(-1)
    vstr = "  ".join(f"  {v:5d}" for v in vals)
    print(f"  {t:3d}  |{vstr}")

print("\n\nLeft diagonal periodicity (a_{-(t-d)}(t) for fixed d):")
for d in range(10):
    diag = [grid[t, center - t + d] for t in range(max(d+1, 1), steps+1)]
    diag_str = ''.join(map(str, diag[:80]))
    found_period = None
    for p in range(1, min(101, len(diag) // 3)):
        if all(diag[i] == diag[i+p] for i in range(min(100, len(diag) - p))):
            found_period = p
            break
    if found_period:
        print(f"  d={d}: period={found_period}, {diag_str[:40]}...")
    else:
        print(f"  d={d}: no period ≤ 100, {diag_str[:40]}...")
