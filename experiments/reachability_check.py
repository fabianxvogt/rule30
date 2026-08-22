#!/usr/bin/env python3
"""
Check strong connectivity (and reachability from initial class) in the
predictive-state quotient graph S_h.

The quotient graph has:
- Nodes: classes in S_h
- Edges: (c, c') labeled by bit b, meaning c' = delta_h(c, b)

BUT delta_h may not be well-defined (shown earlier).

Alternative: we use the CROSS-LEVEL transition.
Actually, let's reason about what "reachable" means for the driven trajectory.

The driven trajectory produces a sequence of h-TRUNCATED right-half states.
s(0) = (0,0,...,0)  [h zeros]
s(t+1) = rule30_next(s(t), center(t))[:h]

The CLASS of s(t) is q_h(s(t)).

The question: is every class in S_h reachable from q_h((0,...,0)) via some finite
prefix of boundary bits?

This is equivalent to: for every class c in S_h, does there exist a bit sequence
b_0, ..., b_{k-1} and a sequence of width-h states s_0=(0,..,0), s_1, ..., s_k
such that:
  s_{i+1} = rule30_next(s_i, b_i)[:h]
  q_h(s_k) = c ?

We can answer this via BFS in the RAW state space (width-h bit strings), lifted
to quotient classes.

Note: this is different from the intra-level transition on CLASSES (which was
not well-defined). Here we work in the RAW state space and ask which classes
are reachable.
"""

from __future__ import annotations

import argparse
from itertools import product
from collections import deque


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


def bfs_reachable_classes(
    h: int,
    q: dict[tuple[int, ...], int],
    total_classes: int,
) -> dict[int, int]:
    """BFS from the all-zeros state: find which classes are reachable and the
    minimum number of steps to first reach each class.

    Returns: dict class_id -> min_steps_to_reach (or not present if unreachable)
    """
    initial = (0,) * h
    initial_class = q[initial]

    # BFS: state is an h-bit string (tuple)
    # We track which CLASSES have been visited (not individual states)
    visited_states: set[tuple[int, ...]] = {initial}
    queue: deque[tuple[tuple[int, ...], int]] = deque([(initial, 0)])
    class_first_reach: dict[int, int] = {initial_class: 0}

    while queue:
        state, t = queue.popleft()
        for b in (0, 1):
            nxt = rule30_next(state, b)[:h]
            if nxt not in visited_states:
                visited_states.add(nxt)
                cid = q[nxt]
                if cid not in class_first_reach:
                    class_first_reach[cid] = t + 1
                queue.append((nxt, t + 1))

            # Even if nxt was already visited, check its class
            else:
                cid = q[nxt]
                if cid not in class_first_reach:
                    class_first_reach[cid] = t + 1

    return class_first_reach


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-horizon", type=int, default=14)
    args = parser.parse_args()

    max_h = args.max_horizon

    print(f"Checking reachability in predictive-state quotient graphs h=1..{max_h}")
    print()
    print(f"{'h':>3} | {'|S_h|':>7} | {'reachable':>9} | {'all?':>5} | {'max_bfs_depth':>14} | "
          f"{'raw_states_visited':>19}")
    print("-" * 70)

    prev = None
    for h in range(max_h + 1):
        cm = build_quotient_at_horizon(h, prev)
        prev = cm

        if h == 0:
            print(f"{h:>3} | {1:>7} | {1:>9} | {'yes':>5} | {0:>14} | {1:>19}")
            continue

        total_classes = max(cm.values()) + 1
        class_reach = bfs_reachable_classes(h, cm, total_classes)
        reachable_count = len(class_reach)
        all_reachable = (reachable_count == total_classes)
        max_depth = max(class_reach.values()) if class_reach else 0
        raw_visited = sum(1 for _ in product(range(2), repeat=h))  # 2^h total raw states

        # Actually count how many raw states were visited (BFS visits all of them if strongly connected)
        # Let's recount from BFS for accuracy
        visited_count = count_reachable_states(h, cm)

        print(f"{h:>3} | {total_classes:>7} | {reachable_count:>9} | "
              f"{'yes' if all_reachable else 'NO':>5} | {max_depth:>14} | "
              f"{visited_count:>19} / {2**h}")

        if not all_reachable:
            unreachable = [c for c in range(total_classes) if c not in class_reach]
            print(f"  Unreachable classes: {unreachable[:10]}")


def count_reachable_states(h: int, q: dict) -> int:
    """Count how many raw width-h states are reachable from all-zeros."""
    initial = (0,) * h
    visited: set[tuple[int, ...]] = {initial}
    queue: deque[tuple[int, ...]] = deque([initial])
    while queue:
        state = queue.popleft()
        for b in (0, 1):
            nxt = rule30_next(state, b)[:h]
            if nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)
    return len(visited)


if __name__ == "__main__":
    main()
