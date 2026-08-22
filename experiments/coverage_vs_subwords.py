#!/usr/bin/env python3
"""
Verify: the truncated trajectory visits classes whose corresponding h-tuples
do NOT appear as subwords of the center column.

This proves that coverage is a DYNAMICAL property, not a subword property.
The trajectory reaches these states through indirect paths.
"""
from __future__ import annotations

import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, make_transition_tables


def main():
    bits_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "results", "center-column-1000000.txt")
    with open(bits_file) as f:
        bits = [int(c) for c in f.read().strip() if c in '01']
    
    N = len(bits)
    
    for h in [18, 19, 20]:
        print(f"\n{'='*60}")
        print(f"h={h}")
        
        q = build_quotient(h)
        total = max(q.values()) + 1
        
        trans, cls_of = make_transition_tables(q, h)
        
        # Run trajectory
        current = 0  # all-zeros
        visited_classes = set()
        visited_classes.add(cls_of[current])
        visited_tuples = set()
        
        # Also track which classes are visited via which raw states
        class_first_visit = {}
        class_first_raw = {}
        
        c0 = cls_of[current]
        class_first_visit[c0] = 0
        class_first_raw[c0] = current
        
        for t in range(min(N, 1000000)):
            current = trans[bits[t]][current]
            c = cls_of[current]
            if c not in class_first_visit:
                class_first_visit[c] = t + 1
                class_first_raw[c] = current
            visited_classes.add(c)
        
        # Check subword occurrences
        subword_classes = set()
        for i in range(N - h + 1):
            w = tuple(bits[i:i+h])
            if w in q:
                subword_classes.add(q[w])
        
        # Compare
        traj_only = visited_classes - subword_classes
        subword_only = subword_classes - visited_classes
        both = visited_classes & subword_classes
        
        print(f"|S_{h}| = {total}")
        print(f"Classes visited by trajectory: {len(visited_classes)}")
        print(f"Classes whose tuples appear as subwords: {len(subword_classes)}")
        print(f"  In both: {len(both)}")
        print(f"  Trajectory only (NOT subwords): {len(traj_only)}")
        print(f"  Subwords only (NOT trajectory): {len(subword_only)}")
        
        if traj_only:
            print(f"\n  Classes visited by trajectory but NOT by subword occurrence:")
            for cid in sorted(traj_only):
                step = class_first_visit.get(cid, -1)
                raw = class_first_raw.get(cid, -1)
                # Decode raw state
                tup = []
                v = raw
                for _ in range(h):
                    tup.append(v & 1)
                    v >>= 1
                tup_str = ''.join(str(b) for b in tup)
                print(f"    Class {cid}: first visit at step {step}, via state {tup_str}")
        
        # IMPORTANT: Check that subword-based class assignment is correct
        # A class can be visited by the trajectory even if NONE of its member
        # tuples appear as subwords, because the trajectory STATE is not a subword
        # -- it's the result of evolving the truncated system.
        
        # Verify: the trajectory's h-tuple at each step is NOT necessarily a subword
        # Let's check how many trajectory states are also subwords
        current = 0
        traj_is_subword = 0
        traj_not_subword = 0
        subword_set = set()
        for i in range(min(N - h + 1, 100000)):
            subword_set.add(tuple(bits[i:i+h]))
        
        current = 0
        for t in range(min(N, 100000)):
            current = trans[bits[t]][current]
            # Decode
            tup = []
            v = current
            for _ in range(h):
                tup.append(v & 1)
                v >>= 1
            if tuple(tup) in subword_set:
                traj_is_subword += 1
            else:
                traj_not_subword += 1
        
        print(f"\n  In first 100k steps:")
        print(f"    Trajectory state is a subword: {traj_is_subword}")
        print(f"    Trajectory state is NOT a subword: {traj_not_subword}")
        print(f"    Fraction that are subwords: {traj_is_subword/(traj_is_subword+traj_not_subword):.4f}")


if __name__ == "__main__":
    main()
