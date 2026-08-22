"""
Light-cone edge injection analysis.

Key insight from difference_refined.py: the expanding light cone continuously 
injects fresh differences into the d-field. Even if the bulk became periodic,
the edge never does because at x ≈ t, cells a_x(t+p) and a_x(t) have seen
DIFFERENT numbers of effective boundary bits.

This experiment quantifies the edge injection rate and analyzes whether
the injected differences must propagate back to column 1.

STRUCTURAL ARGUMENT BEING TESTED:
1. At time t, the light cone edge is at x ≈ t.
2. d(t+1) near the edge has a nonzero "source term" from the light cone expansion.
3. In Rule 30, information propagates LEFT at speed 1 (left-permutativity).
4. Therefore differences injected at x ≈ t reach column 1 by time ≈ 2t.
5. This creates an infinite sequence of injection events that reach column 1.
6. For d_1 to be zero, ALL of these must cancel — which seems impossible if
   the injection pattern is sufficiently complex.
"""

import numpy as np


def simulate_right_half(boundary_word, K, T):
    """Simulate with periodic boundary. Returns grid[t][x], x=0..K."""
    p = len(boundary_word)
    grid = np.zeros((T, K + 2), dtype=np.uint8)
    for t in range(T):
        grid[t, 0] = boundary_word[t % p]
    for t in range(T - 1):
        for x in range(1, K + 1):
            grid[t + 1, x] = grid[t, x - 1] ^ (grid[t, x] | grid[t, x + 1])
    return grid[:, :K + 1]


def experiment_edge_injection_pattern():
    """
    At each time t, look at the "edge region" (x near t) and count the 
    number of nonzero d-cells being "injected" (i.e., d nonzero at x > t-p
    where the difference is fresh from the light-cone expansion).
    """
    print("=== Edge injection pattern ===\n")
    
    boundary = [1, 0]
    p = 2
    K = 600
    T = 500
    
    grid = simulate_full(boundary, K, T)
    
    print(f"Boundary '10' (p={p})")
    print(f"At each time t, count d-cells near the light cone edge x≈t:\n")
    print(f"  t   | d at x=t-2 | d at x=t-1 | d at x=t | d at x=t+1 | d at x=t+2 | edge injection")
    print(f"  ----|------------|------------|----------|------------|------------|---------------")
    
    edge_bits = []
    for t in range(p, T - p):
        d_vals = []
        for dx in [-2, -1, 0, 1, 2]:
            x = t + dx
            if 0 <= x <= K and t + p < T:
                d_vals.append(grid[t + p, x] ^ grid[t, x])
            else:
                d_vals.append(-1)
        
        # "Edge injection": d nonzero at x = t+1 (just beyond light cone)
        # This is the "fresh" difference from the cone expansion
        edge_bit = d_vals[3]  # x = t+1
        edge_bits.append(edge_bit)
        
        if t <= 30 or t % 50 == 0:
            print(f"  {t:4d} | {d_vals[0]:10d} | {d_vals[1]:10d} | {d_vals[2]:8d} | {d_vals[3]:10d} | {d_vals[4]:10d} | {'YES' if edge_bit == 1 else 'no'}")
    
    # Statistics of edge injection
    edge_bits = np.array(edge_bits)
    print(f"\n  Total time steps: {len(edge_bits)}")
    print(f"  Edge injection fraction: {np.mean(edge_bits):.4f}")
    print(f"  Edge injection never stops: {np.all(edge_bits[-100:] > 0) or np.mean(edge_bits[-100:]) > 0.3}")
    

def simulate_full(boundary_word, K, T):
    """Same as simulate_right_half but returns full grid."""
    p = len(boundary_word)
    grid = np.zeros((T, K + 2), dtype=np.uint8)
    for t in range(T):
        grid[t, 0] = boundary_word[t % p]
    for t in range(T - 1):
        for x in range(1, K + 1):
            grid[t + 1, x] = grid[t, x - 1] ^ (grid[t, x] | grid[t, x + 1])
    return grid


def experiment_edge_pattern_structure():
    """
    Analyze the PATTERN of the edge injection bits over time.
    At the light cone edge, a_x(t) for x = t follows a specific formula:
    
    a_t(t) = the right-edge diagonal, which we know from edge_structure.py
    has period doubling.
    
    a_t(t+p) = the edge value p steps later.
    
    d_t(t) = a_t(t+p) XOR a_t(t)
    
    Since the right edge diag has period 1 (always 1 for the rightmost cell),
    the d at the exact edge involves comparing edges at different times.
    
    More precisely: a_t(t) = right edge diagonal value. For the single-seed IC,
    a_t(t) = 1 for all t >= 1 (the rightmost cell in the light cone).
    
    So d_t(t) = a_t(t+p) XOR 1. And a_t(t+p) = a_t(t+p), which depends on
    the values at positions t-1, t, t+1 at time t+p-1. Since x=t is inside
    the light cone at time t+p, a_t(t+p) is generally nonzero.
    """
    print("\n=== Edge pattern structure ===\n")
    
    boundary = [1, 0]
    p = 2
    K = 600
    T = 500
    
    grid = simulate_full(boundary, K, T)
    
    # Right edge values: a_t(t) for t = 1, 2, ...
    print("Right edge a_t(t) values:")
    edge_vals = [grid[t, t] for t in range(1, min(T, K))]
    print(f"  {edge_vals[:50]}")
    print(f"  All 1? {all(v == 1 for v in edge_vals[:200])}")
    
    # d at exact edge: d_t(t) = a_t(t+p) XOR a_t(t)
    print(f"\nd_t(t) = a_t(t+p) XOR a_t(t) at light cone edge:")
    d_edge = []
    for t in range(1, min(T - p, K)):
        d_val = grid[t + p, t] ^ grid[t, t]
        d_edge.append(d_val)
    print(f"  {d_edge[:80]}")
    print(f"  Fraction nonzero: {np.mean(d_edge):.4f}")
    
    # d at one step inside: d_{t-1}(t) = a_{t-1}(t+p) XOR a_{t-1}(t)
    print(f"\nd_{{t-1}}(t) at one step inside edge:")
    d_inside = []
    for t in range(2, min(T - p, K)):
        d_val = grid[t + p, t - 1] ^ grid[t, t - 1]
        d_inside.append(d_val)
    print(f"  {d_inside[:80]}")
    print(f"  Fraction nonzero: {np.mean(d_inside):.4f}")
    

def experiment_leftward_propagation_speed():
    """
    Track how d-patterns propagate leftward.
    
    If we introduce a single difference at position x at time t,
    it should propagate left at speed 1 (due to left-permutativity).
    
    But we're not looking at single differences — the entire right half
    has a complex d-field. The question is: do the edge-injected
    differences constructively add up at column 1?
    
    Strategy: Compare d_1(t) with the edge injection pattern at t/2
    (since a difference injected at x≈t/2 reaches column 1 at time t).
    """
    print("\n=== Leftward propagation correlation ===\n")
    
    boundary = [1, 0]
    p = 2
    K = 1000
    T = 2000
    
    grid = simulate_full(boundary, K, T)
    
    # d_1(t) values
    d1 = np.array([grid[t + p, 1] ^ grid[t, 1] for t in range(T - p)])
    
    # Edge injection at time s: d at x=s  
    # A difference at x=s, time s reaches x=1 at time s + (s-1) = 2s-1
    # So d_1(t) should correlate with edge injection at time s ≈ (t+1)/2
    
    # Compute edge injection pattern
    edge_inj = []
    for s in range(1, min(T - p, K)):
        d_val = grid[s + p, s] ^ grid[s, s]
        edge_inj.append(d_val)
    edge_inj = np.array(edge_inj)
    
    # Check correlation: d_1(2s-1) vs edge_inj(s)
    print("Correlation between d_1(2s-1) and edge injection at s:")
    N = min(len(edge_inj), (T - p) // 2) - 1
    d1_at_2s = np.array([d1[2 * s - 1] for s in range(1, N + 1)])
    edge_at_s = edge_inj[:N]
    
    if np.std(d1_at_2s) > 0 and np.std(edge_at_s) > 0:
        corr = np.corrcoef(d1_at_2s.astype(float), edge_at_s.astype(float))[0, 1]
        print(f"  Pearson correlation: {corr:.4f}")
    
    # Agreement fraction
    agree = np.mean(d1_at_2s == edge_at_s)
    print(f"  Agreement fraction: {agree:.4f}")
    
    # But really, d_1(t) is affected by ALL edge injections, not just one.
    # The path from edge x=s to column 1 takes s-1 steps, arriving at time t=2s-1.
    # Multiple paths interfere. That's what makes this hard.
    
    print(f"\n  Note: d_1(t) receives contributions from ALL edge points,")
    print(f"  not just one. Multiple paths interfere constructively/destructively.")
    print(f"  The low correlation ({corr:.3f}) reflects this multi-path interference.")


def experiment_d_conservation():
    """
    Is there a conservation law for d? 
    
    Check if sum(d_x(t), x=1..K) is conserved or has a pattern.
    In some systems, perturbations satisfy conservation laws.
    """
    print("\n=== d-field conservation check ===\n")
    
    boundary = [1, 0]
    p = 2
    K = 300
    T = 500
    
    grid = simulate_full(boundary, K, T)
    
    print(f"Boundary '10' (p={p})")
    print(f"Total d-mass M(t) = sum(d_x(t), x=1..K):\n")
    
    masses = []
    for t in range(T - p):
        d = np.array([grid[t + p, x] ^ grid[t, x] for x in range(1, K + 1)])
        masses.append(np.sum(d))
    
    print(f"  t=0: M={masses[0]}")
    print(f"  t=10: M={masses[10]}")
    print(f"  t=50: M={masses[50]}")
    print(f"  t=100: M={masses[100]}")
    print(f"  t=200: M={masses[200]}")
    print(f"  t=300: M={masses[min(300, T - p - 1)]}")
    
    # Is M(t) increasing? (Light cone expansion adds new d-cells)
    masses = np.array(masses)
    diffs = masses[1:] - masses[:-1]
    print(f"\n  Mean M(t): {np.mean(masses):.1f}")
    print(f"  Mean ΔM(t): {np.mean(diffs):.3f}")
    print(f"  M is {'increasing' if np.mean(diffs) > 0 else 'decreasing or constant'}")
    
    # Normalized by active width (t cells active at time t)
    norm_masses = [masses[t] / max(t + 1, 1) for t in range(len(masses))]
    print(f"\n  Normalized M(t)/t at t=50: {norm_masses[50]:.4f}")
    print(f"  Normalized M(t)/t at t=100: {norm_masses[100]:.4f}")
    print(f"  Normalized M(t)/t at t=200: {norm_masses[200]:.4f}")
    print(f"  Normalized M(t)/t at t=300: {norm_masses[min(300, T - p - 1)]:.4f}")
    print(f"  → Density d/width stabilizes at ~{np.mean(norm_masses[100:]):.4f}")


if __name__ == "__main__":
    experiment_edge_injection_pattern()
    experiment_edge_pattern_structure()
    experiment_leftward_propagation_speed()
    experiment_d_conservation()
