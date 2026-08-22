#!/usr/bin/env python3
"""
CRITICAL INSIGHT: The driving sequence (center column) is NOT independent of 
the state. The center column bit at step t is the output of the RIGHT HALF 
evolving with the LEFT half's boundary conditions.

But in our framework:
- The state s_t ∈ {0,1}^h is the right-half configuration (truncated to width h)
- The boundary bit b_t is the center column bit
- s_{t+1} = f_{b_t}(s_t)
- The output we care about is b_t itself

So the center column b_t is EXTERNALLY given (from the left half) — it's not 
determined by s_t. The key question is: what properties must the external 
driving sequence {b_t} have to ensure coverage?

We showed:
- Full subword complexity is NOT sufficient (can avoid some states while 
  having full complexity)
- Periodic sequences fail
- Random i.i.d. sequences succeed
- The center column succeeds (empirically)

NEW APPROACH: Can we prove coverage by using BOTH:
1. The IFS structure (joint surjectivity, near-synchronization)
2. Properties of the driving sequence that follow from the COUPLING with the 
   left half (the center column can't be adversarial because it comes from 
   the left half which has its own dynamics)

Actually, there's an even more fundamental point:

For the PROOF, we assume the center column is periodic with period p.
Under this assumption:
- The driving sequence {b_t} has subword complexity p at length p (at most p 
  distinct p-grams)
- The trajectory {s_t} is eventually periodic with period dividing some P

We need: for ALL h, the trajectory visits ALL classes.

For h large enough that |S_h| > p, the trajectory can have at most p+T 
distinct states (where T is the transient). So if |S_h| > p + T, we need 
more than p+T classes to be visited — impossible.

WAIT: the trajectory visits states, not classes directly. But each state maps 
to a class. So #distinct classes ≤ #distinct states ≤ p + T.

For h large enough, |S_h| > p + T → NOT all classes visited → contradiction 
with Coverage Hypothesis.

So the proof structure is:
1. Assume period p
2. Show |S_h| → ∞ (proved)
3. Show coverage for all h (Coverage Hypothesis — THE GAP)
4. Contradiction: p + T < |S_h| for large h

The issue is step 3. We need to prove: ASSUMING the center column is periodic 
with period p, the trajectory visits all S_h classes for every h.

But wait — if the center column is periodic with period p, then the driven 
trajectory is eventually periodic. Can it visit all |S_h| classes for every h?

For small h (where |S_h| ≤ p), yes it's possible (the trajectory might visit 
enough states). For large h (where |S_h| > p), it's IMPOSSIBLE.

So the Coverage Hypothesis ALREADY FAILS for large h under periodicity!
THAT'S THE WHOLE POINT — we don't need to prove coverage "assuming periodicity."
We prove coverage WITHOUT assuming periodicity, and then periodicity gives 
a contradiction.

So the question is: can we prove coverage for the ACTUAL center column?

And the answer is: we don't KNOW the actual center column is aperiodic yet — 
that's what we're trying to prove. We can't use properties of the actual 
center column that depend on it being aperiodic.

THE REAL PROOF STRUCTURE should be:
1. |S_h| → ∞ (proved)
2. Coverage Hypothesis: the trajectory visits all classes for every h (THE GAP)
3. Assuming period p: trajectory has ≤ p + T distinct values
4. For large h: |S_h| > p + T, contradiction with (2)

And (2) must hold REGARDLESS of whether the center column is periodic or not.
So we need (2) for EVERY possible center column — even periodic ones.

But we just showed periodic sequences CAN fail coverage (for large h)!

So the argument structure seems circular. Let me re-examine.

Actually, no. The Coverage Hypothesis doesn't need to hold for ALL driving 
sequences. It needs to hold for the SPECIFIC driving sequence that is the 
center column of Rule 30 started from the single-cell initial condition.

And we need to establish (2) as a FACT about that specific sequence.
This can be done:
a) Computationally (verified up to h=23)
b) Theoretically — by proving some property of the Rule 30 dynamics

For theoretical approach, we could try:
- The center column has a property P (to be determined)
- Property P implies coverage in the driven IFS
- Rule 30 dynamics guarantees property P

Let me check: what properties does the center column have that random 
sequences also have but periodic sequences don't?

ANSWER: The center column is THE OUTPUT of the RIGHT-HALF dynamics.
Specifically, the output bit o_t = s_t[0] (the leftmost bit of the state).

Wait — is this true? In the truncated system, the state s_t is the 
right-half configuration. The CENTER COLUMN is the boundary between left 
and right halves. It's an INPUT to the right half, not an output.

Let me clarify the relationship between the center column and the right half.

In Rule 30 from single-cell initial condition:
- At time t, the FULL row has cells at positions roughly [-t, t]
- The center cell (position 0) has value b_t
- The right half is positions [1, t]
- To evolve the right half, we need the center cell b_t (boundary condition)

So b_t is determined by the FULL Rule 30 dynamics, not by the right half alone.
The right-half state s_t doesn't determine b_t.

So {b_t} is an externally imposed sequence on the right-half dynamics. We can't 
derive properties of {b_t} from the right-half dynamics alone.

Could we instead derive properties from the LEFT half?
Or from the FULL CA evolution?

Here's the key idea: b_t = full_row_t[0], and it depends on the full row at time t-1.
In particular: b_t = row_{t-1}[-1] XOR (row_{t-1}[0] OR row_{t-1}[1])
where [-1], [0], [1] are positions in the previous row.

The center column satisfies a SELF-CONSISTENCY: it's the output of the full CA 
dynamics that includes both halves. This self-consistency is what makes the 
problem hard.

So the proof strategy should use this self-consistency somehow.

Let me compute: is there a direct relationship between b_t and s_t?
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import rule30_next_tuple


def full_rule30(n_steps):
    """Simulate full Rule 30 from single cell, return center column and right states."""
    # Use wide enough row
    width = 2 * n_steps + 3
    center = width // 2
    
    row = [0] * width
    row[center] = 1
    
    center_column = [row[center]]
    right_states = [tuple(row[center+1:center+1+n_steps])]  # will be truncated
    
    for t in range(n_steps):
        new_row = [0] * width
        for i in range(1, width - 1):
            new_row[i] = row[i-1] ^ (row[i] | row[i+1])
        row = new_row
        center_column.append(row[center])
        
        # Right half: positions center+1, center+2, ...
        right_state = tuple(row[center+1:center+1+n_steps])
        right_states.append(right_state)
    
    return center_column, right_states


def main():
    n = 50
    center, rights = full_rule30(n)
    
    print("=== Center column vs right-half relationship ===")
    print(f"Step | b_t | s_t[0] | s_t[0..4]")
    print("-" * 50)
    
    for t in range(min(30, n+1)):
        b_t = center[t]
        s_t = rights[t]
        s0 = s_t[0] if len(s_t) > 0 else '-'
        s_short = s_t[:5] if len(s_t) >= 5 else s_t
        print(f"  {t:3d} |  {b_t}  |   {s0}    | {s_short}")
    
    # Check: is b_t related to s_{t-1} in any way?
    print("\n=== Correlation: b_t vs s_{t-1}[0] ===")
    same = 0
    for t in range(1, n+1):
        if center[t] == rights[t-1][0]:
            same += 1
    print(f"  b_t == s_{{t-1}}[0] for {same}/{n} steps ({same/n*100:.1f}%)")
    
    # Check: can b_t be predicted from s_t?
    # b_t depends on the left half, which we don't have in the right state.
    # But the Rule 30 update for position 0 involves positions -1, 0, 1:
    # b_t = row_{t-1}[-1] XOR (row_{t-1}[0] OR row_{t-1}[1])
    # row_{t-1}[0] = b_{t-1}
    # row_{t-1}[1] = s_{t-1}[0]  (first cell of right half at time t-1)
    # row_{t-1}[-1] = left half's rightmost cell at time t-1
    
    # So b_t = L_{t-1} XOR (b_{t-1} OR s_{t-1}[0])
    # where L_{t-1} is the left half's cell adjacent to center at time t-1.
    
    # This means b_t = L_{t-1} XOR (b_{t-1} OR s_{t-1}[0])
    # The right-half dynamics knows s_{t-1} and b_{t-1}, but not L_{t-1}.
    # L_{t-1} is the "missing information" — it comes from the left half.
    
    print(f"\n=== Decomposition: b_t = L_{{t-1}} XOR (b_{{t-1}} OR s_{{t-1}}[0]) ===")
    # Compute L from the full simulation
    width = 2 * n + 3
    cntr = width // 2
    row = [0] * width
    row[cntr] = 1
    
    for t in range(1, min(20, n+1)):
        new_row = [0] * width
        for i in range(1, width - 1):
            new_row[i] = row[i-1] ^ (row[i] | row[i+1])
        prev_row = row
        row = new_row
        
        b_t = row[cntr]
        b_prev = prev_row[cntr]
        s_prev_0 = prev_row[cntr + 1]
        L_prev = prev_row[cntr - 1]
        
        computed = L_prev ^ (b_prev | s_prev_0)
        print(f"  t={t:2d}: b_t={b_t}, L_{{t-1}}={L_prev}, b_{{t-1}}={b_prev}, "
              f"s_{{t-1}}[0]={s_prev_0}, computed={computed}, match={computed == b_t}")


if __name__ == "__main__":
    main()
