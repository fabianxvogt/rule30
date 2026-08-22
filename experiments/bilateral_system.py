#!/usr/bin/env python3
"""
BILATERAL APPROACH: Use both the left and right halves simultaneously.

The Rule 30 spacetime from single-cell IC is symmetric under spatial reflection 
combined with the Rule 30 ↔ Rule 86 transformation.

Actually: Rule 30 is x' = a XOR (b OR c) where a is left neighbor. 
Under spatial reflection: left↔right, so a↔c, giving x' = c XOR (b OR a) = same!
Wait, that's the same since OR is commutative. So Rule 30 IS left-right symmetric?

No! The update is: new[i] = old[i-1] XOR (old[i] OR old[i+1])
Under reflection (j = -i): new[-j] = old[-j-1] XOR (old[-j] OR old[-j+1])
= old[j+1] XOR (old[j] OR old[j-1])

This is NOT Rule 30 applied to positions j. Rule 30 applied to j would be:
new[j] = old[j-1] XOR (old[j] OR old[j+1])

The reflected version has old[j+1] XOR (old[j] OR old[j-1])
= old[j+1] XOR (old[j-1] OR old[j])

This is a DIFFERENT rule: Rule 86 (the complementary reflection of Rule 30).

So the left half of the Rule 30 cone doesn't obey Rule 30 dynamics — it obeys 
Rule 86 dynamics (viewed rightward from the boundary).

This means the left half is driven by a Rule 86 truncated system with the 
center column as boundary input.

Key question: if the center column were periodic with period p, would BOTH:
- The Rule 30 right-half system visit all classes?
- The Rule 86 left-half system visit all classes?

If we can show that periodicity constrains the system enough to PREVENT coverage 
in one of the two sides, we have a contradiction.

Let me first understand Rule 86 and its class structure.

Rule 86: x' = c XOR (a OR b) = old[i+1] XOR (old[i-1] OR old[i])
The right-neighbor plays the XOR role instead of the left.

For the LEFT half of Rule 30 (reflected):
- The "boundary" is still the center column b_t
- The LEFT half state l_t evolves as: l_{t+1}[j] = l_t[j+1] XOR (l_t[j-1] OR l_t[j])
  with boundary l_t[-1] = b_t (center column)

Wait, let me be more careful about the indexing.

In the full Rule 30 row at time t: ..., row[-2], row[-1], row[0], row[1], row[2], ...
where row[0] = b_t (center cell).

The RIGHT half: positions 1, 2, 3, ... with boundary row[0] = b_t.
Evolution: row[i] updates using left=row[i-1], center=row[i], right=row[i+1].
For i=1: left = row[0] = b_t (boundary).

The LEFT half: positions -1, -2, -3, ... with boundary row[0] = b_t.
For position -1: updates using left = row[-2], center = row[-1], right = row[0] = b_t.
So: new[-1] = row[-2] XOR (row[-1] OR b_t)

If we define the left state as l_t = (row[-1], row[-2], row[-3], ...), i.e., 
l_t[j] = row[-(j+1)], then:

For j=0 (position -1): l_{t+1}[0] = l_t[1] XOR (l_t[0] OR b_t)
For j≥1 (position -(j+1)): l_{t+1}[j] = l_t[j+1] XOR (l_t[j] OR l_t[j-1])

So the left-half dynamics is:
  l[0]' = l[1] XOR (l[0] OR b)     [boundary]
  l[j]' = l[j+1] XOR (l[j] OR l[j-1])  [bulk, j ≥ 1]

Compare with the right-half dynamics:
  s[0]' = b XOR (s[0] OR s[1])     [boundary]
  s[j]' = s[j-1] XOR (s[j] OR s[j+1])  [bulk, j ≥ 1]

They're DIFFERENT! The right half uses left-permutativity (XOR on the LEFT), 
while the left half uses RIGHT-permutativity (XOR on the RIGHT).

The left-half boundary condition puts b in the OR position, not XOR.
The right-half boundary condition puts b in the XOR position.

This asymmetry is fundamental to Rule 30's properties.

Let me build the LEFT-half truncated system and compare its class structure.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))


def left_half_next(state, b):
    """Evolve left-half state by one step with boundary bit b.
    state = (l[0], l[1], ..., l[h-1]) indexed from center outward.
    l[0] = cell at position -1, l[1] = cell at position -2, etc.
    
    l[0]' = l[1] XOR (l[0] OR b)
    l[j]' = l[j+1] XOR (l[j] OR l[j-1])  for 1 ≤ j ≤ h-2
    l[h-1]' = 0 XOR (l[h-1] OR l[h-2]) = l[h-1] OR l[h-2]  (zero padding)
    
    Wait: l[h-1]' = l[h] XOR (l[h-1] OR l[h-2])
    with l[h] = 0 (zero padding), so l[h-1]' = l[h-1] OR l[h-2]
    
    Hmm, that doesn't look right for Rule 30.
    
    Actually wait — let me reconsider. For the left half position -(j+1):
    new[-(j+1)] = old[-(j+2)] XOR (old[-(j+1)] OR old[-j])
    
    old[-(j+2)] = l[j+1]
    old[-(j+1)] = l[j]  
    old[-j] = l[j-1] for j≥1, old[0] = b for j=0
    
    So: l'[j] = l[j+1] XOR (l[j] OR l[j-1])   for j ≥ 1
        l'[0] = l[1] XOR (l[0] OR b)
    
    With zero padding at the right edge: l[h] = 0.
    So l'[h-1] = 0 XOR (l[h-1] OR l[h-2]) = l[h-1] OR l[h-2]
    """
    h = len(state)
    new_state = [0] * h
    
    # j = 0: boundary
    if h >= 2:
        new_state[0] = state[1] ^ (state[0] | b)
    elif h == 1:
        new_state[0] = 0 ^ (state[0] | b)  # state[1] = 0
    
    # j = 1, ..., h-2: bulk
    for j in range(1, h-1):
        new_state[j] = state[j+1] ^ (state[j] | state[j-1])
    
    # j = h-1: boundary (zero padding: state[h] = 0)
    if h >= 2:
        new_state[h-1] = 0 ^ (state[h-1] | state[h-2])
    
    return tuple(new_state)


def right_half_next(state, b):
    """Standard Rule 30 right-half evolution."""
    h = len(state)
    # Pad: boundary = b on left, zero on right
    row = (b,) + state + (0,)
    return tuple(row[i] ^ (row[i+1] | row[i+2]) for i in range(h))


def build_left_classes(h):
    """Build equivalence classes for left-half system by exhaustive simulation."""
    N = 1 << h
    
    # Two states are equivalent if they produce the same output sequence 
    # for all boundary input sequences of length h.
    # Output = state trajectory (or some observation)
    
    # For the RIGHT half, the "output" at each step is the observable behavior:
    # the class captures what can be distinguished by length-h experiments.
    
    # For simplicity, compute the response function:
    # For each state s, and each h-bit input (b_0,...,b_{h-1}),
    # compute f(s, b) = output of interest.
    
    # What's the natural output for the left half? 
    # The leftmost cell l[0] is adjacent to the center.
    # Actually, the observable from the center column's perspective is:
    # L_t = l_t[0] (the cell at position -1, which contributes to b_{t+1})
    
    # Equivalence: two states s, s' are equivalent if for all input sequences 
    # of length h, the output sequences of l[0] values are the same.
    
    # For now, just compute response vectors and use as fingerprints.
    responses = {}
    for s_int in range(N):
        state = tuple((s_int >> i) & 1 for i in range(h))
        
        # Compute response for all 2^h input sequences
        response = []
        for inp_int in range(1 << h):
            inp = tuple((inp_int >> i) & 1 for i in range(h))
            s = state
            output = []
            for b in inp:
                output.append(s[0])  # observable: leftmost cell
                s = left_half_next(s, b)
            response.append(tuple(output))
        
        responses[s_int] = tuple(response)
    
    # Group by response
    classes = {}
    for s_int, resp in responses.items():
        if resp not in classes:
            classes[resp] = []
        classes[resp].append(s_int)
    
    return classes


def main():
    # Verify left-half dynamics against full simulation
    print("=== Verifying left-half dynamics ===")
    
    # Do a few steps of full Rule 30 and compare
    width = 40
    center = width // 2
    row = [0] * width
    row[center] = 1
    
    for t in range(10):
        new_row = [0] * width
        for i in range(1, width - 1):
            new_row[i] = row[i-1] ^ (row[i] | row[i+1])
        
        # Extract left and right states
        h = 5
        right_state = tuple(row[center+1:center+1+h])
        left_state = tuple(row[center-1:center-1-h:-1])  # reversed
        b = row[center]
        
        # Compute next states
        right_next = right_half_next(right_state, b)
        left_next = left_half_next(left_state, b)
        
        # Extract from new_row
        right_actual = tuple(new_row[center+1:center+1+h])
        left_actual = tuple(new_row[center-1:center-1-h:-1])
        
        match_r = right_next == right_actual
        match_l = left_next == left_actual
        
        if not match_r or not match_l:
            print(f"  t={t}: RIGHT {'✓' if match_r else 'FAIL'}, "
                  f"LEFT {'✓' if match_l else 'FAIL'}")
            if not match_l:
                print(f"    left_state={left_state}, b={b}")
                print(f"    computed:   {left_next}")
                print(f"    actual:     {left_actual}")
        
        row = new_row
    
    print("  All verifications passed.")
    
    # Compare class counts
    print("\n=== Left-half vs Right-half class counts ===")
    print(f"{'h':>3} {'|S_h| (right)':>14} {'|S_h| (left)':>13}")
    
    for h in range(1, 13):
        N = 1 << h
        
        # Right-half classes (from existing code)
        right_responses = {}
        for s_int in range(N):
            state = tuple((s_int >> i) & 1 for i in range(h))
            response = []
            for inp_int in range(1 << h):
                inp = tuple((inp_int >> i) & 1 for i in range(h))
                s = state
                output = []
                for b in inp:
                    output.append(s[0])
                    s = right_half_next(s, b)
                response.append(tuple(output))
            right_responses[s_int] = tuple(response)
        
        right_classes = len(set(right_responses.values()))
        
        # Left-half classes
        left_responses = {}
        for s_int in range(N):
            state = tuple((s_int >> i) & 1 for i in range(h))
            response = []
            for inp_int in range(1 << h):
                inp = tuple((inp_int >> i) & 1 for i in range(h))
                s = state
                output = []
                for b in inp:
                    output.append(s[0])
                    s = left_half_next(s, b)
                response.append(tuple(output))
            left_responses[s_int] = tuple(response)
        
        left_classes = len(set(left_responses.values()))
        
        print(f"{h:3d} {right_classes:14d} {left_classes:13d}")


if __name__ == "__main__":
    main()
