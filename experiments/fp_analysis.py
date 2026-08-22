"""
Deep analysis of F_p (the p-step map on the right half) and its fixed-point-free property.

Key finding from spacetime_consistency.py: For boundary [1,0] (period 2),
F_p has ZERO fixed points for ALL K tested (1..18).

If F_p is fixed-point-free for ALL K, then the truncated right half can 
never settle into a period-p cycle from ANY initial state. This would be 
a strong structural property.

Even stronger: if F_p^n has no fixed points for "most" n, the right half
avoids many possible periods.

This experiment:
1. Verify the fixed-point-free property more thoroughly
2. Check other boundaries (periods 3, 5, etc.)
3. Analyze WHY there are no fixed points (algebraic structure)
4. Check if F_p is a permutation (bijective) or not
5. Explore what this implies for the full (infinite) system
"""

import numpy as np
from collections import defaultdict
import time


def apply_one_step(state, boundary_bit, K):
    """Apply one Rule 30 step to width-K right half."""
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


def state_to_int(s):
    val = 0
    for i in range(len(s)):
        val |= int(s[i]) << i
    return val


def int_to_state(val, K):
    return np.array([(val >> i) & 1 for i in range(K)], dtype=np.uint8)


def experiment_fixed_point_free():
    """Check if F_p is fixed-point-free for various boundaries and K."""
    print("=== Fixed-point-free check for F_p ===\n")
    
    boundaries = {
        '[1,0] (p=2)': [1, 0],
        '[0,1] (p=2)': [0, 1],
        '[1,1] (p=1)': [1, 1],  # constant 1, period 1
        '[0,0] (p=1)': [0, 0],  # constant 0, period 1
        '[1,0,0] (p=3)': [1, 0, 0],
        '[1,1,0] (p=3)': [1, 1, 0],
        '[1,0,1,0,0] (p=5)': [1, 0, 1, 0, 0],
    }
    
    for name, bnd in boundaries.items():
        p = len(bnd)
        print(f"Boundary {name}:")
        for K in range(1, 21):
            n_states = 2**K
            if n_states > 2**20:
                break
            
            n_fixed = 0
            for s_int in range(n_states):
                state = int_to_state(s_int, K)
                result = apply_full_period(state, bnd, K)
                r_int = state_to_int(result)
                if s_int == r_int:
                    n_fixed += 1
            
            marker = " ✓" if n_fixed == 0 else f" ← {n_fixed} fixed point(s)!"
            print(f"  K={K:>2}: {n_fixed} fixed points{marker}")
        print()


def experiment_fp_bijectivity():
    """Check if F_p is a bijection (permutation) on {0,1}^K."""
    print("=== Bijectivity of F_p ===\n")
    
    boundaries = {
        '[1,0] (p=2)': [1, 0],
        '[1,0,0] (p=3)': [1, 0, 0],
        '[0,0] (p=1, const 0)': [0, 0],
        '[1,1] (p=1, const 1)': [1, 1],
    }
    
    for name, bnd in boundaries.items():
        p = len(bnd)
        print(f"Boundary {name}:")
        for K in range(1, 19):
            n_states = 2**K
            fp_map = {}
            image = set()
            for s_int in range(n_states):
                state = int_to_state(s_int, K)
                result = apply_full_period(state, bnd, K)
                r_int = state_to_int(result)
                fp_map[s_int] = r_int
                image.add(r_int)
            
            is_bij = len(image) == n_states
            print(f"  K={K:>2}: |image|={len(image):>6}, 2^K={n_states:>6}, "
                  f"bijective={is_bij}")
        print()


def experiment_fp_powers():
    """
    Check fixed points of F_p^n for various n.
    If F_p^n has no fixed point, then there's no period-n orbit of F_p of length dividing n.
    """
    print("=== Fixed points of F_p^n (boundary [1,0]) ===\n")
    
    bnd = [1, 0]
    
    for K in [6, 8, 10, 12, 14]:
        n_states = 2**K
        
        # Build F_p map
        fp_map = {}
        for s_int in range(n_states):
            state = int_to_state(s_int, K)
            result = apply_full_period(state, bnd, K)
            fp_map[s_int] = state_to_int(result)
        
        # For each n, count fixed points of F_p^n
        print(f"K={K} (2^K = {n_states}):")
        row = "  "
        for n in range(1, 31):
            # Build F_p^n by composing
            fpn_map = {}
            for s_int in range(n_states):
                current = s_int
                for _ in range(n):
                    current = fp_map[current]
                fpn_map[s_int] = current
            
            n_fixed = sum(1 for s in range(n_states) if fpn_map[s] == s)
            row += f"n={n}:{n_fixed} "
        print(row)
        print()


def experiment_single_step_maps():
    """
    Analyze the individual one-step maps f_0 and f_1 (driven by boundary bit 0 or 1).
    F_p = f_{b_{p-1}} ∘ ... ∘ f_{b_0}
    
    Key question: Are f_0, f_1 bijective individually?
    What's the structure of the semigroup generated by f_0, f_1?
    """
    print("=== Single-step maps f_0, f_1 ===\n")
    
    for K in range(1, 17):
        n_states = 2**K
        
        f = {0: {}, 1: {}}
        img = {0: set(), 1: set()}
        
        for b in [0, 1]:
            for s_int in range(n_states):
                state = int_to_state(s_int, K)
                result = apply_one_step(state, b, K)
                r_int = state_to_int(result)
                f[b][s_int] = r_int
                img[b].add(r_int)
        
        bij_0 = len(img[0]) == n_states
        bij_1 = len(img[1]) == n_states
        
        # F_p for [1,0] = f_0 ∘ f_1
        fp_img = set()
        fp_fixed = 0
        for s_int in range(n_states):
            r = f[0][f[1][s_int]]  # f_0(f_1(s)), not f_1(f_0(s))
            # Wait — boundary [1,0] means step 0 has b=1, step 1 has b=0
            # So F_p = f_0 ∘ f_1  (first apply f_1 at phase 0=b_0=1, then f_0 at phase 1=b_1=0)
            # Actually: boundary = [b_0, b_1, ...], step t uses b_{t mod p}
            # For [1,0]: step 0 uses b=1, step 1 uses b=0
            # F_p(s) = f_{b_1}(f_{b_0}(s)) = f_0(f_1(s))
            fp_img.add(r)
            if r == s_int:
                fp_fixed += 1
        
        # Also check F_p = f_1 ∘ f_0 (other composition order, for shifted phase)
        fp2_img = set()
        fp2_fixed = 0
        for s_int in range(n_states):
            r = f[1][f[0][s_int]]
            fp2_img.add(r)
            if r == s_int:
                fp2_fixed += 1
        
        print(f"K={K:>2}: f_0 bij={bij_0}, |img(f_0)|={len(img[0]):>6}; "
              f"f_1 bij={bij_1}, |img(f_1)|={len(img[1]):>6}; "
              f"F_p=f_0∘f_1 fixed={fp_fixed}, |img|={len(fp_img):>6}; "
              f"f_1∘f_0 fixed={fp2_fixed}")


def experiment_why_no_fixed_points():
    """
    Try to understand WHY F_p has no fixed points.
    
    F_p(s) = s means: starting from state s, after p steps of the boundary-driven
    right half, we return to exactly s.
    
    One insight: the rightmost non-zero cell has specific dynamics.
    If s has rightmost 1 at position k, after p steps the rightmost 1 is at
    position k + something (since Rule 30 expands rightward at speed 1 from
    a non-zero cell).
    
    More precisely: if state has a non-zero cell at position k and zero for all
    positions > k, then after one Rule 30 step, cell k+1 gets the value
    a_k XOR (a_{k+1} OR a_{k+2}) = a_k XOR 0 = a_k.
    Wait, that's the CELL at position k+1, which depends on:
    L = a_k, C = a_{k+1} = 0, R = a_{k+2} = 0
    new[k+1] = a_k XOR (0 OR 0) = a_k
    
    So if a_k = 1, then the rightmost 1 moves to k+1.
    The rightmost non-zero cell propagates right at speed 1.
    
    After p steps, the rightmost 1 is at position k+p (approximately).
    But for F_p(s) = s, we need the rightmost 1 at the SAME position.
    
    This is only possible if the rightmost 1 hits the boundary (position K)
    and gets truncated, OR if the propagation doesn't extend for some reason.
    
    Wait — a_k could be 0 at the rightmost position. Let me be more careful.
    The rightmost non-zero cell: at position k, a_k = 1. After one step:
    new[k] = a_{k-1} XOR (a_k OR a_{k+1}) = a_{k-1} XOR 1 = 1 - a_{k-1}
    new[k+1] = a_k XOR (a_{k+1} OR a_{k+2}) = 1 XOR 0 = 1
    
    So new state has a 1 at position k+1. The rightmost 1 shifted right.
    
    After p steps from a state with rightmost 1 at position k (k < K-p):
    The rightmost 1 is at position k+p.
    
    For F_p(s) = s: we'd need rightmost 1 at k+p = k, which is impossible.
    
    UNLESS the state is all zeros! Let's check: F_p(0) = ?
    """
    print("\n=== Why no fixed points: rightmost cell analysis ===\n")
    
    bnd = [1, 0]
    
    # Check F_p on the zero state
    for K in [5, 10, 15, 20]:
        state = np.zeros(K, dtype=np.uint8)
        result = apply_full_period(state, bnd, K)
        print(f"K={K}: F_p(0) = {state_to_int(result)} " 
              f"(state: {''.join(map(str, result[:min(K,30)]))})")
    
    print()
    print("F_p(0) ≠ 0 because the periodic boundary injects 1s from the left.")
    print()
    
    # For non-zero states: track rightmost 1
    print("Rightmost non-zero cell tracking (K=30, boundary [1,0]):")
    K = 30
    for start_pos in [0, 5, 10, 15, 20, 25]:
        state = np.zeros(K, dtype=np.uint8)
        state[start_pos] = 1
        
        positions = []
        for step in range(len(bnd)):
            b = bnd[step]
            state = apply_one_step(state, b, K)
            if np.any(state):
                rm = np.max(np.where(state))
            else:
                rm = -1
            positions.append(rm)
        
        print(f"  Start at {start_pos}: after p={len(bnd)} steps, "
              f"rightmost 1 at {positions[-1]}")
    
    print()
    print("KEY ARGUMENT:")
    print("  Let s have rightmost 1 at position k, with k < K - p.")
    print("  After each Rule 30 step, the rightmost 1 propagates right by 1.")
    print("  After p steps, rightmost 1 is at position k + p.")
    print("  So F_p(s) has rightmost 1 at k + p ≠ k.")
    print("  Therefore F_p(s) ≠ s for any such state.")
    print()
    print("  For k ≥ K - p: the rightmost 1 might hit the boundary and get")
    print("  truncated. Let's check if those states can be fixed points.")
    
    # Check states with rightmost 1 near boundary
    K = 15
    n_fixed = 0
    near_boundary = 0
    for s_int in range(2**K):
        state = int_to_state(s_int, K)
        if np.any(state):
            rm = np.max(np.where(state))
        else:
            rm = -1
        
        if rm >= K - len(bnd):
            near_boundary += 1
            result = apply_full_period(state, bnd, K)
            if state_to_int(result) == s_int:
                n_fixed += 1
                print(f"  FIXED POINT: K={K}, state={''.join(map(str, state))}")
    
    print(f"\n  K={K}: States with rightmost 1 at position ≥ {K-len(bnd)}: "
          f"{near_boundary}, fixed points among them: {n_fixed}")
    
    # Also check zero state
    state = np.zeros(K, dtype=np.uint8)
    result = apply_full_period(state, bnd, K)
    print(f"  Zero state: F_p(0) = {''.join(map(str, result))}, "
          f"fixed? {np.array_equal(state, result)}")
    
    print()
    print("THEOREM (informal): F_p has no fixed points because:")
    print("  1. The zero state maps to a non-zero state (boundary injects 1s)")
    print("  2. Non-zero states with rightmost 1 at k < K-p: rightmost 1 shifts to k+p ≠ k")  
    print("  3. Non-zero states with rightmost 1 near K: also not fixed (empirically)")
    print()
    print("The rightmost-1 shift argument is ALMOST a proof. For case 3 (near boundary),")
    print("the truncation could in principle create fixed points, but Rule 30's")
    print("specific dynamics prevent it.")


def experiment_orbit_period_growth():
    """
    More detailed period analysis of the IC=0 orbit under F_p.
    
    The question: does the period of the IC orbit grow without bound as K → ∞?
    If YES, this would show: no finite p can make the truncated column periodic
    with a period that stabilizes.
    
    But this is for the TRUNCATED system. We need the INFINITE system.
    """
    print("\n=== IC=0 orbit period growth under F_p ===\n")
    
    bnd = [1, 0]
    p = 2
    
    print(f"Boundary: {bnd} (period {p})")
    print(f"{'K':>3} | {'Preperiod':>10} | {'Period':>10} | {'log2(period)':>12}")
    print("-" * 50)
    
    for K in range(1, 26):
        state = np.zeros(K, dtype=np.uint8)
        seen = {}
        found = False
        
        for step in range(2000000):
            key = state.tobytes()
            if key in seen:
                preperiod = seen[key]
                period = step - seen[key]
                log2p = np.log2(period) if period > 0 else 0
                print(f"{K:>3} | {preperiod:>10} | {period:>10} | {log2p:>12.2f}")
                found = True
                break
            seen[key] = step
            state = apply_full_period(state, bnd, K)
        
        if not found:
            print(f"{K:>3} | {'> 2M':>10} | {'> 2M':>10} | {'?':>12}")
    
    print()
    print("Note: This is the period of the IC=0 orbit in the width-K truncated system,")
    print("measured in units of F_p (i.e., every p actual steps = 1 F_p step).")
    print("The actual period of column 1 is this × p.")


if __name__ == "__main__":
    experiment_single_step_maps()
    print("=" * 60)
    experiment_fixed_point_free()
    print("=" * 60)
    experiment_fp_powers()
    print("=" * 60)
    experiment_why_no_fixed_points()
    print("=" * 60)
    experiment_orbit_period_growth()
