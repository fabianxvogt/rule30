#!/usr/bin/env python3
"""
Find which class in S_h is not visited by the first M center-column bits.
Uses a fast approach: build the quotient incrementally and track visits.
"""
from __future__ import annotations
import sys
import os
from itertools import product
sys.path.insert(0, os.path.dirname(__file__))
from rule30_center_column import generate_center_column_bitwise


def rule30_next_h(state: int, boundary_bit: int, h: int) -> int:
    """Apply Rule 30 to h-bit integer state with given boundary bit.
    Returns the first h bits of the result as an integer."""
    # state is h bits (MSB = leftmost = boundary side)
    # Row is: boundary_bit | state[0]..state[h-1] | 0 (implicit 0 on right)
    result = 0
    prev = boundary_bit
    for i in range(h):
        cur = (state >> (h - 1 - i)) & 1
        nxt = (state >> (h - 2 - i)) & 1 if i < h - 1 else 0
        bit = prev ^ (cur | nxt)
        result = (result << 1) | bit
        prev = cur
    return result


def rule30_next_tuple(state: tuple[int, ...], boundary_bit: int) -> tuple[int, ...]:
    w = len(state)
    row = (boundary_bit,) + state + (0,)
    return tuple(row[i] ^ (row[i+1] | row[i+2]) for i in range(w))


def build_quotient_at_horizon(h, prev_class):
    if h == 0:
        return {(): 0}
    signatures = {}
    for state in product(range(2), repeat=h):
        fb = state[0]
        if prev_class is None:
            sig = (fb, 0, 0)
        else:
            s0 = rule30_next_tuple(state, 0)[:h - 1]
            s1 = rule30_next_tuple(state, 1)[:h - 1]
            sig = (fb, prev_class[s0], prev_class[s1])
        signatures[state] = sig
    sig_to_id: dict = {}
    stc: dict = {}
    for state, sig in signatures.items():
        if sig not in sig_to_id:
            sig_to_id[sig] = len(sig_to_id)
        stc[state] = sig_to_id[sig]
    return stc


def main():
    h = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    steps = int(sys.argv[2]) if len(sys.argv) > 2 else 2_000_000

    print(f"Building quotient maps h=0..{h}...")
    prev = None
    for hh in range(h + 1):
        cm = build_quotient_at_horizon(hh, prev)
        prev = cm
    q = cm
    total_classes = max(q.values()) + 1
    print(f"|S_{h}| = {total_classes} classes")

    # Build class-to-states and state-to-class lookup
    # For fast lookup, use integer encoding
    state_to_class = {}
    class_to_first_state = {}
    for state_tuple, cid in q.items():
        state_int = int("".join(map(str, state_tuple)), 2) if h > 0 else 0
        state_to_class[state_int] = cid
        if cid not in class_to_first_state:
            class_to_first_state[cid] = state_tuple

    print(f"Generating {steps} center-column bits...")
    center = generate_center_column_bitwise(steps - 1)
    print(f"Done ({len(center)} bits). Tracing trajectory at h={h}...")

    state_tuple = (0,) * h
    state_int = 0
    visited = set()
    visited.add(q[state_tuple])
    first_visit = {q[state_tuple]: 0}

    for t in range(1, steps):
        bit = center[t - 1]
        state_tuple = rule30_next_tuple(state_tuple, bit)[:h]
        cid = q[state_tuple]
        if cid not in visited:
            visited.add(cid)
            first_visit[cid] = t
            if len(visited) == total_classes:
                print(f"All {total_classes} classes visited by step {t}!")
                break
        if t % 500000 == 0:
            print(f"  t={t}: {len(visited)}/{total_classes} classes visited...")

    missing = [cid for cid in range(total_classes) if cid not in visited]
    print(f"\nAfter {min(steps, t+1)} steps: {len(visited)}/{total_classes} classes visited.")

    if missing:
        print(f"\nMissing {len(missing)} class(es):")
        for cid in missing:
            states_in_class = [s for s, c in q.items() if c == cid]
            print(f"  Class {cid}: {len(states_in_class)} raw states")
            for s in sorted(states_in_class)[:5]:
                bits = "".join(map(str, s))
                print(f"    {bits}")
            if len(states_in_class) > 5:
                print(f"    ... and {len(states_in_class)-5} more")
    else:
        # Show top 5 rarest (latest first visit)
        print("\nTop 5 rarest (latest first-visit):")
        sorted_fv = sorted(first_visit.items(), key=lambda x: -x[1])
        for cid, fvt in sorted_fv[:5]:
            states_in_class = [s for s, c in q.items() if c == cid]
            bits = "".join(map(str, states_in_class[0]))
            print(f"  class {cid}: first_visit={fvt}, size={len(states_in_class)}, ex: {bits}")


if __name__ == "__main__":
    main()
