#!/usr/bin/env python3
"""
Invalid exploratory script kept only as a record of a discarded deterministic-class assumption.
"""

raise SystemExit(
    "Invalid analysis: same-h predictive classes do not define deterministic transitions under fixed input."
)

from itertools import product
from collections import defaultdict, deque
import sys


def rule30_next_tuple(state, boundary_bit):
    w = len(state)
    row = (boundary_bit,) + state + (0,)
    return tuple(row[i] ^ (row[i+1] | row[i+2]) for i in range(w))


def analyze_h(h):
    # Build signatures for S_h
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

    zeros = (0,) * h
    zeros_cls = cid_map[zeros]
    ones = (1,) * h
    ones_cls = cid_map.get(ones, -1)

    # Build transitions
    trans = {}
    for cid, state in reps.items():
        trans[cid] = {b: cid_map[rule30_next_tuple(state, b)] for b in (0, 1)}

    # Forward BFS from zeros_cls
    visited_fwd = {zeros_cls}
    q = deque([zeros_cls])
    while q:
        c = q.popleft()
        for b in (0, 1):
            nxt = trans[c][b]
            if nxt not in visited_fwd:
                visited_fwd.add(nxt)
                q.append(nxt)

    # Classes NOT reachable from zeros
    unreachable = set(range(n_classes)) - visited_fwd

    if not unreachable:
        print(f"h={h}: all {n_classes} classes reachable from zeros. zeros_cls={zeros_cls}")
        return

    # For each unreachable class, find which classes CAN reach it
    # Build reverse graph
    rev = defaultdict(set)
    for c in range(n_classes):
        for b in (0, 1):
            rev[trans[c][b]].add(c)

    print(f"h={h}: {len(unreachable)} classes NOT reachable from zeros (cls {zeros_cls}):")
    for uc in sorted(unreachable):
        # Backward BFS from uc: who can reach uc?
        predset = {uc}
        q = deque([uc])
        while q:
            c = q.popleft()
            for prev in rev[c]:
                if prev not in predset:
                    predset.add(prev)
                    q.append(prev)
        rep = reps[uc]
        wt = sum(rep)
        print(f"  cls {uc:4d}: rep={rep}, wt={wt}, predecessors={len(predset)}")
        # Check if any predecessor is reachable from zeros
        pred_reachable_from_zeros = predset & visited_fwd
        print(f"    predecessors reachable from zeros: {len(pred_reachable_from_zeros)}/{len(predset)}")
        if pred_reachable_from_zeros:
            # Find shortest path from zeros to any such predecessor
            example_pred = next(iter(pred_reachable_from_zeros))
            print(f"    example predecessor reachable from zeros: cls {example_pred} rep={reps[example_pred]}")
    print()


for h in [7, 8, 9, 10, 11, 12]:
    analyze_h(h)
    if h >= 11:
        break  # too slow for larger h with this exhaustive method
