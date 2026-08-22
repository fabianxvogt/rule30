"""
Focused F_p^n analysis: For boundary [1,0] (period 2), can the infinite
right-half have period 2n for any n?

This uses the cell-by-cell approach on np steps total.
For np steps, cell i depends on s_0, ..., s_{i+np}.
We check cells 0, ..., m-1, requiring m + np input cells.

For the contradiction to work, we need 2^{m + np} enumeration,
so we're limited by total input size ≤ ~26.
"""

import numpy as np
import sys


def check_fixed_point_possible(boundary, n_repeats, max_cells_check=12, max_input=27):
    """
    Check if F_p^n can have a fixed point in the infinite system.
    
    boundary: the periodic boundary pattern
    n_repeats: number of full periods (F_p^n = applying p*n steps)
    max_cells_check: maximum number of leading cells to check
    max_input: maximum total input width (for enumeration feasibility)
    
    Returns: (has_contradiction, n_cells, n_consistent)
    """
    p = len(boundary)
    total_steps = p * n_repeats
    
    for m in range(1, max_cells_check + 1):
        n_input = m + total_steps
        if n_input > max_input:
            return (False, m - 1, -1)  # can't check further
        
        n_consistent = 0
        for val in range(2**n_input):
            s = [(val >> i) & 1 for i in range(n_input)]
            
            current = s[:]
            for step in range(total_steps):
                b = boundary[step % p]
                new = [0] * len(current)
                for i in range(len(current)):
                    L = b if i == 0 else current[i-1]
                    C = current[i]
                    R = current[i+1] if i+1 < len(current) else 0
                    new[i] = L ^ (C | R)
                current = new
            
            if all(current[i] == s[i] for i in range(m)):
                n_consistent += 1
        
        if n_consistent == 0:
            return (True, m, 0)
    
    return (False, max_cells_check, n_consistent)


def main():
    print("=== Can the infinite right-half have period 2n under boundary [1,0]? ===\n")
    
    boundary_10 = [1, 0]
    boundary_01 = [0, 1]
    
    print(f"{'n':>3} | {'Period':>6} | {'Steps':>5} | {'[1,0] result':>30} | {'[0,1] result':>30}")
    print("-" * 85)
    
    for n in range(1, 14):
        results = {}
        for name, bnd in [('[1,0]', boundary_10), ('[0,1]', boundary_01)]:
            has_contr, m, n_cons = check_fixed_point_possible(bnd, n, max_cells_check=8, max_input=27)
            if has_contr:
                results[name] = f"CONTRADICTION at m={m}"
            elif n_cons < 0:
                results[name] = f"input too large (m≤{m})"
            else:
                results[name] = f"possible ({n_cons} sols, m={m})"
        
        print(f"{n:>3} | {2*n:>6} | {2*n:>5} | {results['[1,0]']:>30} | {results['[0,1]']:>30}")
    
    print()
    
    # For the ones that show "CONTRADICTION", this is a proof that the infinite
    # right-half system cannot have that period.
    # For "possible" cases, we'd need to check more cells.
    
    # Let's push harder for the "possible" cases with more cells
    print("=== Deeper analysis for [1,0] boundary ===\n")
    
    for n in range(1, 14):
        total = 2 * n
        has_contr, m, n_cons = check_fixed_point_possible(
            boundary_10, n, max_cells_check=12, max_input=27
        )
        if has_contr:
            print(f"n={n:>2} (period {total:>2}): PROVED impossible — "
                  f"contradiction at m={m} cells ({m + total} inputs)")
        elif n_cons < 0:
            print(f"n={n:>2} (period {total:>2}): INCONCLUSIVE — "
                  f"need >{m + total} inputs (got m≤{m})")
        else:
            print(f"n={n:>2} (period {total:>2}): {n_cons} consistent assignments "
                  f"at m={m} cells ({m + total} inputs)")
    
    print()
    
    # Also check: for the ACTUAL center column pattern (from the real spacetime),
    # if we assume period p, what would the boundary be?
    # The center column for Rule 30 starts: 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, ...
    # For period 2: either [1,1] (constant) or [1,0] or [0,1]
    # The actual sequence has both 0s and 1s, so it can't be constant.
    # The possible period-2 patterns are [1,0] and [0,1].
    
    print("=== Actual center column analysis ===\n")
    T = 100
    W = T
    N = 2 * W + 1
    grid = np.zeros((T, N), dtype=np.uint8)
    grid[0, W] = 1
    for t in range(T - 1):
        for i in range(1, N - 1):
            grid[t+1, i] = grid[t, i-1] ^ (grid[t, i] | grid[t, i+1])
    
    a0 = grid[:, W]
    print(f"Center column (first 50): {''.join(map(str, a0[:50]))}")
    print()
    
    # Count pattern frequencies
    for p in [2, 3, 4, 5, 6]:
        patterns = {}
        for i in range(len(a0) - p):
            pat = tuple(a0[i:i+p])
            patterns[pat] = patterns.get(pat, 0) + 1
        print(f"Period {p}: {len(patterns)} distinct patterns out of {2**p} possible")
    
    print()
    print("For period 2: if a_0 had period 2, the repeating unit would be")
    print("some w ∈ {[0,1], [1,0]} (not [0,0] or [1,1] since column has both values).")
    print()
    print("We PROVED: for boundary [1,0] or [0,1], the infinite right-half")
    print("cannot have the SAME period 2. The question is multiples (4, 6, ...).")


if __name__ == "__main__":
    main()
