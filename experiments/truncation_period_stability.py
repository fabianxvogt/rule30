#!/usr/bin/env python3
"""
Check whether the truncated right-half period stabilizes as truncation width grows.

For each truncation width K, we:
1. Evolve the width-K right half with periodic boundary c(t) = 1,0,1,0,... (period 2)
2. Find the eventual period and pre-period of column 1

If the period stabilizes, this supports the claim that the true a_1 is eventually periodic.
"""
import numpy as np

def evolve_right_half_truncated(K, boundary, max_steps):
    """
    Evolve the width-K truncated right half.
    State: a_1, a_2, ..., a_K (K cells)
    Boundary: a_0(t) = boundary[t % len(boundary)] for t >= 0
    Update: a_k(t+1) = a_{k-1}(t) XOR (a_k(t) OR a_{k+1}(t))
    with a_0(t) = boundary value, a_{K+1}(t) = 0
    """
    p = len(boundary)
    state = np.zeros(K+2, dtype=np.int8)  # state[1..K] = a_1..a_K, state[0]=boundary, state[K+1]=0
    
    col1_values = []
    states_seen = {}
    
    for t in range(max_steps):
        state[0] = boundary[t % p]
        state[K+1] = 0
        
        col1_values.append(int(state[1]))
        
        # Check for repeated state at same phase
        phase = t % p
        state_key = (phase, tuple(state[1:K+1]))
        if state_key in states_seen:
            pre_period = states_seen[state_key]
            period = t - pre_period
            return col1_values, pre_period, period
        states_seen[state_key] = t
        
        # Evolve
        new_state = np.zeros(K+2, dtype=np.int8)
        for k in range(1, K+1):
            new_state[k] = state[k-1] ^ (state[k] | state[k+1])
        state = new_state
    
    return col1_values, None, None

# Test with different periodic boundaries
boundaries = {
    "10 (p=2)": [1, 0],
    "110 (p=3)": [1, 1, 0],
    "1010 (p=4)": [1, 0, 1, 0],
    "11010 (p=5)": [1, 1, 0, 1, 0],
}

for name, boundary in boundaries.items():
    p = len(boundary)
    print(f"\nBoundary: {name}")
    print(f"{'K':>5} | {'Pre-period':>12} {'Period':>10} {'Period/p':>10}")
    print("-" * 45)
    
    for K in range(2, 41):
        max_steps = min(2 * 2**K, 200000)
        col1, pre_per, per = evolve_right_half_truncated(K, boundary, max_steps)
        
        if per is not None:
            print(f"{K:5d} | {pre_per:12d} {per:10d} {per/p:10.1f}")
        else:
            print(f"{K:5d} | {'not found':>12} {'':>10}")

print("\n\n--- Checking whether col 1 values stabilize across truncations ---")
# For boundary "10", compare col 1 across different K values
boundary = [1, 0]
print(f"\nBoundary: 10 (p=2)")
check_len = 500
prev_values = None
for K in [5, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100]:
    max_steps = check_len + 100
    col1, _, _ = evolve_right_half_truncated(K, boundary, max_steps)
    values = col1[:check_len]
    if prev_values is not None:
        # Find first disagreement
        agree_up_to = check_len
        for i in range(min(check_len, len(values), len(prev_values))):
            if values[i] != prev_values[i]:
                agree_up_to = i
                break
        print(f"K={K:4d}: agrees with K={prev_K} up to t={agree_up_to} (validity ~2K={2*prev_K})")
    else:
        print(f"K={K:4d}: (baseline)")
    prev_values = values
    prev_K = K
