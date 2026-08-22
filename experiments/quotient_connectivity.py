#!/usr/bin/env python3
"""
Analyze the transition graph of the S_h quotient automaton for strong connectivity.

For each horizon h, builds the directed graph where nodes are S_h classes and there are
directed edges class --b--> class' for b in {0,1} (the boundary bit input). Then:

1. Checks if the graph is STRONGLY CONNECTED (every class reachable from every other).
2. Finds SCCs (strongly connected components) — if not strongly conn, how many SCCs?
3. Reports the condensation DAG structure.
4. Checks if there's a single "bottom" SCC (all classes in one SCC or all reachable from root).

This is key for the proof: if the quotient automaton is strongly connected, then any 
driving sequence that visits all classes in some SCC will eventually visit ALL classes.
"""
from __future__ import annotations

import sys, os
from itertools import product
from collections import deque, defaultdict

sys.path.insert(0, os.path.dirname(__file__))


def rule30_next_tuple(state: tuple, boundary_bit: int) -> tuple:
    w = len(state)
    row = (boundary_bit,) + state + (0,)
    return tuple(row[i] ^ (row[i+1] | row[i+2]) for i in range(w))


def build_quotient(h: int) -> dict:
    """Build quotient map from h-tuples to class IDs (fast bottom-up)."""
    prev = None
    for hh in range(h + 1):
        if hh == 0:
            cm = {(): 0}
        else:
            signatures = {}
            for state in product(range(2), repeat=hh):
                if prev is None:
                    sig = (state[0], 0, 0)
                else:
                    s0 = rule30_next_tuple(state, 0)[:hh - 1]
                    s1 = rule30_next_tuple(state, 1)[:hh - 1]
                    sig = (state[0], prev[s0], prev[s1])
                signatures[state] = sig
            sig_to_id = {}
            cm = {}
            for state, sig in signatures.items():
                if sig not in sig_to_id:
                    sig_to_id[sig] = len(sig_to_id)
                cm[state] = sig_to_id[sig]
        prev = cm
    return cm


def build_raw_state_transitions(q: dict, h: int):
    """
    Build the raw-state-level transition graph.
    
    Returns:
        n_classes: int
        state_trans: dict[state_tuple][bit] -> next_state_tuple (truncated to h bits)
        state_to_class: same as q
    """
    n_classes = max(q.values()) + 1
    state_trans = {}
    for state in q:
        state_trans[state] = {}
        for bit in range(2):
            ns = rule30_next_tuple(state, bit)[:h]
            state_trans[state][bit] = ns
    return n_classes, state_trans


def scc_kosaraju(n: int, adj: list[list[int]], radj: list[list[int]]) -> list[int]:
    """Kosaraju's algorithm. Returns component id for each node (0-indexed SCCs)."""
    visited = [False] * n
    order = []
    
    def dfs1(v):
        stack = [(v, iter(adj[v]))]
        visited[v] = True
        while stack:
            u, it = stack[-1]
            try:
                w = next(it)
                if not visited[w]:
                    visited[w] = True
                    stack.append((w, iter(adj[w])))
            except StopIteration:
                order.append(u)
                stack.pop()
    
    for v in range(n):
        if not visited[v]:
            dfs1(v)
    
    comp = [-1] * n
    comp_id = 0
    visited2 = [False] * n
    
    def dfs2(v, c):
        stack = [v]
        visited2[v] = True
        comp[v] = c
        while stack:
            u = stack.pop()
            for w in radj[u]:
                if not visited2[w]:
                    visited2[w] = True
                    comp[w] = c
                    stack.append(w)
    
    for v in reversed(order):
        if not visited2[v]:
            dfs2(v, comp_id)
            comp_id += 1
    
    return comp


def analyze_quotient_graph(h: int, verbose: bool = False) -> dict:
    """
    Analyze the S_h raw state transition graph for reachability from all-zeros.
    
    Key question: from the all-zeros raw state, how many distinct S_h classes can be reached
    via BFS over all possible boundary bit sequences?
    
    Returns a dict with analysis results.
    """
    print(f"  h={h}...", end="", flush=True)
    q = build_quotient(h)
    n_classes = max(q.values()) + 1
    
    # BFS over raw states from all-zeros
    zeros = tuple([0] * h)
    visited_states = {zeros}
    visited_classes = {q[zeros]}
    frontier = deque([zeros])
    
    while frontier:
        state = frontier.popleft()
        for bit in range(2):
            ns = rule30_next_tuple(state, bit)[:h]
            if ns not in visited_states:
                visited_states.add(ns)
                visited_classes.add(q[ns])
                frontier.append(ns)
    
    n_states_reachable = len(visited_states)
    n_classes_reachable = len(visited_classes)
    all_states_reachable = (n_states_reachable == 2**h)
    all_classes_reachable = (n_classes_reachable == n_classes)
    
    print(f" |S_h|={n_classes}, states_reached={n_states_reachable}/{2**h}, "
          f"classes_reached={n_classes_reachable}/{n_classes}")
    
    if verbose and not all_states_reachable:
        # Find unreachable classes
        unreachable = set(range(n_classes)) - visited_classes
        print(f"    Unreachable classes: {sorted(unreachable)[:10]}")
    
    return {
        "h": h,
        "n_classes": n_classes,
        "n_raw_states": 2**h,
        "states_reachable": n_states_reachable,
        "classes_reachable": n_classes_reachable,
        "all_states_reachable": all_states_reachable,
        "all_classes_reachable": all_classes_reachable,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-horizon", type=int, default=18)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    
    print(f"Checking raw-state reachability from all-zeros for h=1..{args.max_horizon}")
    print()
    
    results = []
    for h in range(1, args.max_horizon + 1):
        r = analyze_quotient_graph(h, verbose=args.verbose)
        results.append(r)
    
    print()
    print("Summary:")
    print(f"{'h':>4} | {'|S_h|':>6} | {'2^h':>8} | {'states_reached':>14} | {'classes_reached':>15} | {'all_states':>10} | {'all_classes':>11}")
    print("-" * 85)
    for r in results:
        as_ = "YES" if r["all_states_reachable"] else "NO"
        ac = "YES" if r["all_classes_reachable"] else "NO"
        print(f"{r['h']:>4} | {r['n_classes']:>6} | {r['n_raw_states']:>8} | {r['states_reachable']:>14} | {r['classes_reachable']:>15} | {as_:>10} | {ac:>11}")


if __name__ == "__main__":
    main()
