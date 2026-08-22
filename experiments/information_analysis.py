"""
Information compression argument.

Key idea: if c(t) has period p, then the right-half state at time t is determined
by (t mod p) and the initial condition (all zeros). So the right-half state is 
a periodic function of t mod p, but the right-half state space grows.

More precisely: let R(t) = (a_1(t), a_2(t), ..., a_t(t)) be the "full" right-half
state at time t. We know:
  R(t) depends only on c(0), c(1), ..., c(t-1) and the initial condition.
  If c is periodic with period p, then R(t) is determined by t mod p and t itself.

The "projection" a_1(t) = first component of R(t).

QUESTION: Can a_1(t) be periodic with period p when R(t) has growing dimension?

ANOTHER APPROACH: Finite-state encoding.

If a_1(t) is eventually periodic with period q (some multiple of p), then the 
pair (a_0(t), a_1(t)) can be represented by a finite automaton with ≤ lcm(p, q) 
states. By Proposition 2, this gives ALL left columns periodic.

So the question reduces to: can the "compression" from growing R(t) to a_1(t)
produce a periodic output even though the full state R(t) is not periodic?

In general, YES — projecting a growing-dimension system to a single coordinate CAN
give a periodic result. Example: linear recurrence a_1(t) = some fixed function
regardless of the growing state.

But Rule 30's NONLINEARITY and mixing should prevent this. The question is how to
formalize "should prevent."

EXPERIMENT: Check whether the mapping from the "relevant" part of R(t) to a_1(t+1)
depends on a growing number of coordinates, or whether a bounded number suffice.
"""

import numpy as np


def simulate_right_half(boundary, K, T):
    """Simulate right half with periodic boundary."""
    p = len(boundary)
    grid = np.zeros((T, K + 2), dtype=np.uint8)
    for t in range(T):
        grid[t, 0] = boundary[t % p]
    for t in range(T - 1):
        for x in range(1, K + 1):
            grid[t + 1, x] = grid[t, x - 1] ^ (grid[t, x] | grid[t, x + 1])
    return grid[:, :K + 1]


def experiment_effective_memory():
    """
    At time t, a_1(t+1) = a_0(t) XOR (a_1(t) OR a_2(t)).
    So a_1(t+1) depends on a_0(t) (known, periodic) and a_1(t), a_2(t).
    
    a_2(t+1) = a_1(t) XOR (a_2(t) OR a_3(t)).
    So a_2(t+1) depends on a_1(t), a_2(t), a_3(t).
    
    In general, to predict a_1(t+1) from information at time t, we need a_0(t),
    a_1(t), a_2(t). But a_1(t) itself depends on a_0(t-1), a_1(t-1), a_2(t-1).
    
    Backward chain: to compute a_1(T), we need a_x(T-n) for x up to n+1.
    So the "effective memory depth" grows linearly.
    
    If c(t) is periodic with period p, can we compute a_1(t) using only
    a bounded amount of state? That is, does there exist a finite-state
    function F such that a_1(t) = F(t mod p, memory_state(t)) where
    memory_state is updated using only itself and c(t)?
    
    The answer would be YES if a_1 is eventually periodic, and NO otherwise.
    
    Let's test: for various periodic boundaries, find the MINIMUM memory
    (number of right-half cells) needed to predict a_1(t+1) from information
    at time t.
    """
    print("=== Effective memory for a_1 prediction ===\n")
    
    boundaries = [
        ([1, 0], "10"),
        ([1, 1, 0], "110"),
    ]
    
    K = 200
    T = 1000
    
    for boundary, name in boundaries:
        p = len(boundary)
        grid = simulate_right_half(boundary, K, T)
        
        print(f"Boundary '{name}' (p={p}):")
        print(f"  Testing: can a_1(t+1) be predicted from (t mod p, a_1..a_w(t)) for width w?\n")
        
        # For each width w, check if the mapping (t mod p, a_1(t)..a_w(t)) -> a_1(t+1)
        # is a deterministic function (i.e., the same input always gives the same output)
        for w in range(1, 30):
            # Collect (input -> output) pairs
            mapping = {}
            deterministic = True
            violation_time = -1
            
            for t in range(w, T - 1):  # start at w to ensure all cells are in light cone
                phase = t % p
                state = tuple(grid[t, x] for x in range(1, w + 1))
                key = (phase, state)
                output = grid[t + 1, 1]
                
                if key in mapping:
                    if mapping[key] != output:
                        deterministic = False
                        violation_time = t
                        break
                else:
                    mapping[key] = output
            
            if deterministic:
                print(f"  w={w}: DETERMINISTIC ({len(mapping)} distinct states seen)")
                break
            else:
                n_states = len(mapping)
                if w <= 5 or w % 5 == 0:
                    print(f"  w={w}: NOT deterministic (first violation at t={violation_time}, {n_states} states)")
        
        print()


def experiment_growing_dependence():
    """
    Show that the dependence of a_1(t) on distant cells grows with t.
    
    Specifically: find the RIGHTMOST cell a_x(t0) that affects a_1(T)
    for various T, starting from a fixed t0.
    
    Method: perturb a_x(t0) and see if a_1(T) changes.
    """
    print("=== Growing dependence radius ===\n")
    
    boundary = [1, 0]
    p = 2
    K = 500
    T = 400
    
    grid = simulate_right_half(boundary, K, T)
    
    print(f"Boundary '10' (p={p})")
    print(f"For each time T, find rightmost cell at t=0 that affects a_1(T):\n")
    
    for T_check in [10, 20, 50, 100, 200, 300]:
        if T_check >= T:
            break
        
        rightmost_dep = 0
        for x_perturb in range(1, min(T_check + 5, K)):
            # Simulate with perturbation at (x=x_perturb, t=0)
            grid2 = np.zeros((T_check + 1, K + 2), dtype=np.uint8)
            # Perturbing a_x(0) from 0 to 1
            grid2[0, x_perturb] = 1
            
            # Re-simulate
            for t in range(T_check):
                grid2[t, 0] = boundary[t % p]
                for x in range(1, K + 1):
                    grid2[t + 1, x] = grid2[t, x - 1] ^ (grid2[t, x] | grid2[t, x + 1])
            
            # Check if a_1(T_check) changed
            if grid2[T_check, 1] != grid[T_check, 1]:
                rightmost_dep = max(rightmost_dep, x_perturb)
        
        print(f"  T={T_check}: rightmost cell at t=0 affecting a_1(T) = {rightmost_dep}")
    
    print()
    print("  If rightmost_dep ~ T, then a_1(T) depends on O(T) initial cells.")
    print("  A finite-state encoder would need O(1) memory, creating a contradiction")
    print("  if the dependence truly grows.")


def experiment_mutual_information():
    """
    For periodic boundary, compute empirical mutual information between
    the "far right" state a_x(t) and a_1(t+x) (delayed column 1).
    
    If a_1 is periodic, I(a_x(t); a_1(t+x)) should be 0 for large x
    (since a_1 is determined by t mod q alone).
    
    If a_1 is NOT periodic, there should be nonzero mutual information
    between far-right cells and future column 1 values.
    """
    print("=== Mutual information between distant cells and column 1 ===\n")
    
    boundary = [1, 0]
    p = 2
    K = 200
    T = 5000
    
    grid = simulate_right_half(boundary, K, T)
    
    print(f"Boundary '10' (p={p}), K={K}, T={T}")
    print(f"I(a_x(t); a_1(t+x)) for various x:\n")
    
    for x in [1, 2, 5, 10, 20, 50, 100]:
        if x >= K or x >= T:
            break
        
        # Empirical joint distribution of (a_x(t), a_1(t+x))
        n00 = n01 = n10 = n11 = 0
        count = 0
        for t in range(x, T - x):
            ax = grid[t, x]
            a1_delayed = grid[t + x, 1]
            if ax == 0 and a1_delayed == 0:
                n00 += 1
            elif ax == 0 and a1_delayed == 1:
                n01 += 1
            elif ax == 1 and a1_delayed == 0:
                n10 += 1
            else:
                n11 += 1
            count += 1
        
        # Mutual information
        p_joint = np.array([[n00, n01], [n10, n11]], dtype=float) / count
        p_ax = p_joint.sum(axis=1)
        p_a1 = p_joint.sum(axis=0)
        
        mi = 0.0
        for i in range(2):
            for j in range(2):
                if p_joint[i, j] > 0 and p_ax[i] > 0 and p_a1[j] > 0:
                    mi += p_joint[i, j] * np.log2(p_joint[i, j] / (p_ax[i] * p_a1[j]))
        
        print(f"  x={x:3d}: I = {mi:.6f} bits, p(a_x=1) = {p_ax[1]:.3f}, p(a_1=1) = {p_a1[1]:.3f}")
    
    print()
    print("  If I doesn't decay to 0, column 1 retains information from distant cells.")
    print("  This suggests infinite effective memory → not periodic.")


if __name__ == "__main__":
    experiment_effective_memory()
    experiment_growing_dependence()
    experiment_mutual_information()
