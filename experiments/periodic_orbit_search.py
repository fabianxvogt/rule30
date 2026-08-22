#!/usr/bin/env python3
"""
Search for periodic orbits in the predictive-state quotient system.

If the center column were eventually periodic with period p, the projected
trajectory in S_h would also be eventually periodic with period dividing p.
This means there must exist a p-periodic orbit in S_h consistent with the
transition structure.

A p-periodic orbit is a sequence of classes c_0, c_1, ..., c_{p-1} in S_h
and boundary bits b_0, b_1, ..., b_{p-1} in {0,1} such that:
  delta(c_i, b_i) = c_{(i+1) mod p}

where delta is the transition map c_i -[b_i]-> c_{i-1 at horizon h-1}... wait,
the transition goes DOWN in horizon.  Let me think more carefully.

Actually the transition map is:
  At each time step, the center-column bit b(t) drives the update:
  right_half_{t+1}(x) = f(right_half_t, b(t), x)
  And in the quotient this becomes:
  [right_half_{t+1}]_h = delta_h([ right_half_t ]_h, b(t))

where delta_h : S_h x {0,1} -> S_h is the FULL-HORIZON transition
(not the cross-horizon one we checked earlier for well-definedness).

So we need to compute the SELF-MAP delta_h on S_h (not the cross-level map).

This is different from what we computed in predictive_state_growth.py!
In that script, we checked that the cross-level map (S_h -> S_{h-1}) is
well-defined.  Here we need the intra-level map (S_h -> S_h).

For a p-periodic orbit driven by bit sequence b_0, ..., b_{p-1}:
  c_1 = delta_h(c_0, b_0)
  c_2 = delta_h(c_1, b_1)
  ...
  c_0 = delta_h(c_{p-1}, b_{p-1})

If such an orbit exists, the center column COULD be eventually periodic with
period p (at least not ruled out by horizon-h predictive states alone).

If NO such orbit exists at any h, that proves non-periodicity.

We compute delta_h by direct simulation of the right half-plane quotient.
"""

from __future__ import annotations

import argparse
import sys
import os
from itertools import product

sys.path.insert(0, os.path.dirname(__file__))


def rule30_next(state: tuple[int, ...], boundary_bit: int) -> tuple[int, ...]:
    w = len(state)
    if w == 0:
        return ()
    row = (boundary_bit,) + state + (0,)
    return tuple(row[i] ^ (row[i + 1] | row[i + 2]) for i in range(w))


def build_quotient_at_horizon(h, prev_class):
    if h == 0:
        return {(): 0}
    signatures = {}
    for state in product(range(2), repeat=h):
        fb = state[0]
        if prev_class is None:
            sig = (fb, 0, 0)
        else:
            s0 = rule30_next(state, 0)[:h - 1]
            s1 = rule30_next(state, 1)[:h - 1]
            sig = (fb, prev_class[s0], prev_class[s1])
        signatures[state] = sig
    sig_to_id: dict = {}
    stc: dict = {}
    for state, sig in signatures.items():
        if sig not in sig_to_id:
            sig_to_id[sig] = len(sig_to_id)
        stc[state] = sig_to_id[sig]
    return stc


def build_intra_level_transitions(
    h: int,
    state_to_class: dict[tuple[int, ...], int],
    total_classes: int,
) -> tuple[dict[tuple[int, int], int], bool]:
    """Build the intra-level transition table delta_h: S_h x {0,1} -> S_h.

    delta_h(c, b) = the class of next(state, b) truncated to width h,
    where state is any representative of class c.

    Returns (transition_table, is_well_defined).
    The transition table maps (class_id, bit) -> class_id.
    """
    transition: dict[tuple[int, int], int] = {}
    well_defined = True
    for state, cid in state_to_class.items():
        for b in (0, 1):
            nxt = rule30_next(state, b)[:h]  # stay at width h!
            target_cid = state_to_class[nxt]
            key = (cid, b)
            if key in transition:
                if transition[key] != target_cid:
                    well_defined = False
                    # keep going to see all conflicts
            else:
                transition[key] = target_cid
    return transition, well_defined


def find_periodic_orbits(
    transition: dict[tuple[int, int], int],
    total_classes: int,
    max_period: int,
) -> list[tuple[int, list[int], list[int]]]:
    """Find all periodic orbits of period <= max_period in the transition system.

    A periodic orbit is represented as (period, class_sequence, bit_sequence).
    We only find orbits reachable from class 0 (the all-zeros initial state class).

    Returns list of (period, class_ids, bits).
    """
    # BFS / DFS to enumerate all sequences from class 0
    # State: (current_class, class_sequence_so_far, bit_sequence_so_far)
    # We look for cycles.

    found_orbits: list[tuple[int, list[int], list[int]]] = []
    # seen_prefixes: to avoid re-exploring. key = (current_class, depth)
    # Actually we want ALL orbits, not just those reachable from class 0.
    # -> search for cycles in the full graph.

    # For each starting class, do DFS up to depth max_period.
    found_orbit_sigs: set[frozenset] = set()

    for start_class in range(total_classes):
        # DFS
        stack: list[tuple[int, list[int], list[int]]] = [
            (start_class, [start_class], [])
        ]
        while stack:
            cur, cls_seq, bit_seq = stack.pop()
            depth = len(bit_seq)
            if depth >= max_period:
                continue
            for b in (0, 1):
                key = (cur, b)
                if key not in transition:
                    continue
                nxt = transition[key]
                new_bits = bit_seq + [b]
                new_cls = cls_seq + [nxt]
                if nxt == start_class:
                    # Found an orbit of length depth+1
                    p = depth + 1
                    sig = frozenset(enumerate(new_cls[:-1]))  # canonical
                    if sig not in found_orbit_sigs:
                        found_orbit_sigs.add(sig)
                        found_orbits.append((p, new_cls[:-1], new_bits))
                elif nxt not in cls_seq:
                    stack.append((nxt, new_cls, new_bits))
                # else: nxt already in path but not = start_class -> not a simple cycle from start

    return found_orbits


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--horizon", type=int, default=8,
                        help="Horizon h to analyze (default: 8)")
    parser.add_argument("--max-period", type=int, default=8,
                        help="Maximum period to search for (default: 8)")
    args = parser.parse_args()

    h = args.horizon
    max_period = args.max_period

    print(f"Building quotient maps h=0..{h}...")
    prev = None
    for hh in range(h + 1):
        cm = build_quotient_at_horizon(hh, prev)
        prev = cm
    q = cm
    total_classes = max(q.values()) + 1
    print(f"|S_{h}| = {total_classes} classes.")

    print(f"Building intra-level transition delta_{h}: S_{h} x {{0,1}} -> S_{h}...")
    trans, wd = build_intra_level_transitions(h, q, total_classes)
    print(f"Is well-defined: {wd}")
    if not wd:
        print("WARNING: intra-level transition is NOT well-defined at this horizon.")
        print("This would mean two states in the same class map to different classes under the same bit.")
        print("This would be a significant structural finding.")
    print()

    # Analyse the structure of the intra-level transition
    # For each class, find where it goes under 0 and 1
    print("Transition summary (first 20 classes):")
    print(f"{'class':>7} | {'->0':>7} | {'->1':>7}")
    print("-" * 27)
    for c in range(min(20, total_classes)):
        t0 = trans.get((c, 0), "?")
        t1 = trans.get((c, 1), "?")
        print(f"{c:>7} | {str(t0):>7} | {str(t1):>7}")

    print()

    # Find all periodic orbits ≤ max_period
    print(f"Searching for periodic orbits with period <= {max_period}...")
    orbits = find_periodic_orbits(trans, total_classes, max_period)
    print(f"Found {len(orbits)} distinct periodic orbits.")
    print()
    if orbits:
        print("Shortest orbits:")
        for (p, cls_seq, bit_seq) in sorted(orbits, key=lambda x: x[0])[:20]:
            bits_str = "".join(map(str, bit_seq))
            cls_str = " -> ".join(map(str, cls_seq)) + " -> ..."
            print(f"  period={p}, bits=[{bits_str}], classes: {cls_str}")
    else:
        print("No periodic orbits found with period <= %d." % max_period)
        print("This means: if the center column were eventually periodic with period <= %d," % max_period)
        print("then at horizon h=%d the projected trajectory would be periodic but no such orbit exists." % h)
        print("=> Center column is NOT eventually periodic with period <= %d (by horizon-%d analysis)." % (max_period, h))


if __name__ == "__main__":
    main()
