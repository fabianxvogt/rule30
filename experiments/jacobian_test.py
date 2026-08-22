#!/usr/bin/env python3
"""
Understand WHY the h-step map is bijective from every starting state.

Key insight to test: The internal map (ignoring position 0) 
  s -> (s'_1, ..., s'_{h-1})
is always bijective (left-permutativity). Then b sets s'_0 freely via XOR.

But for general starts, the light-cone argument doesn't apply.
Let's examine the structure more carefully.

For h steps from arbitrary s_0 with bits b_0,...,b_{h-1}:
- s_1 = f(s_0, b_0)
- s_2 = f(s_1, b_1)  
- ...
- s_h = f(s_{h-1}, b_{h-1})

where f(s, b) = rule30_next_tuple(s, b).

The question: is the map (b_0,...,b_{h-1}) -> s_h injective for fixed s_0?

We know f(s, b) differs from f(s, b') only at position 0 (since b only enters position 0).
So f(s, 0) and f(s, 1) differ exactly at position 0.

This means: changing b_k ONLY affects positions 0..something in subsequent steps.

Actually - let me think about what "b_k affects" in s_h.

Step k: b_k changes s_{k+1}[0] (flips it), everything else same.
Step k+1: s_{k+1}[0] being different affects s_{k+2}[0] and s_{k+2}[1].
  - s_{k+2}[0] = b_{k+1} XOR (s_{k+1}[0] OR s_{k+1}[1]) — changed
  - s_{k+2}[1] = s_{k+1}[0] XOR (s_{k+1}[1] OR s_{k+1}[2]) — changed
Step k+2: the change at positions 0,1 propagates to 0,1,2
...
After (h-k) additional steps, the change has spread to positions 0...(h-k).

So changing b_k affects positions 0 through (h-1-k) in s_h.

In particular:
- b_{h-1} affects only position 0 of s_h
- b_{h-2} affects positions 0,1 of s_h
- b_{h-3} affects positions 0,1,2 of s_h
- ...
- b_0 affects positions 0...(h-1) of s_h (all positions)

This is UPPER TRIANGULAR structure! (with position 0 ↔ MSB, position h-1 ↔ LSB)

b_{h-1} -> affects s_h[0] only (and does so by XOR, so it toggles it)
b_{h-2} -> affects s_h[0] and s_h[1]
...

Actually wait, this is the REVERSE triangular: b_{h-1-j} affects positions 0..j.
The Jacobian (partial derivatives over GF(2)) should be lower-triangular when 
rows are indexed by position 0..h-1 and columns by b_{h-1}, b_{h-2}, ..., b_0.

A lower-triangular matrix over GF(2) is invertible iff all diagonal entries are 1.

The diagonal entry ∂s_h[j] / ∂b_{h-1-j}: does b_{h-1-j} always have a non-zero
effect on position j?

Let's verify computationally.
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import rule30_next_tuple
import random


def compute_jacobian(h, s0):
    """Compute the GF(2) Jacobian of the map (b_0,...,b_{h-1}) -> s_h, 
    starting from state s0.
    
    J[i][j] = 1 iff flipping b_j changes s_h[i].
    """
    # Base: all zeros boundary
    base_boundary = [0] * h
    state_base = s0
    for b in base_boundary:
        state_base = rule30_next_tuple(state_base, b)[:h]
    
    jacobian = [[0]*h for _ in range(h)]
    
    for j in range(h):
        # Flip b_j
        boundary = list(base_boundary)
        boundary[j] = 1
        state = s0
        for b in boundary:
            state = rule30_next_tuple(state, b)[:h]
        
        for i in range(h):
            jacobian[i][j] = state[i] ^ state_base[i]
    
    return jacobian


def main():
    for h in [5, 8, 10, 12]:
        print(f"\n=== h={h} ===")
        
        # Test from all-zeros
        s0 = (0,) * h
        J = compute_jacobian(h, s0)
        
        print(f"Jacobian from all-zeros (rows=positions, cols=b_0..b_{h-1}):")
        if h <= 10:
            for row in J:
                print("  " + "".join(str(x) for x in row))
        
        # Check diagonal (position j, bit b_{h-1-j})
        diag = [J[j][h-1-j] for j in range(h)]
        print(f"  Diagonal (J[j][h-1-j]): {diag}")
        print(f"  Lower-triangular? ", end="")
        
        lt = True
        for i in range(h):
            for j in range(h):
                # j-th column corresponds to b_j
                # b_j should only affect positions 0...(h-1-j)
                # So J[i][j] should be 0 if i > h-1-j, i.e., j > h-1-i
                if j > h-1-i and J[i][j] != 0:
                    lt = False
        print(f"{'YES' if lt else 'NO'}")
        
        # Check from random starts
        random.seed(42)
        all_diag_one = True
        all_lt = True
        for trial in range(min(100, 2**h)):
            rs = tuple(random.randint(0, 1) for _ in range(h))
            J2 = compute_jacobian(h, rs)
            d = [J2[j][h-1-j] for j in range(h)]
            if not all(x == 1 for x in d):
                all_diag_one = False
                print(f"  DIAGONAL FAIL at start={''.join(str(x) for x in rs)}: {d}")
            for i in range(h):
                for j in range(h):
                    if j > h-1-i and J2[i][j] != 0:
                        all_lt = False
        
        print(f"  100 random starts: all diagonal=1? {all_diag_one}, all lower-triangular? {all_lt}")
        
        # Determinant check (should be 1 if lower-triangular with all-1 diagonal)
        # But let's also verify by computing rank
        if h <= 10:
            # Gaussian elimination over GF(2)
            random.seed(99)
            rs = tuple(random.randint(0, 1) for _ in range(h))
            J3 = compute_jacobian(h, rs)
            # Copy
            M = [row[:] for row in J3]
            rank = 0
            for col in range(h):
                # Find pivot
                pivot = None
                for row in range(rank, h):
                    if M[row][col]:
                        pivot = row
                        break
                if pivot is None:
                    continue
                M[rank], M[pivot] = M[pivot], M[rank]
                for row in range(h):
                    if row != rank and M[row][col]:
                        for c in range(h):
                            M[row][c] ^= M[rank][c]
                rank += 1
            print(f"  Rank of Jacobian (random start): {rank}/{h}")


if __name__ == "__main__":
    main()
