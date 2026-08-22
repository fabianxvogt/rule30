#!/usr/bin/env python3
"""
The truncated width-h system defines an IFS (Iterated Function System) with two maps f_0, f_1.

Key facts from experiments:
1. Individual maps f_b are NOT bijective (image ~0.6 * 2^h)
2. For fixed starting state, the map (b_0,...,b_{h-1}) -> s_h IS bijective
3. For fixed boundary bits, the map s_0 -> s_h is CONTRACTING

This means the IFS is:
- "Input-bijective" (universal bijectivity): any input sequence reaches any target from any start
- "State-contracting" (synchronizing): different starting states converge under same inputs

What matters for coverage: the trajectory s(0), s(1), ... under CENTER COLUMN driving.

Question: does the orbit of the IFS under center-column driving visit all S_h classes?

Key idea: Think of the quotient dynamics. The trajectory on CLASS level is NOT deterministic
(different raw states in same class can go to different classes). But the ACTUAL trajectory
picks one specific path. For coverage, we need this specific path to visit all classes.

Let's study the CLASS-LEVEL dynamics more carefully:

For each raw state s, define class(s). Then:
class(f_b(s)) depends on both class(s) AND the specific representative s within the class.

How many distinct class transitions are possible from a given class?
"""
from __future__ import annotations
import os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import build_quotient, rule30_next_tuple


def main():
    for h in [8, 10, 12, 15, 18]:
        print(f"\n=== h={h} ===")
        q = build_quotient(h)
        total_classes = max(q.values()) + 1
        print(f"  |S_{h}| = {total_classes}")
        
        # For each class c and each bit b: what's the set of possible next classes?
        class_to_states = defaultdict(list)
        for state, cid in q.items():
            class_to_states[cid].append(state)
        
        # Count nondeterminism
        multi_image_count = {0: 0, 1: 0}
        max_image_size = {0: 0, 1: 0}
        total_reachable_classes = {0: set(), 1: set()}
        
        for b in [0, 1]:
            for cid, states in class_to_states.items():
                next_classes = set()
                for s in states:
                    ns = rule30_next_tuple(s, b)[:h]
                    nc = q.get(ns, -1)
                    next_classes.add(nc)
                
                total_reachable_classes[b].update(next_classes)
                
                if len(next_classes) > 1:
                    multi_image_count[b] += 1
                    max_image_size[b] = max(max_image_size[b], len(next_classes))
        
        for b in [0, 1]:
            print(f"  b={b}: {multi_image_count[b]}/{total_classes} classes have MULTIPLE next-classes "
                  f"(max {max_image_size[b]} options)")
            print(f"       {len(total_reachable_classes[b])} classes reachable")
        
        # The key question: from each class, how many distinct (class, bit) -> next_class pairs?
        # This is the "class transition graph"
        class_edges = defaultdict(set)  # (cid, b) -> set of possible next classes
        for b in [0, 1]:
            for cid, states in class_to_states.items():
                for s in states:
                    ns = rule30_next_tuple(s, b)[:h]
                    nc = q[ns]
                    class_edges[(cid, b)].add(nc)
        
        # How many classes are reachable from any class in 1 step (either b)?
        one_step_reach = {}
        for cid in range(total_classes):
            reach = class_edges[(cid, 0)] | class_edges[(cid, 1)]
            one_step_reach[cid] = reach
        
        sizes = [len(v) for v in one_step_reach.values()]
        print(f"  1-step reachability: min={min(sizes)}, max={max(sizes)}, "
              f"avg={sum(sizes)/len(sizes):.1f}")
        
        # How many steps to reach all classes via BFS on class graph?
        # (non-deterministic BFS: from class c, we can go to any class in one_step_reach[c])
        start_class = q[(0,)*h]  # all-zeros class
        reached = {start_class}
        frontier = {start_class}
        bfs_steps = 0
        while frontier and len(reached) < total_classes:
            bfs_steps += 1
            next_frontier = set()
            for c in frontier:
                for nc in one_step_reach[c]:
                    if nc not in reached:
                        reached.add(nc)
                        next_frontier.add(nc)
            frontier = next_frontier
        
        print(f"  BFS from all-zeros class: reaches {len(reached)}/{total_classes} classes "
              f"in {bfs_steps} steps")
        
        if h <= 12:
            # Check: is the class transition graph STRONGLY connected?
            # (Can we reach any class from any class?)
            # Use BFS from each class
            all_reach_all = True
            min_reach = total_classes
            for start_c in range(total_classes):
                reached_c = {start_c}
                frontier_c = {start_c}
                while frontier_c:
                    nf = set()
                    for c in frontier_c:
                        for nc in one_step_reach[c]:
                            if nc not in reached_c:
                                reached_c.add(nc)
                                nf.add(nc)
                    frontier_c = nf
                if len(reached_c) < total_classes:
                    all_reach_all = False
                    min_reach = min(min_reach, len(reached_c))
            
            if all_reach_all:
                print(f"  Class transition graph: STRONGLY CONNECTED ✓")
            else:
                print(f"  Class transition graph: NOT strongly connected (min reach: {min_reach})")


if __name__ == "__main__":
    main()
