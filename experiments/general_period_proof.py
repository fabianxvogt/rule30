"""
Extend the cell-by-cell fixed-point-free proof to:
1. All non-constant period-2 boundaries
2. General period p (for the SAME period: a_1 can't have same period as a_0)
3. Check if a_1 can have period kp (multiples) — does the infinite-system
   argument still give contradictions?
"""

import numpy as np
from itertools import product


def rule30_step(L, C, R):
    """One cell Rule 30 update."""
    return L ^ (C | R)


def trace_fp_symbolically(boundary, n_cells):
    """
    Symbolically (by enumeration) trace what F_p does to the first n_cells,
    as a function of s_0, ..., s_{n_cells + p - 1}.
    
    For each assignment of (s_0, ..., s_{n_cells+p-1}), compute F_p(s)_i for i < n_cells.
    
    p = len(boundary).
    
    Returns: for each input assignment, the output values of cells 0..n_cells-1.
    """
    p = len(boundary)
    # We need s_0 through s_{n_cells + p - 1} to determine cells 0..n_cells-1 after p steps
    n_input = n_cells + p
    
    results = {}  # input_tuple -> output_tuple
    
    for input_val in range(2**n_input):
        s = [(input_val >> i) & 1 for i in range(n_input)]
        
        # Apply p Rule 30 steps
        current = s[:]
        for step in range(p):
            b = boundary[step]
            new = [0] * len(current)
            for i in range(len(current)):
                L = b if i == 0 else current[i-1]
                C = current[i]
                R = current[i+1] if i+1 < len(current) else 0
                new[i] = L ^ (C | R)
            current = new
        
        output = tuple(current[:n_cells])
        input_key = tuple(s[:n_cells])
        extra = tuple(s[n_cells:])
        
        if input_key not in results:
            results[input_key] = {}
        results[input_key][extra] = output
    
    return results


def experiment_all_period2():
    """
    Check all non-constant period-2 boundaries.
    For [1,0] and [0,1]: does the cell-by-cell argument give contradiction?
    """
    print("=== All period-2 boundaries: cell-by-cell analysis ===\n")
    
    for boundary in [[1, 0], [0, 1]]:
        p = len(boundary)
        print(f"Boundary {boundary} (period {p}):")
        
        n_check = 4  # check cells 0..3
        results = trace_fp_symbolically(boundary, n_check)
        
        # Find all (s_0,...,s_{n_check-1}) that are consistent with F_p(s)_i = s_i
        # for all i < n_check across ALL possible extensions (s_{n_check},...,s_{n_check+p-1})
        
        # Actually, for the INFINITE system, F_p(s)_i depends on s_0,...,s_{i+p}.
        # For cell i to be preserved, we need F_p(s)_i = s_i for ALL extensions.
        # Wait no — in the infinite system, the extension IS fixed (it's part of s).
        # F_p(s)_i depends on s_0,...,s_{i+p} only (local dependency for p steps).
        
        # So: for cell i to be preserved, there EXISTS an extension such that
        # F_p(s)_i = s_i. The question is whether ALL cells can be simultaneously
        # preserved.
        
        # Let's enumerate: for each (s_0,s_1,...,s_{n_check+p-1}), check if
        # F_p(s)_i = s_i for i = 0,...,n_check-1.
        
        n_total = n_check + p
        n_consistent = 0
        consistent_inputs = []
        
        for val in range(2**n_total):
            s = [(val >> i) & 1 for i in range(n_total)]
            
            # Apply p Rule 30 steps
            current = s[:]
            for step in range(p):
                b = boundary[step]
                new = [0] * len(current)
                for i in range(len(current)):
                    L = b if i == 0 else current[i-1]
                    C = current[i]
                    R = current[i+1] if i+1 < len(current) else 0
                    new[i] = L ^ (C | R)
                current = new
            
            # Check cells 0..n_check-1
            match = all(current[i] == s[i] for i in range(n_check))
            if match:
                n_consistent += 1
                if n_consistent <= 5:
                    consistent_inputs.append(s[:n_total])
        
        print(f"  Assignments of (s_0,...,s_{n_total-1}) with F_p(s)_i=s_i for i<{n_check}: "
              f"{n_consistent} / {2**n_total}")
        
        if n_consistent == 0:
            print(f"  → PROVED: No fixed point possible (first {n_check} cells give contradiction)")
        else:
            print(f"  → {n_consistent} consistent assignments found:")
            for s in consistent_inputs[:5]:
                print(f"    {''.join(map(str, s))}")
        print()


def experiment_general_period_cell_by_cell():
    """
    For each period p from 1 to 8, and each non-constant boundary,
    check how many cells need to be examined before getting a contradiction.
    """
    print("=== General period: minimum cells for contradiction ===\n")
    
    for p in range(1, 8):
        print(f"Period p={p}:")
        
        for bnd_int in range(2**p):
            boundary = [(bnd_int >> i) & 1 for i in range(p)]
            
            # Skip constant boundaries
            if all(b == boundary[0] for b in boundary):
                print(f"  {boundary}: CONSTANT — skip")
                continue
            
            # Progressively check more cells until contradiction
            found_contradiction = False
            for n_check in range(1, min(20, 2 * p + 4)):
                n_total = n_check + p
                if n_total > 24:  # limit computation
                    break
                
                n_consistent = 0
                for val in range(2**n_total):
                    s = [(val >> i) & 1 for i in range(n_total)]
                    
                    current = s[:]
                    for step in range(p):
                        b = boundary[step]
                        new = [0] * len(current)
                        for i in range(len(current)):
                            L = b if i == 0 else current[i-1]
                            C = current[i]
                            R = current[i+1] if i+1 < len(current) else 0
                            new[i] = L ^ (C | R)
                        current = new
                    
                    match = all(current[i] == s[i] for i in range(n_check))
                    if match:
                        n_consistent += 1
                
                if n_consistent == 0:
                    print(f"  {boundary}: CONTRADICTION at n_check={n_check} "
                          f"(using {n_total} input cells)")
                    found_contradiction = True
                    break
            
            if not found_contradiction:
                # Check with larger n but sampling
                print(f"  {boundary}: no contradiction found with ≤{n_check} cells "
                      f"({n_consistent} consistent)")
        print()


def experiment_fp_n_infinite():
    """
    For F_p^n (n periods, i.e., np steps): does the cell-by-cell argument
    still give a contradiction in the infinite system?
    
    This is whether a_1 can have period np when a_0 has period p.
    
    Apply np Rule 30 steps with boundary cycling through [b_0,...,b_{p-1}]
    n times. Check if cells 0,...,m can all return to original values.
    """
    print("=== F_p^n analysis for infinite system (boundary [1,0]) ===\n")
    
    boundary = [1, 0]
    p = len(boundary)
    
    for n in range(1, 16):
        total_steps = n * p
        
        # For m cells checked, we need m + total_steps input cells
        # (each step extends dependency by 1)
        
        # Start with checking just cell 0, then more
        for m in range(1, 12):
            n_input = m + total_steps
            if n_input > 26:  # computational limit
                break
            
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
                
                match = all(current[i] == s[i] for i in range(m))
                if match:
                    n_consistent += 1
            
            if n_consistent == 0:
                print(f"  n={n:>2} (period {n*p:>2}): contradiction at m={m} "
                      f"({n_input} input cells)")
                break
        else:
            if n_input <= 26:
                print(f"  n={n:>2} (period {n*p:>2}): {n_consistent} consistent "
                      f"assignments with m={m} cells ({n_input} inputs)")
            else:
                print(f"  n={n:>2} (period {n*p:>2}): computation too large "
                      f"(would need {m + total_steps} input cells)")


def experiment_fp_n_for_01():
    """Same as above but for boundary [0,1]."""
    print("\n=== F_p^n analysis for infinite system (boundary [0,1]) ===\n")
    
    boundary = [0, 1]
    p = len(boundary)
    
    for n in range(1, 16):
        total_steps = n * p
        
        for m in range(1, 12):
            n_input = m + total_steps
            if n_input > 26:
                break
            
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
                
                match = all(current[i] == s[i] for i in range(m))
                if match:
                    n_consistent += 1
            
            if n_consistent == 0:
                print(f"  n={n:>2} (period {n*p:>2}): contradiction at m={m} "
                      f"({n_input} input cells)")
                break
        else:
            if n_input <= 26:
                print(f"  n={n:>2} (period {n*p:>2}): {n_consistent} consistent "
                      f"assignments with m={m} cells ({n_input} inputs)")
            else:
                print(f"  n={n:>2} (period {n*p:>2}): computation too large")


if __name__ == "__main__":
    experiment_all_period2()
    experiment_general_period_cell_by_cell()
    experiment_fp_n_infinite()
    experiment_fp_n_for_01()
