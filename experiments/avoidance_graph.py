#!/usr/bin/env python3
"""
More careful avoidance analysis.

Question: Given any target state t, what is the largest subword complexity a sequence 
can have while avoiding t forever?

Approach: Build the "avoidance graph" — states reachable without visiting t.
The avoidance graph is a subgraph of the full directed graph (states are {0,1}^h \ {t}).
From state s, edges go to f_0(s) and f_1(s), but only if the target is not f_b(s).

The sequences that avoid t correspond to walks in this avoidance graph.
The subword complexity of such walks is related to the structure of this graph.

Key: If the avoidance graph has a strongly connected component containing the 
starting state, then indefinite avoidance is possible. The subword complexity 
is related to the size and structure of this SCC.
"""
from __future__ import annotations
import os, sys
from collections import deque
sys.path.insert(0, os.path.dirname(__file__))
from fast_class_coverage2 import rule30_next_tuple


def build_maps(h):
    N = 1 << h
    f = [[0]*N, [0]*N]
    for b in range(2):
        for s_int in range(N):
            state = tuple((s_int >> i) & 1 for i in range(h))
            ns = rule30_next_tuple(state, b)[:h]
            f[b][s_int] = sum(bit << i for i, bit in enumerate(ns))
    return f


def avoidance_graph(h, f, target):
    """Build directed graph of states reachable while avoiding target.
    Returns: adjacency list, where adj[s] = [(b, s') for valid transitions]
    """
    N = 1 << h
    adj = {s: [] for s in range(N) if s != target}
    for s in adj:
        for b in range(2):
            s_next = f[b][s]
            if s_next != target:
                adj[s].append((b, s_next))
    return adj


def find_sccs(adj, nodes):
    """Tarjan's SCC algorithm."""
    index_counter = [0]
    stack = []
    lowlink = {}
    index = {}
    on_stack = {}
    sccs = []
    
    def strongconnect(v):
        index[v] = index_counter[0]
        lowlink[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack[v] = True
        
        for _, w in adj.get(v, []):
            if w not in index:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif on_stack.get(w, False):
                lowlink[v] = min(lowlink[v], index[w])
        
        if lowlink[v] == index[v]:
            scc = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.append(w)
                if w == v:
                    break
            sccs.append(scc)
    
    for v in nodes:
        if v not in index:
            strongconnect(v)
    
    return sccs


def subword_complexity_of_walk(adj, start, max_len, max_steps=100000):
    """Estimate subword complexity of walks in the graph from start.
    Returns: dict mapping length -> number of distinct subwords seen.
    """
    import random
    random.seed(42)
    
    # Generate a long random walk
    walk = []
    state = start
    for _ in range(max_steps):
        edges = adj.get(state, [])
        if not edges:
            break
        b, s_next = random.choice(edges)
        walk.append(str(b))
        state = s_next
    
    walk_str = ''.join(walk)
    
    result = {}
    for l in range(1, max_len + 1):
        seen = set()
        for i in range(len(walk_str) - l + 1):
            seen.add(walk_str[i:i+l])
        result[l] = len(seen)
    
    return result


def main():
    for h in [5, 8, 10, 12]:
        N = 1 << h
        f = build_maps(h)
        
        print(f"\n{'='*60}")
        print(f"h={h}, N={N}")
        print(f"{'='*60}")
        
        # Analyze avoidance graph for each target
        scc_sizes = []
        max_scc_reachable = 0
        
        for target in range(N):
            adj = avoidance_graph(h, f, target)
            nodes = [s for s in range(N) if s != target]
            sccs = find_sccs(adj, nodes)
            
            max_scc = max(len(scc) for scc in sccs) if sccs else 0
            scc_sizes.append(max_scc)
            
            # Is the starting state (0) in a nontrivial SCC?
            for scc in sccs:
                if 0 in scc and len(scc) > 1:
                    if len(scc) > max_scc_reachable:
                        max_scc_reachable = len(scc)
        
        # Statistics
        scc_sizes.sort(reverse=True)
        print(f"  Max SCC size across all targets: {max(scc_sizes)}")
        print(f"  Min SCC size across all targets: {min(scc_sizes)}")
        print(f"  Mean SCC size: {sum(scc_sizes)/len(scc_sizes):.1f}")
        print(f"  Max SCC reachable from state 0: {max_scc_reachable}")
        
        # Detailed analysis for a few targets
        for target in [0, 1, N//2]:
            adj = avoidance_graph(h, f, target)
            nodes = [s for s in range(N) if s != target]
            sccs = find_sccs(adj, nodes)
            
            nontrivial = [scc for scc in sccs if len(scc) > 1]
            max_scc = max(len(scc) for scc in sccs) if sccs else 0
            
            # Check if 0 can reach a big SCC
            reachable = set()
            queue = deque([0 if target != 0 else 1])
            reachable.add(queue[0])
            while queue:
                v = queue.popleft()
                for _, w in adj.get(v, []):
                    if w not in reachable:
                        reachable.add(w)
                        queue.append(w)
            
            print(f"\n  Target={target}: max SCC={max_scc}, "
                  f"#nontrivial SCCs={len(nontrivial)}, "
                  f"|reachable from {'0' if target != 0 else '1'}|={len(reachable)}")
            
            # Check: how many bits observed in the avoidance walk?
            start = 0 if target != 0 else 1
            sw = subword_complexity_of_walk(adj, start, min(h+2, 20), max_steps=50000)
            for l in sorted(sw.keys()):
                if l <= h + 2:
                    print(f"    subword complexity at length {l}: {sw[l]}/{min(2**l, 50000)}")
        
        # KEY: for how many targets is the avoidance graph strongly connected 
        # (single SCC of size N-1)?
        fully_connected = sum(1 for s in scc_sizes if s == N - 1)
        print(f"\n  Targets with fully-connected avoidance graph: {fully_connected}/{N}")


if __name__ == "__main__":
    main()
