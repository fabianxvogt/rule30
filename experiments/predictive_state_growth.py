#!/usr/bin/env python3
"""
Fast computation of predictive-state quotient class counts for large horizons.

Instead of enumerating all 2^h boundary words, we compute the quotient algebras
recursively:

  Two width-h states A and B are horizon-h equivalent iff
    (a) A[0] == B[0]  (same first output bit; the adjacent column bit at this step)
    (b) for each boundary bit b in {0,1}:
          next(A, b) restricted to width h-1 is horizon-(h-1) equivalent to
          next(B, b) restricted to width h-1

where next(state, b) applies one Rule 30 step with boundary input b.

We build the equivalence partition horizon by horizon, starting at h=0 where all
empty states are trivially equivalent (one class), or from the first nontrivial
horizon h=1.

The state space at each horizon h is {0,1}^h. At h=1 there are 2 states; the
partition is refined as h grows.

This is O(2^h * h) per horizon rather than O(4^h) per horizon for the naive
enumeration, allowing us to push to h=20 or beyond.
"""

from __future__ import annotations

import argparse
from itertools import product


def rule30_next(state: tuple[int, ...], boundary_bit: int) -> tuple[int, ...]:
    """One step of Rule 30 on a finite right-half strip of width len(state).

    The strip represents cells at positions 1, 2, ..., w (right of center).
    - Position 1's left neighbor is the boundary bit (center column value).
    - Position w's right neighbor is always 0 (open boundary).

    Returns the next row of the same width.
    """
    w = len(state)
    if w == 0:
        return ()
    # Pad: left ghost = boundary_bit, right ghost = 0
    row = (boundary_bit,) + state + (0,)
    return tuple(row[i] ^ (row[i + 1] | row[i + 2]) for i in range(w))


def build_quotient_at_horizon(
    h: int,
    prev_class: dict[tuple[int, ...], int] | None,
) -> dict[tuple[int, ...], int]:
    """Build the horizon-h predictive-state class map.

    Each state is a tuple of h bits.  Two states are equivalent at horizon h iff
    they share the same label under the recursive criterion (see module docstring).

    prev_class maps width-(h-1) states to their horizon-(h-1) class ids.
    At h=0, prev_class is None (no previous level needed).
    """
    if h == 0:
        # Single trivial class: the empty state ().
        return {(): 0}

    # Build a canonical signature for each width-h state.
    # Signature: (first_output_bit,
    #             class_of_successor_on_0_at_h-1,
    #             class_of_successor_on_1_at_h-1)
    #
    # Note: successor on boundary bit b is a width-h state (we drop the last
    # cell to get width h-1 for querying prev_class).
    signatures: dict[tuple[int, ...], tuple] = {}
    for state in product(range(2), repeat=h):
        first_bit = state[0]  # output: the cell adjacent to the boundary
        if prev_class is None:
            # h=1; predecessor horizon is 0 => only one class (the empty state).
            sig = (first_bit, 0, 0)
        else:
            succ0 = rule30_next(state, 0)
            succ1 = rule30_next(state, 1)
            # Restrict successor to width h-1 to query prev_class.
            # The right-most cell "falls off" as the horizon shrinks.
            succ0_h1 = succ0[: h - 1]
            succ1_h1 = succ1[: h - 1]
            c0 = prev_class[succ0_h1]
            c1 = prev_class[succ1_h1]
            sig = (first_bit, c0, c1)
        signatures[state] = sig

    # Assign class ids by canonical signature.
    sig_to_id: dict[tuple, int] = {}
    state_to_class: dict[tuple[int, ...], int] = {}
    for state, sig in signatures.items():
        if sig not in sig_to_id:
            sig_to_id[sig] = len(sig_to_id)
        state_to_class[state] = sig_to_id[sig]

    return state_to_class


def build_transition_table(
    h: int,
    class_h: dict[tuple[int, ...], int],
    class_h1: dict[tuple[int, ...], int],
) -> dict[tuple[int, int], int]:
    """Build the transition table (class_id_at_h, boundary_bit) -> class_id_at_h-1.

    This should be well-defined (i.e., all states in the same class-at-h map to
    the same class-at-h-1 for each boundary bit).
    """
    transition: dict[tuple[int, int], int] = {}
    conflicts: list[str] = []
    for state, cid in class_h.items():
        for b in (0, 1):
            succ = rule30_next(state, b)
            succ_h1 = succ[: h - 1]
            target = class_h1[succ_h1]
            key = (cid, b)
            if key in transition:
                if transition[key] != target:
                    conflicts.append(f"conflict at class={cid} bit={b}")
            else:
                transition[key] = target
    if conflicts:
        raise ValueError(f"Transition not well-defined: {conflicts[:3]}")
    return transition


def analyze_class_growth(max_horizon: int) -> None:
    print(f"Computing predictive-state quotients up to horizon {max_horizon}...")
    print()

    all_class_maps: dict[int, dict[tuple[int, ...], int]] = {}
    class_counts: list[int] = []

    prev = None
    for h in range(max_horizon + 1):
        cm = build_quotient_at_horizon(h, prev)
        all_class_maps[h] = cm
        n_classes = max(cm.values()) + 1 if cm else 1
        class_counts.append(n_classes)
        prev = cm

    print("horizon | classes | raw_states | compression_ratio")
    print("--------|---------|------------|------------------")
    for h, n in enumerate(class_counts):
        raw = 2 ** h if h > 0 else 1
        ratio = raw / n
        print(f"  h={h:2d}  | {n:7d} | {raw:10d} | {ratio:.4f}")

    print()

    # Check differences and ratios to look for a pattern.
    print("Growth analysis (consecutive ratios and differences):")
    print("  h | classes | diff_from_prev | ratio_from_prev")
    print("  --|---------|----------------|----------------")
    for h in range(1, max_horizon + 1):
        n = class_counts[h]
        prev_n = class_counts[h - 1]
        diff = n - prev_n
        ratio = n / prev_n if prev_n > 0 else float("nan")
        print(f"  {h:2d} | {n:7d} | {diff:14d} | {ratio:.6f}")

    print()

    # Examine whether differences form a linear recurrence.
    # Compute second differences.
    diffs = [class_counts[h] - class_counts[h - 1] for h in range(1, max_horizon + 1)]
    print("First differences:", diffs)
    if len(diffs) >= 2:
        second_diffs = [diffs[i] - diffs[i - 1] for i in range(1, len(diffs))]
        print("Second differences:", second_diffs)
    if len(diffs) >= 3:
        third_diffs = [second_diffs[i] - second_diffs[i - 1] for i in range(1, len(second_diffs))]
        print("Third differences:", third_diffs)

    print()

    # Transition table checks at each horizon >= 1.
    print("Transition well-definedness checks:")
    all_well_defined = True
    for h in range(1, max_horizon + 1):
        if h == 0:
            continue
        cm_h = all_class_maps[h]
        cm_h1 = all_class_maps[h - 1]
        try:
            trans = build_transition_table(h, cm_h, cm_h1)
            n_classes_h = max(cm_h.values()) + 1
            targets_on_0 = len({trans[(c, 0)] for c in range(n_classes_h) if (c, 0) in trans})
            targets_on_1 = len({trans[(c, 1)] for c in range(n_classes_h) if (c, 1) in trans})
            print(
                f"  h={h}: well_defined=True  "
                f"domain={n_classes_h} targets_on_0={targets_on_0} targets_on_1={targets_on_1}"
            )
        except ValueError as e:
            print(f"  h={h}: well_defined=False  ({e})")
            all_well_defined = False

    print()
    if all_well_defined:
        print("All transitions well-defined: nested predictive-state system confirmed.")
    else:
        print("WARNING: Some transitions are not well-defined.")

    # At the max horizon, print the full transition table.
    h = max_horizon
    if h >= 1:
        cm_h = all_class_maps[h]
        cm_h1 = all_class_maps[h - 1]
        trans = build_transition_table(h, cm_h, cm_h1)
        n_classes = max(cm_h.values()) + 1
        print(f"\nFull transition table at h={h} ({n_classes} classes):")
        print("  class_id | on_0 | on_1 | representative_state")
        # Find a representative state for each class.
        representatives: dict[int, tuple[int, ...]] = {}
        for state, cid in cm_h.items():
            if cid not in representatives:
                representatives[cid] = state
        ids = sorted(range(n_classes))
        for cid in ids:
            rep = representatives.get(cid, ())
            rep_str = "".join(str(b) for b in rep)
            t0 = trans.get((cid, 0), -1)
            t1 = trans.get((cid, 1), -1)
            print(f"  {cid:8d} | {t0:4d} | {t1:4d} | {rep_str}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fast recursive computation of predictive-state quotient class counts."
    )
    parser.add_argument(
        "--max-horizon",
        type=int,
        default=16,
        help="Maximum horizon to compute (default: 16).",
    )
    args = parser.parse_args()
    analyze_class_growth(args.max_horizon)


if __name__ == "__main__":
    main()
