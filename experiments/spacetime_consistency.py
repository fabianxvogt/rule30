"""
Spacetime self-consistency analysis for Rule 30 center column periodicity.

Core idea: If a_0 has period p after time T, then the entire spacetime must be
consistent with BOTH:
  (A) Rule 30 update: a_x(t+1) = a_{x-1}(t) XOR (a_x(t) OR a_{x+1}(t))
  (B) Temporal periodicity: a_0(t+p) = a_0(t) for all t >= T
  (C) Single-cell IC: a_x(0) = delta_{x,0}

This experiment explores structural consequences of (A)+(B)+(C) simultaneously.

Key angles:
1. Left reconstruction chain: Given a_0 periodic, what constraints does the
   full spacetime consistency place on a_1?
2. Parity / linear constraints: Rule 30 has XOR component. What linear 
   (mod 2) constraints arise from the periodicity assumption?
3. Light-cone diagonal constraints: a_{-t}(t) = 1 always. Combined with 
   periodicity of a_0, what does this force?
4. Information flow accounting: How many independent bits does the periodicity
   assumption constrain vs how many the right half produces?
"""

import numpy as np
from collections import defaultdict


def rule30_full(T, width):
    """
    Simulate Rule 30 on a finite grid of given width, centered at 0.
    Returns grid[-width:width+1] x [0:T].
    """
    W = width
    N = 2 * W + 1
    grid = np.zeros((T, N), dtype=np.uint8)
    grid[0, W] = 1  # center cell = 1
    for t in range(T - 1):
        for i in range(1, N - 1):
            L, C, R = grid[t, i-1], grid[t, i], grid[t, i+1]
            grid[t+1, i] = L ^ (C | R)
    return grid, W  # W is the index of center


def experiment_parity_constraints():
    """
    If a_0 has period p, then a_0(t+p) XOR a_0(t) = 0 for all t >= T.
    
    By the Rule 30 update and left-permutativity:
    a_0(t+1) = a_{-1}(t) XOR (a_0(t) OR a_1(t))
    
    So: a_0(t+p+1) XOR a_0(t+1) = 0
    => [a_{-1}(t+p) XOR (a_0(t+p) OR a_1(t+p))] XOR [a_{-1}(t) XOR (a_0(t) OR a_1(t))] = 0
    => d_{-1}(t) XOR [(a_0(t+p) OR a_1(t+p)) XOR (a_0(t) OR a_1(t))] = 0
    
    where d_x(t) = a_x(t+p) XOR a_x(t).
    
    Since a_0(t+p) = a_0(t) (by assumption), the OR terms simplify:
    - If a_0(t) = 1: OR(1, a_1(t+p)) = 1 = OR(1, a_1(t)), so the OR difference is 0
      => d_{-1}(t) = 0
    - If a_0(t) = 0: OR(0, a_1(t+p)) = a_1(t+p), OR(0, a_1(t)) = a_1(t)
      => d_{-1}(t) = a_1(t+p) XOR a_1(t) = d_1(t)
    
    So the constraint is: d_{-1}(t) = (1 - a_0(t)) * d_1(t)
    
    This connects the left and right d-values through the center column!
    Let's verify this and explore its consequences.
    """
    print("=== Parity constraint: d_{-1}(t) = (1-a_0(t)) * d_1(t) ===\n")
    
    T = 500
    grid, W = rule30_full(T, T)
    
    # Extract columns
    a0 = grid[:, W]
    a1 = grid[:, W + 1]
    am1 = grid[:, W - 1]
    
    # For various hypothetical periods, check the constraint
    for p in [2, 3, 5, 7, 10, 13]:
        # d_x(t) = a_x(t+p) XOR a_x(t)
        d0 = a0[:-p] ^ a0[p:]
        d1 = a1[:-p] ^ a1[p:]
        dm1 = am1[:-p] ^ am1[p:]
        a0_trunc = a0[:-p]
        
        # Check: dm1(t) should equal (1 - a0(t)) * d1(t) when d0(t) = 0
        # (regardless of whether d0 is actually 0 everywhere)
        
        # At positions where d0 = 0:
        mask_d0_zero = (d0 == 0)
        if mask_d0_zero.sum() > 0:
            lhs = dm1[mask_d0_zero]
            rhs = (1 - a0_trunc[mask_d0_zero]) * d1[mask_d0_zero]
            errors = np.sum(lhs != rhs)
            print(f"p={p}: d0=0 at {mask_d0_zero.sum()}/{len(d0)} positions, "
                  f"constraint d_{'{-1}'}=(1-a0)*d1 errors: {errors}")
    
    print()
    print("If a_0 is periodic with period p, then d_0 ≡ 0 (eventually).")
    print("The constraint then becomes: d_{-1}(t) = (1-a_0(t)) · d_1(t) for ALL t.")
    print("This means d_{-1} = 0 iff d_1(t) = 0 whenever a_0(t) = 0.")
    print()
    
    # Now the key question: iterate this leftward
    # From a_x(t+1) = a_{x-1}(t) XOR (a_x(t) OR a_{x+1}(t)):
    # d_x(t+1) = d_{x-1}(t) XOR [OR(a_x(t+p), a_{x+1}(t+p)) XOR OR(a_x(t), a_{x+1}(t))]
    #
    # For general x, the OR nonlinearity couples everything.
    # But at x=0 with d_0 ≡ 0: the constraint is exact and algebraic.
    
    print("Iterating the constraint further left:")
    print("a_{-2}(t) = a_{-1}(t+1) XOR (a_{-1}(t) OR a_0(t))")
    print("d_{-2}(t) = d_{-1}(t+1) XOR [OR stuff involving d_{-1} and d_0=0]")
    print()
    
    # Verify: with d_0 = 0, what's the exact d_{-2} constraint?
    # a_{-1}(t+1) = a_{-2}(t) XOR (a_{-1}(t) OR a_0(t))
    # a_{-1}(t+p+1) = a_{-2}(t+p) XOR (a_{-1}(t+p) OR a_0(t+p))
    # d_{-1}(t+1) = d_{-2}(t) XOR [OR(a_{-1}(t+p), a_0(t+p)) XOR OR(a_{-1}(t), a_0(t))]
    # 
    # Since a_0(t+p) = a_0(t):
    # OR(a_{-1}(t+p), a_0(t)) XOR OR(a_{-1}(t), a_0(t))
    # = when a_0(t)=1: OR=1 both sides, XOR=0
    # = when a_0(t)=0: a_{-1}(t+p) XOR a_{-1}(t) = d_{-1}(t)
    #
    # So: d_{-1}(t+1) = d_{-2}(t) XOR (1-a_0(t)) * d_{-1}(t)
    # => d_{-2}(t) = d_{-1}(t+1) XOR (1-a_0(t)) * d_{-1}(t)
    
    print("CHAIN OF CONSTRAINTS (assuming d_0 ≡ 0):")
    print("  d_{-1}(t) = (1-a_0(t)) · d_1(t)")
    print("  d_{-2}(t) = d_{-1}(t+1) ⊕ (1-a_0(t)) · d_{-1}(t)")
    print("  d_{-3}(t) = d_{-2}(t+1) ⊕ (1-a_{-1}(t)) · d_{-2}(t)")  
    print("  ... in general:")
    print("  d_{x-1}(t) = d_x(t+1) ⊕ (1-a_x(t)) · d_x(t)  [when d_{x+1}≡0]")
    print()
    print("Wait — that's only valid when d_{x+1} ≡ 0 too.")
    print("The general formula is:")
    print("  d_{x-1}(t) = d_x(t+1) ⊕ [OR(a_x(t+p), a_{x+1}(t+p)) ⊕ OR(a_x(t), a_{x+1}(t))]")
    print()
    
    # Let's verify the chain numerically for a specific "hypothetical period"
    # Pick times where d_0 happens to be 0 for a certain stretch, and check
    print("Numerical verification of the constraint chain:")
    p = 2
    d = {}
    for x in range(-10, 11):
        col = grid[:, W + x]
        d[x] = col[:-p] ^ col[p:]
    
    # Check constraint: d_{-1}(t) = (1-a0(t)) * d_1(t) where d_0(t)=0
    mask = (d[0] == 0)
    t_vals = np.where(mask)[0][:50]  # first 50 positions where d_0=0
    
    if len(t_vals) > 0:
        lhs = d[-1][t_vals]
        rhs = (1 - a0[t_vals]) * d[1][t_vals]
        print(f"  p=2: Constraint at {len(t_vals)} positions where d_0=0: errors = {np.sum(lhs!=rhs)}")


def experiment_diagonal_periodicity_clash():
    """
    The left-edge property says a_{-t}(t) = 1 for ALL t >= 1.
    
    If a_0 has period p after time T, then a_0(t) = a_0(t+p) for t >= T.
    
    Consider the spacetime triangle (x, t) with x + t = 0 (the left-edge diagonal):
    a_{-t}(t) = 1, so this diagonal is the constant sequence 1.
    
    Now consider shifting: what about the diagonal x + t = -p?
    a_{-t-p}(t) for t >= 0. At t large enough (t >= T), if all columns x <= 0 
    are period p, then a_x(t+p) = a_x(t), so:
    a_{-t-p}(t) = a_{-(t+p)+p-p}(t) ... hmm, this gets circular.
    
    Let's try a different approach: if ALL columns y <= 0 are p-periodic after
    time T (which follows from Prop 2 once we have TWO adjacent columns),
    then a_{-t}(t) = a_{-t}(t + kp) for any k with t + kp >= T.
    
    But a_{-t}(t) = 1 and for t' = t + kp with t' >> t, the cell (-t, t') is 
    INSIDE the light cone (not on the edge), so it could be anything.
    
    The clash would be: a_{-t}(t) = 1, and a_{-t}(t+kp) = a_{-t}(t) = 1.
    So periodicity says a_{-t} must take value 1 at times t, t+p, t+2p, ...
    But a_{-t}(t) = 1 is a boundary fact only at t = |x|. For later times,
    column -t evolves according to the driven dynamics.
    
    Let's check: does column x become periodic, and what value does it take
    at times t ≡ |x| (mod p)?
    """
    print("\n=== Diagonal periodicity clash analysis ===\n")
    
    T = 300
    grid, W = rule30_full(T, T)
    
    # Check: for column x (x < 0), what's a_x at the light-cone edge vs later
    for x in [-5, -10, -20, -50, -100]:
        if -x < T:
            edge_val = grid[-x, W + x]  # a_x(|x|) — should be 1
            # Check values at t = |x| + k*p for p = 2, 3, 5
            for p in [2, 3, 5]:
                vals = []
                for k in range(20):
                    t = -x + k * p
                    if t < T:
                        vals.append(grid[t, W + x])
                if len(vals) > 2:
                    print(f"  x={x}: a_x(|x|)={edge_val}, "
                          f"a_x(|x|+k*{p}) for k=0..{len(vals)-1}: "
                          f"{''.join(map(str, vals))}")
    
    print()
    print("Observation: The left-edge diagonal value a_{-t}(t)=1 doesn't directly")
    print("constrain periodicity, because it's a single sample per column.")
    

def experiment_right_half_entropy():
    """
    When a_0 has period p, the right half (x >= 1) is driven by a periodic boundary.
    The right half starts from IC a_x(0) = 0 for x >= 1.
    
    Key question: Does the right half "remember" its initial condition forever,
    or does it approach a periodic attractor?
    
    If it approaches an attractor, then a_1 IS eventually periodic (closing the gap).
    If it remembers forever, the IC introduces non-periodic behavior that persists.
    
    The "memory" manifests as the growing light cone: at time t, cells 1..t are
    influenced by the IC, cells t+1,... are still 0.
    
    For a finite truncation width K:
    - It's a finite-state system (2^K states) driven by period-p input
    - MUST become eventually periodic
    - Period P(K) divides 2^K * p (trivially)
    - Empirically P(K) grows rapidly and doesn't stabilize
    
    This experiment quantifies the relationship between K and P(K) more precisely.
    """
    print("\n=== Right-half attractor analysis ===\n")
    
    # Simulate the right half driven by a periodic a_0
    def simulate_right_half(p, boundary, K, max_steps):
        """
        Simulate cells 1..K with:
        - Cell 0 = boundary[t mod p]  (periodic input)
        - Cell K+1 = 0  (zero padding)
        - Rule 30 update for cells 1..K
        - IC: all zeros
        Returns the sequence of states and the detected period.
        """
        state = np.zeros(K, dtype=np.uint8)  # cells 1..K
        
        # Record (boundary_phase, state) tuples to detect periodicity
        seen = {}
        col1 = []
        
        for t in range(max_steps):
            phase = t % p
            col1.append(state[0])
            
            key = (phase, state.tobytes())
            if key in seen:
                return col1, t - seen[key], seen[key]
            seen[key] = t
            
            # Update
            new_state = np.zeros(K, dtype=np.uint8)
            for i in range(K):
                if i == 0:
                    L = boundary[phase]
                else:
                    L = state[i - 1]
                C = state[i]
                R = state[i + 1] if i + 1 < K else 0
                new_state[i] = L ^ (C | R)
            state = new_state
        
        return col1, None, None
    
    # Analyze period growth for various boundaries
    print("Period P(K) of width-K truncated right half:")
    print(f"{'K':>4} | {'p=2 (10)':>12} | {'p=3 (100)':>12} | {'p=5 (10100)':>12}")
    print("-" * 55)
    
    boundaries = {
        'p=2 (10)': [1, 0],
        'p=3 (100)': [1, 0, 0],
        'p=5 (10100)': [1, 0, 1, 0, 0],
    }
    
    for K in [5, 10, 15, 20, 25, 30]:
        row = f"{K:>4} |"
        for name, bnd in boundaries.items():
            col1, period, preperiod = simulate_right_half(len(bnd), bnd, K, 200000)
            if period:
                row += f" {period:>12d} |"
            else:
                row += f" {'> 200000':>12s} |"
        print(row)
    
    print()

    # For p=2, let's look at the Hamming distance between state at time t and t+p
    # to see if it grows or stays bounded
    print("State difference (right half) between t and t+p over time:")
    p = 2
    boundary = [1, 0]
    K = 100
    max_t = 500
    
    state = np.zeros(K, dtype=np.uint8)
    states = [state.copy()]
    
    for t in range(max_t):
        phase = t % p
        new_state = np.zeros(K, dtype=np.uint8)
        for i in range(K):
            L = boundary[phase] if i == 0 else state[i-1]
            C = state[i]
            R = state[i+1] if i+1 < K else 0
            new_state[i] = L ^ (C | R)
        state = new_state
        states.append(state.copy())
    
    # Hamming distance between state(t) and state(t+p) for same phase
    print(f"\n  K={K}, p={p}, boundary={boundary}")
    for t in range(10, max_t - p, 50):
        s1 = states[t]
        s2 = states[t + p]
        hamming = np.sum(s1 != s2)
        # Also check how far the difference extends
        diff = s1 ^ s2
        if np.any(diff):
            rightmost_diff = np.max(np.where(diff))
        else:
            rightmost_diff = -1
        print(f"  t={t:>4}: Hamming(state(t), state(t+p)) = {hamming:>3}, "
              f"rightmost diff at cell {rightmost_diff}")


def experiment_constraint_counting():
    """
    Information-theoretic constraint counting.
    
    Assume a_0 is periodic with period p after time T.
    
    In the time window [T, T+N] (N steps):
    - The center column provides p bits of information (0 new information per step)
    - The right half generates ~N new bits at the expanding light cone
    - The left half is fully determined by reconstructing from (a_0, a_1)
    
    If a_0 is periodic, then a_0 provides 0 new bits per step.
    But the right half needs to be driven by a_0, and the right edge 
    of the light cone produces 1 new bit per step.
    
    The question is whether p bits from the periodic a_0 are enough to
    constrain the semi-infinite right half.
    
    More precisely: How many right-half configurations are consistent with
    a given periodic a_0 boundary? If this number grows without bound, 
    there might be a consistent one. If it's constrained to shrink, there
    can't be.
    
    Let's count the number of valid right-half configurations.
    """
    print("\n=== Constraint counting: consistent right-half configs ===\n")
    
    # For a given periodic boundary a_0, count how many width-K right-half
    # initial states lead to the correct a_0 (matching the boundary) at the
    # output.
    #
    # Wait — the right half is DRIVEN by a_0 as input, not constrained to
    # produce a_0 as output. The center column IS the input, and the right
    # half just evolves.
    #
    # So the real constraint is on a_1: the FULL system (two-sided infinite)
    # must satisfy Rule 30 everywhere. Given periodic a_0, a_1 is whatever
    # the right-half dynamics produce.
    #
    # The actual constraint for a contradiction is:
    #   a_0(t+1) = a_{-1}(t) XOR (a_0(t) OR a_1(t))
    # This links the left half, center, and right half.
    #
    # If a_0 is periodic, then a_0(t+1) is known. So:
    #   a_{-1}(t) = a_0(t+1) XOR (a_0(t) OR a_1(t))
    #
    # a_1 is produced by the right-half dynamics (driven by a_0).
    # a_{-1} is then DETERMINED by the formula above.
    #
    # For this to form a valid left half, a_{-1} must be consistent with 
    # the Rule 30 update linking a_{-1}, a_{-2}, and a_0:
    #   a_{-1}(t+1) = a_{-2}(t) XOR (a_{-1}(t) OR a_0(t))
    # => a_{-2}(t) = a_{-1}(t+1) XOR (a_{-1}(t) OR a_0(t))
    #
    # This is always satisfiable (just define a_{-2} by this formula).
    # So there's NO constraint violation from the left half!
    # The left half reconstructs consistently by definition (Prop 2).
    
    print("Key realization: There is NO constraint violation from consistency!")
    print()
    print("Given:")
    print("  - a_0 periodic with period p")
    print("  - a_x(0) = 0 for x >= 1 (IC)")
    print("  - Rule 30 everywhere")
    print()
    print("The right half evolves deterministically from IC + a_0 boundary.")
    print("This produces a_1(t) for all t.")
    print("Then a_{-1}(t) = a_0(t+1) XOR (a_0(t) OR a_1(t)) is determined.")
    print("Then a_{-2}, a_{-3}, ... are all determined by left reconstruction.")
    print()
    print("The ENTIRE spacetime is determined! There's exactly ONE spacetime")
    print("satisfying Rule 30 + single-cell IC.")
    print()
    print("So the question 'is a_0 periodic?' is asking whether the unique")
    print("Rule 30 spacetime with single-cell IC has a periodic center column.")
    print()
    print("There's no logical inconsistency to find — the spacetime exists")
    print("and is unique. The center column either is or isn't periodic.")
    print()
    print("This means proof-by-contradiction must use STRUCTURAL properties")
    print("of Rule 30, not just consistency counting.")
    
    # Actually wait — there IS a subtlety. The spacetime is determined by IC.
    # But if we ASSUME a_0 is periodic, we're positing a PROPERTY of the
    # already-determined sequence. We need to show this property leads to
    # a contradiction with some other property.
    #
    # The left-edge property a_{-t}(t) = 1 is one such property.
    # If all columns x <= 0 are periodic with period p after time T,
    # then a_{-t}(t+p) = a_{-t}(t) = 1 for t >= T.
    # But a_{-t}(t+p) is the value of column -t at a time INSIDE the light cone.
    # This is perfectly consistent — column -t can take value 1 at t+p.
    
    print("\n--- Can we use the left-edge property? ---")
    print("a_{-t}(t) = 1 for all t >= 1.")
    print("If column -t has period p after time T, then a_{-t}(t+kp) = a_{-t}(t) = 1.")
    print("This means column -t must be 1 at times t, t+p, t+2p, ...")
    print("This is a constraint on column -t, but not necessarily contradictory.")
    print()
    
    # Let's check: for the actual spacetime, at what fraction of times is
    # column x equal to 1?
    T = 300
    grid, W = rule30_full(T, T)
    
    print("Density of 1s in column x (for t in [|x|, T]):")
    for x in [-1, -5, -10, -20, -50, -100]:
        col = grid[-x:T, W + x]
        density = np.mean(col)
        print(f"  x={x:>4}: density={density:.4f}, n_samples={len(col)}")
    
    print()
    print("All densities ~0.5, so the constraint a_{-t}(t)=1 places a fraction 1/p")
    print("of the values to be 1, which is compatible with density ~0.5 for small p.")


def experiment_transfer_matrix():
    """
    New approach: Transfer matrix for the RIGHT half driven by periodic a_0.
    
    The width-K right half has state s(t) = (a_1(t), ..., a_K(t)) in {0,1}^K.
    With periodic a_0 of period p, the evolution over one full period is:
    
    s(t+p) = F_p(s(t))  where F_p is the composition of p one-step maps.
    
    Each one-step map depends on the boundary bit b = a_0(t mod p):
    f_b: {0,1}^K -> {0,1}^K  (with zero-padding at right boundary)
    
    F_p = f_{b_{p-1}} ∘ ... ∘ f_{b_1} ∘ f_{b_0}
    
    For the truncated system to be periodic, we need F_p^n(s) = s for some n.
    The period of s under F_p can be at most 2^K (since the state space is finite).
    
    Key: F_p might have a unique fixed point, or it might have an exponentially
    large period. Let's analyze its structure.
    
    In particular: How many fixed points does F_p have? How does the number
    of periodic orbits grow with K?
    """
    print("\n=== Transfer matrix / orbit structure of F_p ===\n")
    
    def apply_one_step(state, boundary_bit, K):
        """Apply one Rule 30 step to width-K right half with given boundary."""
        new = np.zeros(K, dtype=np.uint8)
        for i in range(K):
            L = boundary_bit if i == 0 else state[i-1]
            C = state[i]
            R = state[i+1] if i+1 < K else 0
            new[i] = L ^ (C | R)
        return new
    
    def apply_full_period(state, boundary, K):
        """Apply p steps (full period) to state."""
        s = state.copy()
        for phase in range(len(boundary)):
            s = apply_one_step(s, boundary[phase], K)
        return s
    
    # For small K, enumerate all orbits of F_p
    boundary = [1, 0]  # period 2
    p = len(boundary)
    
    print(f"Boundary: {boundary} (period {p})")
    print()
    print(f"{'K':>3} | {'#Fixed':>6} | {'#Orbits':>7} | {'Max period':>10} | {'Avg period':>10}")
    print("-" * 55)
    
    for K in range(1, 19):
        # Enumerate all states
        n_states = 2**K
        # Build map F_p
        fp_map = {}
        for s_int in range(n_states):
            state = np.array([(s_int >> i) & 1 for i in range(K)], dtype=np.uint8)
            result = apply_full_period(state, boundary, K)
            r_int = sum(int(result[i]) << i for i in range(K))
            fp_map[s_int] = r_int
        
        # Find orbits
        visited = set()
        n_fixed = 0
        orbit_sizes = []
        
        for s in range(n_states):
            if s in visited:
                continue
            # Trace orbit
            orbit = []
            current = s
            while current not in visited:
                visited.add(current)
                orbit.append(current)
                current = fp_map[current]
            # Check if this orbit is a cycle (current should be in orbit)
            if current in orbit:
                cycle_start = orbit.index(current)
                cycle_len = len(orbit) - cycle_start
                orbit_sizes.append(cycle_len)
                if cycle_len == 1:
                    n_fixed += 1
        
        max_period = max(orbit_sizes) if orbit_sizes else 0
        avg_period = np.mean(orbit_sizes) if orbit_sizes else 0
        print(f"{K:>3} | {n_fixed:>6} | {len(orbit_sizes):>7} | {max_period:>10} | {avg_period:>10.1f}")
    
    print()
    
    # Now check: which fixed point does the IC (all zeros) converge to?
    print("Orbit of IC (all zeros) under F_p:")
    for K in [5, 10, 15, 18]:
        state = np.zeros(K, dtype=np.uint8)
        seen = {}
        for step in range(100000):
            key = state.tobytes()
            if key in seen:
                print(f"  K={K}: enters cycle at step {seen[key]}, period {step - seen[key]}")
                break
            seen[key] = step
            state = apply_full_period(state, boundary, K)
        else:
            print(f"  K={K}: no cycle found in 100000 steps")
    
    # Check for K up to ~22 if feasible  
    print()
    print("Cycle period of IC=0 orbit under F_p (boundary=[1,0]):")
    for K in range(1, 23):
        state = np.zeros(K, dtype=np.uint8)
        seen = {}
        found = False
        for step in range(500000):
            key = state.tobytes()
            if key in seen:
                print(f"  K={K:>2}: preperiod={seen[key]:>6}, period={step - seen[key]:>6}")
                found = True
                break
            seen[key] = step
            state = apply_full_period(state, boundary, K)
        if not found:
            print(f"  K={K:>2}: period > 500000")


def experiment_column1_complexity():
    """
    Measure the complexity of column a_1 when driven by periodic a_0.
    
    If a_1 has low complexity (e.g., eventually periodic, or low Lempel-Ziv 
    complexity), the gap might be bridgeable. If a_1 has maximal complexity,
    periodicity of a_0 is unlikely.
    
    We use:
    1. Lempel-Ziv complexity (number of distinct phrases)
    2. Block entropy H_n (entropy rate of n-grams)
    3. Auto-mutual information I(a_1(t); a_1(t+lag))
    """
    print("\n=== Complexity of column a_1 (true Rule 30) ===\n")
    
    T = 10000
    grid, W = rule30_full(T, T)
    
    a0 = grid[:, W]
    a1 = grid[:, W + 1]
    
    # LZ complexity (Lempel-Ziv 76)
    def lz_complexity(s):
        """Count the number of distinct phrases in LZ76 decomposition."""
        n = len(s)
        i = 0
        c = 0
        while i < n:
            # Find longest match in s[0:i]
            length = 0
            for l in range(1, n - i + 1):
                if s[i:i+l].tobytes() in [s[j:j+l].tobytes() for j in range(i)]:
                    length = l
                else:
                    break
            c += 1
            i += length + 1
        return c
    
    # Simplified LZ: just count unique substrings up to length L
    def count_unique_substrings(s, L):
        """Count unique substrings of length L."""
        subs = set()
        for i in range(len(s) - L + 1):
            subs.add(s[i:i+L].tobytes())
        return len(subs)
    
    # Block entropy
    def block_entropy(s, n):
        """Compute H_n = H(n-grams) / n."""
        counts = defaultdict(int)
        for i in range(len(s) - n + 1):
            key = s[i:i+n].tobytes()
            counts[key] += 1
        total = sum(counts.values())
        H = 0
        for c in counts.values():
            p = c / total
            if p > 0:
                H -= p * np.log2(p)
        return H / n
    
    print("Block entropy rate H_n/n for a_0 and a_1:")
    print(f"{'n':>4} | {'H_n(a_0)/n':>12} | {'H_n(a_1)/n':>12} | {'H_n(random)/n':>14}")
    for n in [1, 2, 3, 4, 5, 8, 10, 12, 15]:
        h0 = block_entropy(a0[:5000], n)
        h1 = block_entropy(a1[:5000], n)
        rnd = block_entropy(np.random.randint(0, 2, 5000).astype(np.uint8), n)
        print(f"{n:>4} | {h0:>12.6f} | {h1:>12.6f} | {rnd:>14.6f}")
    
    print()
    print("Unique substrings of length L (out of 2^L possible):")
    print(f"{'L':>4} | {'a_0':>8} | {'a_1':>8} | {'max 2^L':>8}")
    for L in [5, 8, 10, 12, 15, 18, 20]:
        u0 = count_unique_substrings(a0[:5000], L)
        u1 = count_unique_substrings(a1[:5000], L)
        print(f"{L:>4} | {u0:>8} | {u1:>8} | {2**L:>8}")
    
    print()

    # Auto-mutual information of a_1
    print("Autocorrelation of a_1(t) at various lags:")
    mean1 = np.mean(a1[:5000])
    for lag in [1, 2, 3, 5, 10, 20, 50, 100]:
        x = a1[:5000-lag].astype(float) - mean1
        y = a1[lag:5000].astype(float) - mean1
        corr = np.dot(x, y) / (np.sqrt(np.dot(x, x) * np.dot(y, y)) + 1e-10)
        print(f"  lag={lag:>4}: autocorrelation = {corr:>8.5f}")


if __name__ == "__main__":
    experiment_parity_constraints()
    experiment_diagonal_periodicity_clash()
    experiment_right_half_entropy()
    experiment_constraint_counting()
    experiment_transfer_matrix()
    experiment_column1_complexity()
