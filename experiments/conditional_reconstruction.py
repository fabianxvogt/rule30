"""
Conditional reconstruction analysis.

NEW IDEA: Even without proving a_1 is periodic, we can analyze what happens
when we TRY to reconstruct leftward using only the periodic a_0.

Proposition 2 requires TWO adjacent periodic columns with common period and
same pre-period to reconstruct leftward. But what if we relax this?

APPROACH 1: "Conditional left reconstruction"
When a_0(t) = 1, we can compute a_{-1}(t+1) WITHOUT knowing a_1(t):
  a_{-1}(t+1) = a_0(t) XOR (a_{-1}(t) OR a_0(t))  -- NO, this is wrong
  
Actually: Rule 30 says a_x(t+1) = a_{x-1}(t) XOR (a_x(t) OR a_{x+1}(t))
So x=-1: a_{-1}(t+1) = a_{-2}(t) XOR (a_{-1}(t) OR a_0(t))

We want to SOLVE for a_{-1}(t) given a_0(t+1) and a_0(t), a_1(t).
From x=0: a_0(t+1) = a_{-1}(t) XOR (a_0(t) OR a_1(t))
So: a_{-1}(t) = a_0(t+1) XOR (a_0(t) OR a_1(t))

When a_0(t) = 1:
  a_0(t) OR a_1(t) = 1 (regardless of a_1(t))
  So a_{-1}(t) = a_0(t+1) XOR 1 = 1 - a_0(t+1)
  → a_{-1} is DETERMINED by a_0 alone when a_0(t) = 1 !!!

When a_0(t) = 0:
  a_0(t) OR a_1(t) = a_1(t)
  So a_{-1}(t) = a_0(t+1) XOR a_1(t)
  → a_{-1} DEPENDS on a_1 when a_0(t) = 0

So: a_{-1}(t) is fully determined at the ~60% of times when a_0(t) = 1,
and depends on the unknown a_1(t) at the ~40% of times when a_0(t) = 0.

QUESTION: Is this "partial reconstruction" enough to force a contradiction?

The idea: if a_0 has period p, then a_{-1} is determined at roughly 60% of times.
The remaining 40% are "free" (depend on a_1). Can we show that no choice of 
these free bits makes a_{-1} periodic? If a_{-1} CAN'T be periodic, then we
can't construct a valid spacetime → contradiction.

Actually, we need to be more careful. The question is not whether a_{-1} is 
periodic. The question is whether a VALID spacetime exists where a_0 is periodic.
"""

import numpy as np


def simulate_full_rule30(T, width):
    """
    Simulate full Rule 30 from single cell IC for T steps.
    Returns grid[t][x] indexed from -width to +width.
    """
    W = 2 * width + 1
    grid = np.zeros((T, W), dtype=np.uint8)
    grid[0, width] = 1  # center cell at x=0
    
    for t in range(T - 1):
        for x in range(1, W - 1):
            grid[t + 1, x] = grid[t, x - 1] ^ (grid[t, x] | grid[t, x + 1])
    
    return grid  # grid[t][width + x] = a_x(t)


def experiment_conditional_reconstruction():
    """
    Test the conditional reconstruction: when a_0(t) = 1, a_{-1}(t) is determined.
    Verify this using the actual Rule 30 spacetime.
    """
    print("=== Conditional reconstruction verification ===\n")
    
    T = 200
    width = T + 5
    grid = simulate_full_rule30(T, width)
    center = width  # index offset
    
    correct_count = 0
    total_when_c1 = 0
    total_when_c0 = 0
    errors_c1 = 0
    errors_c0 = 0
    
    for t in range(T - 1):
        a0 = grid[t, center]
        a0_next = grid[t + 1, center]
        a1 = grid[t, center + 1]
        a_m1_true = grid[t, center - 1]
        
        if a0 == 1:
            a_m1_pred = a0_next ^ 1  # XOR 1
            total_when_c1 += 1
            if a_m1_pred != a_m1_true:
                errors_c1 += 1
        else:
            a_m1_pred = a0_next ^ a1
            total_when_c0 += 1
            if a_m1_pred != a_m1_true:
                errors_c0 += 1
    
    print(f"T={T}")
    print(f"When a_0(t)=1: {total_when_c1} times, errors={errors_c1}")
    print(f"When a_0(t)=0: {total_when_c0} times, errors={errors_c0}")
    print(f"→ When a_0=1: a_{'{-1}'} = a_0(t+1) XOR 1, ALWAYS correct")
    print(f"→ When a_0=0: a_{'{-1}'} = a_0(t+1) XOR a_1(t), ALWAYS correct")
    print(f"Fraction of time a_0=1: {total_when_c1/(total_when_c1+total_when_c0):.4f}")


def experiment_further_left_reconstruction():
    """
    Can we reconstruct a_{-2}, a_{-3}, ... using the same trick?
    
    From x=-1: a_{-1}(t+1) = a_{-2}(t) XOR (a_{-1}(t) OR a_0(t))
    So: a_{-2}(t) = a_{-1}(t+1) XOR (a_{-1}(t) OR a_0(t))
    
    If a_{-1}(t) and a_0(t) are both known, this gives a_{-2}(t).
    But a_{-1}(t) is NOT always known (only when a_0(t)=1).
    
    However, we can propagate: if a_0(t), a_0(t-1), ... are all 1 for
    a run of length L, then a_{-1}(t), a_{-1}(t-1), ..., a_{-1}(t-L+1) 
    are all known, and from those we can compute a_{-2} for some timesteps.
    
    Let's quantify how much of the left half we can reconstruct from a_0 alone.
    """
    print("\n=== Further left reconstruction from a_0 alone ===\n")
    
    T = 500
    width = T + 5
    grid = simulate_full_rule30(T, width)
    center = width
    
    # Known cells: start with a_0(t) for all t (known by assumption)
    # Also known: a_0(t+1) for all t (shifted version)
    known = np.full((T, 2 * width + 1), False)
    for t in range(T):
        known[t, center] = True  # a_0(t) always known
    
    # First pass: reconstruct a_{-1} where possible
    a_m1_reconstructed = np.zeros(T, dtype=np.int8)  # -1 = unknown
    a_m1_reconstructed[:] = -1
    
    for t in range(T - 1):
        a0 = grid[t, center]
        a0_next = grid[t + 1, center]
        if a0 == 1:
            a_m1_reconstructed[t] = a0_next ^ 1
            known[t, center - 1] = True
    
    frac_m1_known = np.mean(known[:T-1, center - 1])
    print(f"Fraction of a_{'{-1}'}(t) reconstructed from a_0 alone: {frac_m1_known:.4f}")
    
    # Second pass: where a_{-1}(t) and a_0(t) are BOTH known, reconstruct a_{-2}(t)
    # a_{-2}(t) = a_{-1}(t+1) XOR (a_{-1}(t) OR a_0(t))
    a_m2_count = 0
    for t in range(T - 1):
        if known[t, center - 1] and known[t + 1, center - 1]:
            # Both a_{-1}(t) and a_{-1}(t+1) are known
            known[t, center - 2] = True
            a_m2_count += 1
    
    frac_m2_known = a_m2_count / (T - 1)
    print(f"Fraction of a_{'{-2}'}(t) reconstructed: {frac_m2_known:.4f}")
    
    # Continue for a_{-3}, a_{-4}, ...
    for col in range(3, 15):
        count = 0
        for t in range(T - 1):
            if known[t, center - col + 1] and known[t + 1, center - col + 1]:
                known[t, center - col] = True
                count += 1
        frac = count / (T - 1)
        print(f"Fraction of a_{'{-' + str(col) + '}'}(t) reconstructed: {frac:.4f}")
        if frac < 0.001:
            print(f"  → Reconstruction dies out at column {col}")
            break
    
    # Now check: where a_{-1} is NOT known (a_0(t)=0), what values CAN a_{-1} take?
    print(f"\n  Analysis of 'free' positions (where a_0(t)=0):")
    free_times = [t for t in range(T - 1) if grid[t, center] == 0]
    print(f"  Number of free times: {len(free_times)}")
    
    # Check consecutive free times
    max_consecutive = 0
    current_run = 0
    for t in range(T - 1):
        if grid[t, center] == 0:
            current_run += 1
            max_consecutive = max(max_consecutive, current_run)
        else:
            current_run = 0
    
    print(f"  Max consecutive a_0=0 run: {max_consecutive}")
    
    # Average run length of a_0=1
    runs_of_1 = []
    current = 0
    for t in range(T - 1):
        if grid[t, center] == 1:
            current += 1
        elif current > 0:
            runs_of_1.append(current)
            current = 0
    if current > 0:
        runs_of_1.append(current)
    
    if runs_of_1:
        print(f"  Runs of a_0=1: mean={np.mean(runs_of_1):.2f}, max={max(runs_of_1)}, "
              f"distribution: {np.bincount(runs_of_1)[:10]}")


def experiment_free_bit_constraints():
    """
    When a_0(t)=0, a_{-1}(t) = a_0(t+1) XOR a_1(t).
    
    If a_0 is periodic with period p, then the "constraint" is:
    a_{-1}(t) = c((t+1) mod p) XOR a_1(t)
    
    For the left reconstruction to work (Proposition 2 style), we need
    a_{-1} to be periodic. So we need:
    
    a_{-1}(t+p) = a_{-1}(t) for all t > T.
    
    At times when a_0(t)=1: a_{-1}(t) = c(t+1) XOR 1, which IS periodic with period p.
    At times when a_0(t)=0: a_{-1}(t) = c(t+1) XOR a_1(t), so:
    a_{-1}(t+p) = c(t+1) XOR a_1(t+p)
    a_{-1}(t) = c(t+1) XOR a_1(t)
    
    For a_{-1}(t+p) = a_{-1}(t), we need a_1(t+p) = a_1(t).
    
    So a_{-1} periodic ↔ a_1 periodic (at times when a_0=0).
    
    This is the SAME condition as needing a_1 to be periodic. We're going in circles.
    
    BUT: what if a_{-1} being periodic is not necessary for the contradiction?
    What if we just need something WEAKER?
    
    Key observation: We need a_{-1} to satisfy the Rule 30 constraint with a_0 and a_{-2}.
    Even if a_{-1} is not periodic, we need a VALID spacetime to exist.
    
    CONSTRAINT: The spacetime must be consistent with Rule 30 everywhere.
    If a_0 is periodic, does a valid spacetime EXIST starting from the single-cell IC?
    
    Of course it does — the actual Rule 30 spacetime IS such a spacetime (with the
    actual, non-periodic center column). But if we ASSUME a_0 is periodic, we're asking
    whether there exists a spacetime where:
    1. Rule 30 holds everywhere
    2. a_0(t+p) = a_0(t) for all t > T
    3. Initial condition: single cell at t=0
    
    The actual Rule 30 spacetime satisfies (1) and (3) but NOT (2) (empirically).
    If we could show (1)+(2)+(3) is inconsistent, that proves aperiodicity.
    """
    print("\n=== Constraint analysis for periodic a_0 ===\n")
    print("This is the fundamental question: is there a spacetime satisfying")
    print("Rule 30 everywhere + a_0 periodic + single-cell IC?")
    print()
    print("If YES → no contradiction (proof fails)")
    print("If NO → center column cannot be periodic (proof succeeds)")
    print()
    print("The actual Rule 30 spacetime exists and satisfies Rule 30 + IC.")
    print("Assuming it also has a_0 periodic (proof by contradiction),")
    print("we need to derive an inconsistency from the combination of all three.")
    print()
    print("Current approaches and their status:")
    print("  1. Two-column (Jen): Works if a_1 is also periodic → gap")
    print("  2. Coverage counting: Vacuous due to Prop 13 bug → gap")
    print("  3. Difference propagation: d≠0 persists but can't prove → gap")
    print("  4. Growing dependence: a_1(T) depends on O(T^0.6) cells → suggestive only")
    print()
    print("NEW IDEA: Topological entropy approach")
    print("  Rule 30 (as a CA) has positive topological entropy h > 0.")
    print("  A periodic configuration has zero topological entropy.")
    print("  But this refers to SPATIAL periodicity, not temporal periodicity.")
    print("  Need to connect spatial and temporal entropy.")


def experiment_jen_extension():
    """
    Can we extend Jen's argument by replacing the exact a_1(t) with a 
    PARTIAL reconstruction?
    
    Jen's argument (our Proposition 2): if a_0 and a_1 are both periodic with
    common period Q, then all columns to the left are periodic with period Q,
    hence some far-left column is eventually zero, contradicting the left-edge 
    property.
    
    Can we use a PARTIAL a_1 (known at ~60% of times) + periodicity of a_0
    to reach the same conclusion?
    
    The reconstruction formula: a_{-1}(t) = a_0(t+1) XOR (a_0(t) OR a_1(t))
    - When a_0(t)=1: a_{-1}(t) determined → periodic if a_0 is periodic
    - When a_0(t)=0: a_{-1}(t) = a_0(t+1) XOR a_1(t) → depends on unknown a_1
    
    If a_{-1} has period Q where Q divides some p·L, we can continue leftward.
    But we need a_{-1} to be periodic first.
    
    ALTERNATIVE: Use the "sandwiching" approach.
    
    Suppose a_0 has period p. Define two sequences:
    a_{-1}^+ (taking a_1 = 0 when unknown) and a_{-1}^- (taking a_1 = 1 when unknown).
    
    Both are periodic (since a_0 is periodic and the "choice" is fixed).
    The true a_{-1} is "sandwiched" between them in some sense.
    
    But XOR/OR don't have a natural ordering, so "sandwiching" doesn't work directly.
    """
    print("\n=== Jen extension: partial reconstruction ===\n")
    
    # Compute a_{-1} under the assumption a_0 has period p
    # with two choices for a_1 at the unknown times
    T = 100
    p = 5  # hypothetical period
    
    # Generate a periodic boundary
    np.random.seed(42)
    period_word = np.random.randint(0, 2, size=p)
    
    print(f"Hypothetical periodic boundary with period p={p}: {list(period_word)}")
    
    # Simulate right half to get the "true" a_1
    K = 200
    grid = np.zeros((T, K + 2), dtype=np.uint8)
    for t in range(T):
        grid[t, 0] = period_word[t % p]
    for t in range(T - 1):
        for x in range(1, K + 1):
            grid[t + 1, x] = grid[t, x - 1] ^ (grid[t, x] | grid[t, x + 1])
    
    # Compute a_{-1} under different a_1 choices
    a_m1_true = np.zeros(T - 1, dtype=np.uint8)
    a_m1_opt0 = np.zeros(T - 1, dtype=np.uint8)  # a_1 = 0 when unknown
    a_m1_opt1 = np.zeros(T - 1, dtype=np.uint8)  # a_1 = 1 when unknown
    
    for t in range(T - 1):
        a0 = period_word[t % p]
        a0_next = period_word[(t + 1) % p]
        a1_true = grid[t, 1]
        
        a_m1_true[t] = a0_next ^ (a0 | a1_true)
        a_m1_opt0[t] = a0_next ^ (a0 | 0)
        a_m1_opt1[t] = a0_next ^ (a0 | 1)
    
    # Check: when a_0(t)=1, all three agree
    agree_when_1 = sum(1 for t in range(T-1) 
                       if period_word[t % p] == 1 and 
                       a_m1_true[t] == a_m1_opt0[t] == a_m1_opt1[t])
    times_when_1 = sum(1 for t in range(T-1) if period_word[t % p] == 1)
    
    print(f"\nWhen a_0=1 ({times_when_1} times): all agree? {agree_when_1 == times_when_1}")
    
    # When a_0(t)=0, opt0 and opt1 always differ
    differ_when_0 = sum(1 for t in range(T-1) 
                        if period_word[t % p] == 0 and 
                        a_m1_opt0[t] != a_m1_opt1[t])
    times_when_0 = sum(1 for t in range(T-1) if period_word[t % p] == 0)
    
    print(f"When a_0=0 ({times_when_0} times): opt0 != opt1? {differ_when_0} / {times_when_0}")
    
    # Are opt0 and opt1 periodic?
    is_opt0_periodic = all(a_m1_opt0[t] == a_m1_opt0[t + p] for t in range(T - 1 - p))
    is_opt1_periodic = all(a_m1_opt1[t] == a_m1_opt1[t + p] for t in range(T - 1 - p))
    print(f"\na_{'{-1}'}(opt0) periodic with period {p}? {is_opt0_periodic}")
    print(f"a_{'{-1}'}(opt1) periodic with period {p}? {is_opt1_periodic}")
    
    # Is the true a_{-1} periodic? (From the actual right-half simulation)
    is_true_periodic = all(a_m1_true[t] == a_m1_true[t + p] for t in range(T - 1 - p))
    print(f"a_{'{-1}'}(true) periodic with period {p}? {is_true_periodic}")
    
    # Number of free bits in one period
    free_per_period = sum(1 for t in range(p) if period_word[t] == 0)
    print(f"\nFree bits per period: {free_per_period} / {p}")
    print(f"  → {2**free_per_period} possible a_{'{-1}'} patterns per period")
    print(f"  → The 'true' pattern is one of these {2**free_per_period} choices")
    print(f"  → Each choice gives a periodic a_{'{-1}'} (period p or divisor)")
    print()
    print(f"KEY INSIGHT: ANY a_1 pattern at the free positions gives a")
    print(f"periodic a_{'{-1}'}! So the periodicity of a_{'{-1}'} is automatic.")
    print(f"The question is whether there EXISTS a choice of a_1 that is")
    print(f"consistent with Rule 30 for the RIGHT half.")


if __name__ == "__main__":
    experiment_conditional_reconstruction()
    experiment_further_left_reconstruction()
    experiment_free_bit_constraints()
    experiment_jen_extension()
