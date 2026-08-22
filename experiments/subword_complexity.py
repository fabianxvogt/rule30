#!/usr/bin/env python3
"""
Study the relationship between subword complexity of the center column and
class coverage in the predictive-state quotient.

Key question: do N distinct length-h subwords of the center column correspond to
N distinct classes in S_h?  If yes, then the number of distinct classes visited =
the subword complexity function k_c(h) of the center column.

If the center column has period p, then k_c(h) <= p for all h >= 1 (since only p
distinct length-h windows can appear in a period-p sequence).  But if k_c(h) > p
for some h, the column is not period-p.  And if k_c(h) = |S_h| ~ exp(h^{2/3}),
it already shows non-periodicity (since p >= k_c(h) >= exp(h^{2/3}) - const, 
contradicting fixed p).

We measure:
1. k_c(h) = number of distinct length-h subwords in a long prefix of center column.
2. Number of distinct classes in S_h visited by those k_c(h) subwords.
3. Whether distinct subwords -> distinct classes (injective mapping).
"""

from __future__ import annotations

import argparse
import sys
import os
from itertools import product

sys.path.insert(0, os.path.dirname(__file__))
from rule30_center_column import generate_center_column_bitwise


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


def get_class_for_word(
    word: tuple[int, ...],
    h: int,
    q: dict[tuple[int, ...], int],
) -> int:
    """Given a boundary word of length h, simulate the driven right half from
    all-zeros for h steps and return the resulting class at horizon h.

    The word w = (b_0, b_1, ..., b_{h-1}) drives the system:
      s(0) = (0,...,0)
      s(t+1) = rule30_next(s(t), w[t])[:h]
    Return q[s(h)].
    """
    state = (0,) * h
    for b in word:
        nxt = rule30_next(state, b)[:h]
        state = nxt
    return q[state]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-horizon", type=int, default=14,
                        help="Maximum horizon h to analyze (default: 14)")
    parser.add_argument("--steps", type=int, default=500000,
                        help="Length of center-column prefix for subword discovery (default: 500000)")
    args = parser.parse_args()

    max_h = args.max_horizon
    steps = args.steps

    print(f"Generating {steps} center-column bits...")
    center = generate_center_column_bitwise(steps - 1)
    assert len(center) == steps
    print("Done.")
    print()

    print(f"Building quotient maps h=0..{max_h}...")
    quotients: dict[int, dict] = {}
    prev = None
    for h in range(max_h + 1):
        cm = build_quotient_at_horizon(h, prev)
        quotients[h] = cm
        prev = cm
    print("Done.")
    print()

    print("Subword complexity vs. class coverage analysis:")
    print()
    hdr = (
        f"{'h':>3} | {'2^h':>8} | {'|S_h|':>7} | {'k_c(h)':>8} | "
        f"{'classes_hit':>11} | {'all_S_h?':>8} | {'injective?':>10}"
    )
    print(hdr)
    print("-" * len(hdr))

    for h in range(1, max_h + 1):
        q = quotients[h]
        total_classes = max(q.values()) + 1
        n = len(center)

        # Collect all distinct length-h subwords of the center column
        # and their corresponding classes
        subwords_seen: dict[tuple[int, ...], int] = {}  # word -> class_id
        class_from_word: dict[tuple[int, ...], set[int]] = {}  # class -> set of words hit it

        for i in range(n - h + 1):
            word = tuple(center[i: i + h])
            if word not in subwords_seen:
                cid = get_class_for_word(word, h, q)
                subwords_seen[word] = cid
                if cid not in class_from_word:
                    class_from_word[cid] = set()
                class_from_word[cid].add(word)

        k_h = len(subwords_seen)  # subword complexity
        classes_hit = len(class_from_word)  # distinct classes covered by words
        all_s_h = classes_hit == total_classes
        # Injective: each class hit by exactly one word? No -- check if word-to-class is injective
        # (distinct words -> distinct classes)
        injective = (k_h == classes_hit)

        print(f"{h:>3} | {2**h:>8} | {total_classes:>7} | {k_h:>8} | "
              f"{classes_hit:>11} | {'yes' if all_s_h else 'no':>8} | "
              f"{'yes' if injective else 'no':>10}")

    print()
    print("Notes:")
    print("  k_c(h)      = number of distinct length-h subwords in the center-column prefix")
    print("  classes_hit = number of S_h classes reachable by steering with a length-h word")
    print("  all_S_h?    = do the subwords collectively hit all |S_h| classes?")
    print("  injective?  = do distinct subwords map to distinct classes (k_c(h) == classes_hit)?")
    print()
    print("Key implication: if k_c(h) >= |S_h| and the map is injective (or surjective),")
    print("then non-periodicity follows from |S_h| growing faster than any linear bound.")


if __name__ == "__main__":
    main()
