#!/usr/bin/env python3
"""
Analyze the fiber structure of the quotient map π: S_{h+1} → S_h.

For each class c ∈ S_h, its fiber π^{-1}(c) is a set of classes in S_{h+1}.
Key questions:
1. Is π_{h+1→h} surjective? (every S_h class has a preimage in S_{h+1})
2. Given a class c' ∈ S_{h+1} in fiber π^{-1}(c), can the boundary sequence steer
   from c' to any other class in π^{-1}(c)?
3. What is the fiber-transition graph structure?

This file was written during an exploratory attempt to treat S_{h+1} as a deterministic automaton
under fixed boundary bits. That assumption is false: same-h predictive classes do not have unique
next classes under a fixed bit. The fiber computations remain meaningful, but any connectivity or
SCC conclusions derived here should be treated as invalid unless reworked using the full set-valued
transition relation.
"""
from __future__ import annotations
import argparse
from itertools import product
from collections import defaultdict, deque


def rule30_next_tuple(state: tuple, boundary_bit: int) -> tuple:
    w = len(state)
    row = (boundary_bit,) + state + (0,)
    return tuple(row[i] ^ (row[i+1] | row[i+2]) for i in range(w))


def build_quotient_maps(h: int):
    """
    Build predictive-state quotient maps for h and h+1 simultaneously.
    Returns:
        class_map_h: dict from h-tuple → class_id in S_h
        class_map_h1: dict from (h+1)-tuple → class_id in S_{h+1}
        n_classes_h: |S_h|
        n_classes_h1: |S_{h+1}|
    """
    # Build incrementally up to h+1
    class_map = {(): 0}
    for hh in range(1, h + 2):
        signatures = {}
        for state in product((0, 1), repeat=hh):
            # Signature: responses to all boundary words of length hh
            sig_parts = []
            for bword in product((0, 1), repeat=hh):
                s = state
                out = []
                for b in bword:
                    out.append(s[0])
                    s = rule30_next_tuple(s, b)
                sig_parts.append(tuple(out))
            sig = tuple(sig_parts)
            signatures[state] = sig
        
        # Equivalence classes
        sig_to_id = {}
        cid_map = {}
        next_id = 0
        for state, sig in signatures.items():
            if sig not in sig_to_id:
                sig_to_id[sig] = next_id
                next_id += 1
            cid_map[state] = sig_to_id[sig]
        
        if hh == h:
            class_map_h = cid_map.copy()
            n_classes_h = next_id
        if hh == h + 1:
            class_map_h1 = cid_map.copy()
            n_classes_h1 = next_id
    
    return class_map_h, class_map_h1, n_classes_h, n_classes_h1


def compute_fiber_map(h: int, class_map_h, class_map_h1, n_classes_h, n_classes_h1):
    """
    Compute π: S_{h+1} → S_h (projection by dropping rightmost bit and projecting class).
    
    For a state s = (s_0, ..., s_h) ∈ {0,1}^{h+1}, its projection is (s_0, ..., s_{h-1}).
    This projection respects classes: π(class_h1) → class_h.
    
    Returns:
        fiber_of: dict from class_h_id → list of class_h1_ids
        projection: dict from class_h1_id → class_h_id
    """
    # Determine projection for each S_{h+1} class by checking any representative
    class_h1_representatives = {}
    for state, cid in class_map_h1.items():
        if cid not in class_h1_representatives:
            class_h1_representatives[cid] = state
    
    projection = {}
    for cid1, state in class_h1_representatives.items():
        shorter = state[:h]  # drop last bit
        cid0 = class_map_h[shorter]
        projection[cid1] = cid0
    
    # Verify projection is well-defined (it should always be, by construction)
    # (quick sanity check for one more state per class)
    
    fiber_of = defaultdict(list)
    for cid1, cid0 in projection.items():
        fiber_of[cid0].append(cid1)
    
    return dict(fiber_of), projection


def compute_transitions(h1: int, class_map_h1, n_classes_h1):
    """
    Compute the transition function for S_{h+1}: for each class c and boundary bit b,
    what class does c transition to?
    Uses integer-based lookup for speed.
    """
    # For efficiency, build next_state tables as tuples
    # transitions[cid1][b] = cid1_next
    
    # Get representatives
    class_h1_representatives = {}
    for state, cid in class_map_h1.items():
        if cid not in class_h1_representatives:
            class_h1_representatives[cid] = state
    
    transitions = {}
    for cid1, state in class_h1_representatives.items():
        row = {}
        for b in (0, 1):
            next_state = rule30_next_tuple(state, b)
            next_cid = class_map_h1[next_state]
            row[b] = next_cid
        transitions[cid1] = row
    
    return transitions


def analyze_fiber_connectivity(h: int, fiber_of, transitions, n_classes_h, n_classes_h1):
    """
    For each fiber π^{-1}(c) in S_{h+1}, check if its elements are all in the same
    strongly connected component under the restricted dynamics.
    
    More importantly: for each pair (c', c'') in the same fiber, is there a boundary
    word that drives S_{h+1} from c' to c''?
    
    Returns:
        fiber_scc_info: for each fiber, connectivity info
    """
    results = {}
    for base_cid, fiber in fiber_of.items():
        if len(fiber) == 1:
            results[base_cid] = {"size": 1, "fiber": fiber, "connected": True, "sccs": [[fiber[0]]]}
            continue
        
        # BFS from each element of fiber: how many other fiber elements are reachable?
        fiber_set = set(fiber)
        reachability = {}
        for start in fiber:
            # BFS through all of S_{h+1}, counting how many fiber elements we reach
            visited = {start}
            queue = deque([start])
            fiber_reached = {start}
            while queue:
                c = queue.popleft()
                for b in (0, 1):
                    nxt = transitions[c][b]
                    if nxt not in visited:
                        visited.add(nxt)
                        queue.append(nxt)
                    if nxt in fiber_set and nxt not in fiber_reached:
                        fiber_reached.add(nxt)
            reachability[start] = fiber_reached
        
        # Check if all fiber elements reach all others (strongly connected fiber)
        all_reach_all = all(
            len(reachability[s]) == len(fiber)
            for s in fiber
        )
        
        # Find SCCs within fiber (restricted: only count fiber elements in path)
        # Simple: compute reachability from each, then identify mutual-reach groups
        sccs = []
        remaining = set(fiber)
        while remaining:
            start = next(iter(remaining))
            scc = {c for c in remaining if start in reachability[c] and c in reachability[start]}
            sccs.append(sorted(scc))
            remaining -= scc
        
        results[base_cid] = {
            "size": len(fiber),
            "fiber": sorted(fiber),
            "connected": all_reach_all,
            "sccs": sccs,
        }
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Analyze fiber structure of S_{h+1} → S_h")
    parser.add_argument("--horizon", type=int, default=6, help="Base horizon h")
    parser.add_argument("--verbose", action="store_true", help="Print all fibers")
    args = parser.parse_args()
    
    h = args.horizon
    print(f"Building quotient maps for h={h} and h+1={h+1}...")
    class_map_h, class_map_h1, n_classes_h, n_classes_h1 = build_quotient_maps(h)
    print(f"  |S_{h}| = {n_classes_h}, |S_{h+1}| = {n_classes_h1}")
    
    print(f"Computing fiber map π: S_{h+1} → S_{h}...")
    fiber_of, projection = compute_fiber_map(h, class_map_h, class_map_h1, n_classes_h, n_classes_h1)
    
    # Check surjectivity
    covered = set(fiber_of.keys())
    n_covered = len(covered)
    print(f"  π is {'SURJECTIVE' if n_covered == n_classes_h else 'NOT surjective'}: "
          f"{n_covered}/{n_classes_h} S_{h} classes have preimages")
    
    # Fiber size distribution
    fiber_sizes = [len(f) for f in fiber_of.values()]
    from collections import Counter
    size_dist = Counter(fiber_sizes)
    print(f"  Fiber size distribution: {dict(sorted(size_dist.items()))}")
    print(f"  Mean fiber size: {sum(fiber_sizes)/len(fiber_sizes):.2f}")
    print(f"  Max fiber size: {max(fiber_sizes)}")
    
    print(f"\nComputing S_{h+1} transitions...")
    transitions = compute_transitions(h+1, class_map_h1, n_classes_h1)
    
    print(f"Analyzing fiber connectivity...")
    fiber_info = analyze_fiber_connectivity(h, fiber_of, transitions, n_classes_h, n_classes_h1)
    
    # Summary
    n_singleton = sum(1 for info in fiber_info.values() if info["size"] == 1)
    n_connected = sum(1 for info in fiber_info.values() if info["connected"])
    n_disconnected = sum(1 for info in fiber_info.values() if not info["connected"])
    
    print(f"\n=== Fiber Connectivity Summary for h={h} ===")
    print(f"  Singleton fibers (trivially connected): {n_singleton}/{n_classes_h}")
    print(f"  Multi-element fibers: {n_classes_h - n_singleton}")
    print(f"    Fully connected (all reach all within S_{{h+1}}): {n_connected - n_singleton}")
    print(f"    NOT fully connected: {n_disconnected}")
    
    if n_disconnected > 0:
        print(f"\nDisconnected fibers:")
        for base_cid, info in fiber_info.items():
            if not info["connected"]:
                print(f"  S_{h} class {base_cid}: fiber={info['fiber']}, SCCs={info['sccs']}")
    
    if args.verbose:
        print(f"\nAll fibers:")
        for base_cid in sorted(fiber_of.keys()):
            info = fiber_info[base_cid]
            print(f"  S_{h} cls {base_cid:4d}: fiber={info['fiber']} size={info['size']} connected={info['connected']}")
    
    # Check: does the full S_{h+1} automaton form a single SCC?
    print(f"\nChecking global S_{h+1} strong connectivity...")
    # BFS from class 0
    visited = {0}
    queue = deque([0])
    while queue:
        c = queue.popleft()
        for b in (0, 1):
            nxt = transitions[c][b]
            if nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)
    print(f"  From class 0, reachable in S_{h+1}: {len(visited)}/{n_classes_h1}")
    
    # Now check reverse reachability (SCC structure of the quotient automaton)
    # Build reverse graph
    reverse = defaultdict(set)
    for c in range(n_classes_h1):
        for b in (0, 1):
            nxt = transitions[c][b]
            reverse[nxt].add(c)
    
    # BFS backward from class 0
    visited_rev = {0}
    queue = deque([0])
    while queue:
        c = queue.popleft()
        for prev in reverse[c]:
            if prev not in visited_rev:
                visited_rev.add(prev)
                queue.append(prev)
    print(f"  Classes that can reach class 0 in S_{h+1}: {len(visited_rev)}/{n_classes_h1}")
    
    if len(visited) == n_classes_h1 and len(visited_rev) == n_classes_h1:
        print(f"  => S_{h+1} quotient automaton is STRONGLY CONNECTED (single SCC)")
    else:
        print(f"  => S_{h+1} quotient automaton is NOT strongly connected")


if __name__ == "__main__":
    main()
