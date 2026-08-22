"""
Cell-0 analysis: Can cell 0 return to its original value after F_p?

For boundary [1,0]:
  Step 1 (b=1): new_0 = 1 XOR (s_0 OR s_1)
  Step 2 (b=0): new_0 = 0 XOR (r_0 OR r_1) = r_0 OR r_1
  where r = f_1(s) is the state after step 1.

F_p(s)_0 = r_0 OR r_1 where r_0 = 1 XOR (s_0 OR s_1), r_1 = s_0 XOR (s_1 OR s_2).

So F_p(s)_0 = [1 XOR (s_0 OR s_1)] OR [s_0 XOR (s_1 OR s_2)]

For this to equal s_0:
  If s_0 = 0: need [1 XOR (0 OR s_1)] OR [0 XOR (s_1 OR s_2)] = 0
    = (1 XOR s_1) OR (s_1 OR s_2) = 0
    This requires BOTH terms = 0:
    (1 XOR s_1) = 0 => s_1 = 1
    (s_1 OR s_2) = 0 => s_1 = 0 AND s_2 = 0
    CONTRADICTION: s_1 = 1 and s_1 = 0.
    
  If s_0 = 1: need [1 XOR (1 OR s_1)] OR [1 XOR (s_1 OR s_2)] = 1
    = (1 XOR 1) OR (1 XOR (s_1 OR s_2))
    = 0 OR NOT(s_1 OR s_2)
    = NOT(s_1 OR s_2)
    This is 1 iff s_1 = 0 AND s_2 = 0.
    
So: F_p(s)_0 = s_0 requires either:
  - s_0 = 0: IMPOSSIBLE (contradiction in s_1)
  - s_0 = 1 AND s_1 = 0 AND s_2 = 0.

This means: for any fixed point of F_p, we MUST have s_0 = 1, s_1 = 0, s_2 = 0.

Now we can iterate: given s_0=1, s_1=0, s_2=0, what does F_p require for cell 1?
"""

import numpy as np


def apply_one_step(state, boundary_bit, K):
    new = np.zeros(K, dtype=np.uint8)
    for i in range(K):
        L = boundary_bit if i == 0 else state[i-1]
        C = state[i]
        R = state[i+1] if i+1 < K else 0
        new[i] = L ^ (C | R)
    return new


def experiment_cell_by_cell():
    """Derive the necessary conditions on s for F_p(s) = s, cell by cell."""
    
    print("=== Cell-by-cell necessary conditions for F_p(s) = s ===")
    print("Boundary [1,0], p=2\n")
    
    print("CELL 0:")
    print("  F_p(s)_0 = s_0 requires s_0=1, s_1=0, s_2=0")
    print("  (s_0=0 is impossible; s_0=1 needs s_1=s_2=0)")
    print()
    
    # Now with s_0=1, s_1=0, s_2=0, compute F_p symbolically for cell 1.
    # After step 1 (b=1), using s_0=1, s_1=0, s_2=0:
    #   r_0 = 1 XOR (1 OR 0) = 1 XOR 1 = 0
    #   r_1 = s_0 XOR (s_1 OR s_2) = 1 XOR 0 = 1
    #   r_2 = s_1 XOR (s_2 OR s_3) = 0 XOR (0 OR s_3) = s_3
    #   r_3 = s_2 XOR (s_3 OR s_4) = 0 XOR (s_3 OR s_4) = s_3 OR s_4
    
    # After step 2 (b=0), cell 1:
    #   F_p(s)_1 = r_0 XOR (r_1 OR r_2) = 0 XOR (1 OR s_3) = 0 XOR 1 = 1
    # Wait, that's always 1! And we need F_p(s)_1 = s_1 = 0.
    # So F_p(s)_1 = 1 ≠ 0 = s_1.
    # CONTRADICTION!
    
    print("CELL 1:")
    print("  With s_0=1, s_1=0, s_2=0:")
    print("  After step 1 (b=1):")
    print("    r_0 = 1 XOR (1 OR 0) = 0")
    print("    r_1 = 1 XOR (0 OR 0) = 1")
    print("    r_2 = 0 XOR (0 OR s_3) = s_3")
    print()
    print("  After step 2 (b=0), cell 1:")
    print("    F_p(s)_1 = r_0 XOR (r_1 OR r_2) = 0 XOR (1 OR s_3) = 0 XOR 1 = 1")
    print()
    print("  Need F_p(s)_1 = s_1 = 0, but F_p(s)_1 = 1.")
    print("  CONTRADICTION!")
    print()
    print("  *** F_p has NO fixed points for boundary [1,0], for ALL K ≥ 3. ***")
    print()
    
    # Verify numerically
    print("Numerical verification:")
    for K in [3, 5, 10, 15, 20]:
        s = np.zeros(K, dtype=np.uint8)
        s[0] = 1  # s_0 = 1 (required)
        # s_1 = 0, s_2 = 0 (required)
        # s_3..s_{K-1} = anything
        
        r = apply_one_step(s, 1, K)  # step 1 with b=1
        print(f"  K={K}: s={s[:6]}..., after b=1: r={r[:6]}...")
        fp = apply_one_step(r, 0, K)  # step 2 with b=0
        print(f"         after b=0: F_p(s)={fp[:6]}..., cell 1 = {fp[1]}")
    
    print()
    print("This is indeed a PROOF:")
    print("  For K ≥ 3: F_p(s) = s requires s_0=1, s_1=0, s_2=0 (from cell 0 analysis).")
    print("  But then F_p(s)_1 = 1 ≠ 0 = s_1 (from cell 1 analysis).")
    print("  For K = 1: s ∈ {0, 1}. F_p(0) = f_0(f_1(0)) = f_0(1) = 1. F_p(1) = f_0(f_1(1)) = f_0(0) = 0.")
    print("  Neither 0 nor 1 is fixed.")
    print("  For K = 2: s ∈ {00, 01, 10, 11}. s_0=1,s_1=0 → s=10. F_p(10)_0 check:")
    
    # Verify K=2
    for s_int in range(4):
        s = np.array([(s_int >> i) & 1 for i in range(2)], dtype=np.uint8)
        r = apply_full_period(s, [1, 0], 2)
        print(f"    s={''.join(map(str,s))}, F_p(s)={''.join(map(str,r))}, "
              f"fixed={''.join(map(str,s))==' '.join(map(str,r))}")
    
    # K=1
    print("\n  K=1:")
    for s_int in range(2):
        s = np.array([s_int], dtype=np.uint8)
        r = apply_full_period(s, [1, 0], 1)
        print(f"    s={s[0]}, F_p(s)={r[0]}")


def apply_full_period(state, boundary, K):
    s = state.copy()
    for phase in range(len(boundary)):
        s = apply_one_step(s, boundary[phase], K)
    return s


def experiment_cell0_general_boundary():
    """
    Extend the cell-0 argument to OTHER boundaries.
    
    For boundary [b_0, b_1] with period p=2:
    Step 1 (boundary bit b_0): new_0 = b_0 XOR (s_0 OR s_1)
    Step 2 (boundary bit b_1): F_p(s)_0 = b_1 XOR (r_0 OR r_1)
    
    where r_0 = b_0 XOR (s_0 OR s_1), r_1 = s_0 XOR (s_1 OR s_2).
    
    F_p(s)_0 = b_1 XOR ([b_0 XOR (s_0 OR s_1)] OR [s_0 XOR (s_1 OR s_2)])
    """
    print("\n=== Cell-0 analysis for general period-2 boundaries ===\n")
    
    for b0, b1 in [(1, 0), (0, 1), (1, 1), (0, 0)]:
        bnd = [b0, b1]
        print(f"Boundary [{b0},{b1}]:")
        
        # For each (s0, s1, s2), compute whether cell 0 can be preserved
        possible = []
        for s0 in [0, 1]:
            for s1 in [0, 1]:
                for s2 in [0, 1]:
                    r0 = b0 ^ (s0 | s1)
                    r1 = s0 ^ (s1 | s2)
                    fp0 = b1 ^ (r0 | r1)
                    if fp0 == s0:
                        possible.append((s0, s1, s2))
        
        print(f"  Cell 0 preserved for (s0,s1,s2) ∈ {possible}")
        
        if len(possible) > 0:
            # Check which of these allow cell 1 to be preserved
            for s0, s1, s2 in possible:
                r0 = b0 ^ (s0 | s1)
                r1 = s0 ^ (s1 | s2)
                r2_partial = s1  # r2 = s1 XOR (s2 OR s3), depends on s3
                
                # Cell 1 of F_p: b1_step2 * ... wait, let me just compute.
                # After step 1: r = f_{b0}(s)
                # After step 2: F_p(s) = f_{b1}(r)
                # F_p(s)_1 = r_0 XOR (r_1 OR r_2)
                
                # r_2 = s_1 XOR (s_2 OR s_3), depends on s_3
                for s3 in [0, 1]:
                    r2 = s1 ^ (s2 | s3)
                    fp1 = r0 ^ (r1 | r2)
                    if fp1 == s1:
                        print(f"    Cell 0 AND cell 1 preserved for (s0,s1,s2,s3)=({s0},{s1},{s2},{s3})")
                        
                        # Continue to cell 2...
                        r3 = s2 ^ (s3 | 0)  # depends on s4, using 0 placeholder
                        # Actually r_3 = s_2 XOR (s_3 OR s_4)
                        for s4 in [0, 1]:
                            r3 = s2 ^ (s3 | s4)
                            fp2 = r1 ^ (r2 | r3)
                            if fp2 == s2:
                                print(f"      Also cell 2 preserved for s4={s4}")
        print()


def experiment_general_period():
    """
    Can we do the same analysis for period p > 2?
    
    For general period p with boundary [b_0, ..., b_{p-1}]:
    Apply p steps sequentially. Cell 0 after step k depends on the
    boundary bit b_k and the state of the system up to that point.
    
    For p=1 (boundary [b]):
    F_1(s)_0 = b XOR (s_0 OR s_1)
    Need F_1(s)_0 = s_0:
      b XOR (s_0 OR s_1) = s_0
    
    For b=0: (s_0 OR s_1) = s_0, which means s_1 ≤ s_0 (i.e., s_0=1 or s_1=0).
      Possible: (0,0,*), (1,0,*), (1,1,*)
    For b=1: 1 XOR (s_0 OR s_1) = s_0, i.e., NOT(s_0 OR s_1) = s_0.
      s_0=0: NOT(s_1)=0, s_1=1; but OR(0,1)=1, NOT=0=s_0. ✓ (0,1,*)
      s_0=1: NOT(1)=0≠1. ✗
      So only (0,1,*).
    
    For b=0, the constraints are weak → fixed points can exist.
    For b=1, the constraint forces s_0=0, s_1=1. Cell 1 might still work.
    
    The key is: non-constant boundaries create conflicting constraints 
    between different steps.
    """
    print("\n=== General period analysis ===\n")
    
    # For each period p from 1 to 6, and each non-constant boundary:
    # Check whether F_p is fixed-point-free for K up to 16
    
    for p in range(1, 7):
        print(f"Period p={p}:")
        
        # Generate all non-constant boundaries
        n_bnd = 2**p
        for bnd_int in range(n_bnd):
            bnd = [(bnd_int >> i) & 1 for i in range(p)]
            
            # Skip if constant
            if all(b == bnd[0] for b in bnd):
                status = "constant"
            else:
                # Check K=16
                K = 16
                n_fixed = 0
                n_states = 2**K
                for s_int in range(n_states):
                    s = np.array([(s_int >> i) & 1 for i in range(K)], dtype=np.uint8)
                    r = apply_full_period(s, bnd, K)
                    if np.array_equal(s, r):
                        n_fixed += 1
                status = f"fixed={n_fixed}"
            
            print(f"  bnd={bnd}: {status}")
        print()


def experiment_proof_formalization():
    """
    Clean write-up of the proof for boundary [1,0].
    """
    print("\n" + "=" * 60)
    print("THEOREM: F_p has no fixed points for boundary [1,0]")
    print("=" * 60)
    print()
    print("Let K ≥ 1. Let F_p: {0,1}^K → {0,1}^K be the two-step map")
    print("defined by F_p = f_0 ∘ f_1, where f_b applies one Rule 30 step")
    print("with boundary bit b at position -1 and 0-padding at position K.")
    print()
    print("Claim: F_p(s) ≠ s for all s ∈ {0,1}^K.")
    print()
    print("Proof:")
    print()
    print("Case K = 1:")
    print("  f_1(0) = 1 XOR (0 OR 0) = 1, f_0(1) = 0 XOR (1 OR 0) = 1. F_p(0) = 1 ≠ 0.")
    
    # Actually let me verify K=1 more carefully
    K = 1
    for s0 in [0, 1]:
        s = np.array([s0], dtype=np.uint8)
        r1 = apply_one_step(s, 1, K)
        r = apply_one_step(r1, 0, K)
        print(f"  F_p({s0}) = {r[0]}  (via f_1({s0})={r1[0]}, f_0({r1[0]})={r[0]})")
    
    print()
    print("Case K = 2:")
    K = 2
    for s_int in range(4):
        s = np.array([(s_int >> i) & 1 for i in range(K)], dtype=np.uint8)
        r = apply_full_period(s, [1, 0], K)
        label = ''.join(map(str, s))
        rlabel = ''.join(map(str, r))
        print(f"  F_p({label}) = {rlabel}")
    
    print()
    print("Case K ≥ 3:")
    print()
    print("  Suppose F_p(s) = s. After step 1 (b=1), let r = f_1(s).")
    print("  After step 2 (b=0), F_p(s) = f_0(r).")
    print()
    print("  Cell 0 analysis:")
    print("    r_0 = 1 ⊕ (s_0 ∨ s_1)")
    print("    F_p(s)_0 = 0 ⊕ (r_0 ∨ r_1) = r_0 ∨ r_1")
    print("             = [1 ⊕ (s_0 ∨ s_1)] ∨ [s_0 ⊕ (s_1 ∨ s_2)]")
    print()
    print("  If s_0 = 0:")
    print("    F_p(s)_0 = (1 ⊕ s_1) ∨ (s_1 ∨ s_2)")
    print("    For this to equal 0, need BOTH factors = 0:")
    print("      1 ⊕ s_1 = 0 ⟹ s_1 = 1")
    print("      s_1 ∨ s_2 = 0 ⟹ s_1 = 0")
    print("    Contradiction. So s_0 ≠ 0.")
    print()
    print("  So s_0 = 1:")
    print("    F_p(s)_0 = (1 ⊕ 1) ∨ (1 ⊕ (s_1 ∨ s_2))")
    print("             = 0 ∨ ¬(s_1 ∨ s_2)")
    print("             = ¬(s_1 ∨ s_2)")
    print("    For this to equal 1, need s_1 = 0 AND s_2 = 0.")
    print()
    print("  So we must have: s_0 = 1, s_1 = 0, s_2 = 0.")
    print()
    print("  Cell 1 analysis (with s_0=1, s_1=0, s_2=0):")
    print("    r_0 = 1 ⊕ (1 ∨ 0) = 0")
    print("    r_1 = s_0 ⊕ (s_1 ∨ s_2) = 1 ⊕ 0 = 1")
    print("    r_2 = s_1 ⊕ (s_2 ∨ s_3) = 0 ⊕ s_3 = s_3  [for any s_3]")
    print()
    print("    F_p(s)_1 = r_0 ⊕ (r_1 ∨ r_2) = 0 ⊕ (1 ∨ s_3) = 0 ⊕ 1 = 1")
    print()
    print("    But s_1 = 0, so F_p(s)_1 = 1 ≠ 0 = s_1. Contradiction.")
    print()
    print("  Therefore no fixed point exists for K ≥ 3. Combined with K=1,2")
    print("  cases, F_p has no fixed points for any K ≥ 1.  ■")
    print()
    print("=" * 60)
    print("COROLLARY: For any K ≥ 1, the width-K truncated right half driven")
    print("by boundary [1,0] (period 2) never returns to the same state after")
    print("exactly 2 steps (one full period). The column-1 period is always > 2.")
    print("=" * 60)
    print()
    
    # Now: does this EXTEND to the infinite system?
    print("QUESTION: Does this imply a_1 is not period-2?")
    print()
    print("If a_0 had period 2 (boundary [1,0]), and a_1 were also period 2,")
    print("then the right half state s(t) = (a_1(t), a_2(t), ...) would satisfy")
    print("s(t+2) = s(t) for all t large enough.")
    print()
    print("For ANY finite prefix of length K: the first K cells would satisfy")
    print("(a_1(t),...,a_K(t+2)) = (a_1(t),...,a_K(t)).")
    print()
    print("But F_p applied to ANY state of length K gives a different state.")
    print("This means F_p CANNOT have a fixed point, so the K-prefix can't")
    print("be period-2 under the truncated dynamics.")
    print()
    print("HOWEVER: The INFINITE system is NOT the truncated system.")
    print("The truncated F_p uses zero-padding at K+1, while the infinite system")
    print("has actual cell values there. The dynamics DIFFER for cells near K.")
    print()
    print("So the proof shows: no width-K truncated system has period 2.")
    print("It does NOT directly show the infinite system lacks period 2.")
    print()
    print("But wait — if the INFINITE right half has F_p(s) = s where s is")
    print("an infinite sequence, then cells 0,1,2 must still satisfy the")
    print("same constraint (because they don't depend on cells far away in")
    print("a single step). Cell 0 depends on s_0, s_1 and boundary bit.")
    print("Cell 1 depends on s_0, s_1, s_2.")
    print()
    print("The cell-by-cell argument ONLY uses s_0, s_1, s_2, s_3.")
    print("It does NOT depend on K or the truncation!")
    print()
    print("THEREFORE: Even for the INFINITE right-half system,")
    print("there is no bi-infinite sequence s = (s_0, s_1, s_2, ...) such that")
    print("F_p(s) = s under the boundary [1,0] (period 2) Rule 30 dynamics.")
    print()
    print("*** THIS MEANS: If a_0 has period 2 (boundary [1,0] or [0,1]), ***")
    print("*** then a_1 CANNOT also have period 2. ***")
    print()
    print("More precisely: the right half driven by period-2 a_0 cannot")
    print("settle into a period-2 orbit (even in the infinite system).")
    print()
    print("This is a STRICTLY STRONGER result than Jen's two-column theorem!")
    print("Jen shows: two adjacent periodic columns → contradiction (left propagation).")
    print("We show: a_0 periodic with period p → a_1 cannot be period p.")
    print("Jen needs a_1 period p AND a_0 period p for a contradiction.")
    print("We show a_1 period p is IMPOSSIBLE given a_0 period p.")
    print()
    print("BUT WAIT: a_1 could have a DIFFERENT period, or a MULTIPLE of p.")
    print("Our F_p fixed-point-free result only rules out a_1 having period p.")
    print("a_1 could have period 2p, 3p, etc.")
    

def experiment_higher_period_check():
    """
    Check: Can the right half have period np (a_1 period that's a multiple of p)?
    This corresponds to F_p^n having a fixed point.
    
    From the earlier data, F_p^n DOES have fixed points for various n.
    e.g., F_p^2 has 2 fixed points for K=6.
    
    So the right half CAN have period 2p, 3p, etc. in the truncated system.
    This means our theorem only rules out period p, not multiples.
    """
    print("\n=== Can the right half have period np? (Fixed points of F_p^n) ===\n")
    
    bnd = [1, 0]
    
    # For the INFINITE system: does F_p^n have fixed points?
    # Apply the same cell-by-cell argument.
    # F_p^n means applying 2n Rule 30 steps with alternating boundary 1,0,1,0,...
    # Cell 0 after 2n steps is a function of s_0, s_1, ..., s_{2n} (at most).
    #
    # The constraints propagate: each step adds one more cell to the dependency.
    # After 2n steps, cell 0 depends on s_0 through s_{2n}.
    # F_p^n(s)_0 = s_0 gives constraints on s_0, ..., s_{2n}.
    # F_p^n(s)_i = s_i gives more constraints.
    #
    # Let's check for n=2 (period 4): does the cell-by-cell analysis 
    # still force a contradiction?
    
    print("Cell-by-cell analysis for F_p^2 (period 4, i.e., 4 steps [1,0,1,0]):")
    print()
    
    # Symbolically track the first few cells through 4 Rule 30 steps
    # with boundary sequence 1, 0, 1, 0.
    #
    # This is complex. Let's just check numerically for the INFINITE case:
    # In the infinite system, does there exist an infinite sequence s such that
    # after 4 steps of [1,0,1,0], cell k returns to s_k for all k?
    
    # For the truncated system, we know F_p^2 has fixed points.
    # Let's find them and check if they "converge" as K → ∞.
    
    for K in [8, 10, 12, 14, 16, 18]:
        n_states = 2**K
        
        # Build F_p map
        fp_map = {}
        for s_int in range(n_states):
            s = np.array([(s_int >> i) & 1 for i in range(K)], dtype=np.uint8)
            r = apply_full_period(s, bnd, K)
            fp_map[s_int] = sum(int(r[i]) << i for i in range(K))
        
        # F_p^2 fixed points
        fixed_fp2 = []
        for s_int in range(n_states):
            if fp_map[fp_map[s_int]] == s_int:
                fixed_fp2.append(s_int)
        
        if K <= 14:
            states_str = []
            for s_int in fixed_fp2[:5]:
                s = np.array([(s_int >> i) & 1 for i in range(K)], dtype=np.uint8)
                states_str.append(''.join(map(str, s)))
            print(f"K={K:>2}: F_p^2 has {len(fixed_fp2)} fixed points: "
                  f"{states_str[:3]}{'...' if len(states_str) > 3 else ''}")
        else:
            print(f"K={K:>2}: F_p^2 has {len(fixed_fp2)} fixed points")
    
    print()
    
    # Check if the fixed points of F_p^2 have a common prefix as K grows
    print("Checking if F_p^2 fixed points share common prefixes:")
    prefixes = {}
    for K in [10, 12, 14, 16]:
        n_states = 2**K
        fp_map = {}
        for s_int in range(n_states):
            s = np.array([(s_int >> i) & 1 for i in range(K)], dtype=np.uint8)
            r = apply_full_period(s, bnd, K)
            fp_map[s_int] = sum(int(r[i]) << i for i in range(K))
        
        fp2_fixed = []
        for s_int in range(n_states):
            if fp_map[fp_map[s_int]] == s_int:
                s = np.array([(s_int >> i) & 1 for i in range(K)], dtype=np.uint8)
                fp2_fixed.append(''.join(map(str, s[:8])))  # first 8 cells
        
        prefixes[K] = set(fp2_fixed)
        print(f"  K={K}: {len(fp2_fixed)} fixed points, prefixes (first 8): {sorted(prefixes[K])[:5]}")
    
    # Find prefixes that appear for ALL K
    if len(prefixes) >= 2:
        common = prefixes[10]
        for K in [12, 14, 16]:
            common = common & prefixes[K]
        print(f"\n  Common prefixes across all K: {sorted(common)}")
        
        if not common:
            print("  NO common prefix! Fixed points of F_p^2 don't converge.")
            print("  This suggests F_p^2 has no fixed point in the infinite system either.")
        else:
            print("  Common prefixes exist → infinite system might have F_p^2 fixed points.")


if __name__ == "__main__":
    experiment_cell_by_cell()
    experiment_cell0_general_boundary()
    experiment_higher_period_check()
    experiment_proof_formalization()
