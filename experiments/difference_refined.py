"""
Refined difference propagation analysis.

Focus on the key structural question: given periodic boundary a_0 with period p,
starting from all-zeros initial condition, does d_x(t) = a_x(t+p) XOR a_x(t)
ever become identically zero in the right half?

KEY INSIGHT: At time t, the right half state a_1..a_K is determined by the
boundary bits a_0(0), a_0(1), ..., a_0(t-1). Since a_0 has period p (after
pre-period 0 since we're assuming periodic from the start), the boundary
sequence is w^infty = www... where w has length p.

The difference d(t) compares the state after seeing t+p boundary bits vs t bits.
Since both see the same periodic pattern, d is comparing:
  - a(t+p): state after w^{floor((t+p)/p)} boundary bits
  - a(t): state after w^{floor(t/p)} boundary bits

Both trajectories see the same periodic input, just shifted by one full period.
The difference arises only from the INITIAL CONDITION.

After many complete periods, the system's "memory" of the initial condition
should fade IF the dynamics is mixing. Rule 30 is expected to be mixing,
so d should decay. BUT the right half keeps growing (light cone expansion),
and each new cell sees a "fresh" initial condition (zero).

This experiment measures whether d_1(t) converges to 0 as t -> infty.
If it doesn't, then the right half column 1 is NOT eventually periodic,
which would be important for the proof.
"""

import numpy as np


def simulate_full_right_half(boundary_word, K, T):
    """
    Simulate right half with periodic boundary.
    boundary_word: list of bits, repeated cyclically.
    Returns grid[t][x] for t=0..T-1, x=0..K.
    x=0 is boundary column a_0.
    """
    p = len(boundary_word)
    grid = np.zeros((T, K + 2), dtype=np.uint8)  # extra column for zero padding
    
    for t in range(T):
        grid[t, 0] = boundary_word[t % p]
    
    for t in range(T - 1):
        for x in range(1, K + 1):
            grid[t + 1, x] = grid[t, x - 1] ^ (grid[t, x] | grid[t, x + 1])
    
    return grid[:, :K + 1]


def check_column_periodicity(grid, x, p, start_check=0):
    """
    Check if column x becomes periodic with period p after time start_check.
    Returns (is_periodic, first_violation_time_or_None).
    """
    T = grid.shape[0]
    for t in range(start_check, T - p):
        if grid[t, x] != grid[t + p, x]:
            return False, t
    return True, None


def experiment_column1_periodicity():
    """
    Direct test: for periodic boundary, is a_1(t) eventually periodic with same period?
    """
    print("=== Direct test: is column 1 eventually periodic? ===\n")
    
    boundaries = [
        ([1, 0], "10"),
        ([1, 1, 0], "110"),
        ([1, 0, 1, 0], "1010"),
        ([1], "1"),
        ([0, 1], "01"),
        ([1, 1, 0, 1, 0], "11010"),
    ]
    
    K = 200
    T = 4000
    
    for boundary, name in boundaries:
        p = len(boundary)
        grid = simulate_full_right_half(boundary, K, T)
        
        print(f"Boundary '{name}' (p={p}), K={K}, T={T}:")
        
        # Check column 1 for period p
        is_p, first_viol = check_column_periodicity(grid, 1, p, start_check=0)
        print(f"  Period p={p}: {'YES' if is_p else f'NO (first violation at t={first_viol})'}")
        
        # Check column 1 for period 2p, 3p, ..., up to 20p
        for mult in range(2, 21):
            q = mult * p
            if q >= T // 2:
                break
            is_q, first_viol = check_column_periodicity(grid, 1, q, start_check=0)
            if is_q:
                print(f"  Period {mult}p={q}: YES (periodic from t=0)")
                break
        else:
            print(f"  No period mp found for m=2..20")
        
        # Check for ANY eventual period up to 100
        found_period = False
        for q in range(1, min(101, T // 4)):
            is_q, _ = check_column_periodicity(grid, 1, q, start_check=T // 2)
            if is_q:
                # Double check with a longer suffix
                is_q2, _ = check_column_periodicity(grid, 1, q, start_check=T // 4)
                if is_q2:
                    print(f"  Eventually periodic with period {q} (from t={T//4})")
                    found_period = True
                    break
        if not found_period:
            print(f"  No eventual period ≤ 100 found (checked last {T//4} steps)")
        
        print()


def experiment_d1_long_time():
    """
    Track d_1(t) = a_1(t+p) XOR a_1(t) over very long time.
    Key question: does the FRACTION of time d_1 != 0 decay to zero?
    """
    print("=== d_1(t) long-time behavior ===\n")
    
    boundaries = [
        ([1, 0], "10"),
        ([1, 1, 0], "110"),
        ([0, 1], "01"),
    ]
    
    K = 500
    T = 10000
    
    for boundary, name in boundaries:
        p = len(boundary)
        grid = simulate_full_right_half(boundary, K, T)
        
        print(f"Boundary '{name}' (p={p}), K={K}, T={T}:")
        
        # Compute d_1(t) = grid[t+p, 1] ^ grid[t, 1]
        d1 = np.zeros(T - p, dtype=np.uint8)
        for t in range(T - p):
            d1[t] = grid[t + p, 1] ^ grid[t, 1]
        
        # Compute running fraction of d_1 != 0
        windows = [100, 500, 1000, 2000, 5000]
        print(f"  Running fraction of d_1 != 0:")
        for w in windows:
            if w >= T - p:
                continue
            # Last w steps
            frac = np.mean(d1[T - p - w:T - p])
            # First w steps
            frac_first = np.mean(d1[:w])
            # Middle w steps
            mid_start = (T - p - w) // 2
            frac_mid = np.mean(d1[mid_start:mid_start + w])
            print(f"    Window {w}: first={frac_first:.4f}, middle={frac_mid:.4f}, last={frac:.4f}")
        
        # Is there a clear trend? Compare 10 consecutive 500-step windows
        window = 500
        n_windows = (T - p) // window
        fracs = []
        for i in range(n_windows):
            f = np.mean(d1[i * window:(i + 1) * window])
            fracs.append(f)
        
        if len(fracs) >= 4:
            first_quarter = np.mean(fracs[:len(fracs)//4])
            last_quarter = np.mean(fracs[-len(fracs)//4:])
            print(f"  Trend: first quarter avg={first_quarter:.4f}, last quarter avg={last_quarter:.4f}")
            if abs(first_quarter - last_quarter) < 0.02:
                print(f"  → No decay detected (difference {abs(first_quarter-last_quarter):.4f})")
            elif last_quarter < first_quarter:
                print(f"  → Possible decay (ratio {last_quarter/first_quarter:.3f})")
            else:
                print(f"  → Increasing (ratio {last_quarter/first_quarter:.3f})")
        
        print()


def experiment_d_cross_column_correlations():
    """
    Check if d_1(t) and d_2(t) are correlated. If the propagation is effectively
    random, this tells us about mixing.
    """
    print("=== Cross-column d correlations ===\n")
    
    boundary = [1, 0]
    p = 2
    K = 100
    T = 10000
    
    grid = simulate_full_right_half(boundary, K, T)
    T_eff = T - p
    
    d = np.zeros((T_eff, K + 1), dtype=np.uint8)
    for t in range(T_eff):
        d[t] = grid[t + p, :K + 1] ^ grid[t, :K + 1]
    
    # Correlation between adjacent d columns
    print(f"Boundary '10' (p={p}), K={K}, T={T}")
    print(f"Correlation between d_x(t) and d_{{x+1}}(t):")
    for x in [1, 2, 3, 5, 10, 20, 50]:
        if x + 1 > K:
            break
        # Use only the part where both columns are "active" (past the light cone)
        start = x + 2  # after light cone reaches column x+1
        if start >= T_eff:
            continue
        dx = d[start:, x].astype(float)
        dx1 = d[start:, x + 1].astype(float)
        if np.std(dx) > 0 and np.std(dx1) > 0:
            corr = np.corrcoef(dx, dx1)[0, 1]
        else:
            corr = float('nan')
        print(f"  d_{x} vs d_{x+1}: corr = {corr:.4f}")
    
    print()
    
    # Autocorrelation of d_1
    d1 = d[:, 1].astype(float)
    print(f"Autocorrelation of d_1(t):")
    for lag in [1, 2, 3, 4, 5, 10, 20, 50]:
        if lag >= T_eff:
            break
        corr = np.corrcoef(d1[:T_eff - lag], d1[lag:])[0, 1]
        print(f"  lag {lag}: {corr:.4f}")


def experiment_light_cone_boundary():
    """
    CRUCIAL check: The right half starts from all zeros. The light cone expands at 
    speed 1. At time t, only cells x=1..t can be nonzero. This means d_x(t) for 
    x > t is comparing two zeros, so d = 0 there. But at x = t-p+1..t (near the
    light cone edge), d is comparing cells that have seen the boundary bits for
    different amounts of time. This boundary effect never goes away.
    
    This "permanent light-cone boundary mismatch" is what keeps d nonzero.
    Even though the periodic input eventually makes the BULK periodic, the
    expanding edge continuously injects fresh differences.
    """
    print("=== Light-cone boundary effect on d ===\n")
    
    boundary = [1, 0]
    p = 2
    K = 500
    T = 500
    
    grid = simulate_full_right_half(boundary, K, T)
    
    print(f"Boundary '10' (p={p})")
    print(f"Checking d at the light-cone edge region at various times:\n")
    
    for t in [20, 50, 100, 200, 400]:
        if t + p >= T:
            continue
        # At time t, cells x > t should be 0
        # d_x(t) = a_x(t+p) ^ a_x(t)
        # For x near t: a_x(t) might be 0 (just at edge), a_x(t+p) nonzero
        
        edge_region = list(range(max(1, t - 10), min(K, t + 5)))
        vals = []
        for x in edge_region:
            a_t = grid[t, x]
            a_tp = grid[t + p, x] if t + p < T else 0
            d_val = a_t ^ a_tp
            vals.append((x, a_t, a_tp, d_val))
        
        print(f"  t={t}: (column x, a(t), a(t+p), d)")
        for x, at, atp, dv in vals:
            marker = " <-- light cone edge" if x == t else ""
            print(f"    x={x}: {at} {atp} {dv}{marker}")
        print()


if __name__ == "__main__":
    experiment_column1_periodicity()
    experiment_d1_long_time()
    experiment_d_cross_column_correlations()
    experiment_light_cone_boundary()
