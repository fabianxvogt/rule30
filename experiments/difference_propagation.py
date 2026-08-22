"""
Difference propagation experiment.

Given that c(t) = a_0(t) is periodic with period p, simulate the right half
a_1(t), a_2(t), ... driven by this periodic boundary, and compute the difference
field d_x(t) = a_x(t+p) - a_x(t) (mod 2).

If d_0 = 0 (by assumption), what happens to d_1, d_2, ...?

We use width-K truncations for various K and observe how the difference field
behaves.
"""

import numpy as np

def simulate_right_half(boundary, K, T):
    """
    Simulate the right half (columns 1..K) driven by boundary sequence a_0(t).
    
    Rule 30: a(x, t+1) = a(x-1, t) XOR (a(x, t) OR a(x+1, t))
    
    Here x=0 is the boundary (given), x=1..K are internal, x=K+1 = 0 (padding).
    
    Returns: grid[t][x] for t=0..T-1, x=0..K (x=0 is boundary)
    """
    grid = np.zeros((T, K+1), dtype=np.uint8)
    # Set boundary
    for t in range(T):
        grid[t, 0] = boundary[t % len(boundary)] if t < T else 0
    
    # Internal cells start at 0
    for t in range(T - 1):
        for x in range(1, K + 1):
            left = grid[t, x - 1]
            center = grid[t, x]
            right = grid[t, x + 1] if x + 1 <= K else 0
            grid[t + 1, x] = left ^ (center | right)
        # Boundary is already set
    
    return grid


def compute_difference_field(grid, p):
    """Compute d_x(t) = grid[t+p, x] XOR grid[t, x] for t+p < T."""
    T, W = grid.shape
    T_eff = T - p
    d = np.zeros((T_eff, W), dtype=np.uint8)
    for t in range(T_eff):
        d[t] = grid[t + p] ^ grid[t]
    return d


def analyze_difference(boundary_bits, p, K_values, T):
    """Analyze difference propagation for given periodic boundary."""
    boundary = boundary_bits  # one period
    
    print(f"\nBoundary period p={p}, pattern={boundary_bits}")
    print(f"Simulation length T={T}")
    print()
    
    for K in K_values:
        grid = simulate_right_half(boundary, K, T)
        d = compute_difference_field(grid, p)
        T_eff = d.shape[0]
        
        # Check d_0 should be 0 (boundary is periodic with period p)
        d0_nonzero = np.count_nonzero(d[:, 0])
        
        # For each column x, count number of times d_x != 0
        col_activity = []
        for x in range(min(K + 1, 30)):  # check first 30 columns
            nonzero_count = np.count_nonzero(d[:, x])
            col_activity.append(nonzero_count)
        
        # First time d_1 becomes nonzero
        d1_first = -1
        for t in range(T_eff):
            if d[t, 1] != 0:
                d1_first = t
                break
        
        # Check: does d ever become all-zero (after being nonzero)?
        last_nonzero_t = -1
        for t in range(T_eff - 1, -1, -1):
            if np.any(d[t, 1:]):
                last_nonzero_t = t
                break
        
        # Total d nonzero cells
        total_nonzero = np.count_nonzero(d[:, 1:])
        
        print(f"  K={K}:")
        print(f"    d_0 nonzero count: {d0_nonzero} (should be 0)")
        print(f"    d_1 first nonzero at t={d1_first}")
        print(f"    Last t with any d_x!=0 (x>0): {last_nonzero_t} / {T_eff-1}")
        print(f"    Total nonzero d cells (x>0): {total_nonzero}")
        print(f"    Column activity (first 20): {col_activity[:20]}")
        print()


def experiment_actual_rule30():
    """
    More interesting: use the ACTUAL Rule 30 center column (not periodic!).
    Show that d_x is NOT zero for any x, confirming the center column is not periodic.
    
    But we can also check: for hypothetical periodic boundaries, how does
    the difference penetrate?
    """
    # Test with various periodic boundaries
    T = 2000
    K_values = [10, 20, 40, 80]
    
    # Period 2: boundary = "10"
    analyze_difference([1, 0], p=2, K_values=K_values, T=T)
    
    # Period 3: boundary = "110"  
    analyze_difference([1, 1, 0], p=3, K_values=K_values, T=T)
    
    # Period 1: boundary = "1"
    analyze_difference([1], p=1, K_values=K_values, T=T)
    
    # Period 1: boundary = "0"
    analyze_difference([0], p=1, K_values=K_values, T=T)


def experiment_difference_spatial_profile():
    """
    For a periodic boundary, look at how the fraction of time d_x != 0
    varies with x. Does it stay nonzero? Does it decay?
    """
    print("\n=== Spatial profile of difference activity ===")
    
    boundaries = [
        ([1, 0], 2, "10"),
        ([1, 1, 0], 3, "110"),
        ([1, 0, 1, 0], 4, "1010"),
    ]
    
    K = 100
    T = 5000
    
    for boundary, p, name in boundaries:
        grid = simulate_right_half(boundary, K, T)
        d = compute_difference_field(grid, p)
        T_eff = d.shape[0]
        
        print(f"\nBoundary '{name}' (p={p}), K={K}, T={T}:")
        print(f"  x  | fraction d_x!=0 | first nonzero t | mean run length")
        print(f"  ---|-----------------|-----------------|----------------")
        
        for x in range(min(K + 1, 50)):
            col = d[:, x]
            nonzero_count = np.count_nonzero(col)
            frac = nonzero_count / T_eff
            
            first_nz = -1
            for t in range(T_eff):
                if col[t] != 0:
                    first_nz = t
                    break
            
            # Mean run length of consecutive 1s
            if nonzero_count > 0:
                runs = []
                current_run = 0
                for t in range(T_eff):
                    if col[t] != 0:
                        current_run += 1
                    elif current_run > 0:
                        runs.append(current_run)
                        current_run = 0
                if current_run > 0:
                    runs.append(current_run)
                mean_run = np.mean(runs) if runs else 0
            else:
                mean_run = 0
            
            if x <= 5 or x % 5 == 0:
                print(f"  {x:3d} | {frac:15.4f} | {first_nz:15d} | {mean_run:14.2f}")


def experiment_difference_support_growth():
    """
    Key question: does the SUPPORT of d (set of x where d_x(t) != 0 for some t <= T)
    grow with time?
    
    If d_0 = 0 but d is not identically zero, the nonzero region must expand.
    How fast?
    """
    print("\n=== Difference support growth over time ===")
    
    boundary = [1, 0]
    p = 2
    K = 200
    T = 1000
    
    grid = simulate_right_half(boundary, K, T)
    d = compute_difference_field(grid, p)
    T_eff = d.shape[0]
    
    print(f"Boundary '10' (p={p}), K={K}, T={T}")
    print(f"  t   | rightmost x with d_x(t)!=0 | total nonzero cells | d_1(t)")
    print(f"  ----|------------------------------|---------------------|-------")
    
    for t in range(0, T_eff, 10):
        row = d[t]
        rightmost = -1
        for x in range(K, -1, -1):
            if row[x] != 0:
                rightmost = x
                break
        total = np.count_nonzero(row)
        d1 = d[t, 1] if 1 < d.shape[1] else 0
        
        if t <= 50 or t % 50 == 0:
            print(f"  {t:4d} | {rightmost:28d} | {total:19d} | {d1}")


if __name__ == "__main__":
    experiment_actual_rule30()
    experiment_difference_spatial_profile()
    experiment_difference_support_growth()
