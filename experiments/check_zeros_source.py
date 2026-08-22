#!/usr/bin/env python3
"""Invalid exploratory script kept only as a record of a discarded deterministic-class assumption."""

raise SystemExit(
    "Invalid analysis: same-h predictive classes do not define deterministic transitions under fixed input."
)
from itertools import product
from collections import defaultdict, deque


def rule30_next_tuple(state, boundary_bit):
    w = len(state)
    row = (boundary_bit,) + state + (0,)
    return tuple(row[i] ^ (row[i+1] | row[i+2]) for i in range(w))


def analyze_zeros_reachability(h):
    # Build signatures
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
    next_id = 0
    for state, sig in signatures.items():
        if sig not in sig_to_id:
            sig_to_id[sig] = next_id
            next_id += 1
        cid_map[state] = sig_to_id[sig]
    n_classes = next_id

    zeros = (0,) * h
    zeros_cls = cid_map[zeros]

    # Build transitions
    reps = {}
    for state, cid in cid_map.items():
        if cid not in reps:
            reps[cid] = state

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

    # Reverse BFS from zeros_cls
    rev = defaultdict(set)
    for c in range(n_classes):
        for b in (0, 1):
            rev[trans[c][b]].add(c)

    visited_rev = {zeros_cls}
    q = deque([zeros_cls])
    while q:
        c = q.popleft()
        for prev in rev[c]:
            if prev not in visited_rev:
                visited_rev.add(prev)
                q.append(prev)

    # Class of zeros in S_h: what does it transition to under b=0 and b=1?
    zeros_t0 = trans[zeros_cls][0]
    zeros_t1 = trans[zeros_cls][1]

    print(f"h={h}: zeros_cls={zeros_cls}, n_classes={n_classes}")
    print(f"  zeros -> b=0: cls {zeros_t0}, b=1: cls {zeros_t1}")
    print(f"  Forward from zeros: {len(visited_fwd)}/{n_classes} (universal source: {len(visited_fwd)==n_classes})")
    print(f"  Can reach zeros (backward): {len(visited_rev)}/{n_classes}")
    print()


for h in range(3, 13):
    analyze_zeros_reachability(h)
