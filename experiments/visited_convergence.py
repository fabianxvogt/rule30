#!/usr/bin/env python3
"""
For FIXED N, does the number of visited classes at horizon h converge to a limit?

Theory: At each step, the trajectory is in some class in S_h. Over N steps,
it visits at most N+1 distinct classes. But different horizons might have 
different effective class counts.

For the actual center column: as h grows, the quotient map refines, so the 
number of visited classes should be non-decreasing (each class at h projects
to a unique class at h-1 via rho_h, so visiting k distinct classes at h 
means visiting AT LEAST k distinct classes at h-1).

Wait, that's the wrong direction. Let me think...

Actually: rho_h maps S_h -> S_{h-1}. If we visit classes c1, ..., ck at horizon h,
they map to rho_h(c1), ..., rho_h(ck) at horizon h-1. But rho_h is surjective,
not injective. So the number of visited classes at h-1 is ≤ k (could be less if 
two visited classes at h map to the same class at h-1).

No wait: rho_h is NOT what relates the trajectory at horizon h to the trajectory
at horizon h-1. The trajectory at horizon h IS the trajectory at horizon h-1 plus
some extra refinement. Actually, the trajectory at horizon h consists of the h-bit
right-half states, and the trajectory at horizon h-1 consists of the (h-1)-bit 
right-half states obtained by truncating the last bit.

So the raw state at time t in horizon h is s^h(t) = (a_1(t), ..., a_h(t)), and
the raw state at horizon h-1 is s^{h-1}(t) = (a_1(t), ..., a_{h-1}(t)) = rho(s^h(t)).

So: class visited at horizon h at time t = [s^h(t)]_h, and this maps under rho_h
to [rho(s^h(t))]_{h-1} = [s^{h-1}(t)]_{h-1} = class visited at horizon h-1 at time t.

So: the number of distinct classes visited at horizon h-1 over N steps is exactly
the number of distinct rho_h-images of the classes visited at horizon h. Since 
rho_h is not injective, the visited count at h-1 is ≤ visited count at h.

For the proof: V_h(N) = number of classes visited at horizon h in first N steps.
Then V_{h-1}(N) ≤ V_h(N). So V_h(N) is non-decreasing in h (for fixed N).

If V_h(N) < |S_h| for some h, that's fine. The question is: does V_h(N) → ∞ 
as h → ∞ for FIXED N? Since V_h(N) ≤ N+1, it must stabilize for large h.

For a periodic sequence with period p: V_h(N) ≤ p + T for all h (where T is 
the pre-period). So V_h(N) converges to some value ≤ p + T.

For Rule 30: V_h(N) should converge to N+1 (or close) for small N, since
the trajectory state at each step is effectively "random" and distinct.

Let me check this: as h grows large (much larger than N), do the raw states
at times 0, 1, ..., N become pairwise predictively inequivalent?
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables


def main():
    # Load center column bits
    bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "results", "center-column-1000000.txt")
    with open(bits_file) as f:
        bits = [int(c) for c in f.read().strip() if c in '01']
    
    N_steps = 100
    print(f"Tracking trajectory for first {N_steps} steps")
    print(f"{'h':>3} {'|S_h|':>7} {'V_h':>5} {'distinct raw':>13}")
    print("-" * 35)
    
    for h in range(1, 25):
        if h > 20:
            # For h > 20 we can't easily build the quotient, skip
            break
        q = build_quotient(h)
        total_classes = max(q.values()) + 1
        next_state, class_table = make_transition_tables(q, h)
        
        state = 0
        visited_classes = set()
        visited_classes.add(class_table[state])
        visited_raw = set()
        visited_raw.add(state)
        
        for t in range(1, N_steps + 1):
            state = next_state[bits[t-1]][state]
            visited_classes.add(class_table[state])
            visited_raw.add(state)
        
        print(f"{h:3d} {total_classes:7d} {len(visited_classes):5d} {len(visited_raw):13d}")
    
    # For larger N, check the convergence
    print(f"\n\nChecking V_h(N) convergence for N=1000:")
    N_steps = 1000
    print(f"{'h':>3} {'|S_h|':>7} {'V_h':>5}")
    print("-" * 20)
    
    for h in range(1, 21):
        q = build_quotient(h)
        total_classes = max(q.values()) + 1
        next_state, class_table = make_transition_tables(q, h)
        
        state = 0
        visited_classes = set()
        visited_classes.add(class_table[state])
        
        for t in range(1, N_steps + 1):
            state = next_state[bits[t-1]][state]
            visited_classes.add(class_table[state])
        
        print(f"{h:3d} {total_classes:7d} {len(visited_classes):5d}")


if __name__ == "__main__":
    main()
