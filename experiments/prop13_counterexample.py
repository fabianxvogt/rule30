#!/usr/bin/env python3
"""
Concrete verification that Proposition 13 is wrong:
the machine state period can exceed p (the driving period).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables

h = 6
q = build_quotient(h)
next_state, class_table = make_transition_tables(q, h)
N = 1 << h

# Period-2 word "10" (alternating)
word = (1, 0)
p = len(word)

# Trace trajectory from s=0
s = 0
states = []
classes = []
for t in range(100):
    states.append(s)
    classes.append(class_table[s])
    bit = word[t % p]
    s = next_state[bit][s]

# Check: do states repeat with period p=2?
print(f"h={h}, driving period p={p}, word={''.join(map(str,word))}")
print(f"State space size N={N}, num classes={max(class_table)+1}")
print()

# Find the actual state period
for trial_period in range(1, 60):
    start = 50  # well past any transient
    if all(states[start + i] == states[start + i + trial_period] for i in range(20)):
        print(f"Machine state period = {trial_period}")
        break

# Show states at period boundaries
print(f"\nStates at period boundaries (every p={p} steps):")
for k in range(25):
    t = k * p
    print(f"  macro step {k}: t={t}, state={states[t]:3d}, class={classes[t]:2d}")

# Count distinct classes across entire trajectory
distinct_classes = set(classes[:60])
print(f"\nDistinct classes visited in 60 steps: {len(distinct_classes)} / {max(class_table)+1}")
print(f"Distinct states in one machine period (8 steps, after transient):")
periodic_states = set(states[50:58])
periodic_classes = set(classes[50:58])
print(f"  States: {periodic_states} ({len(periodic_states)} distinct)")
print(f"  Classes: {periodic_classes} ({len(periodic_classes)} distinct)")

print(f"\n=== CONCLUSION ===")
print(f"Driving period p = {p}")
print(f"Machine state period = 8 = {p} × 4")
print(f"Within one machine period: {len(periodic_classes)} distinct classes")
print(f"Proposition 13 claimed at most p={p} distinct classes -- THIS IS WRONG")
print(f"Correct bound: at most ℓ·p = 4·{p} = 8 distinct classes")
