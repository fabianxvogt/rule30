#!/usr/bin/env python3
"""
Invalid exploratory script.

This script assumes a deterministic transition on S_h obtained by applying the local rule to a single
representative of each predictive class. That assumption is false: at fixed h, a predictive class and
input bit can map to multiple different predictive classes. Any SCC output from this file is therefore
not mathematically meaningful.
"""
from itertools import product
from collections import defaultdict, deque
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


def rule30_next_tuple(state, boundary_bit):
    w = len(state)
    row = (boundary_bit,) + state + (0,)
    return tuple(row[i] ^ (row[i+1] | row[i+2]) for i in range(w))


def build_quotient(h):
    signatures = {}
    for state in product((0, 1), repeat=h):
        sig_parts = []
        for bword in product((0, 1), repeat=h):
            s = state
            out = []
            for b in bword:
                out.append(s[0])
                s = rule30_next_tuple(s, b)
            sig_parts.append(tuple(out))
        signatures[state] = tuple(sig_parts)

    sig_to_id = {}
    cid_map = {}
    reps = {}
    next_id = 0
    for state, sig in signatures.items():
        if sig not in sig_to_id:
            sig_to_id[sig] = next_id
            reps[next_id] = state
            next_id += 1
        cid_map[state] = sig_to_id[sig]
    n_classes = next_id
    return cid_map, reps, n_classes


def compute_sccs(trans, n_classes):
    """Kosaraju's algorithm for SCCs."""
    # Step 1: DFS on forward graph, record finish order
    visited = set()
    finish_order = []

    def dfs_forward(start):
        stack = [(start, False)]
        while stack:
            node, returning = stack.pop()
            if returning:
                finish_order.append(node)
                continue
            if node in visited:
                continue
            visited.add(node)
            stack.append((node, True))
            for b in (0, 1):
                nxt = trans[node][b]
                if nxt not in visited:
                    stack.append((nxt, False))

    for c in range(n_classes):
        if c not in visited:
            dfs_forward(c)

    # Step 2: Build reverse graph
    rev = defaultdict(set)
    for c in range(n_classes):
        for b in (0, 1):
            rev[trans[c][b]].add(c)

    # Step 3: DFS on reverse graph in reverse finish order
    visited2 = set()
    sccs = []

    def dfs_reverse(start):
        scc = []
        stack = [start]
        while stack:
            node = stack.pop()
            if node in visited2:
                continue
            visited2.add(node)
            scc.append(node)
            for prev in rev[node]:
                if prev not in visited2:
                    stack.append(prev)
        return scc

    for c in reversed(finish_order):
        if c not in visited2:
            scc = dfs_reverse(c)
            sccs.append(scc)

    return sccs


def main():
    raise SystemExit(
        "Invalid analysis: same-h predictive classes do not define deterministic transitions under fixed input."
    )

    h = int(sys.argv[1]) if len(sys.argv) > 1 else 9

    print(f"Building S_{h} quotient...")
    cid_map, reps, n_classes = build_quotient(h)
    print(f"  |S_{h}| = {n_classes}")

    # Build transitions
    trans = {}
    for cid, state in reps.items():
        trans[cid] = {b: cid_map[rule30_next_tuple(state, b)] for b in (0, 1)}

    # Compute SCCs
    print(f"Computing SCCs...")
    sccs = compute_sccs(trans, n_classes)
    print(f"  Number of SCCs: {len(sccs)}")
    print(f"  SCC size distribution:")
    from collections import Counter
    size_dist = Counter(len(s) for s in sccs)
    for sz, cnt in sorted(size_dist.items()):
        print(f"    size={sz}: {cnt} SCCs")

    # Identify SCC of zeros
    zeros = (0,) * h
    zeros_cls = cid_map[zeros]
    zeros_scc_id = next(i for i, scc in enumerate(sccs) if zeros_cls in scc)
    zeros_scc = sccs[zeros_scc_id]
    print(f"\n  all-zeros class {zeros_cls} is in SCC #{zeros_scc_id} of size {len(zeros_scc)}")

    # Condensation DAG: which SCCs can reach which?
    scc_of = {}
    for i, scc in enumerate(sccs):
        for c in scc:
            scc_of[c] = i

    # BFS from zeros_scc in condensation
    scc_edges = set()
    for c in range(n_classes):
        for b in (0, 1):
            nxt = trans[c][b]
            si, sj = scc_of[c], scc_of[nxt]
            if si != sj:
                scc_edges.add((si, sj))

    # Forward BFS from zeros_scc in condensation
    visited_cond = {zeros_scc_id}
    q = deque([zeros_scc_id])
    while q:
        s = q.popleft()
        for (si, sj) in scc_edges:
            if si == s and sj not in visited_cond:
                visited_cond.add(sj)
                q.append(sj)

    reachable_classes = sum(len(sccs[i]) for i in visited_cond)
    print(f"  SCCs reachable from zeros_scc: {len(visited_cond)}/{len(sccs)}")
    print(f"  Classes reachable from zeros via SCC DAG: {reachable_classes}/{n_classes}")

    # Which SCCs are NOT reachable?
    unreachable_sccs = set(range(len(sccs))) - visited_cond
    unreachable_classes = [c for i in unreachable_sccs for c in sccs[i]]
    print(f"\n  Unreachable SCCs: {len(unreachable_sccs)}, containing {len(unreachable_classes)} classes")
    for uc in unreachable_classes:
        rep = reps[uc]
        wt = sum(rep)
        print(f"    cls {uc:4d}: rep={rep}, wt={wt}, in SCC #{scc_of[uc]} (size {len(sccs[scc_of[uc]])})")

    # Now trace actual center-column trajectory and record first-visit times for unreachable classes
    # Use the precomputed file for fast tracing
    bit_file = "results/center-column-1000000.txt"
    if not os.path.exists(bit_file):
        print(f"\nFile {bit_file} not found; skipping empirical trace")
        return

    print(f"\nTracing center-column trajectory to find unreachable-from-zeros classes...")
    with open(bit_file) as f:
        bits_str = f.read().strip()

    # Integer-based lookup: faster state transitions
    next_state = [{}, {}]
    for b in (0, 1):
        for cid, state in reps.items():
            ns = rule30_next_tuple(state, b)
            next_state[b][cid] = cid_map[ns]

    # Initial state: rightmost h bits starting from zeros (center column starts from 0 seed)
    # The initial right-half state is all-zeros
    state = cid_map[(0,) * h]
    unreachable_set = set(unreachable_classes)
    first_visits = {}

    for t, ch in enumerate(bits_str):
        b = int(ch)
        if state in unreachable_set and state not in first_visits:
            first_visits[state] = t
        state = next_state[b][state]

    # Check which unreachable classes were visited
    print(f"  Of {len(unreachable_classes)} unreachable-from-zeros classes:")
    visited_count = 0
    for uc in sorted(unreachable_classes):
        if uc in first_visits:
            visited_count += 1
            rep = reps[uc]
            wt = sum(rep)
            print(f"    cls {uc:4d} (wt={wt}): VISITED at t={first_visits[uc]}")
        else:
            rep = reps[uc]
            wt = sum(rep)
            print(f"    cls {uc:4d} (wt={wt}): NOT visited in {len(bits_str)} steps")
    print(f"  {visited_count}/{len(unreachable_classes)} unreachable-from-zeros classes visited in 1M steps")


if __name__ == "__main__":
    main()
