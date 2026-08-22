"""
Linearized difference analysis.

The d-field satisfies:
d_x(t+1) = d_{x-1}(t) ⊕ d_x(t) ⊕ d_{x+1}(t) 
            ⊕ a_x(t)·d_{x+1}(t) ⊕ d_x(t)·a_{x+1}(t) ⊕ d_x(t)·d_{x+1}(t)

The LINEAR part is Rule 90: d_x(t+1) = d_{x-1}(t) ⊕ d_x(t) ⊕ d_{x+1}(t)
The nonlinear corrections involve products of d and a.

KEY QUESTION: Is the nonlinear correction small enough that the linear analysis
gives the correct qualitative behavior?

For Rule 90 (the linear part), the behavior is well-known:
- It's the XOR of left-shift and right-shift
- Solutions evolve like Pascal's triangle mod 2  
- A localized perturbation spreads at speed 1 in both directions
- The total mass (population count) follows fractal dynamics

If the linear approximation is good, then edge-injected perturbations 
propagate to column 1 following Rule 90 paths, which means the perturbation
at time 2s (from edge injection at time s) has amplitude determined by
Pascal's triangle structure.

This experiment compares:
1. True d-field (from full Rule 30 simulation)
2. Linearized d-field (Rule 90 with same initial/boundary conditions)
"""

import numpy as np


def simulate_rule30_right_half(boundary_word, K, T):
    """Simulate Rule 30 right half with periodic boundary."""
    p = len(boundary_word)
    grid = np.zeros((T, K + 2), dtype=np.uint8)
    for t in range(T):
        grid[t, 0] = boundary_word[t % p]
    for t in range(T - 1):
        for x in range(1, K + 1):
            grid[t + 1, x] = grid[t, x - 1] ^ (grid[t, x] | grid[t, x + 1])
    return grid[:, :K + 1]


def compute_true_d(grid, p):
    """True difference field d_x(t) = grid[t+p,x] XOR grid[t,x]."""
    T, W = grid.shape
    d = np.zeros((T - p, W), dtype=np.uint8)
    for t in range(T - p):
        d[t] = grid[t + p] ^ grid[t]
    return d


def simulate_linearized_d(d_init, d_boundary, K, T_eff):
    """
    Simulate the LINEARIZED d-field using Rule 90:
    d_x(t+1) = d_{x-1}(t) ⊕ d_x(t) ⊕ d_{x+1}(t)
    
    d_boundary[t] = value at x=0 for each time step
    d_init = initial condition d_x(0) for x=0..K
    """
    d = np.zeros((T_eff, K + 2), dtype=np.uint8)
    d[0, :K + 1] = d_init[:K + 1]
    
    for t in range(T_eff - 1):
        d[t + 1, 0] = d_boundary[t + 1] if t + 1 < len(d_boundary) else 0
        for x in range(1, K + 1):
            d[t + 1, x] = d[t, x - 1] ^ d[t, x] ^ d[t, x + 1]
    
    return d[:, :K + 1]


def simulate_full_nonlinear_d(grid, d_init, d_boundary, K, T_eff, p):
    """
    Simulate the FULL nonlinear d-field:
    d_x(t+1) = d_{x-1} ⊕ d_x ⊕ d_{x+1} ⊕ a_x·d_{x+1} ⊕ d_x·a_{x+1} ⊕ d_x·d_{x+1}
    
    Uses the actual a-field from the grid for the nonlinear terms.
    """
    d = np.zeros((T_eff, K + 2), dtype=np.uint8)
    d[0, :K + 1] = d_init[:K + 1]
    
    for t in range(T_eff - 1):
        d[t + 1, 0] = d_boundary[t + 1] if t + 1 < len(d_boundary) else 0
        for x in range(1, K + 1):
            dx_1 = d[t, x - 1]
            dx = d[t, x]
            dx1 = d[t, x + 1] if x + 1 <= K else 0
            ax = grid[t, x]
            ax1 = grid[t, x + 1] if x + 1 <= K else 0
            
            linear = dx_1 ^ dx ^ dx1
            nonlinear = (ax & dx1) ^ (dx & ax1) ^ (dx & dx1)
            d[t + 1, x] = linear ^ nonlinear
    
    return d[:, :K + 1]


def experiment_compare_linear_vs_true():
    """Compare linearized (Rule 90) d vs true d."""
    print("=== Linear (Rule 90) vs True d comparison ===\n")
    
    boundary = [1, 0]
    p = 2
    K = 200
    T = 500
    
    grid = simulate_rule30_right_half(boundary, K, T)
    d_true = compute_true_d(grid, p)
    T_eff = d_true.shape[0]
    
    # Initial condition for d: d_x(0) = grid[p, x] ^ grid[0, x]
    d_init = d_true[0]
    
    # Boundary for d: d_0(t) should be 0 (periodic boundary assumption)
    d_boundary = np.zeros(T_eff, dtype=np.uint8)
    
    # Linearized d
    d_linear = simulate_linearized_d(d_init, d_boundary, K, T_eff)
    
    # Full nonlinear d (reconstructed)
    d_recon = simulate_full_nonlinear_d(grid, d_init, d_boundary, K, T_eff, p)
    
    # Compare
    print(f"Boundary '10' (p={p}), K={K}, T={T}")
    
    # Agreement between true d and reconstructed d (sanity check)
    agree_recon = np.mean(d_true == d_recon)
    print(f"\n  True d vs Reconstructed d: {agree_recon:.4f} agreement")
    if agree_recon < 0.99:
        print(f"  WARNING: Reconstruction doesn't match! Check implementation.")
        # Check first few differences
        for t in range(min(10, T_eff)):
            diff = np.where(d_true[t] != d_recon[t])[0]
            if len(diff) > 0:
                print(f"    t={t}: disagreement at x={diff[:5]}")
    
    # Agreement between true d and linear d
    print(f"\n  True d vs Linear d (Rule 90):")
    for window_start, window_end in [(0, 50), (50, 100), (100, 200), (200, 300), (300, 400)]:
        if window_end > T_eff:
            break
        agree = np.mean(d_true[window_start:window_end, 1:50] == d_linear[window_start:window_end, 1:50])
        print(f"    t={window_start}-{window_end}, x=1-49: {agree:.4f} agreement")
    
    # Column 1 specifically  
    print(f"\n  Column 1: True d_1 vs Linear d_1:")
    d1_true = d_true[:, 1]
    d1_linear = d_linear[:, 1]
    
    agree_total = np.mean(d1_true == d1_linear)
    print(f"    Overall agreement: {agree_total:.4f}")
    
    # Do they diverge over time?
    for start in range(0, T_eff - 100, 100):
        agree = np.mean(d1_true[start:start+100] == d1_linear[start:start+100])
        print(f"    t={start}-{start+100}: {agree:.4f}")
    
    # Key question: does the linearized d_1 also remain nonzero?
    print(f"\n  Linear d_1 fraction nonzero: {np.mean(d1_linear):.4f}")
    print(f"  True d_1 fraction nonzero: {np.mean(d1_true):.4f}")


def experiment_rule90_closed_form():
    """
    Rule 90 has a closed-form solution:
    d_x(t) = XOR over all paths from initial nonzero positions to (x,t).
    
    For a single point source at (x0, 0), the Rule 90 evolution gives:
    d_x(t) = C(t, (x-x0+t)/2) mod 2  (if x-x0+t is even, else 0)
    where C(n,k) is the binomial coefficient.
    
    The d at the edge x=t has a PERIODIC source (period 2p for p=2 boundary).
    Can we analyze this using Rule 90 closed-form?
    """
    print("\n=== Rule 90 closed-form analysis ===\n")
    
    # For the edge-injected d, consider each injection as a point source.
    # Edge injection at (x=s, t=s) for even s (with value 1).
    # Rule 90 evolution: this source reaches column 1 at time t = s + (s-1) = 2s-1
    # with amplitude C(s-1, (1-s+(2s-1))/2) = C(s-1, (s-1)/2) = C(s-1, (s-1)/2)
    # This is only nonzero when s-1 is even, i.e., s is odd.
    # For s odd: C(s-1, (s-1)/2) mod 2 = C(s-1, (s-1)/2).
    # By Lucas' theorem, this depends on the binary representation.
    
    # Let's just compute it directly:
    print("Edge injection at x=s, t=s reaches column 1 at t=2s-1.")
    print("Under Rule 90, the contribution to d_1(2s-1) is C(s-1, (s-1)/2) mod 2:")
    print()
    
    from math import comb
    
    contributions = []
    for s in range(1, 100):
        travel_time = s - 1
        x_displacement = s - 1  # from x=s to x=1
        # Rule 90: to go from (s, s) to (1, 2s-1) requires travel_time = s-1 steps
        # and displacement x = s-1 to the left.
        # In Rule 90, a source at the origin at t=0 reaches position x at time t with
        # amplitude C(t, (t+x)/2) mod 2 if (t+x) is even, else 0.
        # Here we go from source at x=s to target x=1, so displacement = -(s-1).
        # Equivalently, amplitude = C(s-1, (s-1 + (-(s-1)))/2) = C(s-1, 0) = 1 mod 2.
        # Wait, that can't be right... Let me reconsider.
        
        # Rule 90: d_x(t+1) = d_{x-1}(t) XOR d_{x+1}(t)
        # Actually full Rule 90 is: d_x(t+1) = d_{x-1}(t) XOR d_x(t) XOR d_{x+1}(t)
        # which is NOT the standard Rule 90. Let me recheck.
        
        # Standard Rule 90: d_x(t+1) = d_{x-1}(t) XOR d_{x+1}(t)
        # Our linear part: d_x(t+1) = d_{x-1}(t) XOR d_x(t) XOR d_{x+1}(t)
        # This is actually Rule 150 (XOR of all three neighbors including self).
        
        # Rule 150 propagation: for a point source at (x0, t0),
        # d_x(t0 + dt) = C(dt, (x-x0+dt)/2) mod 2 when (x-x0+dt) is even
        # Actually Rule 150 is more complex than Rule 90 for closed forms.
        
        # Let me just simulate it.
        pass
    
    # Direct simulation of Rule 150 from point source
    K_sim = 200
    T_sim = 200
    
    # Point source at (x=100, t=0) in a width-200 grid
    d_ps = np.zeros((T_sim, K_sim + 1), dtype=np.uint8)
    d_ps[0, 100] = 1
    
    for t in range(T_sim - 1):
        for x in range(1, K_sim):
            d_ps[t + 1, x] = d_ps[t, x - 1] ^ d_ps[t, x] ^ d_ps[t, x + 1]
    
    # Check: does the point source reach all positions?
    print("Point source at x=100, t=0 propagation (Rule 150 = linear part):")
    for dt in [10, 20, 50, 100, 150]:
        if dt >= T_sim:
            break
        # Find nonzero positions at time dt
        nz = np.where(d_ps[dt] != 0)[0]
        leftmost = nz[0] if len(nz) > 0 else -1
        rightmost = nz[-1] if len(nz) > 0 else -1
        count = len(nz)
        print(f"  t={dt}: {count} nonzero cells, range [{leftmost}, {rightmost}]")
    
    # Check d at x=50 (50 to the left of source) over time
    print(f"\n  d at x=50 (displacement -50 from source):")
    vals_50 = [d_ps[t, 50] for t in range(T_sim)]
    first_nz = -1
    for t in range(T_sim):
        if d_ps[t, 50] != 0:
            first_nz = t
            break
    print(f"  First nonzero at t={first_nz}")
    if first_nz >= 0:
        print(f"  Values at t={first_nz}..{first_nz+20}: {vals_50[first_nz:first_nz+20]}")
    
    # Multi-source: simulate many edge injections
    print(f"\n  Multi-source simulation (edge injections at x=s, t=s for s=1,3,5,...):")
    d_multi = np.zeros((T_sim, K_sim + 1), dtype=np.uint8)
    
    # Add sources at (s, s) for odd s
    for s in range(1, T_sim, 2):
        if s <= K_sim:
            d_multi[s, s] ^= 1
    
    # Evolve with Rule 150
    # Need to handle sources being added at future times
    d_multi2 = np.zeros((T_sim, K_sim + 1), dtype=np.uint8)
    for s in range(1, T_sim, 2):
        if s <= K_sim:
            d_multi2[s, s] = 1  # source
    
    for t in range(T_sim - 1):
        for x in range(1, K_sim):
            d_multi2[t + 1, x] ^= d_multi2[t, x - 1] ^ d_multi2[t, x] ^ d_multi2[t, x + 1]
    
    # Check column 1 of the multi-source
    d1_multi = [d_multi2[t, 1] for t in range(T_sim)]
    print(f"  d_1 values: {d1_multi[:40]}")
    print(f"  d_1 fraction nonzero: {np.mean(d1_multi):.4f}")


if __name__ == "__main__":
    experiment_compare_linear_vs_true()
    experiment_rule90_closed_form()
